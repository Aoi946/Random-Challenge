#!/usr/bin/env python3
"""
Example Usage of Randomness Checker

This script demonstrates various ways to use the randomness checker
to evaluate sequences for true randomness vs human-generated patterns.
"""

import pandas as pd
from randomness_checker import check_sequence_randomness, print_randomness_report, get_required_metrics

def demo_basic_usage():
    """
    Demonstrate basic usage of the randomness checker.
    """
    print("DEMO: Basic Usage")
    print("=" * 30)

    # Example metrics for a potentially non-random sequence
    test_metrics = {
        'redundancy': 0.045,          # High - suggests patterns
        'coupon_mean': 22.0,          # Low - suggests clustering
        'coupon_std': 8.5,            # Normal
        'repetition_gap_mean': 7.2,   # Low - suggests frequent repetitions
        'repetition_gap_std': 8.8,    # Normal
        'adjacent': 0.19,             # Normal
        'tpi': 0.75,                  # Low - suggests monotonic trends
        'pl1': 1.5,                   # High - suggests patterns
        'pl2': 1.1,                   # Normal
        'pl3': 1.2,                   # Normal
        'pl4': 0.8,                   # Normal
        'pl5': 1.5,                   # Normal
        'rp': 0.88,                   # Normal
        'autocorr_lag1': 0.25,        # High - suggests correlation
        'adjacent_diff_mean': 2.5,    # Low - suggests small differences
        'adjacent_diff_std': 2.2,     # Normal
        'max_min_ratio': 3.2,         # High - suggests imbalance
        'freq_0': 0.18,               # High - overused digit
        'freq_1': 0.09,               # Normal
        'freq_2': 0.11,               # Normal
        'freq_3': 0.08,               # Normal
        'freq_4': 0.12,               # Normal
        'freq_5': 0.03,               # Low - avoided digit
        'freq_6': 0.10,               # Normal
        'freq_7': 0.07,               # Normal
        'freq_8': 0.11,               # Normal
        'freq_9': 0.09,               # Normal
    }

    # Check randomness
    result = check_sequence_randomness(test_metrics, confidence_level=95)

    # Print detailed report
    print_randomness_report(result)

    return result

def demo_random_sequence():
    """
    Demonstrate checker with a random-like sequence.
    """
    print("\nDEMO: Random-like Sequence")
    print("=" * 35)

    # Example metrics for a random-like sequence
    random_metrics = {
        'redundancy': 0.012,          # Normal - good randomness
        'coupon_mean': 28.5,          # Normal
        'coupon_std': 9.2,            # Normal
        'repetition_gap_mean': 9.3,   # Normal
        'repetition_gap_std': 8.9,    # Normal
        'adjacent': 0.16,             # Normal
        'tpi': 0.94,                  # Normal
        'pl1': 1.05,                  # Normal
        'pl2': 0.98,                  # Normal
        'pl3': 0.9,                   # Normal
        'pl4': 0.4,                   # Normal
        'pl5': 1.2,                   # Normal
        'rp': 0.96,                   # Normal
        'autocorr_lag1': 0.08,        # Normal - low correlation
        'adjacent_diff_mean': 3.35,   # Normal
        'adjacent_diff_std': 2.4,     # Normal
        'max_min_ratio': 1.6,         # Normal - balanced
        'freq_0': 0.11,               # Normal
        'freq_1': 0.09,               # Normal
        'freq_2': 0.10,               # Normal
        'freq_3': 0.12,               # Normal
        'freq_4': 0.08,               # Normal
        'freq_5': 0.11,               # Normal
        'freq_6': 0.09,               # Normal
        'freq_7': 0.10,               # Normal
        'freq_8': 0.11,               # Normal
        'freq_9': 0.09,               # Normal
    }

    result = check_sequence_randomness(random_metrics, confidence_level=95)
    print_randomness_report(result)

    return result

def demo_confidence_levels():
    """
    Demonstrate the difference between 95% and 99% confidence levels.
    """
    print("\nDEMO: Different Confidence Levels")
    print("=" * 40)

    # Borderline case - some metrics slightly outside normal range
    borderline_metrics = {
        'redundancy': 0.022,          # Slightly high
        'coupon_mean': 24.5,          # Slightly low
        'coupon_std': 9.0,            # Normal
        'repetition_gap_mean': 9.0,   # Normal
        'repetition_gap_std': 9.0,    # Normal
        'adjacent': 0.20,             # Normal
        'tpi': 0.83,                  # Slightly low
        'pl1': 1.0,                   # Normal
        'pl2': 1.0,                   # Normal
        'pl3': 1.0,                   # Normal
        'pl4': 0.5,                   # Normal
        'pl5': 1.0,                   # Normal
        'rp': 0.95,                   # Normal
        'autocorr_lag1': 0.16,        # Slightly high
        'adjacent_diff_mean': 3.2,    # Normal
        'adjacent_diff_std': 2.3,     # Normal
        'max_min_ratio': 1.8,         # Normal
        'freq_0': 0.08,               # Normal
        'freq_1': 0.12,               # Normal
        'freq_2': 0.09,               # Normal
        'freq_3': 0.11,               # Normal
        'freq_4': 0.10,               # Normal
        'freq_5': 0.09,               # Normal
        'freq_6': 0.11,               # Normal
        'freq_7': 0.10,               # Normal
        'freq_8': 0.09,               # Normal
        'freq_9': 0.11,               # Normal
    }

    print("Testing with 95% confidence level:")
    print("-" * 35)
    result_95 = check_sequence_randomness(borderline_metrics, confidence_level=95)
    print(f"Assessment: {result_95['assessment']}")
    print(f"Outliers: {result_95['outlier_count']}/27")

    print("\nTesting with 99% confidence level:")
    print("-" * 35)
    result_99 = check_sequence_randomness(borderline_metrics, confidence_level=99)
    print(f"Assessment: {result_99['assessment']}")
    print(f"Outliers: {result_99['outlier_count']}/27")

    print(f"\nDifference: {result_95['outlier_count'] - result_99['outlier_count']} fewer outliers with 99% confidence")

    return result_95, result_99

