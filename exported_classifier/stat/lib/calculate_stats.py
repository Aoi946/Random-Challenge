#!/usr/bin/env python3
"""
Calculate various statistical metrics for random number sequences and save results to a CSV file.
Supports both human-generated and machine-generated (MT) random numbers.
"""

import os
import sys
import csv
import argparse
import pandas as pd
from typing import List, Dict, Tuple

# Import the metrics functions
from metrics import redundancy, coupon, repetition_gap, adjacent, tpi, pl1, pl2, pl3, pl4, pl5, rp, autocorr_lag1, adjacent_diff_stats, max_min_ratio, digit_frequencies

def load_csv_sequences(file_path: str) -> List[List[int]]:
    """
    Load sequences from a CSV file where each row is a sequence of comma-separated digits.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
        
    Returns:
    --------
    List[List[int]]
        A list where each element is a list of integers representing a sequence
    """
    sequences = []
    
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Convert all elements to integers
            sequence = [int(digit) for digit in row]
            sequences.append(sequence)
    
    return sequences

def get_human_rannum_subject_counts() -> Dict[int, int]:
    """
    Return the predefined subject counts for the human_rannum.csv dataset.
    
    Returns:
    --------
    Dict[int, int]
        A dictionary mapping subject IDs to the number of sequences each subject generated
    """
    subject_counts = {}
    
    # Subjects 1-10: 10 sequences each
    for i in range(1, 11):
        subject_counts[i] = 10
    
    # Subject 11: 9 sequences
    subject_counts[11] = 9
    
    # Subjects 12-14: 10 sequences each
    for i in range(12, 15):
        subject_counts[i] = 10
    
    # Subject 15: 8 sequences
    subject_counts[15] = 8
    
    # Subject 16: 9 sequences
    subject_counts[16] = 9
    
    # Subjects 17-20: 10 sequences each
    for i in range(17, 21):
        subject_counts[i] = 10
    
    return subject_counts

def split_sequence_by_subject(
    sequences: List[List[int]], 
    subject_counts: Dict[int, int]
) -> Dict[int, List[List[int]]]:
    """
    Split a list of sequences by subject based on the number of sequences per subject.
    
    Parameters:
    -----------
    sequences : List[List[int]]
        A list of sequences
    subject_counts : Dict[int, int]
        A dictionary mapping subject IDs to the number of sequences each subject generated
        
    Returns:
    --------
    Dict[int, List[List[int]]]
        A dictionary mapping subject IDs to their sequences
    """
    result = {}
    index = 0
    
    for subject_id, count in subject_counts.items():
        result[subject_id] = sequences[index:index+count]
        index += count
    
    return result

def load_and_process_human_rannum(file_path: str) -> Tuple[List[List[int]], Dict[int, List[List[int]]]]:
    """
    Load and process the human_rannum.csv dataset, returning both the full list of sequences
    and the sequences organized by subject.
    
    Parameters:
    -----------
    file_path : str
        Path to the human_rannum.csv file
        
    Returns:
    --------
    Tuple[List[List[int]], Dict[int, List[List[int]]]]
        A tuple containing:
        1. A list of all sequences
        2. A dictionary mapping subject IDs to their sequences
    """
    # Load all sequences
    sequences = load_csv_sequences(file_path)
    
    # Get the predefined subject counts
    subject_counts = get_human_rannum_subject_counts()
    
    # Split sequences by subject
    subject_sequences = split_sequence_by_subject(sequences, subject_counts)
    
    return sequences, subject_sequences

