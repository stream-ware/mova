"""
🛠️ Test Utilities for Mova-Core

Helper functions and utilities for testing mova-core components.
"""

import json
import yaml
import tempfile
import os
from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock, patch
from contextlib import contextmanager


def create_test_config(config_data: Dict[str, Any]) -> str:
    """
    Create temporary config file for testing

    Args:
        config_data: Configuration data

    Returns:
        Path to temporary config file
    """
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    try:
        yaml.dump(config_data, temp_file)
        temp_file.flush()
        return temp_file.name
    finally:
        temp_file.close()


def create_test_log_file(log_entries: List[Dict[str, Any]]) -> str:
    """
    Create temporary log file for testing

    Args:
        log_entries: List of log entry dictionaries

    Returns:
        Path to temporary log file
    """
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
    try:
        for entry in log_entries:
            temp_file.write(f"{entry.get('timestamp', '')} - {entry.get('level', 'INFO')} - {entry.get('message', '')}\n")
        temp_file.flush()
        return temp_file.name
    finally:
        temp_file.close()


@contextmanager
def mock_cli_environment(**env_vars):
    """
    Mock CLI environment variables

    Args:
        **env_vars: Environment variables to set
    """
    with patch.dict(os.environ, env_vars, clear=False):
        yield


@contextmanager
def capture_cli_output():
    """
    Capture CLI output for testing
    """
    import io
    import sys

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        yield stdout_capture, stderr_capture
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def mock_api_response(status_code: int = 200, data: Optional[Dict] = None, error: Optional[str] = None):
    """
    Create mock API response

    Args:
        status_code: HTTP status code
        data: Response data
        error: Error message

    Returns:
        Mock response object
    """
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = data or {}
    response.text = error or ""
    response.ok = status_code < 400
    return response


def assert_cli_output_contains(output: str, expected_strings: List[str]):
    """
    Assert CLI output contains expected strings

    Args:
        output: CLI output text
        expected_strings: List of strings that should be present
    """
    for expected in expected_strings:
        assert expected in output, f"Expected '{expected}' not found in output: {output}"


def assert_log_level_output(output: str, level: str):
    """
    Assert log output contains specific level

    Args:
        output: Log output
        level: Expected log level
    """
    level_indicators = {
        'DEBUG': ['DEBUG', '🐛'],
        'INFO': ['INFO', '📝', 'ℹ️'],
        'WARNING': ['WARNING', 'WARN', '⚠️'],
        'ERROR': ['ERROR', '❌', '🚨'],
        'CRITICAL': ['CRITICAL', '💥']
    }

    indicators = level_indicators.get(level, [level])
    found = any(indicator in output for indicator in indicators)
    assert found, f"Expected log level '{level}' not found in output: {output}"


class MockConfigManager:
    """Mock configuration manager for testing"""

    def __init__(self, config_data: Optional[Dict] = None):
        self.config_data = config_data or {}
        self.load_called = False
        self.save_called = False

    def load(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Mock config loading"""
        self.load_called = True
        return self.config_data.copy()

    def save(self, config_data: Dict[str, Any], config_path: Optional[str] = None):
        """Mock config saving"""
        self.save_called = True
        self.config_data.update(config_data)

    def get(self, key: str, default=None):
        """Mock config get"""
        keys = key.split('.')
        value = self.config_data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


class MockLogger:
    """Mock logger for testing"""

    def __init__(self):
        self.logs = []
        self.debug_called = False
        self.info_called = False
        self.warning_called = False
        self.error_called = False

    def debug(self, message: str, *args, **kwargs):
        self.debug_called = True
        self.logs.append(('DEBUG', message))

    def info(self, message: str, *args, **kwargs):
        self.info_called = True
        self.logs.append(('INFO', message))

    def warning(self, message: str, *args, **kwargs):
        self.warning_called = True
        self.logs.append(('WARNING', message))

    def error(self, message: str, *args, **kwargs):
        self.error_called = True
        self.logs.append(('ERROR', message))

    def get_logs(self, level: Optional[str] = None) -> List[tuple]:
        """Get logs, optionally filtered by level"""
        if level:
            return [log for log in self.logs if log[0] == level]
        return self.logs.copy()


def create_sample_test_data():
    """Create sample test data for various components"""
    return {
        'config': {
            'debug': True,
            'server': {'url': 'http://test:8094'},
            'database': {'host': 'test-db', 'port': 5432}
        },
        'logs': [
            {'level': 'INFO', 'message': 'Test info', 'timestamp': '2023-01-01 10:00:00'},
            {'level': 'ERROR', 'message': 'Test error', 'timestamp': '2023-01-01 10:01:00'}
        ],
        'api_responses': {
            'success': {'status': 'success', 'data': {'key': 'value'}},
            'error': {'status': 'error', 'message': 'Test error'}
        }
    }


def cleanup_temp_files(*file_paths: str):
    """
    Clean up temporary test files

    Args:
        *file_paths: Paths to files to clean up
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass  # Ignore cleanup errors in tests
