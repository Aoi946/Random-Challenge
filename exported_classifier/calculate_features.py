#!/usr/bin/env python3
"""
Feature Calculation Module for Human vs Machine Classifier

This module provides functions to calculate the required features
(statistical metrics and transition probabilities) from raw random number sequences.
"""

import os
import sys
import pandas as pd
import numpy as np

# Add local lib directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stat', 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trans', 'lib'))

# Import calculation modules
from metrics import (
    redundancy, coupon, repetition_gap, adjacent, tpi,
    pl1, pl2, pl3, pl4, pl5, rp, autocorr_lag1,
    adjacent_diff_stats, max_min_ratio, digit_frequencies
)
from transition_probs import calculate_transition_matrix

def calculate_statistical_metrics(sequence):
    """
    Calculate all statistical metrics for a sequence.

    Parameters:
    -----------
    sequence : list or np.array
        Random number sequence (digits 0-9)

    Returns:
    --------
    dict
        Dictionary containing all statistical metrics
    """
    sequence = [int(x) for x in sequence]  # Convert to Python int list

    metrics = {}

    # Basic metrics
    metrics['redundancy'] = redundancy(sequence)

    # Coupon collector
    coupon_stats = coupon(sequence)
    metrics['coupon_mean'] = coupon_stats['mean']
    metrics['coupon_std'] = coupon_stats['std']

    # Repetition gap
    rep_gap_stats = repetition_gap(sequence)
    metrics['repetition_gap_mean'] = rep_gap_stats['mean']
    metrics['repetition_gap_std'] = rep_gap_stats['std']

    # Adjacent patterns
    metrics['adjacent'] = adjacent(sequence)

    # Turning point index
    metrics['tpi'] = tpi(sequence)

    # Poker-like tests
    metrics['pl1'] = pl1(sequence)
    metrics['pl2'] = pl2(sequence)
    metrics['pl3'] = pl3(sequence)
    metrics['pl4'] = pl4(sequence)
    metrics['pl5'] = pl5(sequence)

    # Runs and patterns
    metrics['rp'] = rp(sequence)

    # Autocorrelation
    metrics['autocorr_lag1'] = autocorr_lag1(sequence)

    # Adjacent differences
    adj_diff_stats = adjacent_diff_stats(sequence)
    metrics['adjacent_diff_mean'] = adj_diff_stats['adjacent_diff_mean']
    metrics['adjacent_diff_std'] = adj_diff_stats['adjacent_diff_std']

    # Max-min ratio
    metrics['max_min_ratio'] = max_min_ratio(sequence)

    # Digit frequencies
    freq_stats = digit_frequencies(sequence)
    for i in range(10):
        metrics[f'freq_{i}'] = freq_stats[f'freq_{i}']

    return metrics

def calculate_transition_features(sequence, max_step=5):
    """
    Calculate transition probabilities for steps 1-5.

    Parameters:
    -----------
    sequence : list or np.array
        Random number sequence (digits 0-9)
    max_step : int
        Maximum step to calculate (default: 5 for steps 1-5)

    Returns:
    --------
    dict
        Dictionary containing transition probabilities
    """
    sequence = [int(x) for x in sequence]  # Convert to Python int list

    # Calculate transition probabilities for steps 1-5
    transition_features = {}

    for step in range(1, max_step + 1):
        # Calculate transition matrix for this step
        step_matrix = calculate_transition_matrix(sequence, step)

        # Convert to feature format expected by classifier
        for from_digit in range(10):
            for to_digit in range(10):
                feature_name = f'step{step}_trans_{from_digit}_to_{to_digit}'
                transition_features[feature_name] = step_matrix[from_digit, to_digit]

    return transition_features

def calculate_all_features(sequence):
    """
    Calculate all features required by the classifier.

    Parameters:
    -----------
    sequence : list or np.array
        Random number sequence (digits 0-9)

    Returns:
    --------
    pd.DataFrame
        DataFrame with one row containing all calculated features
    """
    # Calculate statistical metrics
    stat_features = calculate_statistical_metrics(sequence)

    # Calculate transition probabilities (steps 1-5)
    trans_features = calculate_transition_features(sequence, max_step=5)

    # Combine all features
    all_features = {**stat_features, **trans_features}

    # Convert to DataFrame
    return pd.DataFrame([all_features])

def calculate_features_for_sequences(sequences, sequence_ids=None):
    """
    Calculate features for multiple sequences.

    Parameters:
    -----------
    sequences : list of lists/arrays
        List of random number sequences
    sequence_ids : list, optional
        List of sequence identifiers

    Returns:
    --------
    pd.DataFrame
        DataFrame containing features for all sequences
    """
    if sequence_ids is None:
        sequence_ids = list(range(len(sequences)))

    all_features = []

    for i, sequence in enumerate(sequences):
        print(f"Processing sequence {i+1}/{len(sequences)}")
        features = calculate_all_features(sequence)
        features['sequence_id'] = sequence_ids[i]
        all_features.append(features)

    # Combine all features
    result_df = pd.concat(all_features, ignore_index=True)

    # Reorder columns to put sequence_id first
    cols = ['sequence_id'] + [col for col in result_df.columns if col != 'sequence_id']
    result_df = result_df[cols]

    return result_df

def load_sequences_from_csv(filepath, sequence_column='sequence'):
    """
    Load sequences from a CSV file.

    Parameters:
    -----------
    filepath : str
        Path to CSV file containing sequences
    sequence_column : str
        Name of column containing sequences

    Returns:
    --------
    list
        List of sequences as lists of integers
    """
    df = pd.read_csv(filepath)
    sequences = []

    for seq_str in df[sequence_column]:
        # Convert string sequence to list of integers
        sequence = [int(digit) for digit in str(seq_str)]
        sequences.append(sequence)

    return sequences

def example_usage():
    """
    Example of how to use the feature calculation functions.
    """
    # Example sequence
    example_sequence = [1, 4, 7, 2, 9, 0, 3, 8, 5, 6, 1, 3, 9, 2, 7]

    print("Calculating features for example sequence:")
    print(f"Sequence: {example_sequence}")

    # Calculate all features
    features = calculate_all_features(example_sequence)

    print(f"\\nCalculated {len(features.columns)} features:")
    print("Statistical features:")
    stat_cols = [col for col in features.columns if not col.startswith('step')]
    for col in stat_cols[:10]:  # Show first 10
        print(f"  {col}: {features[col].iloc[0]:.4f}")
    print("  ...")

    print("\\nTransition features (first few):")
    trans_cols = [col for col in features.columns if col.startswith('step')]
    for col in trans_cols[:5]:  # Show first 5
        print(f"  {col}: {features[col].iloc[0]:.4f}")
    print("  ...")

    print(f"\\nTotal features: {len(features.columns)}")

    return features

if __name__ == "__main__":
    example_usage()