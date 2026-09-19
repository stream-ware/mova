"""
🧪 Test Fixtures for Mova-Core

Shared fixtures and test utilities for the mova-core test suite.
"""

import pytest
import tempfile
import os
import json
import yaml
from typing import Dict, Any, Generator
from unittest.mock import MagicMock, patch
from pathlib import Path


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample configuration for testing"""
    return {
        'debug': True,
        'log_level': 'DEBUG',
        'server': {
            'url': 'http://localhost:8094',
            'timeout': 30
        },
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'test_mova'
        }
    }


@pytest.fixture
def config_file(temp_dir: str, sample_config: Dict[str, Any]) -> str:
    """Create temporary config file"""
    config_path = os.path.join(temp_dir, 'test_config.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f)
    return config_path


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    with patch('mova_core.logging.logger.MovaLogger') as mock:
        yield mock


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager"""
    with patch('mova_core.config.manager.ConfigManager') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_client():
    """Mock client for API testing"""
    with patch('mova_core.communication.client.MovaClient') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def cli_runner():
    """CLI test runner"""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def sample_log_data():
    """Sample log data for testing"""
    return [
        {
            'timestamp': '2023-01-01 10:00:00',
            'level': 'INFO',
            'message': 'Test info message',
            'module': 'test_module'
        },
        {
            'timestamp': '2023-01-01 10:01:00',
            'level': 'ERROR',
            'message': 'Test error message',
            'module': 'test_module'
        }
    ]


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for system command testing"""
    with patch('subprocess.run') as mock:
        mock.return_value.returncode = 0
        mock.return_value.stdout = 'Test output'
        mock.return_value.stderr = ''
        yield mock
