"""
🛠️ Helper Utilities - Universal Helper Functions

Comprehensive collection of helper functions for common operations
with robust error handling and performance optimization.
"""

import re
import uuid
import time
import functools
from typing import Any, Dict, Optional, Callable, Union
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime
import logging


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string

    Args:
        dt: Datetime object to format
        format_str: Format string for datetime

    Returns:
        Formatted timestamp string
    """
    try:
        if dt is None:
            return ""
        return dt.strftime(format_str)
    except Exception:
        return ""


def parse_duration(duration_str: str) -> float:
    """
    Parse duration string to seconds

    Args:
        duration_str: Duration string like '30s', '5m', '2h', '1d'

    Returns:
        Duration in seconds
    """
    try:
        if not duration_str or not isinstance(duration_str, str):
            return 0.0

        duration_str = duration_str.strip().lower()

        # Extract number and unit
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([smhd]?)$', duration_str)
        if not match:
            return 0.0

        value = float(match.group(1))
        unit = match.group(2) or 's'  # Default to seconds

        # Convert to seconds
        multipliers = {
            's': 1,      # seconds
            'm': 60,     # minutes
            'h': 3600,   # hours
            'd': 86400   # days
        }

        return value * multipliers.get(unit, 1)

    except Exception:
        return 0.0


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    try:
        if seconds < 0:
            return "0s"

        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"

    except Exception:
        return "0s"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human readable string

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    try:
        if size_bytes == 0:
            return "0 B"

        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        unit_index = 0
        size = float(size_bytes)

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"

    except Exception:
        return "0 B"


def generate_uuid(prefix: str = "") -> str:
    """
    Generate UUID with optional prefix

    Args:
        prefix: Optional prefix for UUID

    Returns:
        Generated UUID string
    """
    try:
        generated_uuid = str(uuid.uuid4())
        return f"{prefix}{generated_uuid}" if prefix else generated_uuid
    except Exception:
        # Fallback to timestamp-based ID
        return f"{prefix}{int(time.time() * 1000000)}"


def safe_dict_get(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary value using dot notation

    Args:
        data: Dictionary to search
        key_path: Dot-separated key path (e.g., 'server.host')
        default: Default value if key not found

    Returns:
        Value at key path or default
    """
    try:
        keys = key_path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    except Exception:
        return default


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0,
                    backoff_factor: float = 2.0,
                    exceptions: tuple = (Exception,)) -> Callable:
    """
    Decorator to retry function on failure

    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1

                    if attempt >= max_attempts:
                        raise e

                    logging.warning(f"Attempt {attempt} failed for {func.__name__}: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff_factor

            return None  # Should never reach here

        return wrapper
    return decorator


def validate_email(email: str) -> bool:
    """
    Validate email address format

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    try:
        if not email or not isinstance(email, str):
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    except Exception:
        return False


def validate_url(url: str) -> bool:
    """
    Validate URL format

    Args:
        url: URL to validate

    Returns:
        True if valid URL format
    """
    try:
        if not url or not isinstance(url, str):
            return False

        parsed = urlparse(url.strip())
        return all([parsed.scheme, parsed.netloc])

    except Exception:
        return False


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename for filesystem compatibility

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        Sanitized filename
    """
    try:
        if not filename:
            return "untitled"

        # Remove or replace invalid characters
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(invalid_chars, '_', filename)

        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')

        # Ensure not empty
        if not sanitized:
            sanitized = "untitled"

        # Truncate if too long
        if len(sanitized) > max_length:
            name, ext = Path(sanitized).stem, Path(sanitized).suffix
            max_name_length = max_length - len(ext)
            sanitized = name[:max_name_length] + ext

        return sanitized

    except Exception:
        return "untitled"


def deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries

    Args:
        target: Target dictionary to merge into
        source: Source dictionary to merge from

    Returns:
        Merged dictionary
    """
    try:
        result = target.copy()

        for key, value in source.items():
            if (key in result and
                isinstance(result[key], dict) and
                isinstance(value, dict)):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    except Exception:
        return target


def get_nested_value(data: Dict[str, Any], keys: list, default: Any = None) -> Any:
    """
    Get nested value from dictionary using key list

    Args:
        data: Dictionary to search
        keys: List of keys for nested access
        default: Default value if key not found

    Returns:
        Nested value or default
    """
    try:
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    except Exception:
        return default


def set_nested_value(data: Dict[str, Any], keys: list, value: Any) -> bool:
    """
    Set nested value in dictionary using key list

    Args:
        data: Dictionary to modify
        keys: List of keys for nested access
        value: Value to set

    Returns:
        True if successful
    """
    try:
        current = data

        # Navigate to parent
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set value
        current[keys[-1]] = value
        return True

    except Exception:
        return False


def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary with dot notation keys

    Args:
        data: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Key separator

    Returns:
        Flattened dictionary
    """
    try:
        items = []

        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key

            if isinstance(value, dict):
                items.extend(flatten_dict(value, new_key, sep).items())
            else:
                items.append((new_key, value))

        return dict(items)

    except Exception:
        return {}


def unflatten_dict(data: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """
    Unflatten dictionary with dot notation keys

    Args:
        data: Flattened dictionary
        sep: Key separator

    Returns:
        Nested dictionary
    """
    try:
        result = {}

        for key, value in data.items():
            keys = key.split(sep)
            set_nested_value(result, keys, value)

        return result

    except Exception:
        return {}


def chunk_list(data: list, chunk_size: int) -> list:
    """
    Split list into chunks of specified size

    Args:
        data: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    try:
        if chunk_size <= 0:
            return [data]

        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    except Exception:
        return []


def debounce(wait_time: float) -> Callable:
    """
    Debounce decorator to limit function call frequency

    Args:
        wait_time: Wait time in seconds

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()

            if current_time - last_called[0] >= wait_time:
                last_called[0] = current_time
                return func(*args, **kwargs)

        return wrapper
    return decorator


def memoize(maxsize: int = 128) -> Callable:
    """
    Memoization decorator with LRU cache

    Args:
        maxsize: Maximum cache size

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        return functools.lru_cache(maxsize=maxsize)(func)
    return decorator


def measure_time(func: Callable) -> Callable:
    """
    Decorator to measure function execution time

    Args:
        func: Function to measure

    Returns:
        Decorated function that logs execution time
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_time = end_time - start_time
        logging.debug(f"{func.__name__} executed in {execution_time:.4f}s")

        return result

    return wrapper
