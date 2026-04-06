"""
Data utility functions.
"""

from typing import Tuple


def calculate_next_period(year: int, month: int) -> Tuple[int, int]:
    """
    Calculate next year and month for validation data.
    
    Args:
        year: Current year
        month: Current month
    
    Returns:
        Tuple of (next_year, next_month)
    """
    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    return next_year, next_month
