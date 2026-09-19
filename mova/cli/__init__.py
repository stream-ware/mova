"""
🚀 Mova CLI Package - Modular Command Line Interface

Professional CLI system extracted from monolithic mova.py for better
maintainability, extensibility, and separation of concerns.
"""

__version__ = "2.0.0"
__author__ = "Mova Development Team"

# Core CLI components
from .main_cli import MovaCLI
from .argument_parser import MovaArgumentParser
from .command_router import CommandRouter

# Core utilities
from .utils import (
    detect_service_name,
    make_request,
    parse_time_duration,
    format_log_output
)

# Command handlers
from .commands import *

# Constants
DEFAULT_SERVER = "http://localhost:8094"

__all__ = [
    # Main CLI interface
    'MovaCLI',
    'MovaArgumentParser',
    'CommandRouter',

    # Utilities
    'detect_service_name',
    'make_request',
    'parse_time_duration',
    'format_log_output',

    # Constants
    'DEFAULT_SERVER'
]
