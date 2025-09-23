#!/usr/bin/env python3
"""
Randomness Checker: Test if a sequence exhibits true randomness

This module provides functions to check if computed statistical metrics
indicate that a sequence is truly random (like MT-generated sequences)
or contains non-random patterns (like human-generated sequences).
"""

import pandas as pd
import numpy as np
import os

def check_sequence_randomness(test_metrics, bounds_table=None, confidence_level=95):
    """
    Check if computed metrics indicate randomness.

    Parameters:
    -----------
    test_metrics : dict
        Computed metrics for your 300-digit sequence
        Keys should match metric names in bounds table
    bounds_table : pd.DataFrame, optional
        Bounds table. If None, loads from 'mt_randomness_bounds.csv'
    confidence_level : int
        Use 95 or 99 for different strictness levels

    Returns:
    --------
    dict : Results showing which metrics are outliers
    """

    if bounds_table is None:
        try:
            # Try to load from same directory as this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bounds_path = os.path.join(script_dir, 'mt_randomness_bounds.csv')
            bounds_table = pd.read_csv(bounds_path)
        except FileNotFoundError:
            try:
                # Try current working directory
                bounds_table = pd.read_csv('mt_randomness_bounds.csv')
            except FileNotFoundError:
                raise FileNotFoundError("bounds table not found. Please ensure 'mt_randomness_bounds.csv' exists in the same directory or current working directory.")

    outliers = []
    within_bounds = []
    missing_metrics = []

    bound_col = f'bound_{confidence_level}_'

    for _, row in bounds_table.iterrows():
        metric = row['metric']

        if metric not in test_metrics:
            missing_metrics.append(metric)
            continue

        value = test_metrics[metric]
        lower = row[bound_col + 'lower']
        upper = row[bound_col + 'upper']

        if lower <= value <= upper:
            within_bounds.append({
                'metric': metric,
                'value': value,
                'expected_range': [lower, upper],
                'distance_from_mean': abs(value - row['expected_mean']) / row['expected_std']
            })
        else:
            # Calculate severity of outlier
            if value < lower:
                distance_from_bound = lower - value
                relative_distance = distance_from_bound / (row['expected_mean'] if row['expected_mean'] > 0 else 1)
                direction = 'below'
            else:
                distance_from_bound = value - upper
                relative_distance = distance_from_bound / (row['expected_mean'] if row['expected_mean'] > 0 else 1)
                direction = 'above'

            severity = 'extreme' if relative_distance > 1.0 else 'high' if relative_distance > 0.5 else 'moderate'

            outliers.append({
                'metric': metric,
                'value': value,
                'expected_range': [lower, upper],
                'distance_from_bound': distance_from_bound,
                'relative_distance': relative_distance,
                'direction': direction,
                'severity': severity,
                'std_distance': abs(value - row['expected_mean']) / row['expected_std'],
                'interpretation': row['interpretation']
            })

    total_tested = len(within_bounds) + len(outliers)
    randomness_score = len(within_bounds) / total_tested if total_tested > 0 else 0

    # Determine overall assessment
    if randomness_score > 0.90:
        assessment = 'highly_likely_random'
    elif randomness_score > 0.80:
        assessment = 'likely_random'
    elif randomness_score > 0.70:
        assessment = 'possibly_random'
    elif randomness_score > 0.50:
        assessment = 'possibly_non_random'
    else:
        assessment = 'likely_non_random'

    # Count severe outliers
    severe_outliers = [o for o in outliers if o['severity'] in ['high', 'extreme']]

    return {
        'randomness_score': randomness_score,
        'assessment': assessment,
        'confidence_level': confidence_level,
        'total_metrics_tested': total_tested,
        'within_bounds_count': len(within_bounds),
        'outlier_count': len(outliers),
        'severe_outlier_count': len(severe_outliers),
        'missing_metrics_count': len(missing_metrics),
        'outliers': outliers,
        'within_bounds': within_bounds,
        'missing_metrics': missing_metrics
    }

