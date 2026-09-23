"""Reference identity, annotation controls and leakage-safe measurement utilities.

No function consumes structure reactivity. All coordinates are 0-based half-open.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import hashlib
import math
import re


def stable_id(identifier):
    # Preserve the pseudoautosomal copy suffix; X and Y are different loci.
    return re.sub(r'\.[0-9]+(?=(?:_PAR_Y)?$)', '', identifier)


def unique_index(records, key):
    result = defaultdict(list)
    for row in records:
        result[key(row)].append(row)
    return dict(result)


@dataclass(frozen=True)
class Transcript:
    identifier: str
    gene: str
    chrom: str
    strand: str
    exons: tuple
    biotype: str = 'unknown'

    @property
    def length(self):
        return sum(end-start for start, end in self.exons)

    @property
    def junctions(self):
        return tuple((a[1], b[0]) for a, b in zip(self.exons, self.exons[1:]))


def read_gtf(path):
    exons, info = defaultdict(list), {}
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as handle:
        for line in handle:
            if line.startswith('#'):
                continue
            fields = line.rstrip('\n').split('\t')
            if len(fields) != 9 or fields[2] != 'exon':
                continue
            attrs = dict(re.findall(r'(\w+) "([^"]*)"', fields[8]))
            tid = attrs['transcript_id']
            if 'transcript_version' in attrs and tid == stable_id(tid):
                tid += '.' + attrs['transcript_version']
            current = (stable_id(attrs['gene_id']), fields[0], fields[6],
                       attrs.get('transcript_biotype', attrs.get('transcript_type', 'unknown')))
            if tid in info and info[tid] != current:
                raise ValueError('Ambiguous transcript metadata: '+tid)
            info[tid] = current
            start, end = int(fields[3])-1, int(fields[4])
            if start < 0 or end <= start:
                raise ValueError('Invalid GTF interval')
            exons[tid].append((start, end))
    result = {}
    for tid, intervals in exons.items():
        intervals = tuple(sorted(intervals))
        if any(a[1] > b[0] for a, b in zip(intervals, intervals[1:])):
            raise ValueError('Duplicate or overlapping exons within transcript: '+tid)
        gene, chrom, strand, biotype = info[tid]
        result[tid] = Transcript(tid, gene, chrom, strand, intervals, biotype)
    return result


def fasta_records(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    name, parts = None, []
    with opener(path, 'rt') as handle:
        for line in handle:
            if line.startswith('>'):
                if name is not None:
                    yield name, ''.join(parts)
                name, parts = line[1:].split()[0], []
            else:
                parts.append(line.strip())
        if name is not None:
            yield name, ''.join(parts)


def reverse_complement(sequence):
    return sequence.upper().translate(str.maketrans('ACGTRYMKBDHVN', 'TGCAYRKMVHDBN'))[::-1]


def reconstruct(tx, genome):
    sequence = ''.join(str(genome[tx.chrom][start:end]) for start, end in tx.exons).upper()
    return reverse_complement(sequence) if tx.strand == '-' else sequence


def mapping_class(target, candidates, target_sequence=None, source_sequences=None,
                  reported_length=None, duplicate_target=False):
    """Fail closed: absent source definitions cannot establish equivalence."""
    if not candidates:
        return 'E', 'no_stable_id_candidate'
    if duplicate_target or len(candidates) != 1:
        return 'D', 'duplicate_stable_id'
    source = candidates[0]
    if source is None:
        return 'D', 'source_transcript_definition_unavailable'
    if target is None:
        return 'D', 'target_transcript_definition_unavailable'
    if stable_id(target.identifier) != stable_id(source.identifier):
        return 'E', 'no_stable_id_candidate'
    if (target.gene, target.chrom, target.strand, target.exons) != (
            source.gene, source.chrom, source.strand, source.exons):
        return 'C', 'gene_coordinate_or_exon_mismatch'
    if reported_length is not None and reported_length != target.length:
        return 'C', 'reported_length_mismatch'
    source_seq = (source_sequences or {}).get(source.identifier)
    if target_sequence is None or source_seq is None:
        return 'D', 'sequence_equivalence_unverified'
    if target_sequence.upper() != source_seq.upper():
        return 'C', 'sequence_mismatch'
    if len(target_sequence) != target.length:
        return 'D', 'target_reference_inconsistent'
    return ('A' if target.identifier == source.identifier else 'B'), 'definition_and_sequence_equivalent'


def sequence_features(sequence):
    """Simple prespecified composition features; no fitted feature selection."""
    import numpy as np
    seq = sequence.upper()
    n = len(seq)
    counts = Counter(seq)
    valid = sum(counts[b] for b in 'ACGT')
    entropy = -sum((counts[b]/valid)*math.log2(counts[b]/valid)
                   for b in 'ACGT' if counts[b]) if valid else math.nan
    homopolymer_bases = sum(len(m.group()) for m in re.finditer(r'A{6,}|C{6,}|G{6,}|T{6,}', seq))
    # Low complexity: fraction of fully ACGT 32-nt windows with mononucleotide H <1.5 bits.
    low = math.nan
    if n >= 32:
        arr = np.frombuffer(seq.encode('ascii'), dtype='S1')
        probs = []
        for base in (b'A', b'C', b'G', b'T'):
            cumulative = np.r_[0, np.cumsum(arr == base)]
            probs.append((cumulative[32:]-cumulative[:-32])/32)
        p = np.asarray(probs)
        callable_windows = p.sum(axis=0) == 1
        h = -(p*np.log2(np.where(p > 0, p, 1))).sum(axis=0)
        if callable_windows.any():
            low = float((h[callable_windows] < 1.5).mean())
    return dict(sequence_length=n, gc_fraction=(counts['G']+counts['C'])/valid if valid else math.nan,
                ambiguous_base_fraction=1-valid/n if n else math.nan,
                homopolymer_fraction=homopolymer_bases/n if n else math.nan,
                sequence_entropy=entropy, low_complexity_fraction=low,
                sequence_sha256=hashlib.sha256(seq.encode()).hexdigest())


def annotation_features(transcripts):
    """Exact exon/junction incidence controls, explicitly not miniQuant K-value."""
    import numpy as np
    by_gene = defaultdict(list)
    for tx in transcripts:
        by_gene[(tx.gene, tx.chrom, tx.strand)].append(tx)
    output = {}
    for (_, _, _), txs in by_gene.items():
        events = defaultdict(lambda: [set(), set()])
        for i, tx in enumerate(txs):
            for start, end in tx.exons:
                events[start][0].add(i); events[end][1].add(i)
        points, active, segments = sorted(events), set(), []
        for start, end in zip(points, points[1:]):
            active.difference_update(events[start][1]); active.update(events[start][0])
            if active:
                segments.append((end-start, frozenset(active)))
        junction_members = defaultdict(set)
        for i, tx in enumerate(txs):
            for junction in tx.junctions:
                junction_members[junction].add(i)
        memberships = {members for _, members in segments} | {frozenset(s) for s in junction_members.values()}
        matrix = np.zeros((len(memberships), len(txs)))
        for j, members in enumerate(sorted(memberships, key=lambda s: tuple(sorted(s)))):
            matrix[j, list(members)] = 1
        singular = np.linalg.svd(matrix, compute_uv=False)
        tolerance = max(matrix.shape)*np.finfo(float).eps*singular[0]
        rank = int((singular > tolerance).sum())
        condition = float(singular[0]/singular[-1]) if rank == len(txs) else math.inf
        overlap = np.zeros((len(txs), len(txs)), dtype=int)
        unique = np.zeros(len(txs), dtype=int)
        for length, members in segments:
            indices = list(members)
            overlap[np.ix_(indices, indices)] += length
            if len(indices) == 1:
                unique[indices[0]] += length
        for i, tx in enumerate(txs):
            similarities = [overlap[i,j]/(tx.length+other.length-overlap[i,j])
                            for j, other in enumerate(txs) if i != j]
            output[tx.identifier] = dict(
                isoforms_per_gene=len(txs), exon_count=len(tx.exons),
                unique_exonic_bases=int(unique[i]), shared_exon_fraction=1-unique[i]/tx.length,
                unique_junction_count=sum(len(junction_members[j])==1 for j in tx.junctions),
                max_exon_jaccard=max(similarities, default=0),
                identical_splice_chain_isoforms=sum(other.junctions == tx.junctions for other in txs),
                incidence_rank=rank, incidence_rank_deficiency=len(txs)-rank,
                incidence_condition_number=condition,
                genomic_span=tx.exons[-1][1]-tx.exons[0][0],
                mean_exon_length=tx.length/len(tx.exons))
    return output


def aggregate_technical(values, depths):
    if len(values) != len(depths) or not values or any(d <= 0 for d in depths):
        raise ValueError('Require matching finite positive technical depths')
    if not all(math.isfinite(x) and x >= 0 for x in values+depths):
        raise ValueError('Missing/invalid measurements cannot be zeros')
    return sum(v*d for v, d in zip(values, depths))/sum(depths)


def signed_endpoint(direct_rna, illumina, offset=0.1):
    from statistics import median
    if offset <= 0 or not direct_rna or not illumina:
        raise ValueError('Require positive offset and observations from both protocols')
    if not all(math.isfinite(x) and x >= 0 for x in direct_rna+illumina):
        raise ValueError('Missing/invalid values cannot enter endpoint')
    return median(math.log2(x+offset) for x in direct_rna)-median(math.log2(x+offset) for x in illumina)


def provisional_availability(exact_version_id, reason, callable_fraction,
                             callable_bases, min_fraction=0.5, min_bases=50):
    """Availability-only QC; this does not validate source exon/sequence identity."""
    if not exact_version_id or reason != 'icshape_source_exons_and_sequence_unavailable':
        return False
    if callable_fraction is None or callable_bases is None:
        return False
    return (math.isfinite(callable_fraction) and math.isfinite(callable_bases)
            and callable_fraction >= min_fraction and callable_bases >= min_bases)


def predictor_guard(columns, registry, endpoint_libraries=(), covariate_libraries=()):
    if set(endpoint_libraries) & set(covariate_libraries):
        raise ValueError('Endpoint and covariate libraries overlap')
    for col in columns:
        if col not in registry:
            raise ValueError('Unregistered predictor: '+col)
        if registry[col] not in {'PRE_MEASUREMENT_MOLECULAR', 'ANNOTATION', 'IDENTIFIABILITY'}:
            raise ValueError('Forbidden measurement/target-derived predictor: '+col)
        if any(token in col.lower() for token in ['shape', 'reactivity', 'structure', 'residual']):
            raise ValueError('Structure or residual features prohibited in Phase 3A')


def connected_groups(nodes, edges):
    parent = {node: node for node in nodes}
    def root(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    for a, b in edges:
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    return {node: root(node) for node in nodes}


def grouped_folds(groups, n_folds=5, seed=230923):
    """Deterministic hash-order greedy balancing, independent of outcomes."""
    counts = Counter(groups.values())
    if len(counts) < n_folds:
        raise ValueError('Insufficient independent groups')
    ordered = sorted(counts, key=lambda x: (-counts[x], hashlib.sha256(f'{seed}:{x}'.encode()).hexdigest()))
    sizes, assignment = [0]*n_folds, {}
    for group in ordered:
        fold = min(range(n_folds), key=lambda i: (sizes[i], i))
        assignment[group] = fold
        sizes[fold] += counts[group]
    return {node: assignment[group] for node, group in groups.items()}
