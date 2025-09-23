#!/usr/bin/env python3
"""
Analyze self-transition probabilities for human and MT random number sequences.
This script extracts the self-transition probabilities (digit -> same digit)
from the transition probability data files and creates comparative histograms.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
from scipy import stats

# Define constants
DATA_DIR = Path(__file__).parent.parent / "data"
FIGURES_DIR = Path(__file__).parent.parent / "figures"
HUMAN_FILE = DATA_DIR / "human_transitions.csv"
MT_FILE = DATA_DIR / "mt_transitions.csv"

# Ensure figures directory exists
FIGURES_DIR.mkdir(exist_ok=True)

def load_transition_data(filepath):
    """
    Load transition probability data from a CSV file.
    
    Parameters:
    -----------
    filepath : Path
        Path to the CSV file containing transition probabilities
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing the transition probabilities
    """
    return pd.read_csv(filepath)

def extract_self_transitions(df, step=1):
    """
    Extract self-transition probabilities for each digit for a specified step.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing transition probabilities
    step : int
        The step number to extract self-transitions for (default: 1)
        
    Returns:
    --------
    dict
        Dictionary with digits as keys and lists of self-transition probabilities as values
    """
    self_transitions = {digit: [] for digit in range(10)}
    
    for digit in range(10):
        column_name = f"step{step}_trans_{digit}_to_{digit}"
        # Extract all self-transition probabilities for this digit at specified step
        if column_name in df.columns:
            values = df[column_name].values
            self_transitions[digit].extend(values)
    
    return self_transitions

def plot_self_transition_histograms(human_data, mt_data, save_dir, step=1):
    """
    Create histograms comparing human and MT self-transition probabilities for each digit.
    
    Parameters:
    -----------
    human_data : dict
        Dictionary with digits as keys and lists of self-transition probabilities as values for human data
    mt_data : dict
        Dictionary with digits as keys and lists of self-transition probabilities as values for MT data
    save_dir : Path
        Directory to save the histogram plots
    step : int
        The step number for labeling (default: 1)
    """
    # Skip individual digit histograms - only create combined histogram
        
    # Create a combined histogram for all digits
    # Set the style to match stat figures (in case it was reset)
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 7))
    
    # Combine all digit data
    all_human_data = []
    all_mt_data = []
    
    for digit in range(10):
        all_human_data.extend(human_data[digit])
        all_mt_data.extend(mt_data[digit])
    
    # Calculate overall averages
    human_overall_avg = np.mean(all_human_data)
    mt_overall_avg = np.mean(all_mt_data)
    
    # Create histogram
    bins = np.linspace(0, 0.5, 25)  # Bins from 0 to 0.5 probability
    plt.hist(all_human_data, bins=bins, alpha=0.7, label='Human', color='blue')
    plt.hist(all_mt_data, bins=bins, alpha=0.7, label='MT', color='red')
    
    # No random reference line
    
    # Perform statistical tests on combined data
    # Test for normality first
    human_normal = stats.shapiro(all_human_data)[1] > 0.05 if len(all_human_data) <= 5000 else True
    mt_normal = stats.shapiro(all_mt_data)[1] > 0.05 if len(all_mt_data) <= 5000 else True
    
    # Choose appropriate test
    if human_normal and mt_normal:
        # Both normal - use t-test
        t_stat, p_value = stats.ttest_ind(all_human_data, all_mt_data)
        test_name = "t-test"
    else:
        # At least one not normal - use Mann-Whitney U test
        u_stat, p_value = stats.mannwhitneyu(all_human_data, all_mt_data, alternative='two-sided')
        test_name = "Mann-Whitney U"
    
    # Determine significance level
    if p_value < 0.001:
        sig_text = "p < 0.001 ***"
    elif p_value < 0.01:
        sig_text = f"p = {p_value:.3f} **"
    elif p_value < 0.05:
        sig_text = f"p = {p_value:.3f} *"
    else:
        sig_text = f"p = {p_value:.3f} (n.s.)"
    
    # Add labels and title with statistical test results
    plt.xlabel(f'Self-Transition Probability (Step {step})', fontsize=20)
    plt.ylabel('Count', fontsize=20)
    plt.title(f'Step {step} Self-Transition Probability for All Digits\n{test_name}: {sig_text}', fontsize=24)
    plt.legend(fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.grid(alpha=0.3)
    
    # Save figure
    plt.tight_layout()
    plt.savefig(save_dir / f'step{step}_self_transition_all_digits_histogram.png', dpi=300)
    plt.close()

def main():
    """Main function to execute the analysis workflow."""
    print("Loading transition data...")
    human_df = load_transition_data(HUMAN_FILE)
    mt_df = load_transition_data(MT_FILE)
    
    # Generate histograms for steps 1 through 10
    for step in range(1, 11):
        print(f"Extracting step {step} self-transition probabilities...")
        human_self_transitions = extract_self_transitions(human_df, step)
        mt_self_transitions = extract_self_transitions(mt_df, step)
        
        print(f"Creating histograms for step {step}...")
        plot_self_transition_histograms(human_self_transitions, mt_self_transitions, FIGURES_DIR, step)
    
    print(f"All histograms saved to {FIGURES_DIR}")

if __name__ == "__main__":
    main()