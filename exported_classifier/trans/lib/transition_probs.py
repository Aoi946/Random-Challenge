#!/usr/bin/env python3
"""
Calculate transition probabilities for random number sequences.
This module provides functions to analyze transition probabilities
for 1-10 steps in random number sequences.
"""

import numpy as np
from typing import List, Dict, Union, Tuple

def calculate_transition_matrix(sequence: List[int], step: int = 1, base: int = 10) -> np.ndarray:
    """
    Calculate the transition probability matrix for a given step size.
    
    Parameters:
    -----------
    sequence : List[int]
        A sequence of integers (0-9)
    step : int, optional
        The step size to calculate transitions for (default: 1)
    base : int, optional
        The number base (default: 10 for digits 0-9)
        
    Returns:
    --------
    np.ndarray
        A transition probability matrix of shape (base, base)
        where matrix[i, j] is the probability of transitioning from i to j
    """
    if isinstance(sequence, str):
        sequence = [int(c) for c in sequence if c.isdigit()]
    
    # Initialize transition count matrix with zeros
    transitions = np.zeros((base, base), dtype=int)
    
    # Count transitions
    for i in range(len(sequence) - step):
        from_digit = sequence[i]
        to_digit = sequence[i + step]
        transitions[from_digit, to_digit] += 1
    
    # Convert counts to probabilities
    row_sums = transitions.sum(axis=1, keepdims=True)
    # Avoid division by zero for rows with no transitions
    with np.errstate(divide='ignore', invalid='ignore'):
        probabilities = np.divide(transitions, row_sums, where=row_sums!=0)
    
    # Replace NaN values with zeros
    probabilities = np.nan_to_num(probabilities)
    
    return probabilities

def extract_transition_metrics(prob_matrix: np.ndarray) -> Dict[str, float]:
    """
    Extract metrics from a transition probability matrix.
    
    Parameters:
    -----------
    prob_matrix : np.ndarray
        A transition probability matrix
        
    Returns:
    --------
    Dict[str, float]
        Dictionary containing various transition probability metrics
    """
    base = prob_matrix.shape[0]
    metrics = {}
    
    # Metrics for each possible transition (i -> j)
    for i in range(base):
        for j in range(base):
            metrics[f'trans_{i}_to_{j}'] = prob_matrix[i, j]
    
    return metrics

def calculate_transition_metrics_for_sequence(
    sequence: List[int], 
    steps_range: List[int] = range(1, 11), 
    base: int = 10
) -> Dict[str, float]:
    """
    Calculate transition metrics for multiple step sizes for a sequence.
    
    Parameters:
    -----------
    sequence : List[int]
        A sequence of integers (0-9)
    steps_range : List[int], optional
        The range of step sizes to analyze (default: 1 to 10)
    base : int, optional
        The number base (default: 10 for digits 0-9)
        
    Returns:
    --------
    Dict[str, float]
        Dictionary containing transition metrics for all step sizes
    """
    all_metrics = {}
    
    for step in steps_range:
        # Calculate transition probability matrix for this step
        prob_matrix = calculate_transition_matrix(sequence, step, base)
        
        # Extract metrics from the matrix
        step_metrics = extract_transition_metrics(prob_matrix)
        
        # Add step prefix to metric names
        all_metrics.update({f'step{step}_{key}': value for key, value in step_metrics.items()})
    
    return all_metrics