"""
Human vs Machine Random Number Classifier Package

This package provides tools for classifying random number sequences
as either human-generated or machine-generated.
"""

from .export_classifier import HumanMachineClassifier
from .calculate_features import (
    calculate_all_features,
    calculate_statistical_metrics,
    calculate_transition_features,
    calculate_features_for_sequences
)

__version__ = "1.0.0"
__author__ = "rnglib-self research project"

__all__ = [
    'HumanMachineClassifier',
    'calculate_all_features',
    'calculate_statistical_metrics',
    'calculate_transition_features',
    'calculate_features_for_sequences'
]