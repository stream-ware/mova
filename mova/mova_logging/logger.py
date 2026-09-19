"""
📝 Mova Logging System

Centralized logging for the entire Mova ecosystem with structured output,
multiple handlers, and component-specific contexts.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class MovaLogger:
    """
    Enhanced logging system for Mova components.

    Features:
    - Structured JSON logging
    - Component-specific contexts
    - Multiple output handlers
    - Log level management
    - Performance tracking
    """

    def __init__(self, component_name: str = "mova", log_level: str = "INFO"):
        self.component_name = component_name
        self.name = component_name
        self.logger = logging.getLogger(f"mova.{component_name}")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup console and file handlers with proper formatting"""

        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Custom formatter for structured output
        formatter = MovaFormatter()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        self._log_with_context("info", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        self._log_with_context("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with optional context"""
        self._log_with_context("error", message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        self._log_with_context("debug", message, **kwargs)

    def _log_with_context(self, level: str, message: str, **context):
        """Internal method to log with additional context"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'component': self.component_name,
            'level': level.upper(),
            'message': message,
            **context
        }

        # Use appropriate logging level
        log_method = getattr(self.logger, level)
        log_method(json.dumps(log_data, ensure_ascii=False))


class MovaFormatter(logging.Formatter):
    """
    Custom formatter for Mova logs with colors and structured output.
    """

    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[92m',      # Green
        'WARNING': '\033[93m',   # Yellow
        'ERROR': '\033[91m',     # Red
        'CRITICAL': '\033[95m'   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        """Format log record with colors and structure"""
        try:
            # Try to parse as JSON (structured log)
            log_data = json.loads(record.getMessage())

            # Format structured log
            timestamp = log_data.get('timestamp', '')
            component = log_data.get('component', 'unknown')
            level = log_data.get('level', 'INFO')
            message = log_data.get('message', '')

            # Add color to level
            color = self.COLORS.get(level, '')
            colored_level = f"{color}{level}{self.RESET}"

            # Format: [TIMESTAMP] [COMPONENT] LEVEL: MESSAGE
            formatted = f"[{timestamp}] [{component}] {colored_level}: {message}"

            # Add context if present
            context = {k: v for k, v in log_data.items()
                      if k not in ['timestamp', 'component', 'level', 'message']}
            if context:
                formatted += f" | Context: {json.dumps(context)}"

            return formatted

        except (json.JSONDecodeError, AttributeError):
            # Fallback for non-structured logs
            return super().format(record)


def get_logger(component_name: str, log_level: str = "INFO") -> MovaLogger:
    """
    Factory function to get a logger for a Mova component.

    Args:
        component_name: Name of the component (e.g., 'core', 'movatalk')
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        MovaLogger instance for the component
    """
    return MovaLogger(component_name, log_level)
