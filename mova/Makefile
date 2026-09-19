# Makefile for mova package
# Professional build system for CLI and core utilities

SHELL := /bin/bash
PYTHON := python3
PIP := pip3
PACKAGE_NAME := mova
VERSION := $(shell python3 setup.py --version 2>/dev/null || echo "0.1.0")
DIST_DIR := dist
BUILD_DIR := build
VENV_DIR := venv
TEST_DIR := tests
DOCS_DIR := docs

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
NC := \033[0m # No Color

.PHONY: help install dev-install test test-verbose test-coverage lint format clean build publish dev-publish docs serve-docs check-deps update-deps venv activate backup restore

# Default target
help: ## Show this help message
	@echo -e "$(CYAN)🚀 Mova-Core Build System$(NC)"
	@echo -e "$(WHITE)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation targets
install: clean build ## Install package for production use
	@echo -e "$(BLUE)📦 Installing $(PACKAGE_NAME) v$(VERSION)...$(NC)"
	$(PIP) install .
	@echo -e "$(GREEN)✅ Installation completed!$(NC)"

dev-install: venv ## Install package in development mode with all dependencies
	@echo -e "$(BLUE)🔧 Installing $(PACKAGE_NAME) in development mode...$(NC)"
	$(VENV_DIR)/bin/pip install -e ".[dev,test,docs]"
	$(VENV_DIR)/bin/pip install pytest pytest-cov pytest-asyncio black flake8 mypy sphinx
	@echo -e "$(GREEN)✅ Development installation completed!$(NC)"

# Virtual environment management
venv: ## Create virtual environment
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo -e "$(BLUE)🐍 Creating virtual environment...$(NC)"; \
		$(PYTHON) -m venv $(VENV_DIR); \
		$(VENV_DIR)/bin/pip install --upgrade pip setuptools wheel; \
		echo -e "$(GREEN)✅ Virtual environment created!$(NC)"; \
	else \
		echo -e "$(YELLOW)⚠️  Virtual environment already exists$(NC)"; \
	fi

activate: venv ## Activate virtual environment (source this)
	@echo -e "$(CYAN)To activate virtual environment, run:$(NC)"
	@echo -e "$(WHITE)source $(VENV_DIR)/bin/activate$(NC)"

# Testing targets
test: ## Run all tests
	@echo -e "$(BLUE)🧪 Running tests for $(PACKAGE_NAME)...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/python -m pytest $(TEST_DIR) -v; \
	else \
		$(PYTHON) -m pytest $(TEST_DIR) -v; \
	fi
	@echo -e "$(GREEN)✅ Tests completed!$(NC)"

test-verbose: ## Run tests with verbose output
	@echo -e "$(BLUE)🧪 Running verbose tests...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/python -m pytest $(TEST_DIR) -vvv -s; \
	else \
		$(PYTHON) -m pytest $(TEST_DIR) -vvv -s; \
	fi

test-coverage: ## Run tests with coverage report
	@echo -e "$(BLUE)📊 Running tests with coverage...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/python -m pytest $(TEST_DIR) --cov=mova_core --cov-report=html --cov-report=term; \
	else \
		$(PYTHON) -m pytest $(TEST_DIR) --cov=mova_core --cov-report=html --cov-report=term; \
	fi
	@echo -e "$(GREEN)✅ Coverage report generated in htmlcov/$(NC)"

test-unit: ## Run unit tests only
	@echo -e "$(BLUE)🔬 Running unit tests...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/python -m pytest $(TEST_DIR) -k "unit" -v; \
	else \
		$(PYTHON) -m pytest $(TEST_DIR) -k "unit" -v; \
	fi

test-integration: ## Run integration tests only
	@echo -e "$(BLUE)🔗 Running integration tests...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/python -m pytest $(TEST_DIR) -k "integration" -v; \
	else \
		$(PYTHON) -m pytest $(TEST_DIR) -k "integration" -v; \
	fi

# Code quality targets
lint: ## Run code linting
	@echo -e "$(BLUE)🔍 Running linter...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/flake8 mova_core $(TEST_DIR) --max-line-length=88 --extend-ignore=E203,W503; \
		$(VENV_DIR)/bin/mypy mova_core --ignore-missing-imports; \
	else \
		flake8 mova_core $(TEST_DIR) --max-line-length=88 --extend-ignore=E203,W503; \
		mypy mova_core --ignore-missing-imports; \
	fi
	@echo -e "$(GREEN)✅ Linting completed!$(NC)"

format: ## Format code with black
	@echo -e "$(BLUE)🎨 Formatting code...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/black mova_core $(TEST_DIR) --line-length=88; \
	else \
		black mova_core $(TEST_DIR) --line-length=88; \
	fi
	@echo -e "$(GREEN)✅ Code formatted!$(NC)"

format-check: ## Check code formatting without changes
	@echo -e "$(BLUE)🔍 Checking code format...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/black mova_core $(TEST_DIR) --check --line-length=88; \
	else \
		black mova_core $(TEST_DIR) --check --line-length=88; \
	fi

# Build targets
clean: ## Clean build artifacts
	@echo -e "$(BLUE)🧹 Cleaning build artifacts...$(NC)"
	rm -rf $(BUILD_DIR) $(DIST_DIR) *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	@echo -e "$(GREEN)✅ Cleanup completed!$(NC)"

build: clean ## Build distribution packages
	@echo -e "$(BLUE)🏗️  Building $(PACKAGE_NAME) v$(VERSION)...$(NC)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo -e "$(GREEN)✅ Build completed! Files in $(DIST_DIR):$(NC)"
	@ls -la $(DIST_DIR)

# Publishing targets
publish: build test ## Publish to PyPI (production)
	@echo -e "$(YELLOW)⚠️  Publishing $(PACKAGE_NAME) v$(VERSION) to PyPI...$(NC)"
	@read -p "Are you sure you want to publish to PyPI? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		twine upload $(DIST_DIR)/*; \
		echo -e "$(GREEN)✅ Published to PyPI!$(NC)"; \
	else \
		echo -e "$(RED)❌ Publication cancelled$(NC)"; \
	fi

dev-publish: build ## Publish to TestPyPI (development)
	@echo -e "$(BLUE)🚀 Publishing $(PACKAGE_NAME) v$(VERSION) to TestPyPI...$(NC)"
	twine upload --repository testpypi $(DIST_DIR)/*
	@echo -e "$(GREEN)✅ Published to TestPyPI!$(NC)"
	@echo -e "$(CYAN)Install with: pip install -i https://test.pypi.org/simple/ $(PACKAGE_NAME)$(NC)"

# Documentation targets
docs: ## Generate documentation
	@echo -e "$(BLUE)📚 Generating documentation...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		cd $(DOCS_DIR) && $(VENV_DIR)/bin/sphinx-build -b html . _build/html; \
	else \
		cd $(DOCS_DIR) && sphinx-build -b html . _build/html; \
	fi
	@echo -e "$(GREEN)✅ Documentation generated in $(DOCS_DIR)/_build/html/$(NC)"

serve-docs: docs ## Serve documentation locally
	@echo -e "$(BLUE)🌐 Serving documentation at http://localhost:8000$(NC)"
	@cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8000

# Dependency management
check-deps: ## Check for outdated dependencies
	@echo -e "$(BLUE)🔍 Checking dependencies...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/pip list --outdated; \
	else \
		$(PIP) list --outdated; \
	fi

update-deps: ## Update dependencies
	@echo -e "$(BLUE)⬆️  Updating dependencies...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/pip install --upgrade pip setuptools wheel; \
		$(VENV_DIR)/bin/pip install --upgrade -r requirements.txt 2>/dev/null || true; \
	else \
		$(PIP) install --upgrade pip setuptools wheel; \
		$(PIP) install --upgrade -r requirements.txt 2>/dev/null || true; \
	fi
	@echo -e "$(GREEN)✅ Dependencies updated!$(NC)"

# Security and validation
security-check: ## Run security checks
	@echo -e "$(BLUE)🔒 Running security checks...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_DIR)/bin/pip install bandit safety; \
		$(VENV_DIR)/bin/bandit -r mova_core; \
		$(VENV_DIR)/bin/safety check; \
	else \
		pip install bandit safety; \
		bandit -r mova_core; \
		safety check; \
	fi
	@echo -e "$(GREEN)✅ Security check completed!$(NC)"

validate: lint test security-check ## Run all validation checks
	@echo -e "$(GREEN)✅ All validation checks passed!$(NC)"

# Backup and restore
backup: ## Backup current state
	@echo -e "$(BLUE)💾 Creating backup...$(NC)"
	tar -czf backup-$(shell date +%Y%m%d_%H%M%S).tar.gz --exclude=$(VENV_DIR) --exclude=$(BUILD_DIR) --exclude=$(DIST_DIR) .
	@echo -e "$(GREEN)✅ Backup created!$(NC)"

# Development helpers
dev-setup: venv dev-install ## Complete development environment setup
	@echo -e "$(GREEN)🎉 Development environment ready!$(NC)"
	@echo -e "$(CYAN)Next steps:$(NC)"
	@echo -e "  1. $(WHITE)source $(VENV_DIR)/bin/activate$(NC)"
	@echo -e "  2. $(WHITE)make test$(NC)"
	@echo -e "  3. $(WHITE)make lint$(NC)"

dev-reset: clean ## Reset development environment
	@echo -e "$(YELLOW)⚠️  Resetting development environment...$(NC)"
	rm -rf $(VENV_DIR)
	@echo -e "$(GREEN)✅ Development environment reset!$(NC)"

# Quick development workflow
quick-test: format lint test ## Quick development workflow
	@echo -e "$(GREEN)✅ Quick test workflow completed!$(NC)"

# Package information
info: ## Show package information
	@echo -e "$(CYAN)📋 Package Information$(NC)"
	@echo -e "$(WHITE)Name:$(NC) $(PACKAGE_NAME)"
	@echo -e "$(WHITE)Version:$(NC) $(VERSION)"
	@echo -e "$(WHITE)Python:$(NC) $(shell $(PYTHON) --version)"
	@echo -e "$(WHITE)Pip:$(NC) $(shell $(PIP) --version)"
	@echo -e "$(WHITE)Virtual Env:$(NC) $(shell [ -d "$(VENV_DIR)" ] && echo "Active" || echo "Not created")"
	@echo -e "$(WHITE)Build Dir:$(NC) $(BUILD_DIR)"
	@echo -e "$(WHITE)Dist Dir:$(NC) $(DIST_DIR)"
	@echo -e "$(WHITE)Test Dir:$(NC) $(TEST_DIR)"

# Development status
status: ## Show development status
	@echo -e "$(CYAN)📊 Development Status$(NC)"
	@echo -e "$(WHITE)Tests:$(NC) $(shell find $(TEST_DIR) -name "*.py" -type f | wc -l 2>/dev/null || echo "0") files"
	@echo -e "$(WHITE)Source:$(NC) $(shell find mova_core -name "*.py" -type f | wc -l 2>/dev/null || echo "0") files"
	@echo -e "$(WHITE)Lines of Code:$(NC) $(shell find mova_core -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $$1}' || echo "0")"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo -e "$(WHITE)Installed Packages:$(NC) $$($(VENV_DIR)/bin/pip list | wc -l)"; \
	fi
