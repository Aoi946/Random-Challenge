#!/usr/bin/env python3
"""
Quick Test Script for Randomness Checker

This script provides a simple way to test the randomness checker
with predefined examples.
"""

from randomness_checker import check_sequence_randomness, print_randomness_report

def test_human_pattern():
    """Test with typical human-generated patterns."""
    print("Testing Human-like Pattern")
    print("-" * 30)

    # Typical human biases
    human_metrics = {
        'redundancy': 0.035,          # High redundancy
        'coupon_mean': 21.5,          # Quick digit collection
        'coupon_std': 7.0,            # Low variability
        'repetition_gap_mean': 7.8,   # Short gaps
        'repetition_gap_std': 7.5,    # Low variability
        'adjacent': 0.28,             # High adjacent patterns
        'tpi': 0.78,                  # Low turning points
        'pl1': 1.35,                  # Pattern detection
        'pl2': 1.25,                  # Pattern detection
        'pl3': 1.4,                   # Pattern detection
        'pl4': 1.2,                   # Pattern detection
        'pl5': 2.1,                   # Pattern detection
        'rp': 0.82,                   # Low runs
        'autocorr_lag1': 0.22,        # High correlation
        'adjacent_diff_mean': 2.8,    # Small differences
        'adjacent_diff_std': 2.1,     # Low variability
        'max_min_ratio': 3.5,         # High imbalance
        'freq_0': 0.05,               # Avoided digit
        'freq_1': 0.15,               # Preferred digit
        'freq_2': 0.12,               # Slight preference
        'freq_3': 0.13,               # Slight preference
        'freq_4': 0.09,               # Slightly avoided
        'freq_5': 0.08,               # Avoided
        'freq_6': 0.11,               # Normal
        'freq_7': 0.04,               # Strongly avoided
        'freq_8': 0.12,               # Slight preference
        'freq_9': 0.11,               # Normal
    }

    result = check_sequence_randomness(human_metrics)
    print(f"Score: {result['randomness_score']:.3f}")
    print(f"Assessment: {result['assessment']}")
    print(f"Outliers: {result['outlier_count']}/27")

    return result

def test_machine_pattern():
    """Test with MT-like random pattern."""
    print("\nTesting Machine-like Pattern")
    print("-" * 32)

    # MT-like characteristics
    machine_metrics = {
        'redundancy': 0.009,          # Low redundancy
        'coupon_mean': 30.2,          # Normal collection
        'coupon_std': 11.1,           # Normal variability
        'repetition_gap_mean': 9.4,   # Normal gaps
        'repetition_gap_std': 9.2,    # Normal variability
        'adjacent': 0.16,             # Normal adjacent patterns
        'tpi': 0.96,                  # Good turning points
        'pl1': 0.98,                  # No patterns
        'pl2': 1.02,                  # No patterns
        'pl3': 0.85,                  # No patterns
        'pl4': 0.45,                  # No patterns
        'pl5': 1.15,                  # No patterns
        'rp': 0.97,                   # Good runs
        'autocorr_lag1': 0.03,        # Low correlation
        'adjacent_diff_mean': 3.32,   # Normal differences
        'adjacent_diff_std': 2.38,    # Normal variability
        'max_min_ratio': 1.65,        # Good balance
        'freq_0': 0.102,              # Balanced
        'freq_1': 0.098,              # Balanced
        'freq_2': 0.105,              # Balanced
        'freq_3': 0.095,              # Balanced
        'freq_4': 0.103,              # Balanced
        'freq_5': 0.099,              # Balanced
        'freq_6': 0.101,              # Balanced
        'freq_7': 0.097,              # Balanced
        'freq_8': 0.100,              # Balanced
        'freq_9': 0.100,              # Balanced
    }

    result = check_sequence_randomness(machine_metrics)
    print(f"Score: {result['randomness_score']:.3f}")
    print(f"Assessment: {result['assessment']}")
    print(f"Outliers: {result['outlier_count']}/27")

    return result

def test_borderline_pattern():
    """Test with borderline case."""
    print("\nTesting Borderline Pattern")
    print("-" * 28)

    # Some characteristics slightly outside normal
    borderline_metrics = {
        'redundancy': 0.021,          # Slightly high
        'coupon_mean': 24.8,          # Slightly low
        'coupon_std': 8.9,            # Normal
        'repetition_gap_mean': 9.1,   # Normal
        'repetition_gap_std': 8.8,    # Normal
        'adjacent': 0.19,             # Normal
        'tpi': 0.84,                  # Slightly low
        'pl1': 1.22,                  # Slightly high
        'pl2': 1.05,                  # Normal
        'pl3': 0.95,                  # Normal
        'pl4': 0.52,                  # Normal
        'pl5': 1.35,                  # Normal
        'rp': 0.93,                   # Normal
        'autocorr_lag1': 0.16,        # Slightly high
        'adjacent_diff_mean': 3.15,   # Normal
        'adjacent_diff_std': 2.25,    # Normal
        'max_min_ratio': 2.1,         # Normal
        'freq_0': 0.08,               # Normal
        'freq_1': 0.13,               # Slightly high
        'freq_2': 0.09,               # Normal
        'freq_3': 0.11,               # Normal
        'freq_4': 0.10,               # Normal
        'freq_5': 0.08,               # Normal
        'freq_6': 0.11,               # Normal
        'freq_7': 0.09,               # Normal
        'freq_8': 0.10,               # Normal
        'freq_9': 0.11,               # Normal
    }

    result = check_sequence_randomness(borderline_metrics)
    print(f"Score: {result['randomness_score']:.3f}")
    print(f"Assessment: {result['assessment']}")
    print(f"Outliers: {result['outlier_count']}/27")

    return result

def main():
    """Run quick tests."""
    print("RANDOMNESS CHECKER - QUICK TEST")
    print("=" * 40)

    # Run all tests
    human_result = test_human_pattern()
    machine_result = test_machine_pattern()
    borderline_result = test_borderline_pattern()

    print("\nSUMMARY")
    print("-" * 15)
    print(f"Human-like:    {human_result['assessment']:<20} (Score: {human_result['randomness_score']:.3f})")
    print(f"Machine-like:  {machine_result['assessment']:<20} (Score: {machine_result['randomness_score']:.3f})")
    print(f"Borderline:    {borderline_result['assessment']:<20} (Score: {borderline_result['randomness_score']:.3f})")

    print("\nExpected Results:")
    print("• Human-like should score low (likely_non_random)")
    print("• Machine-like should score high (likely_random)")
    print("• Borderline should be in middle (possibly_random)")

if __name__ == "__main__":
    main()