def calculate_metrics_for_sequence(seq: List[int]) -> Dict:
    """
    Calculate all metrics for a single sequence.
    
    Parameters:
    -----------
    seq : List[int]
        A sequence of integers
        
    Returns:
    --------
    Dict
        Dictionary containing calculated metrics
    """
    # Calculate all metrics
    # 新しい指標が metrics.py に追加された場合、ここに追加するだけでよい
    metrics = {}
    
    # 冗長性
    metrics['redundancy'] = redundancy(seq)
    
    # クーポンコレクター
    coup = coupon(seq)
    metrics['coupon_mean'] = coup['mean']
    metrics['coupon_std'] = coup['std']
    
    # 繰り返し間隔
    rep_gap = repetition_gap(seq)
    metrics['repetition_gap_mean'] = rep_gap['mean']
    metrics['repetition_gap_std'] = rep_gap['std']
    
    # 隣接順序スコア
    metrics['adjacent'] = adjacent(seq)
    
    # ターニングポイントインデックス
    metrics['tpi'] = tpi(seq)
    
    # フェーズ長指標 (Phase Length)
    metrics['pl1'] = pl1(seq)
    metrics['pl2'] = pl2(seq)
    metrics['pl3'] = pl3(seq)
    metrics['pl4'] = pl4(seq)
    metrics['pl5'] = pl5(seq)
    
    # リピートパターン指標 (Repeat Pattern)
    metrics['rp'] = rp(seq)
    
    # 自己相関 (Lag-1 Autocorrelation)
    metrics['autocorr_lag1'] = autocorr_lag1(seq)
    
    # 隣接数字の差の統計
    adj_diff = adjacent_diff_stats(seq)
    metrics['adjacent_diff_mean'] = adj_diff['adjacent_diff_mean']
    metrics['adjacent_diff_std'] = adj_diff['adjacent_diff_std']
    
    # 最大・最小頻度比
    metrics['max_min_ratio'] = max_min_ratio(seq)
    
    # 数字の出現頻度
    digit_freqs = digit_frequencies(seq)
    for digit, freq in digit_freqs.items():
        metrics[digit] = freq
    
    return metrics

def calculate_and_save_metrics(
    sequences: List[List[int]], 
    subject_sequences: Dict[int, List[List[int]]],
    output_path: str,
    source_type: str = "human"
):
    """
    Calculate metrics for each sequence and save results to a CSV file.
    
    Parameters:
    -----------
    sequences : List[List[int]]
        A list of all sequences
    subject_sequences : Dict[int, List[List[int]]]
        A dictionary mapping subject IDs to their sequences
    output_path : str
        Path to save the CSV file
    source_type : str, optional
        The type of random number source ('human' or 'mt')
    """
    # Create data for the CSV
    data = []
    sequence_index = 0
    
    for subject_id, seqs in subject_sequences.items():
        for seq_num, seq in enumerate(seqs):
            # Calculate all metrics
            metrics = calculate_metrics_for_sequence(seq)
            
            # Add metadata
            metrics['sequence_id'] = sequence_index
            metrics['subject_id'] = subject_id
            metrics['sequence_number'] = seq_num + 1  # 1-based sequence numbering
            metrics['source_type'] = source_type
            
            # Add to data
            data.append(metrics)
            sequence_index += 1
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Saved metrics data to {output_path}")
    
    # Print summary
    print(f"\n{source_type.upper()} Metrics Summary:")
    print(f"Total sequences: {len(sequences)}")
    
    # 自動的にすべての数値指標の統計を表示
    numeric_columns = df.select_dtypes(include=['number']).columns
    metric_columns = [col for col in numeric_columns if col not in ['sequence_id', 'subject_id', 'sequence_number']]
    
    # 各指標のサマリを表示
    for metric in metric_columns:
        # 指標名をフォーマットして表示（アンダースコアを空白に置換し、先頭文字を大文字に）
        metric_name = ' '.join(word.capitalize() for word in metric.split('_'))
        print(f"\n{metric_name} Statistics:")
        print(f"Mean: {df[metric].mean():.4f}")
        print(f"Min: {df[metric].min():.4f}")
        print(f"Max: {df[metric].max():.4f}")
    
    # 被験者ごとの平均を表示
    print("\nMean Metrics by Subject:")
    # 主要な指標（mean値）を集計
    main_metrics = [col for col in metric_columns if not col.endswith('_std')]
    subject_means = df.groupby('subject_id')[main_metrics].mean()
    
    for subject_id, row in subject_means.iterrows():
        metrics_str = ", ".join([f"{col.split('_')[0].capitalize()}={row[col]:.4f}" for col in main_metrics])
        print(f"Subject {subject_id}: {metrics_str}")

