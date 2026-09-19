"""
🛠️ Mova Core Utils - Universal Utility Functions

Comprehensive collection of utility functions and helpers for the Mova ecosystem
with performance optimization, error handling, and extensive functionality.
"""

from .helpers import (
    format_duration,
    format_file_size,
    generate_uuid,
    safe_dict_get,
    retry_on_failure,
    validate_email,
    validate_url,
    sanitize_filename
)

from .system import (
    get_system_info,
    check_port_available,
    find_free_port,
    get_process_info,
    kill_process_by_port,
    get_disk_usage,
    get_memory_usage
)

from .text import (
    clean_text,
    extract_numbers,
    truncate_text,
    slugify,
    normalize_whitespace,
    remove_html_tags,
    encode_base64,
    decode_base64
)

from .async_utils import (
    run_async,
    gather_with_concurrency,
    timeout_after,
    async_retry,
    create_task_group
)

__all__ = [
    # Helpers
    'format_duration',
    'format_file_size',
    'generate_uuid',
    'safe_dict_get',
    'retry_on_failure',
    'validate_email',
    'validate_url',
    'sanitize_filename',

    # System
    'get_system_info',
    'check_port_available',
    'find_free_port',
    'get_process_info',
    'kill_process_by_port',
    'get_disk_usage',
    'get_memory_usage',

    # Text
    'clean_text',
    'extract_numbers',
    'truncate_text',
    'slugify',
    'normalize_whitespace',
    'remove_html_tags',
    'encode_base64',
    'decode_base64',

    # Async
    'run_async',
    'gather_with_concurrency',
    'timeout_after',
    'async_retry',
    'create_task_group'
]
