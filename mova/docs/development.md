# 🔧 mova Development Guide

## Overview
This guide covers development setup, coding standards, and workflows for the mova package.

## 🚀 Quick Start

### 1. Development Environment Setup
```bash
# Clone and navigate to mova
cd mova/

# Setup development environment
make dev-setup

# Activate virtual environment
source venv/bin/activate

# Verify installation
make info
```

### 2. Development Workflow
```bash
# Make changes to code
# Format code
make format

# Run linting
make lint

# Run tests
make test

# Quick development check
make quick-test
```

## 📁 Project Structure

```
mova/
├── mova/              # Main package
│   ├── cli/               # CLI components
│   ├── commands/          # Command handlers
│   ├── config/            # Configuration system
│   ├── utils/             # Utilities
│   ├── communication/     # Client communication
│   └── logging/           # Logging system
├── tests/                 # Test suite
├── docs/                  # Documentation
├── Makefile              # Build automation
├── setup.py              # Package configuration
└── requirements*.txt     # Dependencies
```

## 🧪 Testing

### Running Tests
```bash
# All tests
make test

# With coverage
make test-coverage

# Verbose output
make test-verbose

# Unit tests only
make test-unit

# Integration tests only
make test-integration
```

### Writing Tests

#### Unit Test Example
```python
# tests/unit/test_helpers.py
import pytest
from mova.utils.helpers import safe_get, retry

def test_safe_get():
    """Test safe dictionary access"""
    data = {'key': 'value', 'nested': {'inner': 'data'}}

    assert safe_get(data, 'key') == 'value'
    assert safe_get(data, 'missing') is None
    assert safe_get(data, 'missing', 'default') == 'default'
    assert safe_get(data, ['nested', 'inner']) == 'data'

@pytest.mark.asyncio
async def test_retry_decorator():
    """Test retry decorator functionality"""
    call_count = 0

    @retry(max_attempts=3, delay=0.1)
    async def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Test error")
        return "success"

    result = await failing_function()
    assert result == "success"
    assert call_count == 3
```

#### Integration Test Example
```python
# tests/integration/test_cli_integration.py
import pytest
from mova.cli.main_cli import main_cli
from unittest.mock import patch, MagicMock

def test_cli_help_command():
    """Test CLI help command"""
    with patch('sys.argv', ['mova', '--help']):
        with pytest.raises(SystemExit):
            main_cli()

def test_cli_log_list_command():
    """Test CLI log list command"""
    with patch('sys.argv', ['mova', 'log', 'list']):
        with patch('mova.commands.log_handlers.handle_log_list') as mock_handler:
            main_cli()
            mock_handler.assert_called_once()
```

## 📝 Code Style

### Standards
- **Line Length**: 88 characters (Black default)
- **Imports**: Use absolute imports, sort with `isort`
- **Type Hints**: All public functions must have type hints
- **Docstrings**: Google style docstrings for all public methods

### Example Code Style
```python
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def process_data(
    items: List[Dict[str, Any]],
    filter_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Process list of data items with optional filtering.

    Args:
        items: List of data dictionaries to process
        filter_key: Optional key to filter items

    Returns:
        Filtered and processed list of items

    Raises:
        ValueError: If items list is invalid
    """
    if not isinstance(items, list):
        raise ValueError("Items must be a list")

    try:
        processed = []
        for item in items:
            if filter_key and filter_key not in item:
                continue
            processed.append(item)

        logger.info(f"Processed {len(processed)} items")
        return processed

    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise
```

## 🏗️ Build System

### Make Targets
```bash
# Development
make dev-setup          # Complete dev environment
make dev-install        # Development installation
make venv              # Create virtual environment

# Testing
make test              # Run all tests
make test-coverage     # Tests with coverage
make test-unit         # Unit tests only
make test-integration  # Integration tests only

# Code Quality
make lint              # Code linting
make format            # Code formatting
make format-check      # Check formatting
make security-check    # Security analysis

# Building
make clean             # Clean build artifacts
make build             # Build packages
make install           # Production install

# Publishing
make dev-publish       # Publish to TestPyPI
make publish           # Publish to PyPI

# Documentation
make docs              # Generate documentation
make serve-docs        # Serve docs locally

# Utilities
make info              # Package information
make status            # Development status
make backup            # Create backup
```

## 🔧 Configuration

### Environment Variables
```bash
# Development settings
export MOVA_DEBUG=true
export MOVA_LOG_LEVEL=DEBUG
export MOVA_CONFIG_PATH=/path/to/config.yaml

# Server settings
export MOVA_SERVER_URL=http://localhost:8094
export MOVA_SERVER_TIMEOUT=30

# Database settings
export MOVA_DB_HOST=localhost
export MOVA_DB_PORT=5432
```

### Configuration Files
```yaml
# config/development.yaml
debug: true
log_level: DEBUG

server:
  url: "http://localhost:8094"
  timeout: 30

database:
  host: localhost
  port: 5432
  name: mova_dev

logging:
  level: DEBUG
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 🐛 Debugging

### Debug Configuration
```python
# Add to your module for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose CLI output
export MOVA_VERBOSE=true
```

### Common Issues

#### Import Errors
```bash
# If imports fail, check installation
make dev-install

# Verify package is installed
pip list | grep mova
```

#### Test Failures
```bash
# Run with verbose output
make test-verbose

# Check specific test
python -m pytest tests/path/to/test.py::test_function -v
```

## 📦 Dependencies

### Adding Dependencies
1. Add to `setup.py` in appropriate section:
   ```python
   install_requires=[
       'new-package>=1.0.0',
   ]
   ```

2. Update development requirements:
   ```bash
   make update-deps
   ```

3. Test installation:
   ```bash
   make dev-install
   make test
   ```

### Dependency Categories
- **Core**: Required for basic functionality
- **Dev**: Development tools (testing, linting)
- **Docs**: Documentation generation
- **Optional**: Feature-specific dependencies

## 🚀 Release Process

### Version Management
1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Run full test suite: `make validate`
4. Build and test: `make build`
5. Publish to TestPyPI: `make dev-publish`
6. Test installation from TestPyPI
7. Publish to PyPI: `make publish`

### Pre-release Checklist
- [ ] All tests pass
- [ ] Code coverage > 80%
- [ ] Documentation updated
- [ ] Version bumped
- [ ] Changelog updated
- [ ] Security scan clean
- [ ] Dependencies up to date

## 🤝 Contributing

### Pull Request Process
1. Fork repository
2. Create feature branch
3. Make changes following style guide
4. Add tests for new functionality
5. Run `make validate`
6. Submit pull request

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(cli): add new log filtering options`
- `fix(config): resolve environment variable loading`
- `docs(readme): update installation instructions`

## 🆘 Getting Help

### Resources
- **Documentation**: `/docs/`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

### Common Commands
```bash
# Get help on any make target
make help

# Show package information
make info

# Show development status
make status
```
