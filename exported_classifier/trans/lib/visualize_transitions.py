#!/usr/bin/env python3
"""
Visualization script for transition probability metrics.
Creates heatmaps and histograms for transition probabilities.
Supports comparing human-generated and MT-generated random numbers.
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional, Union

def load_transition_data(file_path: str) -> pd.DataFrame:
    """
    Load transition metrics data from CSV file.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file containing transition metrics data
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing the transition metrics data
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded data from {file_path}")
        print(f"Found {len(df)} rows and {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def identify_transition_metrics(df: pd.DataFrame, step: int) -> List[str]:
    """
    Identify transition metrics columns for a specific step.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the transition metrics data
    step : int
        The step size to find transition metrics for
        
    Returns:
    --------
    List[str]
        List of column names that contain transition metrics for the specified step
    """
    # Pattern for transition metrics: step{step}_trans_{i}_to_{j}
    step_pattern = f"step{step}_trans_"
    
    # Find columns that match the pattern
    metric_columns = [col for col in df.columns if col.startswith(step_pattern)]
    
    print(f"Found {len(metric_columns)} transition metrics for step {step}")
    return metric_columns

def create_transition_matrix_heatmap(
    df: pd.DataFrame,
    step: int,
    output_dir: str,
    source_type: str = None,
    figsize: Tuple[int, int] = (10, 8)
) -> None:
    """
    Create a heatmap of the transition matrix for a specific step.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the transition metrics data
    step : int
        The step size to visualize
    output_dir : str
        Directory to save the output figure
    source_type : str, optional
        The type of random number source ('human', 'mt', or None for combined)
    figsize : Tuple[int, int], optional
        Figure size (width, height) in inches (default: (10, 8))
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get transition metrics for this step
    step_metrics = identify_transition_metrics(df, step)
    
    # Filter data by source_type if specified
    if source_type and 'source_type' in df.columns:
        filtered_df = df[df['source_type'] == source_type]
    else:
        filtered_df = df
    
    # Create a 10x10 matrix of transition probabilities
    transition_matrix = np.zeros((10, 10))
    
    # Fill the matrix with average probabilities
    for i in range(10):
        for j in range(10):
            col_name = f"step{step}_trans_{i}_to_{j}"
            if col_name in step_metrics:
                transition_matrix[i, j] = filtered_df[col_name].mean()
    
    # Set the style to match stat figures
    sns.set(style="whitegrid")
    
    # Create heatmap
    plt.figure(figsize=figsize)
    sns.heatmap(
        transition_matrix, 
        annot=True, 
        fmt=".3f", 
        cmap="YlGnBu",
        xticklabels=range(10),
        yticklabels=range(10),
        vmin=0.0,
        vmax=0.2  # Adjust based on your data
    )
    
    # Set labels and title
    plt.xlabel("To Digit", fontsize=20)
    plt.ylabel("From Digit", fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=16)
    title = f"Step {step} Transition Probabilities"
    if source_type:
        title += f" ({source_type.upper()})"
    plt.title(title, fontsize=24)
    
    # Save figure
    filename = f"step{step}_transition_matrix"
    if source_type:
        filename += f"_{source_type}"
    output_path = os.path.join(output_dir, f"{filename}.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Created transition matrix heatmap for step {step} at {output_path}")

def create_comparison_transition_heatmaps(
    human_df: pd.DataFrame,
    mt_df: pd.DataFrame,
    step: int,
    output_dir: str,
    figsize: Tuple[int, int] = (15, 6)
) -> None:
    """
    Create side-by-side heatmaps comparing human and MT transition matrices.
    
    Parameters:
    -----------
    human_df : pd.DataFrame
        DataFrame containing the human transition metrics data
    mt_df : pd.DataFrame
        DataFrame containing the MT transition metrics data
    step : int
        The step size to visualize
    output_dir : str
        Directory to save the output figure
    figsize : Tuple[int, int], optional
        Figure size (width, height) in inches (default: (15, 6))
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get transition metrics for this step
    human_step_metrics = identify_transition_metrics(human_df, step)
    mt_step_metrics = identify_transition_metrics(mt_df, step)
    
    # Create 10x10 matrices of transition probabilities
    human_matrix = np.zeros((10, 10))
    mt_matrix = np.zeros((10, 10))
    diff_matrix = np.zeros((10, 10))
    
    # Fill the matrices with average probabilities
    for i in range(10):
        for j in range(10):
            col_name = f"step{step}_trans_{i}_to_{j}"
            if col_name in human_step_metrics:
                human_matrix[i, j] = human_df[col_name].mean()
            if col_name in mt_step_metrics:
                mt_matrix[i, j] = mt_df[col_name].mean()
    
    # Calculate difference matrix (human - mt)
    diff_matrix = human_matrix - mt_matrix
    
    # Set the style to match stat figures
    sns.set(style="whitegrid")
    
    # Create figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    
    # Plot human heatmap
    sns.heatmap(
        human_matrix, 
        annot=True, 
        fmt=".3f", 
        cmap="YlGnBu",
        xticklabels=range(10),
        yticklabels=range(10),
        vmin=0.0,
        vmax=0.2,  # Adjust based on your data
        ax=axes[0]
    )
    axes[0].set_title(f"Human: Step {step}", fontsize=24)
    axes[0].set_xlabel("To Digit", fontsize=20)
    axes[0].set_ylabel("From Digit", fontsize=20)
    axes[0].tick_params(axis='both', which='major', labelsize=16)
    
    # Plot MT heatmap
    sns.heatmap(
        mt_matrix, 
        annot=True, 
        fmt=".3f", 
        cmap="YlGnBu",
        xticklabels=range(10),
        yticklabels=range(10),
        vmin=0.0,
        vmax=0.2,  # Adjust based on your data
        ax=axes[1]
    )
    axes[1].set_title(f"MT: Step {step}", fontsize=24)
    axes[1].set_xlabel("To Digit", fontsize=20)
    axes[1].set_ylabel("From Digit", fontsize=20)
    axes[1].tick_params(axis='both', which='major', labelsize=16)
    
    # Plot difference heatmap
    sns.heatmap(
        diff_matrix, 
        annot=True, 
        fmt=".3f", 
        cmap="RdBu_r",
        xticklabels=range(10),
        yticklabels=range(10),
        center=0,
        vmin=-0.1,
        vmax=0.1,  # Adjust based on your data
        ax=axes[2]
    )
    axes[2].set_title(f"Difference (Human - MT): Step {step}", fontsize=24)
    axes[2].set_xlabel("To Digit", fontsize=20)
    axes[2].set_ylabel("From Digit", fontsize=20)
    axes[2].tick_params(axis='both', which='major', labelsize=16)
    
    # Save figure
    output_path = os.path.join(output_dir, f"step{step}_comparison.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Created comparison heatmaps for step {step} at {output_path}")

def create_step_comparison_figure(
    df: pd.DataFrame,
    steps_range: List[int],
    output_dir: str,
    source_type: str = None,
    figsize: Tuple[int, int] = (15, 15)
) -> None:
    """
    Create a figure comparing transition matrices for different steps.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the transition metrics data
    steps_range : List[int]
        The steps to include in the comparison
    output_dir : str
        Directory to save the output figure
    source_type : str, optional
        The type of random number source ('human', 'mt', or None for combined)
    figsize : Tuple[int, int], optional
        Figure size (width, height) in inches (default: (15, 15))
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter data by source_type if specified
    if source_type and 'source_type' in df.columns:
        filtered_df = df[df['source_type'] == source_type]
    else:
        filtered_df = df
    
    # Calculate number of rows and columns for subplots
    n_steps = len(steps_range)
    n_cols = min(3, n_steps)  # Maximum 3 columns
    n_rows = (n_steps + n_cols - 1) // n_cols  # Ceiling division
    
    # Create figure and subplots
    # Set the style to match stat figures
    sns.set(style="whitegrid")
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    
    # Make axes iterable even if there's only one subplot
    if n_steps == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    # Plot each step
    for idx, step in enumerate(steps_range):
        if idx >= len(axes):
            break
            
        ax = axes[idx]
        
        # Get transition metrics for this step
        step_metrics = identify_transition_metrics(filtered_df, step)
        
        # Create a 10x10 matrix of transition probabilities
        transition_matrix = np.zeros((10, 10))
        
        # Fill the matrix with average probabilities
        for i in range(10):
            for j in range(10):
                col_name = f"step{step}_trans_{i}_to_{j}"
                if col_name in step_metrics:
                    transition_matrix[i, j] = filtered_df[col_name].mean()
        
        # Create heatmap
        sns.heatmap(
            transition_matrix, 
            annot=False,  # Too many subplots for annotations
            fmt=".3f", 
            cmap="YlGnBu",
            xticklabels=range(10),
            yticklabels=range(10),
            vmin=0.0,
            vmax=0.2,  # Adjust based on your data
            ax=ax
        )
        
        # Set labels and title
        ax.set_xlabel("To Digit", fontsize=20)
        ax.set_ylabel("From Digit", fontsize=20)
        ax.tick_params(axis='both', which='major', labelsize=16)
        title = f"Step {step} Transitions"
        ax.set_title(title, fontsize=24)
    
    # Hide any unused subplots
    for i in range(n_steps, len(axes)):
        axes[i].set_visible(False)
    
    # Add a title to the entire figure
    main_title = "Transition Probabilities by Step"
    if source_type:
        main_title += f" ({source_type.upper()})"
    fig.suptitle(main_title, fontsize=32)
    
    # Save figure
    filename = "all_steps_comparison"
    if source_type:
        filename += f"_{source_type}"
    output_path = os.path.join(output_dir, f"{filename}.png")
    plt.tight_layout(rect=[0, 0, 1, 0.97])  # Make room for suptitle
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Created step comparison figure at {output_path}")

def create_same_digit_transition_plot(
    df: pd.DataFrame,
    steps_range: List[int],
    output_dir: str,
    source_type: str = None,
    figsize: Tuple[int, int] = (10, 6)
) -> None:
    """
    Create a line plot showing the probability of transitioning to the same digit across steps.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the transition metrics data
    steps_range : List[int]
        The steps to include in the plot
    output_dir : str
        Directory to save the output figure
    source_type : str, optional
        The type of random number source ('human', 'mt', or None for combined)
    figsize : Tuple[int, int], optional
        Figure size (width, height) in inches (default: (10, 6))
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter data by source_type if specified
    if source_type and 'source_type' in df.columns:
        filtered_df = df[df['source_type'] == source_type]
    else:
        filtered_df = df
    
    # Initialize data for the plot
    same_digit_probs = []
    
    # Calculate same-digit transition probabilities for each step
    for step in steps_range:
        # Get transition metrics for this step
        step_metrics = identify_transition_metrics(filtered_df, step)
        
        # Calculate average probability of transitioning to the same digit
        same_digit_prob = 0.0
        for i in range(10):
            col_name = f"step{step}_trans_{i}_to_{i}"
            if col_name in step_metrics:
                same_digit_prob += filtered_df[col_name].mean()
        
        same_digit_prob /= 10  # Average across all digits
        same_digit_probs.append(same_digit_prob)
    
    # Set the style to match stat figures
    sns.set(style="whitegrid")
    
    # Create the plot
    plt.figure(figsize=figsize)
    plt.plot(steps_range, same_digit_probs, marker='o', linestyle='-')
    
    # Add reference line for random probability (0.1)
    plt.axhline(y=0.1, color='r', linestyle='--', label='Random (0.1)')
    
    # Set labels and title
    plt.xlabel("Step", fontsize=20)
    plt.ylabel("Probability", fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=16)
    title = "Probability of Transitioning to Same Digit by Step"
    if source_type:
        title += f" ({source_type.upper()})"
    plt.title(title, fontsize=24)
    plt.grid(True)
    plt.legend(fontsize=16)
    
    # Set x-axis to show only the steps
    plt.xticks(steps_range)
    
    # Save figure
    filename = "same_digit_transition"
    if source_type:
        filename += f"_{source_type}"
    output_path = os.path.join(output_dir, f"{filename}.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Created same-digit transition plot at {output_path}")

def create_human_mt_comparison_plot(
    human_df: pd.DataFrame,
    mt_df: pd.DataFrame,
    steps_range: List[int],
    output_dir: str,
    figsize: Tuple[int, int] = (10, 6)
) -> None:
    """
    Create a line plot comparing human and MT same-digit transition probabilities.
    
    Parameters:
    -----------
    human_df : pd.DataFrame
        DataFrame containing the human transition metrics data
    mt_df : pd.DataFrame
        DataFrame containing the MT transition metrics data
    steps_range : List[int]
        The steps to include in the plot
    output_dir : str
        Directory to save the output figure
    figsize : Tuple[int, int], optional
        Figure size (width, height) in inches (default: (10, 6))
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize data for the plot
    human_same_digit_probs = []
    mt_same_digit_probs = []
    
    # Calculate same-digit transition probabilities for each step
    for step in steps_range:
        # Human data
        human_step_metrics = identify_transition_metrics(human_df, step)
        human_same_digit_prob = 0.0
        for i in range(10):
            col_name = f"step{step}_trans_{i}_to_{i}"
            if col_name in human_step_metrics:
                human_same_digit_prob += human_df[col_name].mean()
        human_same_digit_prob /= 10
        human_same_digit_probs.append(human_same_digit_prob)
        
        # MT data
        mt_step_metrics = identify_transition_metrics(mt_df, step)
        mt_same_digit_prob = 0.0
        for i in range(10):
            col_name = f"step{step}_trans_{i}_to_{i}"
            if col_name in mt_step_metrics:
                mt_same_digit_prob += mt_df[col_name].mean()
        mt_same_digit_prob /= 10
        mt_same_digit_probs.append(mt_same_digit_prob)
    
    # Set the style to match stat figures
    sns.set(style="whitegrid")
    
    # Create the plot
    plt.figure(figsize=figsize)
    plt.plot(steps_range, human_same_digit_probs, marker='o', linestyle='-', color='blue', label='Human')
    plt.plot(steps_range, mt_same_digit_probs, marker='s', linestyle='-', color='red', label='MT')
    
    # Add reference line for random probability (0.1)
    plt.axhline(y=0.1, color='green', linestyle='--', label='Random (0.1)')
    
    # Set labels and title
    plt.xlabel("Step", fontsize=20)
    plt.ylabel("Probability", fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.title("Comparison of Same-Digit Transition Probabilities: Human vs MT", fontsize=24)
    plt.grid(True)
    plt.legend(fontsize=16)
    
    # Set x-axis to show only the steps
    plt.xticks(steps_range)
    
    # Save figure
    output_path = os.path.join(output_dir, "human_mt_same_digit_comparison.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Created human vs MT comparison plot at {output_path}")

def main():
    """Main function to load data and create visualizations."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Visualize transition probability metrics.')
    parser.add_argument('--human-input', default='/Users/aoi-kumadaki/rnglib-self/trans/data/human_transitions.csv',
                        help='Path to the human transition metrics CSV file')
    parser.add_argument('--mt-input', default='/Users/aoi-kumadaki/rnglib-self/trans/data/mt_transitions.csv',
                        help='Path to the MT transition metrics CSV file')
    parser.add_argument('--combined-input', default='/Users/aoi-kumadaki/rnglib-self/trans/data/combined_transitions.csv',
                        help='Path to the combined transition metrics CSV file')
    parser.add_argument('--output-dir', default='/Users/aoi-kumadaki/rnglib-self/trans/figures',
                        help='Directory to save the output figures')
    parser.add_argument('--use-combined', action='store_true', 
                        help='Use the combined CSV file instead of separate files')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Define steps range
    steps_range = range(1, 11)
    
    # Create visualizations based on the input options
    if args.use_combined:
        # Load the combined data
        df = load_transition_data(args.combined_input)
        
        # Create transition matrix heatmaps for each step
        for step in steps_range:
            create_transition_matrix_heatmap(df, step, args.output_dir)
        
        # Create step comparison figure
        create_step_comparison_figure(df, steps_range, args.output_dir)
        
        # Create same-digit transition plot
        create_same_digit_transition_plot(df, steps_range, args.output_dir)
        
        print(f"All visualizations complete (using combined data). Output saved to {args.output_dir}/")
    else:
        # Load both human and MT data
        human_df = load_transition_data(args.human_input)
        mt_df = load_transition_data(args.mt_input)
        
        # Create transition matrix heatmaps for each step and source type
        for step in steps_range:
            # Human heatmaps
            create_transition_matrix_heatmap(human_df, step, args.output_dir, source_type="human")
            
            # MT heatmaps
            create_transition_matrix_heatmap(mt_df, step, args.output_dir, source_type="mt")
            
            # Comparison heatmaps
            create_comparison_transition_heatmaps(human_df, mt_df, step, args.output_dir)
        
        # Create step comparison figures
        create_step_comparison_figure(human_df, steps_range, args.output_dir, source_type="human")
        create_step_comparison_figure(mt_df, steps_range, args.output_dir, source_type="mt")
        
        # Create same-digit transition plots
        create_same_digit_transition_plot(human_df, steps_range, args.output_dir, source_type="human")
        create_same_digit_transition_plot(mt_df, steps_range, args.output_dir, source_type="mt")
        
        # Create human vs MT comparison plot
        create_human_mt_comparison_plot(human_df, mt_df, steps_range, args.output_dir)
        
        print(f"All visualizations complete. Output saved to {args.output_dir}/")

if __name__ == "__main__":
    main()