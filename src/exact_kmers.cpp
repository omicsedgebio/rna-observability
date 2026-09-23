// Exact canonical k-mer membership across transcripts using bounded disk buckets.
// Each transcript contributes each distinct k-mer once; repeats within it do not
// create false ambiguity. 2-bit encoding is collision-free for k <= 31.
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

struct Entry { uint64_t kmer; uint32_t transcript; };
static uint64_t mix(uint64_t x) {
    x ^= x >> 30; x *= 0xbf58476d1ce4e5b9ULL;
    x ^= x >> 27; x *= 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}
static int base(char c) {
    switch(std::toupper(static_cast<unsigned char>(c))) {
        case 'A': return 0; case 'C': return 1; case 'G': return 2; case 'T': return 3;
        default: return -1;
    }
}
int main(int argc, char** argv) {
    try {
        if(argc != 5) throw std::runtime_error("usage: exact_kmers fasta k scratch output.tsv");
        const int k=std::stoi(argv[2]);
        if(k<1 || k>31) throw std::runtime_error("k must be 1..31");
        const uint64_t mask=(1ULL << (2*k))-1;
        std::filesystem::path scratch(argv[3]);
        std::filesystem::create_directories(scratch);
        constexpr int buckets=128;
        std::array<std::ofstream, buckets> streams;
        for(int b=0;b<buckets;++b) {
            streams[b].open(scratch/(std::to_string(b)+".bin"),std::ios::binary|std::ios::trunc);
            if(!streams[b]) throw std::runtime_error("cannot open scratch bucket");
        }
        std::vector<std::string> names;
        std::vector<uint64_t> total, unique;
        std::set<std::string> seen;
        std::string name, sequence, line;
        auto emit = [&]() {
            if(name.empty()) return;
            if(!seen.insert(name).second) throw std::runtime_error("duplicate FASTA identifier");
            if(names.size()>=std::numeric_limits<uint32_t>::max()) throw std::runtime_error("too many transcripts");
            uint32_t id=static_cast<uint32_t>(names.size());
            names.push_back(name);
            std::vector<uint64_t> kmers;
            uint64_t fwd=0,rev=0; int n=0;
            for(char c:sequence) {
                int v=base(c);
                if(v<0) { fwd=rev=0; n=0; continue; }
                fwd=((fwd<<2)|v)&mask;
                rev=(rev>>2)|(static_cast<uint64_t>(3-v)<<(2*(k-1)));
                if(++n>=k) kmers.push_back(std::min(fwd,rev));
            }
            std::sort(kmers.begin(),kmers.end());
            kmers.erase(std::unique(kmers.begin(),kmers.end()),kmers.end());
            total.push_back(kmers.size()); unique.push_back(0);
            for(auto value:kmers) {
                auto &stream=streams[mix(value)%buckets];
                stream.write(reinterpret_cast<const char*>(&value),sizeof(value));
                stream.write(reinterpret_cast<const char*>(&id),sizeof(id));
                if(!stream) throw std::runtime_error("scratch write failure");
            }
        };
        std::ifstream fasta(argv[1]);
        if(!fasta) throw std::runtime_error("cannot open FASTA");
        while(std::getline(fasta,line)) {
            if(line.empty()) continue;
            if(line.front()=='>') {
                emit(); name=line.substr(1,line.find_first_of(" \t\r")-1); sequence.clear();
            } else {
                for(char c:line) if(!std::isspace(static_cast<unsigned char>(c))) sequence+=c;
            }
        }
        emit();
        for(auto &stream:streams) stream.close();
        for(int b=0;b<buckets;++b) {
            auto path=scratch/(std::to_string(b)+".bin");
            std::ifstream input(path,std::ios::binary);
            std::vector<Entry> entries;
            entries.reserve(std::filesystem::file_size(path)/12);
            Entry entry;
            while(input.read(reinterpret_cast<char*>(&entry.kmer),8)) {
                if(!input.read(reinterpret_cast<char*>(&entry.transcript),4)) throw std::runtime_error("truncated bucket");
                entries.push_back(entry);
            }
            std::sort(entries.begin(),entries.end(),[](const Entry&a,const Entry&b){
                return a.kmer<b.kmer || (a.kmer==b.kmer && a.transcript<b.transcript);
            });
            for(size_t i=0;i<entries.size();) {
                size_t j=i+1;
                while(j<entries.size() && entries[j].kmer==entries[i].kmer) ++j;
                if(j==i+1) ++unique[entries[i].transcript];
                i=j;
            }
            input.close(); std::filesystem::remove(path);
        }
        std::ofstream output(argv[4]);
        if(!output) throw std::runtime_error("cannot open output");
        output.precision(12);
        output<<"transcript_id\tk\tdistinct_valid_kmers\ttranscript_unique_kmers\tunique_kmer_fraction\n";
        for(size_t i=0;i<names.size();++i) {
            output<<names[i]<<'\t'<<k<<'\t'<<total[i]<<'\t'<<unique[i]<<'\t';
            if(total[i]) output<<static_cast<double>(unique[i])/total[i]; else output<<"NA";
            output<<'\n';
        }
        if(!output) throw std::runtime_error("output write failure");
        std::cerr<<"Exact canonical k-mer membership complete: "<<names.size()<<" transcripts\n";
    } catch(const std::exception &e) { std::cerr<<e.what()<<'\n'; return 1; }
}