def print_randomness_report(result):
    """
    Print a detailed report of the randomness analysis.

    Parameters:
    -----------
    result : dict
        Result from check_sequence_randomness()
    """
    print("RANDOMNESS ANALYSIS REPORT")
    print("=" * 50)

    print(f"Overall Assessment: {result['assessment'].upper()}")
    print(f"Randomness Score: {result['randomness_score']:.3f}")
    print(f"Confidence Level: {result['confidence_level']}%")
    print()

    print(f"Metrics Analysis:")
    print(f"  Total tested: {result['total_metrics_tested']}")
    print(f"  Within bounds: {result['within_bounds_count']}")
    print(f"  Outliers: {result['outlier_count']}")
    print(f"  Severe outliers: {result['severe_outlier_count']}")
    if result['missing_metrics_count'] > 0:
        print(f"  Missing metrics: {result['missing_metrics_count']}")
    print()

    if result['outliers']:
        print("OUTLIER METRICS (suggest non-randomness):")
        print("-" * 40)
        for outlier in sorted(result['outliers'], key=lambda x: x['relative_distance'], reverse=True):
            print(f"{outlier['metric']:18} | {outlier['value']:8.4f} | "
                  f"Expected: [{outlier['expected_range'][0]:6.3f}, {outlier['expected_range'][1]:6.3f}] | "
                  f"{outlier['direction']:5} | {outlier['severity']:8}")
        print()

    if result['severe_outlier_count'] > 0:
        print("INTERPRETATION OF SEVERE OUTLIERS:")
        print("-" * 35)
        for outlier in [o for o in result['outliers'] if o['severity'] in ['high', 'extreme']]:
            print(f"• {outlier['metric']}: {outlier['interpretation']}")
        print()

    # Provide recommendations
    print("RECOMMENDATIONS:")
    print("-" * 15)
    if result['assessment'] in ['highly_likely_random', 'likely_random']:
        print("✓ Sequence appears to be truly random (similar to MT-generated)")
        print("✓ No strong evidence of human patterns or biases")
    elif result['assessment'] == 'possibly_random':
        print("? Sequence may be random, but shows some unusual characteristics")
        print("? Consider additional testing or larger sample size")
    else:
        print("✗ Sequence likely contains non-random patterns")
        print("✗ Strong evidence suggests human generation or biased algorithm")

        # Highlight key indicators
        key_indicators = []
        for outlier in result['outliers']:
            if outlier['metric'] == 'redundancy' and outlier['direction'] == 'above':
                key_indicators.append("High redundancy indicates predictable patterns")
            elif outlier['metric'] == 'autocorr_lag1' and abs(outlier['value']) > 0.15:
                key_indicators.append("Strong autocorrelation suggests sequential dependencies")
            elif outlier['metric'].startswith('freq_') and outlier['severity'] in ['high', 'extreme']:
                key_indicators.append("Digit frequency imbalance suggests human bias")
            elif outlier['metric'] == 'coupon_mean' and outlier['direction'] == 'below':
                key_indicators.append("Fast coupon collection suggests digit clustering")
            elif outlier['metric'] == 'tpi' and outlier['direction'] == 'below':
                key_indicators.append("Low turning points suggest monotonic trends")

        if key_indicators:
            print("\nKey indicators of non-randomness:")
            for indicator in key_indicators[:3]:  # Show top 3
                print(f"  • {indicator}")

