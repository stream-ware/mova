"""
⚙️ Configuration Loader - Advanced Configuration Loading System

Sophisticated configuration loader with multiple format support,
validation, schema management, and advanced loading strategies.
"""

import os
import json
import yaml
import toml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Type
from dataclasses import dataclass
import logging

from .settings import MovaSettings


@dataclass
class LoaderResult:
    """Configuration loading result"""
    success: bool
    data: Dict[str, Any]
    source: str
    errors: List[str]
    warnings: List[str]


class ConfigLoader:
    """
    Advanced configuration loader for multiple formats

    Supports YAML, JSON, TOML, and environment variable loading
    with validation, schema checking, and error reporting.
    """

    def __init__(self):
        """Initialize ConfigLoader"""
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.yaml', '.yml', '.json', '.toml']

    def load_from_file(self, file_path: Union[str, Path]) -> LoaderResult:
        """
        Load configuration from file

        Args:
            file_path: Path to configuration file

        Returns:
            LoaderResult with loading status and data
        """
        file_path = Path(file_path)
        result = LoaderResult(
            success=False,
            data={},
            source=str(file_path),
            errors=[],
            warnings=[]
        )

        try:
            # Check file existence
            if not file_path.exists():
                result.errors.append(f"Configuration file not found: {file_path}")
                return result

            # Check file format
            if file_path.suffix.lower() not in self.supported_formats:
                result.errors.append(f"Unsupported file format: {file_path.suffix}")
                return result

            # Load based on format
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    result.data = yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == '.json':
                    result.data = json.load(f)
                elif file_path.suffix.lower() == '.toml':
                    result.data = toml.load(f)

            result.success = True
            self.logger.info(f"Loaded configuration from: {file_path}")

        except yaml.YAMLError as e:
            result.errors.append(f"YAML parsing error: {e}")
            self.logger.error(f"YAML error in {file_path}: {e}")
        except json.JSONDecodeError as e:
            result.errors.append(f"JSON parsing error: {e}")
            self.logger.error(f"JSON error in {file_path}: {e}")
        except Exception as e:
            result.errors.append(f"Error loading configuration: {e}")
            self.logger.error(f"Error loading {file_path}: {e}")

        return result

    def load_from_directory(self, directory: Union[str, Path],
                          pattern: str = "*.yaml") -> LoaderResult:
        """
        Load configuration from directory

        Args:
            directory: Directory path
            pattern: File pattern to match

        Returns:
            LoaderResult with merged configurations
        """
        directory = Path(directory)
        result = LoaderResult(
            success=False,
            data={},
            source=str(directory),
            errors=[],
            warnings=[]
        )

        try:
            if not directory.exists() or not directory.is_dir():
                result.errors.append(f"Directory not found: {directory}")
                return result

            # Find matching files
            config_files = list(directory.glob(pattern))
            if not config_files:
                result.warnings.append(f"No configuration files found in {directory}")
                result.success = True
                return result

            # Load and merge configurations
            merged_data = {}
            loaded_count = 0

            for config_file in sorted(config_files):
                file_result = self.load_from_file(config_file)

                if file_result.success:
                    self._deep_merge(merged_data, file_result.data)
                    loaded_count += 1
                else:
                    result.errors.extend(file_result.errors)
                    result.warnings.extend(file_result.warnings)

            result.data = merged_data
            result.success = loaded_count > 0

            if loaded_count > 0:
                self.logger.info(f"Loaded {loaded_count} configuration files from {directory}")

        except Exception as e:
            result.errors.append(f"Error loading directory: {e}")
            self.logger.error(f"Error loading directory {directory}: {e}")

        return result

    def load_from_environment(self, prefix: str = "MOVA_") -> LoaderResult:
        """
        Load configuration from environment variables

        Args:
            prefix: Environment variable prefix

        Returns:
            LoaderResult with environment configuration
        """
        result = LoaderResult(
            success=True,
            data={},
            source=f"environment ({prefix}*)",
            errors=[],
            warnings=[]
        )

        try:
            env_data = {}
            count = 0

            for key, value in os.environ.items():
                if key.startswith(prefix):
                    # Convert MOVA_SERVER_PORT to server.port
                    config_key = key[len(prefix):].lower()
                    nested_keys = config_key.split('_')

                    # Convert value to appropriate type
                    converted_value = self._convert_env_value(value)

                    # Set nested value
                    self._set_nested_value(env_data, nested_keys, converted_value)
                    count += 1

            result.data = env_data

            if count > 0:
                self.logger.info(f"Loaded {count} environment variables")
            else:
                result.warnings.append("No environment variables found with prefix")

        except Exception as e:
            result.errors.append(f"Error loading environment: {e}")
            result.success = False
            self.logger.error(f"Error loading environment variables: {e}")

        return result

    def load_with_fallbacks(self, paths: List[Union[str, Path]],
                          env_prefix: str = "MOVA_") -> LoaderResult:
        """
        Load configuration with fallback paths

        Args:
            paths: List of fallback paths to try
            env_prefix: Environment variable prefix

        Returns:
            LoaderResult with merged configuration
        """
        result = LoaderResult(
            success=False,
            data={},
            source="multiple sources",
            errors=[],
            warnings=[]
        )

        try:
            merged_data = {}
            loaded_sources = []

            # Try each fallback path
            for path in paths:
                path = Path(path)

                if path.is_dir():
                    # Load from directory
                    dir_result = self.load_from_directory(path)
                    if dir_result.success:
                        self._deep_merge(merged_data, dir_result.data)
                        loaded_sources.append(f"dir:{path}")
                    result.warnings.extend(dir_result.warnings)
                    result.errors.extend(dir_result.errors)

                elif path.exists():
                    # Load from file
                    file_result = self.load_from_file(path)
                    if file_result.success:
                        self._deep_merge(merged_data, file_result.data)
                        loaded_sources.append(f"file:{path}")
                    result.warnings.extend(file_result.warnings)
                    result.errors.extend(file_result.errors)

            # Load environment variables (highest priority)
            env_result = self.load_from_environment(env_prefix)
            if env_result.success and env_result.data:
                self._deep_merge(merged_data, env_result.data)
                loaded_sources.append("environment")

            result.data = merged_data
            result.success = len(loaded_sources) > 0
            result.source = ", ".join(loaded_sources)

            if loaded_sources:
                self.logger.info(f"Loaded configuration from: {result.source}")

        except Exception as e:
            result.errors.append(f"Error in fallback loading: {e}")
            self.logger.error(f"Error in fallback loading: {e}")

        return result

    def validate_configuration(self, data: Dict[str, Any],
                             settings_class: Type = MovaSettings) -> LoaderResult:
        """
        Validate configuration against settings model

        Args:
            data: Configuration data to validate
            settings_class: Settings class for validation

        Returns:
            LoaderResult with validation status
        """
        result = LoaderResult(
            success=False,
            data=data,
            source="validation",
            errors=[],
            warnings=[]
        )

        try:
            # Attempt to create settings object
            settings = settings_class(**data)
            result.data = settings.dict()
            result.success = True

            self.logger.info("Configuration validation successful")

        except Exception as e:
            result.errors.append(f"Validation error: {e}")
            self.logger.error(f"Configuration validation failed: {e}")

        return result

    def save_to_file(self, data: Dict[str, Any], file_path: Union[str, Path],
                    format_override: Optional[str] = None) -> LoaderResult:
        """
        Save configuration to file

        Args:
            data: Configuration data
            file_path: Target file path
            format_override: Override file format detection

        Returns:
            LoaderResult with save status
        """
        file_path = Path(file_path)
        result = LoaderResult(
            success=False,
            data=data,
            source=str(file_path),
            errors=[],
            warnings=[]
        )

        try:
            # Determine format
            if format_override:
                format_ext = f".{format_override.lower()}"
            else:
                format_ext = file_path.suffix.lower()

            if format_ext not in self.supported_formats:
                result.errors.append(f"Unsupported save format: {format_ext}")
                return result

            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save based on format
            with open(file_path, 'w', encoding='utf-8') as f:
                if format_ext in ['.yaml', '.yml']:
                    yaml.dump(data, f, default_flow_style=False, indent=2, sort_keys=True)
                elif format_ext == '.json':
                    json.dump(data, f, indent=2, sort_keys=True)
                elif format_ext == '.toml':
                    toml.dump(data, f)

            result.success = True
            self.logger.info(f"Saved configuration to: {file_path}")

        except Exception as e:
            result.errors.append(f"Error saving configuration: {e}")
            self.logger.error(f"Error saving to {file_path}: {e}")

        return result

    def _deep_merge(self, target: Dict, source: Dict):
        """Deep merge dictionaries"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Boolean values
        if value.lower() in ['true', '1', 'yes', 'on']:
            return True
        elif value.lower() in ['false', '0', 'no', 'off']:
            return False

        # Numeric values
        try:
            # Try integer first
            if '.' not in value and 'e' not in value.lower():
                return int(value)
            else:
                return float(value)
        except ValueError:
            pass

        # JSON values (lists, dicts)
        if value.startswith(('[', '{')):
            try:
                return json.loads(value)
            except:
                pass

        # Comma-separated list
        if ',' in value:
            return [item.strip() for item in value.split(',')]

        # Default to string
        return value

    def _set_nested_value(self, data: Dict, keys: List[str], value: Any):
        """Set nested dictionary value from key path"""
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value
