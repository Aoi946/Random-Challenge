import math
from collections import Counter
from statistics import mean, stdev

def redundancy(z, base=10):
    """
    Calculate the redundancy of a sequence based on Shannon's entropy.
    
    Redundancy = 1 - (Actual Entropy / Maximum Entropy)
    
    Parameters:
    -----------
    z : list or str
        A sequence of integers (0-9) or a string of digits
    base : int, optional
        The number base (default is 10 for digits 0-9)
        
    Returns:
    --------
    float
        Redundancy value between 0 (completely random) and 
        1 (completely predictable)
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]
    n = len(z)
    if n == 0:
        return 0.0

    freq = Counter(z)
    entropy = -sum((c/n) * math.log2(c/n) for c in freq.values())
    max_entropy = math.log2(base)
    return 1 - entropy / max_entropy

def coupon(z, base=10):
    """
    Calculate the coupon collector's score for a sequence.
    
    The coupon collector's problem measures how many samples (on average) are needed
    to collect a complete set of distinct items.
    
    Parameters:
    -----------
    z : list or str
        A sequence of integers (0-9) or a string of digits
    base : int, optional
        The number base (default is 10 for digits 0-9)
        
    Returns:
    --------
    dict
        Dictionary containing 'mean' and 'std' of the number of steps needed
        to collect all distinct digits
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]
    
    d = range(base)  # baseに対応した集合（例：base=10 → 0〜9）

    def has_all(t):
        return all(i in t for i in d)

    res = []
    for i in range(len(z)):
        tmp = []
        for j in range(len(z) - i):
            tmp.append(z[i + j])
            if has_all(tmp):
                res.append(j + 1)
                break

    if not res:
        return {'mean': len(z) + 1, 'std': len(z) + 1}

    return {'mean': mean(res), 'std': stdev(res) if len(res) > 1 else 0.0}

def repetition_gap(z, base=10):
    """
    Calculate the mean and std of the intervals between repeated appearances
    of the same digit.
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]
    
    d = range(base)
    gaps = []

    positions = {i: [] for i in d}
    for idx, val in enumerate(z):
        if val in positions:
            positions[val].append(idx)

    for indices in positions.values():
        for i in range(1, len(indices)):
            gaps.append(indices[i] - indices[i - 1])

    if not gaps:
        return {'mean': 0.0, 'std': 0.0}

    return {'mean': mean(gaps), 'std': stdev(gaps) if len(gaps) > 1 else 0.0}

def adjacent(z, base=10):
    """
    Calculate the adjacent order score of a sequence.
    
    This metric measures how often consecutive elements in the sequence
    increase or decrease by exactly 1. It returns the combined frequency
    of such ascending and descending steps, as a ratio in [0.0, 1.0].
    
    Parameters:
    -----------
    z : list or str
        A sequence of integers (0 to base-1) or a string of digits
    base : int, optional
        The number base (default is 10 for digits 0–9)
        
    Returns:
    --------
    float
        The proportion of adjacent pairs that differ by exactly ±1
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]

    n = len(z)
    if n < 2:
        return 0.0  # 1文字以下では隣接関係が定義できない

    up = down = 0
    for i in range(n - 1):
        if z[i + 1] == z[i] + 1:
            up += 1
        elif z[i + 1] == z[i] - 1:
            down += 1

    comb = (up + down) / (n - 1)
    return comb

