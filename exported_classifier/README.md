# Human vs Machine Random Number Classifier

This package contains a complete classifier for distinguishing between human-generated and machine-generated random number sequences, along with all necessary feature calculation dependencies.

## Overview

The classifier uses **527 features** derived from:
- **27 statistical metrics** (redundancy, entropy, pattern analysis, etc.)
- **500 transition probabilities** (steps 1-5, each step has 100 transitions: 10×10 digit transitions)

## Performance

- **Accuracy**: 98.31%
- **Precision**: 100.00%
- **Recall**: 96.61%
- **F1 Score**: 98.28%
- **ROC AUC**: 99.60%

## Package Contents

### Core Files
- `human_machine_classifier.pkl` - Trained classifier (LogisticRegression + StandardScaler) - **Download from GitHub Releases**
- `calculate_features.py` - Feature calculation from raw sequences

### Dependencies
- `stat/lib/` - Statistical metrics calculation modules
  - `metrics.py` - All statistical metric calculations
  - `calculate_stats.py` - Main statistical calculation script
  - `utils.py` - Utility functions
  - `visualize_metrics.py` - Visualization tools
- `trans/lib/` - Transition probability calculation modules
  - `transition_probs.py` - Core transition probability calculations
  - `calculate_transitions.py` - Main transition calculation script
  - `analyze_self_transitions.py` - Self-transition analysis
  - `visualize_transitions.py` - Visualization tools


## Quick Start

### 1. Load and Use Classifier

```python
import pickle
from calculate_features import calculate_all_features

# Load the trained classifier (download from GitHub Releases first)
with open('human_machine_classifier.pkl', 'rb') as f:
    classifier = pickle.load(f)

# Calculate features from sequence
sequence = [1, 4, 7, 2, 9, 0, 3, 8, 5, 6, 1, 3, 9, 2, 7]
features = calculate_all_features(sequence)

# Make predictions
prediction = classifier.predict([features])  # 0=Machine, 1=Human
probability = classifier.predict_proba([features])
```

### 2. Calculate Features from Raw Sequences

```python
from calculate_features import calculate_all_features

# Example sequence (list of digits 0-9)
sequence = [1, 4, 7, 2, 9, 0, 3, 8, 5, 6, 1, 3, 9, 2, 7]

# Calculate all required features
features = calculate_all_features(sequence)

# Use with classifier
prediction = classifier.predict(features)
```

### 3. Complete Pipeline

```python
import pickle
from calculate_features import calculate_all_features

# Load classifier
with open('human_machine_classifier.pkl', 'rb') as f:
    classifier = pickle.load(f)

# Your sequence data
sequences = [
    [1, 4, 7, 2, 9, 0, 3, 8, 5, 6],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    # ... more sequences
]

# Process each sequence
results = []
for i, sequence in enumerate(sequences):
    # Calculate features
    features = calculate_all_features(sequence)

    # Make prediction
    prediction = classifier.predict([features])[0]
    probability = classifier.predict_proba([features])[0]

    results.append({
        'sequence_id': i,
        'prediction': 'Human' if prediction == 1 else 'Machine',
        'human_probability': probability[1],
        'machine_probability': probability[0]
    })

# Display results
import pandas as pd
results_df = pd.DataFrame(results)
print(results_df)
```

## Required Features

The classifier expects exactly **527 features** in the following order:

### Statistical Features (27 total)
1. `redundancy` - Shannon entropy-based redundancy measure
2. `coupon_mean` - Mean steps to collect all digits
3. `coupon_std` - Standard deviation of coupon collector
4. `repetition_gap_mean` - Mean gap between repeated digits
5. `repetition_gap_std` - Standard deviation of repetition gaps
6. `adjacent` - Adjacent digit pattern score
7. `tpi` - Turning Point Index
8. `pl1`-`pl5` - Poker-like test statistics
9. `rp` - Runs and patterns score
10. `autocorr_lag1` - Lag-1 autocorrelation
11. `adjacent_diff_mean` - Mean of adjacent differences
12. `adjacent_diff_std` - Standard deviation of adjacent differences
13. `max_min_ratio` - Ratio of max to min digit frequencies
14. `freq_0`-`freq_9` - Frequencies of digits 0-9

### Transition Features (500 total)
- **Step 1**: `step1_trans_0_to_0` through `step1_trans_9_to_9` (100 features)
- **Step 2**: `step2_trans_0_to_0` through `step2_trans_9_to_9` (100 features)
- **Step 3**: `step3_trans_0_to_0` through `step3_trans_9_to_9` (100 features)
- **Step 4**: `step4_trans_0_to_0` through `step4_trans_9_to_9` (100 features)
- **Step 5**: `step5_trans_0_to_0` through `step5_trans_9_to_9` (100 features)

Each `stepX_trans_i_to_j` represents the probability of transitioning from digit `i` to digit `j` at step distance `X`.

## Dependencies

This package requires:
- Python 3.6+
- pandas
- numpy
- scikit-learn
- pickle (built-in)

## Input Requirements

### Sequence Format
- Sequences should be lists or arrays of integers
- Each integer should be in range 0-9
- Minimum recommended sequence length: 50 digits
- Optimal sequence length: 100+ digits

### Feature Calculation
- Features are automatically calculated from raw sequences
- No manual feature engineering required
- All 527 features must be present for prediction

## Model Details

### Architecture
- **Algorithm**: Logistic Regression
- **Regularization**: L2 with C=1.0
- **Feature Scaling**: StandardScaler (z-score normalization)
- **Class Weighting**: Balanced

### Feature Selection Strategy
- **Parameter Reduction**: Uses steps 1-5 instead of 1-10 (50% reduction)
- **Performance Maintained**: >98% accuracy with reduced parameters
- **Computational Efficiency**: Faster feature calculation and prediction

### Training Data
- **Human sequences**: 196 sequences from 20 human subjects
- **Machine sequences**: Generated using Mersenne Twister
- **Validation**: 5-fold cross-validation
- **Test Split**: 30% holdout for final evaluation

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```python
   # Make sure you're in the correct directory
   import sys
   sys.path.append('/path/to/exported_classifier')
   ```

2. **Feature Mismatch**
   ```python
   # Features are calculated automatically from calculate_all_features()
   # Ensure your sequence has sufficient length (≥50 digits recommended)
   features = calculate_all_features(your_sequence)
   print(f"Calculated {len(features)} features")
   ```

3. **Sequence Length Issues**
   - Ensure sequences have sufficient length (≥50 digits recommended)
   - Very short sequences may produce unreliable transition probabilities

4. **Invalid Digit Values**
   - Ensure all sequence values are integers in range 0-9
   - Handle any preprocessing (e.g., removing non-digit characters) before calculation

## License

This classifier is part of the rnglib-self research project for human vs machine random number analysis.