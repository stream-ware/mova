"""
📝 Text Utilities - Advanced Text Processing and Manipulation

Comprehensive text processing utilities for cleaning, formatting, encoding,
and advanced text manipulation with Unicode support and performance optimization.
"""

import re
import html
import base64
import unicodedata
from typing import List, Optional, Dict, Any, Union
from urllib.parse import quote, unquote
import logging


def clean_text(text: str, remove_extra_whitespace: bool = True,
               remove_special_chars: bool = False) -> str:
    """
    Clean and normalize text

    Args:
        text: Input text to clean
        remove_extra_whitespace: Remove extra whitespace
        remove_special_chars: Remove special characters

    Returns:
        Cleaned text
    """
    try:
        if not text:
            return ""

        # Remove HTML tags
        cleaned = remove_html_tags(text)

        # Normalize Unicode
        cleaned = unicodedata.normalize('NFKC', cleaned)

        # Remove special characters if requested
        if remove_special_chars:
            cleaned = re.sub(r'[^\w\s\-_.,!?;:]', '', cleaned)

        # Normalize whitespace
        if remove_extra_whitespace:
            cleaned = normalize_whitespace(cleaned)

        return cleaned.strip()

    except Exception as e:
        logging.error(f"Error cleaning text: {e}")
        return text


def extract_numbers(text: str, include_floats: bool = True) -> List[Union[int, float]]:
    """
    Extract all numbers from text

    Args:
        text: Input text
        include_floats: Include floating point numbers

    Returns:
        List of extracted numbers
    """
    try:
        if not text:
            return []

        if include_floats:
            # Pattern for integers and floats
            pattern = r'-?\d+\.?\d*'
            matches = re.findall(pattern, text)

            numbers = []
            for match in matches:
                try:
                    if '.' in match:
                        numbers.append(float(match))
                    else:
                        numbers.append(int(match))
                except ValueError:
                    continue

            return numbers
        else:
            # Pattern for integers only
            pattern = r'-?\d+'
            matches = re.findall(pattern, text)

            return [int(match) for match in matches]

    except Exception as e:
        logging.error(f"Error extracting numbers: {e}")
        return []


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    try:
        if not text or max_length <= 0:
            return ""

        if len(text) <= max_length:
            return text

        # Account for suffix length
        effective_length = max_length - len(suffix)
        if effective_length <= 0:
            return suffix[:max_length]

        # Try to break at word boundary
        truncated = text[:effective_length]
        last_space = truncated.rfind(' ')

        if last_space > effective_length * 0.8:  # Only break at word if close to end
            truncated = truncated[:last_space]

        return truncated + suffix

    except Exception:
        return text[:max_length] if text else ""


