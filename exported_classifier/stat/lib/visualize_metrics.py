#!/usr/bin/env python3
"""
Visualization script for randomness metrics.
Creates histograms for each numeric metric in the CSV file.
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
from scipy import stats

def load_metrics_data(file_path: str) -> pd.DataFrame:
    """
    Load metrics data from CSV file.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file containing metrics data
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing the metrics data
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded data from {file_path}")
        print(f"Found {len(df)} rows and {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def identify_numeric_metrics(df: pd.DataFrame, exclude_columns: Optional[List[str]] = None) -> List[str]:
    """
    Identify numeric columns (metrics) in the DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the metrics data
    exclude_columns : List[str], optional
        List of column names to exclude from metrics (e.g., 'sequence_id', 'subject_id')
        
    Returns:
    --------
    List[str]
        List of column names that contain numeric metrics
    """
    if exclude_columns is None:
        exclude_columns = ['sequence_id', 'subject_id', 'sequence_number']
    
    # Get numeric columns
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    # Exclude specified columns
    metric_columns = [col for col in numeric_columns if col not in exclude_columns]
    
    print(f"Found {len(metric_columns)} numeric metrics: {', '.join(metric_columns)}")
    return metric_columns

def create_comparison_histograms(
    human_df: pd.DataFrame,
    mt_df: pd.DataFrame,
    metric_columns: List[str],
    output_dir: str,
    bins: int = 20,
    figsize: Tuple[int, int] = (12, 7)
) -> None:
    """
    Create comparison histograms for each metric showing both human and MT data.
    
    Parameters:
    -----------
    human_df : pd.DataFrame
        DataFrame containing the human metrics data
    mt_df : pd.DataFrame
        DataFrame containing the MT metrics data
    metric_columns : List[str]
        List of column names that contain numeric metrics
    output_dir : str
        Directory to save the output figures
    bins : int, optional
        Number of bins for the histograms (default: 20)
    figsize : Tuple[int, int], optional
        Figure size (width, height) in inches (default: (12, 7))
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Set the style
    sns.set(style="whitegrid")
    
    # Create histograms for each metric
    for metric in metric_columns:
        plt.figure(figsize=figsize)
        
        # Get the data for this metric
        human_data = human_df[metric].dropna()
        mt_data = mt_df[metric].dropna()
        
        # Calculate combined range for binning
        min_val = min(human_data.min(), mt_data.min())
        max_val = max(human_data.max(), mt_data.max())
        
        # Handle special cases for coupon metrics which may have very large outliers
        if 'coupon' in metric:
            # For coupon metrics, focus on the 0-75 range to better visualize the bulk of the data
            # while excluding extreme outliers around 300
            max_val = 75.0  # Set a fixed upper limit to get a consistent view
            print(f"Note: For {metric}, limiting range to {max_val:.2f} to focus on the main distribution")
        
        # Create bin edges with uniform width across the combined range
        bin_edges = np.linspace(min_val, max_val, bins + 1)
        
        # Plot histograms without KDE
        sns.histplot(human_data, bins=bin_edges, color='blue', alpha=0.7, label='Human')
        sns.histplot(mt_data, bins=bin_edges, color='red', alpha=0.7, label='MT')
        
        # Perform statistical tests
        # Test for normality first
        human_normal = stats.shapiro(human_data)[1] > 0.05
        mt_normal = stats.shapiro(mt_data)[1] > 0.05
        
        # Choose appropriate test
        if human_normal and mt_normal:
            # Both normal - use t-test
            t_stat, p_value = stats.ttest_ind(human_data, mt_data)
            test_name = "t-test"
        else:
            # At least one not normal - use Mann-Whitney U test
            u_stat, p_value = stats.mannwhitneyu(human_data, mt_data, alternative='two-sided')
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
        
        # Add vertical lines for means
        plt.axvline(human_data.mean(), color='blue', linestyle='--', alpha=0.8,
                   label=f'Human Mean: {human_data.mean():.4f}')
        plt.axvline(mt_data.mean(), color='red', linestyle='--', alpha=0.8,
                   label=f'MT Mean: {mt_data.mean():.4f}')
        
        # Add statistical summary as text box
        stats_text = '\n'.join((
            f'Human: μ={human_data.mean():.4f}, σ²={human_data.var():.4f}',
            f'MT: μ={mt_data.mean():.4f}, σ²={mt_data.var():.4f}'
        ))
        
        props = dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
        plt.text(0.98, 0.98, stats_text, transform=plt.gca().transAxes, 
                fontsize=18, verticalalignment='top', horizontalalignment='right', bbox=props)
        
        # Set labels and title with larger font sizes
        plt.xlabel(metric, fontsize=20)
        plt.ylabel('Count', fontsize=20)
        plt.title(f'Comparison of {metric}: Human vs MT\n{test_name}: {sig_text}', fontsize=24)
        plt.legend(fontsize=16)
        plt.tick_params(axis='both', which='major', labelsize=16)
        
        # Save figure
        output_path = os.path.join(output_dir, f'{metric}_comparison.png')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        
        print(f"Created comparison histogram for {metric} at {output_path}")

def create_histograms(
    df: pd.DataFrame, 
    metric_columns: List[str],
    output_dir: str,
    bins: int = 20,
    figsize: Tuple[int, int] = (10, 6)
) -> None:
    """
    Create histograms for each metric and save them to files.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the metrics data
    metric_columns : List[str]
        List of column names that contain numeric metrics
    output_dir : str
        Directory to save the output figures
    bins : int, optional
        Number of bins for the histograms (default: 20)
    figsize : Tuple[int, int], optional
        Figure size (width, height) in inches (default: (10, 6))
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Set the style
    sns.set(style="whitegrid")
    
    # Check if the dataframe has a 'source_type' column
    has_source_types = 'source_type' in df.columns
    
    # Create histograms for each metric
    for metric in metric_columns:
        plt.figure(figsize=figsize)
        
        if has_source_types:
            # Separate by source type and create comparison histogram
            source_types = df['source_type'].unique()
            
            # Get data for all source types
            all_data = {}
            for source_type in source_types:
                all_data[source_type] = df[df['source_type'] == source_type][metric].dropna()
            
            # Calculate combined range for binning
            min_val = min([data.min() for data in all_data.values()])
            max_val = max([data.max() for data in all_data.values()])
            
            # Handle special cases for metrics with outliers
            if 'coupon' in metric:
                # For coupon metrics, focus on the 0-75 range to better visualize the bulk of the data
                max_val = 75.0  # Set a fixed upper limit to get a consistent view
                print(f"Note: For {metric}, limiting range to {max_val:.2f} to focus on the main distribution")
            
            # Create bin edges with uniform width
            bin_edges = np.linspace(min_val, max_val, bins + 1)
            
            for source_type in source_types:
                # Plot histogram without KDE
                data = all_data[source_type]
                color = 'blue' if source_type == 'human' else 'red'
                sns.histplot(data, bins=bin_edges, alpha=0.7, 
                            label=source_type.capitalize(), color=color)
            
            title = f'Comparison of {metric}: Human vs MT'
        else:
            # Get the data for this metric
            data = df[metric].dropna()
            
            # Handle special cases for metrics with outliers
            min_val = data.min()
            max_val = data.max()
            
            if 'coupon' in metric:
                # For coupon metrics, focus on the 0-75 range to better visualize the bulk of the data
                max_val = 75.0  # Set a fixed upper limit to get a consistent view
                print(f"Note: For {metric}, limiting range to {max_val:.2f} to focus on the main distribution")
            
            # Create bin edges with uniform width
            bin_edges = np.linspace(min_val, max_val, bins + 1)
            
            # Plot histogram without KDE
            sns.histplot(data, bins=bin_edges)
            
            title = f'Distribution of {metric}'
        
        # Set labels and title
        plt.xlabel(metric)
        plt.ylabel('Count')
        plt.title(title)
        plt.legend()
        
        # Save figure
        output_path = os.path.join(output_dir, f'{metric}_histogram.png')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        
        print(f"Created histogram for {metric} at {output_path}")

def create_combined_figure(
    df: pd.DataFrame, 
    metric_columns: List[str],
    output_dir: str,
    bins: int = 15,
) -> None:
    """
    Create a combined figure with histograms for all metrics.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the metrics data
    metric_columns : List[str]
        List of column names that contain numeric metrics
    output_dir : str
        Directory to save the output figure
    bins : int, optional
        Number of bins for the histograms (default: 15)
    """
    # Calculate number of rows and columns for subplots
    n_metrics = len(metric_columns)
    n_cols = min(3, n_metrics)  # Maximum 3 columns
    n_rows = (n_metrics + n_cols - 1) // n_cols  # Ceiling division
    
    # Create figure and subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*5, n_rows*4))
    
    # Make axes iterable even if there's only one subplot
    if n_metrics == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    # Check if the dataframe has a 'source_type' column
    has_source_types = 'source_type' in df.columns
    
    # Plot each metric
    for i, metric in enumerate(metric_columns):
        ax = axes[i]
        
        if has_source_types:
            # Separate by source type and create comparison histogram
            source_types = df['source_type'].unique()
            
            # Get data for all source types
            all_data = {}
            for source_type in source_types:
                all_data[source_type] = df[df['source_type'] == source_type][metric].dropna()
            
            # Calculate combined range for binning
            min_val = min([data.min() for data in all_data.values()])
            max_val = max([data.max() for data in all_data.values()])
            
            # Handle special cases for metrics with outliers
            if 'coupon' in metric:
                # For coupon metrics, focus on the 0-75 range to better visualize the bulk of the data
                max_val = 75.0  # Set a fixed upper limit to get a consistent view
                print(f"Note: For {metric} in all_metrics, limiting range to {max_val:.2f} to focus on the main distribution")
            
            # Create bin edges with uniform width
            bin_edges = np.linspace(min_val, max_val, bins + 1)
            
            for source_type in source_types:
                # Plot histogram without KDE
                data = all_data[source_type]
                color = 'blue' if source_type == 'human' else 'red'
                sns.histplot(data, bins=bin_edges, alpha=0.7, ax=ax,
                            label=source_type.capitalize(), color=color)
            
            title = f'Comparison of {metric}'
        else:
            # Get the data for this metric
            data = df[metric].dropna()
            
            # Handle special cases for metrics with outliers
            min_val = data.min()
            max_val = data.max()
            
            if 'coupon' in metric:
                # For coupon metrics, focus on the 0-75 range to better visualize the bulk of the data
                max_val = 75.0  # Set a fixed upper limit to get a consistent view
                print(f"Note: For {metric} in all_metrics, limiting range to {max_val:.2f} to focus on the main distribution")
            
            # Create bin edges with uniform width
            bin_edges = np.linspace(min_val, max_val, bins + 1)
            
            # Plot histogram without KDE
            sns.histplot(data, bins=bin_edges, ax=ax)
            
            title = f'Distribution of {metric}'
        
        # Set labels and title with larger font sizes
        ax.set_xlabel(metric, fontsize=20)
        ax.set_ylabel('Count', fontsize=20)
        ax.set_title(title, fontsize=24)
        ax.legend(fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=16)
    
    # Hide any unused subplots
    for i in range(n_metrics, len(axes)):
        axes[i].set_visible(False)
    
    # Save figure
    output_path = os.path.join(output_dir, 'all_metrics_histograms.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Created combined histogram at {output_path}")

def create_comparison_combined_figure(
    human_df: pd.DataFrame,
    mt_df: pd.DataFrame,
    metric_columns: List[str],
    output_dir: str,
    bins: int = 15,
) -> None:
    """
    Create a combined figure with comparison histograms for all metrics.
    
    Parameters:
    -----------
    human_df : pd.DataFrame
        DataFrame containing the human metrics data
    mt_df : pd.DataFrame
        DataFrame containing the MT metrics data
    metric_columns : List[str]
        List of column names that contain numeric metrics
    output_dir : str
        Directory to save the output figure
    bins : int, optional
        Number of bins for the histograms (default: 15)
    """
    # Calculate number of rows and columns for subplots
    n_metrics = len(metric_columns)
    n_cols = min(3, n_metrics)  # Maximum 3 columns
    n_rows = (n_metrics + n_cols - 1) // n_cols  # Ceiling division
    
    # Create figure and subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*5, n_rows*4))
    
    # Make axes iterable even if there's only one subplot
    if n_metrics == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    # Plot each metric
    for i, metric in enumerate(metric_columns):
        ax = axes[i]
        
        # Get the data for this metric
        human_data = human_df[metric].dropna()
        mt_data = mt_df[metric].dropna()
        
        # Calculate combined range for binning
        min_val = min(human_data.min(), mt_data.min())
        max_val = max(human_data.max(), mt_data.max())
        
        # Handle special cases for coupon metrics which may have very large outliers
        if 'coupon' in metric:
            # For coupon metrics, focus on the 0-75 range to better visualize the bulk of the data
            max_val = 75.0  # Set a fixed upper limit to get a consistent view
            print(f"Note: For {metric} in combined figure, limiting range to {max_val:.2f} to focus on the main distribution")
        
        # Create bin edges with uniform width across the combined range
        bin_edges = np.linspace(min_val, max_val, bins + 1)
        
        # Plot histograms without KDE
        sns.histplot(human_data, bins=bin_edges, color='blue', alpha=0.7, ax=ax, label='Human')
        sns.histplot(mt_data, bins=bin_edges, color='red', alpha=0.7, ax=ax, label='MT')
        
        # Perform statistical tests
        # Test for normality first
        human_normal = stats.shapiro(human_data)[1] > 0.05 if len(human_data) <= 5000 else True
        mt_normal = stats.shapiro(mt_data)[1] > 0.05 if len(mt_data) <= 5000 else True
        
        # Choose appropriate test
        if human_normal and mt_normal:
            # Both normal - use t-test
            t_stat, p_value = stats.ttest_ind(human_data, mt_data)
            test_name = "t-test"
        else:
            # At least one not normal - use Mann-Whitney U test
            u_stat, p_value = stats.mannwhitneyu(human_data, mt_data, alternative='two-sided')
            test_name = "Mann-Whitney U"
        
        # Determine significance level
        if p_value < 0.001:
            sig_text = "***"
        elif p_value < 0.01:
            sig_text = "**"
        elif p_value < 0.05:
            sig_text = "*"
        else:
            sig_text = "n.s."
        
        # Add vertical lines for means
        ax.axvline(human_data.mean(), color='blue', linestyle='--', alpha=0.8)
        ax.axvline(mt_data.mean(), color='red', linestyle='--', alpha=0.8)
        
        # Add significance annotation with statistics
        stats_text = f"{test_name}\np={p_value:.3f} {sig_text}\nHuman: μ={human_data.mean():.3f}, σ²={human_data.var():.3f}\nMT: μ={mt_data.mean():.3f}, σ²={mt_data.var():.3f}"
        ax.text(0.98, 0.98, stats_text, 
               transform=ax.transAxes, fontsize=14, 
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Set labels and title with larger font sizes
        ax.set_xlabel(metric, fontsize=20)
        ax.set_ylabel('Count', fontsize=20)
        ax.set_title(f'Comparison of {metric}', fontsize=24)
        ax.legend(fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=16)
    
    # Hide any unused subplots
    for i in range(n_metrics, len(axes)):
        axes[i].set_visible(False)
    
    # Save figure
    output_path = os.path.join(output_dir, 'all_metrics_comparison.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Created combined comparison histogram at {output_path}")

def main():
    """Main function to load data and create visualizations."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Visualize randomness metrics.')
    parser.add_argument('--human-input', default='/Users/aoi-kumadaki/rnglib-self/stat/data/human_metrics.csv',
                        help='Path to the human metrics CSV file')
    parser.add_argument('--mt-input', default='/Users/aoi-kumadaki/rnglib-self/stat/data/mt_metrics.csv',
                        help='Path to the MT metrics CSV file')
    parser.add_argument('--combined-input', default='/Users/aoi-kumadaki/rnglib-self/stat/data/combined_metrics.csv',
                        help='Path to the combined metrics CSV file')
    parser.add_argument('--output-dir', default='/Users/aoi-kumadaki/rnglib-self/stat/figures',
                        help='Directory to save the output figures')
    parser.add_argument('--use-combined', action='store_true', 
                        help='Use the combined CSV file instead of separate files')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Create visualizations based on the input options
    if args.use_combined:
        # Load the combined data
        df = load_metrics_data(args.combined_input)
        
        # Identify numeric metrics
        exclude_columns = ['sequence_id', 'subject_id', 'sequence_number', 'source_type']
        metric_columns = identify_numeric_metrics(df, exclude_columns)
        
        # Create histograms
        create_histograms(df, metric_columns, args.output_dir)
        
        # Create combined figure
        create_combined_figure(df, metric_columns, args.output_dir)
        
        print(f"All visualizations complete (using combined data). Output saved to {args.output_dir}/")
    else:
        # Load both human and MT data
        human_df = load_metrics_data(args.human_input)
        mt_df = load_metrics_data(args.mt_input)
        
        # Identify numeric metrics (should be the same for both datasets)
        exclude_columns = ['sequence_id', 'subject_id', 'sequence_number', 'source_type']
        human_metric_columns = identify_numeric_metrics(human_df, exclude_columns)
        mt_metric_columns = identify_numeric_metrics(mt_df, exclude_columns)
        
        # Ensure we're using the same metrics from both datasets
        metric_columns = sorted(list(set(human_metric_columns) & set(mt_metric_columns)))
        print(f"Using {len(metric_columns)} common metrics for comparison")
        
        # Create individual histograms for human data
        create_histograms(human_df, metric_columns, os.path.join(args.output_dir, 'human'))
        
        # Create individual histograms for MT data
        create_histograms(mt_df, metric_columns, os.path.join(args.output_dir, 'mt'))
        
        # Create comparison histograms
        create_comparison_histograms(human_df, mt_df, metric_columns, args.output_dir)
        
        # Create combined comparison figure
        create_comparison_combined_figure(human_df, mt_df, metric_columns, args.output_dir)
        
        print(f"All visualizations complete. Output saved to {args.output_dir}/")
        
    print("To see the comparison histograms, check the files with '_comparison' in their names.")

if __name__ == "__main__":
    main()