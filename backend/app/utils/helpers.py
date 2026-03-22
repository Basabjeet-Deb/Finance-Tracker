"""
Helper utility functions
Common functions used across the application
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def format_currency(amount: float, currency: str = "₹") -> str:
    """
    Format amount as currency string
    
    Args:
        amount: Amount to format
        currency: Currency symbol (default: ₹)
        
    Returns:
        Formatted currency string (e.g., "₹50,000")
    """
    return f"{currency}{amount:,.0f}"


def calculate_percentage(part: float, total: float) -> float:
    """
    Calculate percentage safely (handles division by zero)
    
    Args:
        part: Part value
        total: Total value
        
    Returns:
        Percentage (0-100)
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, 1)


def get_month_range(months_back: int = 0) -> tuple:
    """
    Get start and end dates for a month
    
    Args:
        months_back: Number of months to go back (0 = current month)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.now()
    
    # Calculate target month
    target_month = today.month - months_back
    target_year = today.year
    
    while target_month <= 0:
        target_month += 12
        target_year -= 1
    
    # First day of month
    start_date = datetime(target_year, target_month, 1)
    
    # Last day of month
    if target_month == 12:
        end_date = datetime(target_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(target_year, target_month + 1, 1) - timedelta(days=1)
    
    return start_date.date(), end_date.date()


def get_month_string(months_back: int = 0) -> str:
    """
    Get month string in YYYY-MM format
    
    Args:
        months_back: Number of months to go back (0 = current month)
        
    Returns:
        Month string (e.g., "2026-03")
    """
    today = datetime.now()
    
    target_month = today.month - months_back
    target_year = today.year
    
    while target_month <= 0:
        target_month += 12
        target_year -= 1
    
    return f"{target_year:04d}-{target_month:02d}"


def aggregate_by_category(expenses: List[Dict]) -> Dict[str, float]:
    """
    Aggregate expenses by category
    
    Args:
        expenses: List of expense dicts with 'category' and 'amount'
        
    Returns:
        Dict mapping category to total amount
    """
    aggregated = {}
    
    for expense in expenses:
        category = expense.get("category", "Other")
        amount = expense.get("amount", 0)
        
        if category not in aggregated:
            aggregated[category] = 0
        aggregated[category] += amount
    
    return aggregated


def sort_by_amount(items: Dict[str, float], descending: bool = True) -> List[tuple]:
    """
    Sort dictionary by amount
    
    Args:
        items: Dict mapping keys to amounts
        descending: Sort in descending order (default: True)
        
    Returns:
        List of (key, amount) tuples sorted by amount
    """
    return sorted(items.items(), key=lambda x: x[1], reverse=descending)


def validate_month_format(month_str: str) -> bool:
    """
    Validate month string format (YYYY-MM)
    
    Args:
        month_str: Month string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(month_str, "%Y-%m")
        return True
    except ValueError:
        return False


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers (handles division by zero)
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if denominator is zero
        
    Returns:
        Result of division or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(max_value, value))


def round_to_nearest(value: float, nearest: int = 100) -> float:
    """
    Round value to nearest multiple
    
    Args:
        value: Value to round
        nearest: Round to nearest multiple of this (default: 100)
        
    Returns:
        Rounded value
    """
    return round(value / nearest) * nearest


def log_error(error: Exception, context: str = "") -> None:
    """
    Log error with context
    
    Args:
        error: Exception to log
        context: Additional context string
    """
    if context:
        logger.error(f"{context}: {str(error)}")
    else:
        logger.error(f"Error: {str(error)}")
    
    # Log full traceback in debug mode
    import traceback
    logger.debug(traceback.format_exc())


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries (later dicts override earlier ones)
    
    Args:
        *dicts: Variable number of dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def filter_none_values(data: Dict) -> Dict:
    """
    Remove None values from dictionary
    
    Args:
        data: Dictionary to filter
        
    Returns:
        Dictionary with None values removed
    """
    return {k: v for k, v in data.items() if v is not None}


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