def slugify(text: str, max_length: int = 50, separator: str = "-") -> str:
    """
    Convert text to URL-friendly slug

    Args:
        text: Input text
        max_length: Maximum slug length
        separator: Word separator character

    Returns:
        URL-friendly slug
    """
    try:
        if not text:
            return ""

        # Convert to lowercase
        slug = text.lower().strip()

        # Remove HTML tags
        slug = remove_html_tags(slug)

        # Normalize Unicode and convert to ASCII
        slug = unicodedata.normalize('NFKD', slug)
        slug = slug.encode('ascii', 'ignore').decode('ascii')

        # Replace spaces and special characters with separator
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', separator, slug)

        # Remove leading/trailing separators
        slug = slug.strip(separator)

        # Truncate if too long
        if len(slug) > max_length:
            slug = slug[:max_length].rstrip(separator)

        return slug

    except Exception:
        return "slug"


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text

    Args:
        text: Input text

    Returns:
        Text with normalized whitespace
    """
    try:
        if not text:
            return ""

        # Replace multiple whitespace with single space
        normalized = re.sub(r'\s+', ' ', text)

        # Remove trailing whitespace from lines
        lines = normalized.split('\n')
        normalized_lines = [line.rstrip() for line in lines]

        # Remove empty lines at start and end
        while normalized_lines and not normalized_lines[0].strip():
            normalized_lines.pop(0)
        while normalized_lines and not normalized_lines[-1].strip():
            normalized_lines.pop()

        return '\n'.join(normalized_lines)

    except Exception:
        return text


def remove_html_tags(text: str, keep_content: bool = True) -> str:
    """
    Remove HTML tags from text

    Args:
        text: Input text with HTML
        keep_content: Keep text content of tags

    Returns:
        Text without HTML tags
    """
    try:
        if not text:
            return ""

        if keep_content:
            # Remove HTML tags but keep content
            clean = re.sub(r'<[^>]+>', '', text)

            # Decode HTML entities
            clean = html.unescape(clean)

            return clean
        else:
            # Remove entire HTML tags including content
            clean = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'<[^>]+>', '', clean)

            return html.unescape(clean)

    except Exception:
        return text


def encode_base64(text: str, encoding: str = 'utf-8') -> str:
    """
    Encode text to base64

    Args:
        text: Input text
        encoding: Text encoding

    Returns:
        Base64 encoded string
    """
    try:
        if not text:
            return ""

        encoded_bytes = text.encode(encoding)
        b64_bytes = base64.b64encode(encoded_bytes)
        return b64_bytes.decode('ascii')

    except Exception as e:
        logging.error(f"Error encoding base64: {e}")
        return ""


def decode_base64(encoded_text: str, encoding: str = 'utf-8') -> str:
    """
    Decode base64 text

    Args:
        encoded_text: Base64 encoded text
        encoding: Target text encoding

    Returns:
        Decoded text
    """
    try:
        if not encoded_text:
            return ""

        b64_bytes = encoded_text.encode('ascii')
        decoded_bytes = base64.b64decode(b64_bytes)
        return decoded_bytes.decode(encoding)

    except Exception as e:
        logging.error(f"Error decoding base64: {e}")
        return ""


def word_count(text: str, count_type: str = 'words') -> int:
    """
    Count words, characters, or lines in text

    Args:
        text: Input text
        count_type: Type of count ('words', 'chars', 'lines')

    Returns:
        Count based on type
    """
    try:
        if not text:
            return 0

        if count_type == 'words':
            words = re.findall(r'\b\w+\b', text)
            return len(words)
        elif count_type == 'chars':
            return len(text)
        elif count_type == 'lines':
            return len(text.split('\n'))
        else:
            return 0

    except Exception:
        return 0


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text

    Args:
        text: Input text

    Returns:
        List of extracted URLs
    """
    try:
        if not text:
            return []

        # URL pattern
        url_pattern = r'https?://[^\s<>"\'{}|\\\^`\[\]]+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)

        return urls

    except Exception:
        return []


