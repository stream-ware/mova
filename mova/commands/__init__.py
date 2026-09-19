"""
🎯 Commands Package - Professional CLI Command Handlers

Comprehensive command handler system extracted from monolithic mova.py
with modular, extensible, and maintainable architecture.
"""

__version__ = "2.0.0"
__author__ = "Mova Development Team"

# Core command handlers
from .shell_handler import handle_shell_command
from .log_handlers import (
    handle_list_command,
    handle_info_command,
    handle_warning_command,
    handle_error_command,
    handle_watch_command
)
from .system_handlers import (
    handle_health_command,
    handle_services_command,
    handle_security_command
)
from .web_handlers import handle_http_command
from .voice_handlers import (
    handle_voice_command,
    handle_audio_command
)
from .content_handlers import handle_rss_command

__all__ = [
    # Shell and system commands
    'handle_shell_command',
    'handle_health_command',
    'handle_services_command',
    'handle_security_command',

    # Logging commands
    'handle_list_command',
    'handle_info_command',
    'handle_warning_command',
    'handle_error_command',
    'handle_watch_command',

    # Web commands
    'handle_http_command',

    # Voice commands
    'handle_voice_command',
    'handle_audio_command',

    # Content commands
    'handle_rss_command'
]
