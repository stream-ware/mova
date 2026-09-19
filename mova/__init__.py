"""
🎯 Mova Core - Lightweight Communication Library

Mova Core provides the essential communication and logging infrastructure
for the Mova ecosystem without heavy dependencies.

Core Components:
- Communication: HTTP, WebSocket, messaging
- Logging: Centralized logging system
- Configuration: Environment and file-based config
- Utilities: Common helper functions

This is the foundational component that other Mova extensions build upon.
"""

__version__ = "1.0.0"
__author__ = "Mova Team"

# Core imports
from .communication.client import MovaClient
from .communication.server import MovaServer
from .mova_logging.logger import MovaLogger
from .config.manager import ConfigManager
from .utils.helpers import format_timestamp, parse_duration
from .security.acl_manager import ACLManager, SecurityLevel, SecurityPolicy

# Component interface
from .base import MovaComponent

__all__ = [
    'MovaClient',
    'MovaServer',
    'MovaLogger',
    'ConfigManager',
    'MovaComponent',
    'ACLManager',
    'SecurityLevel',
    'SecurityPolicy',
    'format_timestamp',
    'parse_duration'
]
