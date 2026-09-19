"""
🧪 Test Suite for Mova-Core Package

This package contains comprehensive tests for the mova-core CLI and utilities.
"""

import os
import sys
import pytest

# Add the package to Python path for testing
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
sys.path.insert(0, project_root)

# Test configuration
TEST_CONFIG = {
    'timeout': 30,
    'verbose': True,
    'capture': 'no' if os.environ.get('PYTEST_CAPTURE') == 'no' else 'sys',
    'log_level': os.environ.get('TEST_LOG_LEVEL', 'INFO'),
}

# Test fixtures and utilities available to all tests
from .fixtures import *
from .utils import *

__version__ = "1.0.0"