def tpi(z, base=10):
    """
    Calculate the unscaled Turning Point Index (TPI) of a sequence.
    
    TPI measures how often a sequence switches between increasing
    and decreasing directions, normalized by the expected number of turning
    points for a random sequence of the same length.
    
    Parameters:
    -----------
    z : list or str
        A sequence of integers (0 to base-1) or a string of digits
    base : int, optional
        The number base (default is 10 for digits 0–9)
        
    Returns:
    --------
    float
        Unscaled Turning Point Index (TPI), where 1.0 is the expected value
        for a random sequence. Values > 1.0 indicate more turning points,
        < 1.0 fewer turning points.
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]
    
    m = len(z)
    if m < 3:
        return 0.0  # 定義できない

    # 差分列の符号（0は無視）
    diff = [z[i+1] - z[i] for i in range(m - 1)]
    diff = [d for d in diff if d != 0]

    tp = 0
    for i in range(1, len(diff)):
        if diff[i-1] * diff[i] < 0:
            tp += 1

    expected_tp = (2 / 3) * (m - 2)
    return tp / expected_tp if expected_tp > 0 else 0.0

# --- 共通ユーティリティ関数 ---

import random

# シード設定（再現性のため）
random.seed(42)

def _prepare_sequence(z):
    if isinstance(z, str):
        return [int(c) for c in z if c.isdigit()]
    return z

def _extract_tp_indices(z):
    diff = [z[i+1] - z[i] for i in range(len(z) - 1)]
    diff = [d for d in diff if d != 0]
    tp_indices = []
    for i in range(1, len(diff)):
        if diff[i - 1] * diff[i] < 0:
            tp_indices.append(i)
    return tp_indices

def _empirical_expected_pl(m, d, num_trials=10000, base=10):
    total = 0
    for _ in range(num_trials):
        rand_seq = [random.randint(0, base - 1) for _ in range(m)]
        tp_indices = _extract_tp_indices(rand_seq)
        count = 0
        for i in range(1, len(tp_indices)):
            gap = tp_indices[i] - tp_indices[i - 1]
            if gap == d:
                count += 1
        total += count
    return total / num_trials

def _pl_d(z, d, base=10):
    z = _prepare_sequence(z)
    m = len(z)
    if m < d + 3:
        return 0.0

    tp_indices = _extract_tp_indices(z)

    observed = 0
    for i in range(1, len(tp_indices)):
        gap = tp_indices[i] - tp_indices[i - 1]
        if gap == d:
            observed += 1

    expected = _empirical_expected_pl(m, d, num_trials=1000, base=base)
    return observed / expected if expected > 0 else 0.0

def pl1(z, base=10):
    """Calculate Phase Length PL(d=1)"""
    return _pl_d(z, d=1, base=base)

def pl2(z, base=10):
    """Calculate Phase Length PL(d=2)"""
    return _pl_d(z, d=2, base=base)

def pl3(z, base=10):
    """Calculate Phase Length PL(d=3)"""
    return _pl_d(z, d=3, base=base)

def pl4(z, base=10):
    """Calculate Phase Length PL(d=4)"""
    return _pl_d(z, d=4, base=base)

def pl5(z, base=10):
    """Calculate Phase Length PL(d=5)"""
    return _pl_d(z, d=5, base=base)



def rp(z, base=10):
    """
    Calculate Repeat Pattern (RP) score of a sequence.
    
    RP measures the degree of repeated adjacent pairs (bigrams) in a sequence.
    A higher score means more repetition of local patterns.
    
    Parameters:
    -----------
    z : list or str
        A sequence of integers (0 to base-1) or a string of digits
    base : int, optional
        The number base (default is 10 for digits 0–9)
        
    Returns:
    --------
    float
        The RP score in range [0.0, 1.0], where higher means more repeated bigrams
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]
    
    m = len(z)
    if m < 2:
        return 0.0  # バイグラムが1つもない場合

    # すべての隣接2文字のペア（バイグラム）を取得
    bigrams = [(z[i], z[i+1]) for i in range(m - 1)]
    counts = Counter(bigrams)

    # 一度しか出なかったものの数（NRS）
    nrs = sum(1 for v in counts.values() if v == 1)

    rp_score = 1 - nrs / (m - 1)
    return rp_score

def autocorr_lag1(z, base=10):
    """
    Calculate the lag-1 autocorrelation of the sequence.
    
    This measures the linear relationship between each value 
    and its immediate predecessor.

    Parameters:
    -----------
    z : list or str
        A sequence of integers (0 to base-1) or a string of digits
    base : int, optional
        The number base (default is 10)

    Returns:
    --------
    float
        Lag-1 autocorrelation coefficient
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]

    n = len(z)
    if n < 2:
        return 0.0

    m_z = mean(z)
    numerator = sum((z[i] - m_z) * (z[i - 1] - m_z) for i in range(1, n))
    denominator = sum((v - m_z) ** 2 for v in z)
    return numerator / denominator if denominator != 0 else 0.0

def adjacent_diff_stats(z, base=10):
    """
    Calculate the mean and standard deviation of differences 
    between adjacent digits in the sequence.

    Parameters:
    -----------
    z : list or str
        A sequence of integers (0 to base-1) or a string of digits
    base : int, optional
        The number base (default is 10)

    Returns:
    --------
    dict
        Dictionary with 'adjacent_diff_mean' and 'adjacent_diff_std'
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]

    if len(z) < 2:
        return {'adjacent_diff_mean': 0.0, 'adjacent_diff_std': 0.0}

    diffs = [abs(z[i + 1] - z[i]) for i in range(len(z) - 1)]
    return {
        'adjacent_diff_mean': mean(diffs),
        'adjacent_diff_std': stdev(diffs) if len(diffs) > 1 else 0.0
    }

def max_min_ratio(z, base=10):
    """
    Calculate the ratio of maximum to minimum digit frequencies.

    Parameters:
    -----------
    z : list or str
        A sequence of integers (0 to base-1) or a string of digits
    base : int, optional
        The number base (default is 10)

    Returns:
    --------
    float
        Ratio of max frequency to min frequency among digits
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]

    freq = Counter(z)
    if not freq:
        return 0.0

    max_f = max(freq.values())
    min_f = min(freq.values())
    return max_f / min_f if min_f > 0 else float('inf')

def max_min_ratio(z, base=10):
    """
    Calculate the ratio of maximum to minimum digit frequencies.

    Parameters:
    -----------
    z : list or str
        A sequence of integers (0 to base-1) or a string of digits
    base : int, optional
        The number base (default is 10)

    Returns:
    --------
    float
        Ratio of max frequency to min frequency among digits
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]

    freq = Counter(z)
    if not freq:
        return 0.0

    max_f = max(freq.values())
    min_f = min(freq.values())
    return max_f / min_f if min_f > 0 else float('inf')

def digit_frequencies(z, base=10):
    """
    Calculate normalized frequency of each digit in the sequence.

    Parameters:
    -----------
    z : list or str
        A sequence of integers (0 to base-1) or a string of digits
    base : int, optional
        The number base (default is 10)

    Returns:
    --------
    dict
        Dictionary with keys 'freq_0' to 'freq_{base-1}'
        and values representing relative frequencies.
    """
    if isinstance(z, str):
        z = [int(c) for c in z if c.isdigit()]

    n = len(z)
    freq = Counter(z)
    return {f'freq_{i}': freq.get(i, 0) / n if n > 0 else 0.0 for i in range(base)}