def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text

    Args:
        text: Input text

    Returns:
        List of extracted email addresses
    """
    try:
        if not text:
            return []

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)

        return emails

    except Exception:
        return []


def camel_to_snake(text: str) -> str:
    """
    Convert camelCase to snake_case

    Args:
        text: CamelCase text

    Returns:
        snake_case text
    """
    try:
        if not text:
            return ""

        # Insert underscore before uppercase letters
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', text)
        return snake.lower()

    except Exception:
        return text


def snake_to_camel(text: str, capitalize_first: bool = False) -> str:
    """
    Convert snake_case to camelCase

    Args:
        text: snake_case text
        capitalize_first: Capitalize first letter (PascalCase)

    Returns:
        camelCase text
    """
    try:
        if not text:
            return ""

        components = text.split('_')

        if capitalize_first:
            # PascalCase
            camel = ''.join(word.capitalize() for word in components if word)
        else:
            # camelCase
            camel = components[0] + ''.join(word.capitalize() for word in components[1:] if word)

        return camel

    except Exception:
        return text


def title_case(text: str, exceptions: List[str] = None) -> str:
    """
    Convert text to title case with exceptions

    Args:
        text: Input text
        exceptions: List of words to keep lowercase

    Returns:
        Title case text
    """
    try:
        if not text:
            return ""

        if exceptions is None:
            exceptions = ['a', 'an', 'and', 'as', 'at', 'but', 'by', 'for',
                         'in', 'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet']

        words = text.split()
        title_words = []

        for i, word in enumerate(words):
            # Always capitalize first and last word
            if i == 0 or i == len(words) - 1:
                title_words.append(word.capitalize())
            # Check if word is in exceptions
            elif word.lower() in exceptions:
                title_words.append(word.lower())
            else:
                title_words.append(word.capitalize())

        return ' '.join(title_words)

    except Exception:
        return text


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings

    Args:
        s1: First string
        s2: Second string

    Returns:
        Levenshtein distance
    """
    try:
        if not s1:
            return len(s2) if s2 else 0
        if not s2:
            return len(s1)

        # Create matrix
        rows = len(s1) + 1
        cols = len(s2) + 1
        matrix = [[0] * cols for _ in range(rows)]

        # Initialize first row and column
        for i in range(rows):
            matrix[i][0] = i
        for j in range(cols):
            matrix[0][j] = j

        # Fill matrix
        for i in range(1, rows):
            for j in range(1, cols):
                if s1[i-1] == s2[j-1]:
                    cost = 0
                else:
                    cost = 1

                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )

        return matrix[rows-1][cols-1]

    except Exception:
        return max(len(s1) if s1 else 0, len(s2) if s2 else 0)


def similarity_ratio(s1: str, s2: str) -> float:
    """
    Calculate similarity ratio between two strings (0.0 to 1.0)

    Args:
        s1: First string
        s2: Second string

    Returns:
        Similarity ratio (1.0 = identical, 0.0 = completely different)
    """
    try:
        if not s1 and not s2:
            return 1.0

        max_len = max(len(s1) if s1 else 0, len(s2) if s2 else 0)
        if max_len == 0:
            return 1.0

        distance = levenshtein_distance(s1, s2)
        return 1.0 - (distance / max_len)

    except Exception:
        return 0.0


def wrap_text(text: str, width: int = 80, break_long_words: bool = True) -> List[str]:
    """
    Wrap text to specified width

    Args:
        text: Input text
        width: Line width
        break_long_words: Break words longer than width

    Returns:
        List of wrapped lines
    """
    try:
        if not text or width <= 0:
            return [text] if text else []

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            # Check if adding word would exceed width
            word_length = len(word)
            needed_length = current_length + (1 if current_line else 0) + word_length

            if needed_length <= width:
                # Add word to current line
                current_line.append(word)
                current_length = needed_length
            else:
                # Start new line
                if current_line:
                    lines.append(' '.join(current_line))

                # Handle long words
                if word_length > width and break_long_words:
                    # Break long word
                    while len(word) > width:
                        lines.append(word[:width])
                        word = word[width:]
                    current_line = [word] if word else []
                    current_length = len(word) if word else 0
                else:
                    current_line = [word]
                    current_length = word_length

        # Add remaining line
        if current_line:
            lines.append(' '.join(current_line))

        return lines

    except Exception:
        return [text] if text else []


def mask_sensitive_data(text: str, mask_char: str = '*') -> str:
    """
    Mask sensitive data in text (emails, phone numbers, etc.)

    Args:
        text: Input text
        mask_char: Character to use for masking

    Returns:
        Text with sensitive data masked
    """
    try:
        if not text:
            return ""

        masked = text

        # Mask email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        masked = re.sub(email_pattern, lambda m: m.group()[:3] + mask_char * 5 + m.group()[-4:], masked)

        # Mask phone numbers (simple pattern)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        masked = re.sub(phone_pattern, lambda m: mask_char * len(m.group()), masked)

        # Mask credit card numbers
        cc_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        masked = re.sub(cc_pattern, lambda m: mask_char * len(m.group()), masked)

        return masked

    except Exception:
        return text
