import csv
import pandas as pd
import numpy as np
from typing import List, Union, Tuple, Dict, Optional

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

def load_csv_as_dataframe(file_path: str) -> pd.DataFrame:
    """
    Load sequences from a CSV file into a pandas DataFrame.
    Each row in the CSV becomes a row in the DataFrame.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing the sequences
    """
    # Read the CSV without headers
    df = pd.read_csv(file_path, header=None)
    
    # Process the data if it's in a special format
    if df.shape[1] == 1:
        # If the CSV has only one column with comma-separated values
        sequences = []
        for _, row in df.iterrows():
            # Split by comma and convert to integers
            sequence = [int(digit) for digit in row[0].split(',')]
            sequences.append(sequence)
        
        # Create a new DataFrame with the processed sequences
        max_length = max(len(seq) for seq in sequences)
        padded_sequences = [seq + [np.nan] * (max_length - len(seq)) for seq in sequences]
        return pd.DataFrame(padded_sequences)
    
    return df

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