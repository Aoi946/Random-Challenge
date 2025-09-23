#!/usr/bin/env python3
"""
Calculate transition probability metrics for random number sequences and save results to a CSV file.
Supports both human-generated and machine-generated (MT) random numbers.
"""

import os
import sys
import csv
import argparse
import pandas as pd
from typing import List, Dict, Tuple

# Import the transition probability functions
from transition_probs import calculate_transition_metrics_for_sequence

# Reuse functions from the stat module for loading and processing CSV files
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'stat/lib'))
from calculate_stats import (
    load_csv_sequences, 
    get_human_rannum_subject_counts, 
    split_sequence_by_subject,
    load_and_process_human_rannum
)

def calculate_and_save_transition_metrics(
    sequences: List[List[int]], 
    subject_sequences: Dict[int, List[List[int]]],
    output_path: str,
    source_type: str = "human"
):
    """
    Calculate transition metrics for each sequence and save results to a CSV file.
    
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
            # Calculate transition metrics for steps 1-10
            metrics = calculate_transition_metrics_for_sequence(seq)
            
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
    print(f"Saved transition metrics data to {output_path}")
    
    # Print summary
    print(f"\n{source_type.upper()} Transition Metrics Summary:")
    print(f"Total sequences: {len(sequences)}")
    print(f"Number of transition metrics per sequence: {len(metrics) - 4}")  # Subtract 4 for metadata columns
    print(f"Transition steps analyzed: 1-10")
    print(f"Possible transitions per step: 100 (10×10 transition matrix)")
    print(f"Total metrics: {len(metrics) - 4} metrics × {len(sequences)} sequences = {(len(metrics) - 4) * len(sequences)}")

def process_sequences(input_path, output_path, source_type="human"):
    """
    Process the sequences from the given input file and save the transition metrics to the output file.
    
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
    
    # Calculate transition metrics and save to CSV
    print(f"Calculating transition metrics for {source_type} sequences and saving to CSV...")
    calculate_and_save_transition_metrics(sequences, subject_sequences, output_path, source_type)

def main():
    """Main function to load data, calculate transition metrics, and save to CSV."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Calculate transition probability metrics for number sequences.')
    parser.add_argument('--human', action='store_true', help='Process human-generated random numbers')
    parser.add_argument('--mt', action='store_true', help='Process MT-generated random numbers')
    parser.add_argument('--human-input', default='/Users/aoi-kumadaki/rnglib-self/human_rannum.csv',
                        help='Path to the human random numbers CSV file')
    parser.add_argument('--mt-input', default='/Users/aoi-kumadaki/rnglib-self/mtwist_rannum.csv',
                        help='Path to the MT random numbers CSV file')
    parser.add_argument('--output-dir', default='/Users/aoi-kumadaki/rnglib-self/trans/data',
                        help='Directory to save the output files')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process human data if requested or if no specific option is provided
    if args.human or (not args.human and not args.mt):
        human_output_path = os.path.join(args.output_dir, 'human_transitions.csv')
        process_sequences(args.human_input, human_output_path, "human")
    
    # Process MT data if requested or if no specific option is provided
    if args.mt or (not args.human and not args.mt):
        mt_output_path = os.path.join(args.output_dir, 'mt_transitions.csv')
        process_sequences(args.mt_input, mt_output_path, "mt")
    
    # If both data types are processed, create a combined CSV
    if (args.human and args.mt) or (not args.human and not args.mt):
        human_df = pd.read_csv(os.path.join(args.output_dir, 'human_transitions.csv'))
        mt_df = pd.read_csv(os.path.join(args.output_dir, 'mt_transitions.csv'))
        
        # Combine both datasets
        combined_df = pd.concat([human_df, mt_df], ignore_index=True)
        combined_output_path = os.path.join(args.output_dir, 'combined_transitions.csv')
        combined_df.to_csv(combined_output_path, index=False)
        print(f"\nSaved combined transition metrics to {combined_output_path}")
    
    print("Done!")

if __name__ == "__main__":
    main()