def process_sequences(input_path, output_path, source_type="human"):
    """
    Process the sequences from the given input file and save the metrics to the output file.
    
    Parameters:
    -----------
    input_path : str
        Path to the input CSV file
    output_path : str
        Path to the output CSV file
    source_type : str, optional
        The type of random number source ('human' or 'mt')
    """
    print(f"Loading {source_type} data from {input_path}...")
    
    # Load the data
    if source_type == "human":
        sequences, subject_sequences = load_and_process_human_rannum(input_path)
        print(f"Loaded {len(sequences)} sequences from {len(subject_sequences)} subjects.")
    else:
        # For MT data, we don't have subjects, so we'll create dummy subjects
        sequences = load_csv_sequences(input_path)
        num_sequences = len(sequences)
        
        # Create dummy subject mapping similar to human data structure
        # Each "subject" will have approximately the same number of sequences as human subjects
        subject_counts = get_human_rannum_subject_counts()
        total_human_sequences = sum(subject_counts.values())
        
        # Scale factor to make MT data match human data subject distribution
        scale_factor = num_sequences / total_human_sequences
        
        mt_subject_counts = {}
        sequence_count = 0
        subject_id = 1
        
        while sequence_count < num_sequences:
            # Get count for current subject (proportional to human subject count)
            if subject_id <= len(subject_counts):
                count = round(subject_counts[subject_id] * scale_factor)
            else:
                count = round(list(subject_counts.values())[-1] * scale_factor)
            
            # Make sure we don't exceed the total number of sequences
            count = min(count, num_sequences - sequence_count)
            
            if count > 0:
                mt_subject_counts[subject_id] = count
                sequence_count += count
            
            subject_id += 1
            
            # Break if we've allocated all sequences
            if sequence_count >= num_sequences:
                break
        
        # Split MT sequences by dummy subjects
        subject_sequences = split_sequence_by_subject(sequences, mt_subject_counts)
        print(f"Loaded {len(sequences)} sequences, assigned to {len(subject_sequences)} dummy subjects.")
    
    # Calculate metrics and save to CSV
    print(f"Calculating metrics for {source_type} sequences and saving to CSV...")
    calculate_and_save_metrics(sequences, subject_sequences, output_path, source_type)

def main():
    """Main function to load data, calculate metrics, and save to CSV."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Calculate randomness metrics for number sequences.')
    parser.add_argument('--human', action='store_true', help='Process human-generated random numbers')
    parser.add_argument('--mt', action='store_true', help='Process MT-generated random numbers')
    parser.add_argument('--human-input', default='/Users/aoi-kumadaki/rnglib-self/human_rannum.csv',
                        help='Path to the human random numbers CSV file')
    parser.add_argument('--mt-input', default='/Users/aoi-kumadaki/rnglib-self/mtwist_rannum.csv',
                        help='Path to the MT random numbers CSV file')
    parser.add_argument('--output-dir', default='/Users/aoi-kumadaki/rnglib-self/stat/data',
                        help='Directory to save the output files')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process human data if requested or if no specific option is provided
    if args.human or (not args.human and not args.mt):
        human_output_path = os.path.join(args.output_dir, 'human_metrics.csv')
        process_sequences(args.human_input, human_output_path, "human")
    
    # Process MT data if requested or if no specific option is provided
    if args.mt or (not args.human and not args.mt):
        mt_output_path = os.path.join(args.output_dir, 'mt_metrics.csv')
        process_sequences(args.mt_input, mt_output_path, "mt")
    
    # If both data types are processed, create a combined CSV
    if (args.human and args.mt) or (not args.human and not args.mt):
        human_df = pd.read_csv(os.path.join(args.output_dir, 'human_metrics.csv'))
        mt_df = pd.read_csv(os.path.join(args.output_dir, 'mt_metrics.csv'))
        
        # Combine both datasets
        combined_df = pd.concat([human_df, mt_df], ignore_index=True)
        combined_output_path = os.path.join(args.output_dir, 'combined_metrics.csv')
        combined_df.to_csv(combined_output_path, index=False)
        print(f"\nSaved combined metrics to {combined_output_path}")
    
    print("Done!")

if __name__ == "__main__":
    main()