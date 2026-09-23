"""Outcome-independent mapping decisions and zero-aware measurement endpoints."""
import numpy as np


def detection_status(values, threshold, minimum_supported):
    """Classify replicates as present, absent, or indeterminate without imputation."""
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) == 0 or not np.isfinite(x).all():
        raise ValueError('Complete finite replicate vector required')
    if np.any(x < 0) or threshold <= 0 or not 1 <= minimum_supported <= len(x):
        raise ValueError('Invalid abundance, threshold, or support rule')
    supported = int(np.count_nonzero(x >= threshold))
    if supported >= minimum_supported:
        return 'detected'
    if supported == 0:
        return 'absent'
    return 'indeterminate'


def platform_category(illumina, direct_rna):
    if 'indeterminate' in (illumina, direct_rna):
        return 'indeterminate'
    if illumina == 'detected' and direct_rna == 'detected':
        return 'both'
    if illumina == 'detected':
        return 'illumina_only'
    if direct_rna == 'detected':
        return 'direct_rna_only'
    return 'neither'


def positive_log_ratio(illumina, direct_rna):
    """Conditional ratio; zeros are undefined, never pseudocounted."""
    i, d = np.asarray(illumina, dtype=float), np.asarray(direct_rna, dtype=float)
    if not len(i) or not len(d) or not np.isfinite(i).all() or not np.isfinite(d).all():
        raise ValueError('Complete finite abundance vectors required')
    if (i <= 0).any() or (d <= 0).any():
        return np.nan
    return float(np.median(np.log2(d)) - np.median(np.log2(i)))
