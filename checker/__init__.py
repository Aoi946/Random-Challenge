"""
Randomness Checker Package

A tool for determining if number sequences exhibit true randomness
(like Mersenne Twister) or contain human-generated patterns.

Usage:
    from checker import check_sequence_randomness, print_randomness_report

    result = check_sequence_randomness(your_metrics)
    print_randomness_report(result)
"""

from .randomness_checker import (
    check_sequence_randomness,
    print_randomness_report,
    get_required_metrics
)

__version__ = "1.0.0"
__author__ = "rnglib-self research project"

__all__ = [
    'check_sequence_randomness',
    'print_randomness_report',
    'get_required_metrics'
]