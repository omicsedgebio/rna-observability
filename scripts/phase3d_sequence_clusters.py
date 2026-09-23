#!/usr/bin/env python3
"""Cluster eligible transcript sequences for leakage-safe grouped folds.

Only Ensembl reference sequence, gene identity and the pre-endpoint cohort are
used. No abundance, structure or outcome file is read.
"""
from collections import defaultdict
from pathlib import Path
import csv, gzip, hashlib, json, re, subprocess
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'metadata/final_transcript_cohort.tsv'
GTF = ROOT / '.cache/phase3a/references/ensembl91.gtf.gz'
FASTA = [ROOT / '.cache/phase3a/references/ensembl91.cdna.fa.gz',
         ROOT / '.cache/phase3a/references/ensembl91.ncrna.fa.gz']
CACHE = ROOT / '.cache/phase3d'
FA = CACHE / 'eligible_transcripts.fa'
DB = CACHE / 'eligible_db'
HITS = CACHE / 'blast95.tsv'
OUT = ROOT / 'metadata/transcript_sequence_clusters.tsv'
SUMMARY = ROOT / 'results/tables/phase3d_sequence_cluster_summary.tsv'


class UnionFind:
    def __init__(self, values): self.parent = {x: x for x in values}
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]; x = self.parent[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b: self.parent[b] = a


def stable(tid):
    return re.sub(r'\.[0-9]+(?=(?:_PAR_Y)?$)', '', tid)


def sequences(paths, wanted):
    found = {}
    for path in paths:
        with gzip.open(path, 'rt') as stream:
            name = None; parts = []
            for line in stream:
                if line.startswith('>'):
                    if name is not None and stable(name) in wanted and stable(name) not in found:
                        found[stable(name)] = ''.join(parts).upper()
                    name, parts = line[1:].split()[0], []
                else: parts.append(line.strip())
            if name is not None and stable(name) in wanted and stable(name) not in found:
                found[stable(name)] = ''.join(parts).upper()
    return found


def genes_from_gtf(wanted):
    result = {}
    with gzip.open(GTF, 'rt') as stream:
        for line in stream:
            if line.startswith('#') or '\texon\t' not in line: continue
            fields = line.rstrip('\n').split('\t')
            attrs = dict(re.findall(r'(\w+) "([^"]*)"', fields[8]))
            tid = stable(attrs.get('transcript_id', ''))
            if tid in wanted: result[tid] = stable(attrs.get('gene_id', 'NA'))
    return result


def run_blast():
    CACHE.mkdir(parents=True, exist_ok=True)
    if not FA.exists():
        wanted = set(pd.read_csv(COHORT, sep='\t').stable_id)
        seq = sequences(FASTA, wanted)
        if set(seq) != wanted: raise ValueError(f'missing reference sequences: {len(wanted-set(seq))}')
        with FA.open('w') as stream:
            for tid in sorted(seq): stream.write(f'>{tid}\n{seq[tid]}\n')
    if not (DB.with_suffix('.nhr')).exists():
        subprocess.run(['makeblastdb', '-in', str(FA), '-dbtype', 'nucl', '-out', str(DB), '-parse_seqids'], check=True)
    if not HITS.exists():
        subprocess.run(['blastn', '-task', 'megablast', '-query', str(FA), '-db', str(DB),
                        '-perc_identity', '95', '-qcov_hsp_perc', '90', '-evalue', '1e-20',
                        '-max_target_seqs', '100000', '-num_threads', '4', '-outfmt',
                        '6 qseqid sseqid pident length qlen slen qcovhsp', '-out', str(HITS)], check=True)


def edges(threshold):
    out = []
    with HITS.open() as stream:
        for line in stream:
            q, s, ident, length, qlen, slen, qcov = line.rstrip('\n').split('\t')
            if q == s: continue
            if float(ident) >= threshold and int(length) / min(int(qlen), int(slen)) >= .90:
                out.append((q, s))
    return out


def main():
    cohort = pd.read_csv(COHORT, sep='\t', usecols=['stable_id'])
    wanted = set(cohort.stable_id)
    genes = genes_from_gtf(wanted)
    if set(genes) != wanted: raise ValueError(f'missing GTF genes: {len(wanted-set(genes))}')
    run_blast()
    all_ids = sorted(wanted)
    summaries = []
    assignments = {}
    for threshold in (99.0, 95.0):
        uf = UnionFind(all_ids)
        for q, s in edges(threshold): uf.union(q, s)
        # Same-gene transcripts are always one dependency group.
        by_gene = defaultdict(list)
        for tid, gene in genes.items(): by_gene[gene].append(tid)
        for members in by_gene.values():
            for tid in members[1:]: uf.union(members[0], tid)
        groups = defaultdict(list)
        for tid in all_ids: groups[uf.find(tid)].append(tid)
        gene_sets = {root: {genes[t] for t in members} for root, members in groups.items()}
        summaries.append(dict(identity_threshold=threshold, coverage_threshold=0.90,
            n_transcripts=len(all_ids), n_clusters=len(groups),
            singleton_count=sum(len(x) == 1 for x in groups.values()),
            largest_cluster=max(map(len, groups.values())),
            clusters_with_multiple_genes=sum(len(x) > 1 for x in gene_sets.values()),
            max_genes_in_cluster=max(map(len, gene_sets.values())),
            edges=sum(1 for q, s in edges(threshold)), structure_inputs_read=False,
            sequencing_outcomes_read=False, longbench_inputs_read=False))
        if threshold == 95.0:
            # Stable cluster labels are hash-derived from member IDs and do not
            # depend on union-find traversal order.
            for members in groups.values():
                label = 'SC' + hashlib.sha256('\n'.join(sorted(members)).encode()).hexdigest()[:12]
                for tid in members: assignments[tid] = label
            with (CACHE / 'cluster_members.tsv').open('w') as stream:
                stream.write('stable_id\tgene_id\tsequence_cluster_id\n')
                for tid in all_ids: stream.write(f'{tid}\t{genes[tid]}\t{assignments[tid]}\n')
    with OUT.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['stable_id', 'sequence_cluster_id'], delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows({'stable_id': t, 'sequence_cluster_id': assignments[t]} for t in all_ids)
    with SUMMARY.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(summaries)
    print(json.dumps({'primary_threshold': 95.0, 'coverage_threshold': .90,
                      'n_transcripts': len(all_ids), 'summary': summaries,
                      'structure_inputs_read': False, 'sequencing_outcomes_read': False}, indent=2))


if __name__ == '__main__': main()