def demo_batch_processing():
    """
    Demonstrate batch processing of multiple sequences.
    """
    print("\nDEMO: Batch Processing")
    print("=" * 25)

    # Simulate multiple test sequences
    test_sequences = {
        'human_like_1': {
            'redundancy': 0.055, 'coupon_mean': 20.0, 'autocorr_lag1': 0.30,
            'tpi': 0.70, 'freq_7': 0.02, 'max_min_ratio': 4.0,
            # Add dummy values for other metrics
            **{f'freq_{i}': 0.10 for i in range(10) if i != 7},
            'freq_7': 0.02,  # Override freq_7
            **{metric: 1.0 for metric in ['coupon_std', 'repetition_gap_mean', 'repetition_gap_std',
                                         'adjacent', 'pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'rp',
                                         'adjacent_diff_mean', 'adjacent_diff_std']}
        },
        'machine_like_1': {
            'redundancy': 0.008, 'coupon_mean': 29.0, 'autocorr_lag1': 0.05,
            'tpi': 0.95, 'max_min_ratio': 1.5,
            **{f'freq_{i}': 0.10 for i in range(10)},
            **{metric: 1.0 for metric in ['coupon_std', 'repetition_gap_mean', 'repetition_gap_std',
                                         'adjacent', 'pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'rp',
                                         'adjacent_diff_mean', 'adjacent_diff_std']}
        },
        'borderline_1': {
            'redundancy': 0.019, 'coupon_mean': 25.5, 'autocorr_lag1': 0.14,
            'tpi': 0.86, 'max_min_ratio': 2.4,
            **{f'freq_{i}': 0.10 for i in range(10)},
            **{metric: 1.0 for metric in ['coupon_std', 'repetition_gap_mean', 'repetition_gap_std',
                                         'adjacent', 'pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'rp',
                                         'adjacent_diff_mean', 'adjacent_diff_std']}
        }
    }

    results = []
    for seq_name, metrics in test_sequences.items():
        result = check_sequence_randomness(metrics, confidence_level=95)
        results.append({
            'sequence_name': seq_name,
            'randomness_score': result['randomness_score'],
            'assessment': result['assessment'],
            'outlier_count': result['outlier_count'],
            'severe_outliers': result['severe_outlier_count']
        })

    # Display results in table format
    print(f"{'Sequence':<15} {'Score':<6} {'Assessment':<20} {'Outliers'}")
    print("-" * 60)
    for r in results:
        print(f"{r['sequence_name']:<15} {r['randomness_score']:<6.3f} {r['assessment']:<20} {r['outlier_count']}/27")

    return results

def demo_missing_metrics():
    """
    Demonstrate handling of missing metrics.
    """
    print("\nDEMO: Missing Metrics Handling")
    print("=" * 35)

    # Incomplete metrics (missing some required metrics)
    incomplete_metrics = {
        'redundancy': 0.015,
        'coupon_mean': 28.0,
        'autocorr_lag1': 0.10,
        'tpi': 0.90,
        'freq_0': 0.12,
        'freq_1': 0.08,
        # Missing other freq_* and several other metrics
    }

    print("Testing with incomplete metrics...")
    result = check_sequence_randomness(incomplete_metrics, confidence_level=95)

    print(f"Total metrics tested: {result['total_metrics_tested']}")
    print(f"Missing metrics: {result['missing_metrics_count']}")
    print(f"Missing: {result['missing_metrics'][:5]}...")  # Show first 5

    if result['missing_metrics_count'] > 0:
        print("\nWarning: Analysis may be unreliable with missing metrics")

    return result

def show_required_metrics():
    """
    Display all required metrics.
    """
    print("\nREQUIRED METRICS")
    print("=" * 20)

    required = get_required_metrics()
    print(f"Total required: {len(required)}")
    print("\nStatistical metrics:")
    stat_metrics = [m for m in required if not m.startswith('freq_')]
    for i, metric in enumerate(stat_metrics, 1):
        print(f"{i:2d}. {metric}")

    print("\nFrequency metrics:")
    freq_metrics = [m for m in required if m.startswith('freq_')]
    for i, metric in enumerate(freq_metrics, 1):
        print(f"{i:2d}. {metric}")

def main():
    """
    Run all demonstrations.
    """
    print("RANDOMNESS CHECKER - EXAMPLE USAGE")
    print("=" * 50)

    # Show required metrics first
    show_required_metrics()

    # Run demonstrations
    demo_basic_usage()
    demo_random_sequence()
    demo_confidence_levels()
    demo_batch_processing()
    demo_missing_metrics()

    print("\nDEMONSTRATION COMPLETE")
    print("=" * 25)
    print("Key takeaways:")
    print("• Scores > 0.8 suggest true randomness")
    print("• Multiple outliers indicate human patterns")
    print("• 99% confidence is more conservative than 95%")
    print("• Missing metrics reduce analysis reliability")

if __name__ == "__main__":
    main()