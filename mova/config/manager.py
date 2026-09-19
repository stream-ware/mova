"""
⚙️ Configuration Manager - Centralized Configuration System

Professional configuration management for Mova ecosystem with validation,
environment support, dynamic updates, and comprehensive error handling.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
import logging

from .settings import MovaSettings


class ConfigError(Exception):
    """Configuration-related errors"""
    pass


@dataclass
class ConfigSource:
    """Configuration source information"""
    path: str
    type: str  # 'file', 'env', 'default'
    priority: int = 0
    last_modified: Optional[float] = None


class ConfigManager:
    """
    Centralized configuration manager for Mova ecosystem

    Provides hierarchical configuration loading, validation,
    environment variable support, and dynamic updates.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize ConfigManager

        Args:
            config_dir: Configuration directory path
        """
        self.logger = logging.getLogger(__name__)

        # Configuration directory
        self.config_dir = config_dir or Path.home() / '.mova'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Configuration data
        self._config: Dict[str, Any] = {}
        self._sources: List[ConfigSource] = []
        self._watchers: List[callable] = []

        # Default configuration paths
        self.default_paths = [
            self.config_dir / 'mova.yaml',
            self.config_dir / 'mova.yml',
            self.config_dir / 'mova.json',
            Path('/etc/mova/mova.yaml'),
            Path('./mova.yaml'),
            Path('./config/mova.yaml'),
        ]

        # Load initial configuration
        self._load_defaults()
        self._load_from_files()
        self._load_from_environment()

        self.logger.info(f"ConfigManager initialized with {len(self._sources)} sources")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        try:
            keys = key.split('.')
            value = self._config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value

        except Exception as e:
            self.logger.warning(f"Error getting config key '{key}': {e}")
            return default

    def set(self, key: str, value: Any, save: bool = False) -> bool:
        """
        Set configuration value

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
            save: Whether to save to file

        Returns:
            True if successful
        """
        try:
            keys = key.split('.')
            config = self._config

            # Navigate to parent
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            # Set value
            config[keys[-1]] = value

            # Notify watchers
            self._notify_watchers(key, value)

            # Save if requested
            if save:
                self.save_to_file()

            self.logger.debug(f"Set config '{key}' = {value}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting config key '{key}': {e}")
            return False

    def update(self, config_dict: Dict[str, Any], save: bool = False) -> bool:
        """
        Update configuration with dictionary

        Args:
            config_dict: Configuration dictionary
            save: Whether to save to file

        Returns:
            True if successful
        """
        try:
            self._merge_config(self._config, config_dict)

            # Notify watchers
            for key in config_dict:
                self._notify_watchers(key, config_dict[key])

            if save:
                self.save_to_file()

            self.logger.info(f"Updated configuration with {len(config_dict)} keys")
            return True

        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return False

    def load_from_file(self, file_path: Union[str, Path]) -> bool:
        """
        Load configuration from file

        Args:
            file_path: Path to configuration file

        Returns:
            True if successful
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                self.logger.warning(f"Config file not found: {file_path}")
                return False

            # Determine file type
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                self.logger.error(f"Unsupported config file format: {file_path}")
                return False

            # Merge configuration
            self._merge_config(self._config, config_data)

            # Track source
            source = ConfigSource(
                path=str(file_path),
                type='file',
                priority=1,
                last_modified=file_path.stat().st_mtime
            )
            self._sources.append(source)

            self.logger.info(f"Loaded configuration from: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error loading config from {file_path}: {e}")
            return False

    def save_to_file(self, file_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Save configuration to file

        Args:
            file_path: Target file path (defaults to primary config file)

        Returns:
            True if successful
        """
        try:
            if file_path is None:
                file_path = self.config_dir / 'mova.yaml'
            else:
                file_path = Path(file_path)

            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save based on file extension
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self._config, f, default_flow_style=False, indent=2)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=2)
            else:
                self.logger.error(f"Unsupported save format: {file_path}")
                return False

            self.logger.info(f"Saved configuration to: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False

    def reload(self) -> bool:
        """
        Reload configuration from all sources

        Returns:
            True if successful
        """
        try:
            self.logger.info("Reloading configuration")

            # Clear current config
            self._config.clear()
            self._sources.clear()

            # Reload from sources
            self._load_defaults()
            self._load_from_files()
            self._load_from_environment()

            self.logger.info("Configuration reloaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error reloading configuration: {e}")
            return False

    def get_settings(self) -> MovaSettings:
        """
        Get configuration as MovaSettings object

        Returns:
            MovaSettings instance
        """
        try:
            return MovaSettings.from_dict(self._config)
        except Exception as e:
            self.logger.error(f"Error creating settings object: {e}")
            return MovaSettings()

    def validate_config(self) -> List[str]:
        """
        Validate current configuration

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            # Validate required keys
            required_keys = [
                'server.host',
                'server.port',
                'database.url',
                'logging.level'
            ]

            for key in required_keys:
                if self.get(key) is None:
                    errors.append(f"Missing required configuration: {key}")

            # Validate server port
            port = self.get('server.port')
            if port is not None:
                try:
                    port_int = int(port)
                    if not (1 <= port_int <= 65535):
                        errors.append(f"Invalid server port: {port}")
                except ValueError:
                    errors.append(f"Server port must be integer: {port}")

            # Validate logging level
            log_level = self.get('logging.level')
            if log_level is not None:
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if log_level.upper() not in valid_levels:
                    errors.append(f"Invalid logging level: {log_level}")

        except Exception as e:
            errors.append(f"Configuration validation error: {e}")

        return errors

    def add_watcher(self, callback: callable) -> bool:
        """
        Add configuration change watcher

        Args:
            callback: Function to call on config changes

        Returns:
            True if successful
        """
        try:
            self._watchers.append(callback)
            self.logger.debug("Added configuration watcher")
            return True
        except Exception as e:
            self.logger.error(f"Error adding watcher: {e}")
            return False

    def remove_watcher(self, callback: callable) -> bool:
        """
        Remove configuration change watcher

        Args:
            callback: Function to remove

        Returns:
            True if successful
        """
        try:
            if callback in self._watchers:
                self._watchers.remove(callback)
                self.logger.debug("Removed configuration watcher")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing watcher: {e}")
            return False

    def get_sources(self) -> List[ConfigSource]:
        """
        Get configuration sources

        Returns:
            List of configuration sources
        """
        return self._sources.copy()

    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary

        Returns:
            Configuration dictionary
        """
        return self._config.copy()

    def _load_defaults(self):
        """Load default configuration"""
        defaults = {
            'server': {
                'host': 'localhost',
                'port': 8094,
                'debug': False,
                'workers': 1
            },
            'database': {
                'url': 'sqlite:///mova.db',
                'pool_size': 5,
                'echo': False
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': None
            },
            'tts': {
                'default_engine': 'gtts',
                'default_language': 'en',
                'cache_enabled': True
            },
            'stt': {
                'default_engine': 'whisper',
                'default_language': 'en',
                'model': 'base'
            },
            'audio': {
                'sample_rate': 44100,
                'channels': 2,
                'buffer_size': 1024
            },
            'voice_ui': {
                'wake_word': 'mova',
                'sensitivity': 0.7,
                'timeout': 30
            }
        }

        self._config = defaults
        self._sources.append(ConfigSource(
            path='<defaults>',
            type='default',
            priority=0
        ))

    def _load_from_files(self):
        """Load configuration from files"""
        for path in self.default_paths:
            if path.exists():
                self.load_from_file(path)

    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_prefix = 'MOVA_'
        env_config = {}

        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower().replace('_', '.')

                # Try to convert to appropriate type
                try:
                    if value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    elif value.isdigit():
                        value = int(value)
                    elif '.' in value and value.replace('.', '').isdigit():
                        value = float(value)
                except:
                    pass  # Keep as string

                # Set nested configuration
                keys = config_key.split('.')
                config = env_config
                for k in keys[:-1]:
                    if k not in config:
                        config[k] = {}
                    config = config[k]
                config[keys[-1]] = value

        if env_config:
            self._merge_config(self._config, env_config)
            self._sources.append(ConfigSource(
                path='<environment>',
                type='env',
                priority=2
            ))

    def _merge_config(self, target: Dict, source: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value

    def _notify_watchers(self, key: str, value: Any):
        """Notify configuration watchers of changes"""
        for watcher in self._watchers:
            try:
                watcher(key, value)
            except Exception as e:
                self.logger.warning(f"Watcher error: {e}")