def get_required_metrics():
    """
    Get the list of all 27 required metrics.

    Returns:
    --------
    list : List of metric names
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bounds_path = os.path.join(script_dir, 'mt_randomness_bounds.csv')
        bounds = pd.read_csv(bounds_path)
        return bounds['metric'].tolist()
    except FileNotFoundError:
        return [
            'redundancy', 'coupon_mean', 'coupon_std', 'repetition_gap_mean', 'repetition_gap_std',
            'adjacent', 'tpi', 'pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'rp', 'autocorr_lag1',
            'adjacent_diff_mean', 'adjacent_diff_std', 'max_min_ratio',
            'freq_0', 'freq_1', 'freq_2', 'freq_3', 'freq_4', 'freq_5', 'freq_6', 'freq_7', 'freq_8', 'freq_9'
        ]

def example_usage():
    """
    Example of how to use the randomness checker.
    """
    print("EXAMPLE USAGE")
    print("=" * 20)

    # Example: A sequence that might appear non-random
    test_metrics_non_random = {
        'redundancy': 0.045,          # High (above 0.020)
        'coupon_mean': 22.0,          # Low (below 25.0)
        'coupon_std': 8.5,            # Within bounds
        'repetition_gap_mean': 7.2,   # Low (below 8.0)
        'repetition_gap_std': 8.8,    # Within bounds
        'adjacent': 0.19,             # Within bounds
        'tpi': 0.75,                  # Low (below 0.85)
        'pl1': 1.5,                   # High (above 1.2)
        'pl2': 1.1,                   # Within bounds
        'pl3': 1.2,                   # Within bounds
        'pl4': 0.8,                   # Within bounds
        'pl5': 1.5,                   # Within bounds
        'rp': 0.88,                   # Within bounds
        'autocorr_lag1': 0.25,        # High (above 0.15)
        'adjacent_diff_mean': 2.5,    # Low (below 3.0)
        'adjacent_diff_std': 2.2,     # Within bounds
        'max_min_ratio': 3.2,         # High (above 2.5)
        'freq_0': 0.18,               # High (above 0.14)
        'freq_1': 0.09,               # Within bounds
        'freq_2': 0.11,               # Within bounds
        'freq_3': 0.08,               # Within bounds
        'freq_4': 0.12,               # Within bounds
        'freq_5': 0.03,               # Low (below 0.06)
        'freq_6': 0.10,               # Within bounds
        'freq_7': 0.07,               # Within bounds
        'freq_8': 0.11,               # Within bounds
        'freq_9': 0.09,               # Within bounds
    }

    print("Testing a potentially non-random sequence...")
    result = check_sequence_randomness(test_metrics_non_random, confidence_level=95)
    print_randomness_report(result)

    print("\n" + "="*50)
    print("EXAMPLE: RANDOM-LIKE SEQUENCE")
    print("="*50)

    # Example: A sequence that appears more random
    test_metrics_random = {
        'redundancy': 0.012,          # Within bounds
        'coupon_mean': 28.5,          # Within bounds
        'coupon_std': 9.2,            # Within bounds
        'repetition_gap_mean': 9.3,   # Within bounds
        'repetition_gap_std': 8.9,    # Within bounds
        'adjacent': 0.16,             # Within bounds
        'tpi': 0.94,                  # Within bounds
        'pl1': 1.05,                  # Within bounds
        'pl2': 0.98,                  # Within bounds
        'pl3': 0.9,                   # Within bounds
        'pl4': 0.4,                   # Within bounds
        'pl5': 1.2,                   # Within bounds
        'rp': 0.96,                   # Within bounds
        'autocorr_lag1': 0.08,        # Within bounds
        'adjacent_diff_mean': 3.35,   # Within bounds
        'adjacent_diff_std': 2.4,     # Within bounds
        'max_min_ratio': 1.6,         # Within bounds
        'freq_0': 0.11,               # Within bounds
        'freq_1': 0.09,               # Within bounds
        'freq_2': 0.10,               # Within bounds
        'freq_3': 0.12,               # Within bounds
        'freq_4': 0.08,               # Within bounds
        'freq_5': 0.11,               # Within bounds
        'freq_6': 0.09,               # Within bounds
        'freq_7': 0.10,               # Within bounds
        'freq_8': 0.11,               # Within bounds
        'freq_9': 0.09,               # Within bounds
    }

    print("Testing a random-like sequence...")
    result = check_sequence_randomness(test_metrics_random, confidence_level=95)
    print_randomness_report(result)

if __name__ == "__main__":
    # Load bounds table to verify it exists
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bounds_path = os.path.join(script_dir, 'mt_randomness_bounds.csv')
        bounds = pd.read_csv(bounds_path)
        print(f"Loaded bounds for {len(bounds)} metrics")
        print("\nAvailable metrics:")
        for i, metric in enumerate(bounds['metric'], 1):
            print(f"{i:2d}. {metric}")
        print()

        # Run example
        example_usage()

    except FileNotFoundError:
        print("Error: mt_randomness_bounds.csv not found")
        print("Please ensure the bounds file is in the same directory as this script")

        print("\nRequired metrics:")
        required = get_required_metrics()
        for i, metric in enumerate(required, 1):
            print(f"{i:2d}. {metric}")