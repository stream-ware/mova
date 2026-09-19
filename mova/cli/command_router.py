"""
🔀 Command Router - Professional CLI Command Routing System

Intelligent command routing and execution system extracted from monolithic mova.py
with dynamic handler loading and extensible architecture.
"""

import sys
from typing import Any, Dict, Callable, Optional, Type
import logging
from .utils import print_banner, get_system_info


class CommandRouter:
    """
    Professional command routing system for Mova CLI

    Features:
    - Dynamic command handler loading
    - Extensible command registration
    - Error handling and recovery
    - Performance monitoring
    - Help system integration
    - Plugin support preparation

    Extracted from original mova.py for modular architecture.
    """

    def __init__(self, version: str = "2.0.0", verbose: bool = False):
        """
        Initialize Command Router

        Args:
            version: CLI version
            verbose: Enable verbose logging
        """
        self.version = version
        self.verbose = verbose
        self.logger = self._setup_logger()

        # Command handlers registry
        self.handlers: Dict[str, Callable] = {}
        self.command_metadata: Dict[str, Dict[str, Any]] = {}

        # Performance tracking
        self._command_count = 0
        self._failed_commands = 0

        # Load core command handlers
        self._load_core_handlers()

        if verbose:
            print_banner(self.version)
            self.logger.info("Command router initialized with verbose logging")

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for command router"""
        logger = logging.getLogger("mova.cli.router")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        return logger

    def _load_core_handlers(self):
        """Load core command handlers"""
        try:
            # Import command handlers
            from .commands import (
                handle_shell_command,
                handle_list_command,
                handle_info_command,
                handle_warning_command,
                handle_error_command,
                handle_http_command,
                handle_health_command,
                handle_watch_command,
                handle_services_command,
                handle_security_command,
                handle_voice_command,
                handle_audio_command,
                handle_rss_command
            )

            # Register core handlers
            self.register_handler('shell', handle_shell_command, {
                'description': 'Execute shell commands remotely',
                'category': 'system'
            })
            self.register_handler('list', handle_list_command, {
                'description': 'List logs and events',
                'category': 'logging'
            })
            self.register_handler('info', handle_info_command, {
                'description': 'Send info log message',
                'category': 'logging'
            })
            self.register_handler('warning', handle_warning_command, {
                'description': 'Send warning log message',
                'category': 'logging'
            })
            self.register_handler('error', handle_error_command, {
                'description': 'Send error log message',
                'category': 'logging'
            })
            self.register_handler('http', handle_http_command, {
                'description': 'Execute JavaScript in browser',
                'category': 'web'
            })
            self.register_handler('health', handle_health_command, {
                'description': 'Check server health status',
                'category': 'system'
            })
            self.register_handler('watch', handle_watch_command, {
                'description': 'Monitor logs in real-time',
                'category': 'logging'
            })
            self.register_handler('services', handle_services_command, {
                'description': 'Manage system services',
                'category': 'system'
            })
            self.register_handler('security', handle_security_command, {
                'description': 'Manage security settings',
                'category': 'security'
            })
            self.register_handler('voice', handle_voice_command, {
                'description': 'Voice interface control',
                'category': 'voice'
            })
            self.register_handler('audio', handle_audio_command, {
                'description': 'Audio device management',
                'category': 'voice'
            })
            self.register_handler('rss', handle_rss_command, {
                'description': 'RSS feed processing',
                'category': 'content'
            })

            self.logger.info(f"Loaded {len(self.handlers)} core command handlers")

        except ImportError as e:
            self.logger.warning(f"Some command handlers not available: {e}")
            # Register fallback handlers
            self._register_fallback_handlers()

    def _register_fallback_handlers(self):
        """Register fallback handlers for missing components"""
        def fallback_handler(args):
            print(f"❌ Command '{args.command}' not available")
            print("💡 This command requires additional dependencies or modules")
            return False

        fallback_commands = [
            'shell', 'list', 'info', 'warning', 'error', 'http',
            'health', 'watch', 'services', 'security', 'voice', 'audio', 'rss'
        ]

        for cmd in fallback_commands:
            if cmd not in self.handlers:
                self.register_handler(cmd, fallback_handler, {
                    'description': f'{cmd.title()} command (fallback)',
                    'category': 'fallback'
                })

    def register_handler(self, command: str, handler: Callable,
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Register command handler

        Args:
            command: Command name
            handler: Handler function
            metadata: Optional command metadata
        """
        self.handlers[command] = handler
        self.command_metadata[command] = metadata or {}

        if self.verbose:
            self.logger.debug(f"Registered handler for command: {command}")

    def unregister_handler(self, command: str) -> bool:
        """
        Unregister command handler

        Args:
            command: Command name

        Returns:
            True if handler was removed
        """
        if command in self.handlers:
            del self.handlers[command]
            if command in self.command_metadata:
                del self.command_metadata[command]

            self.logger.info(f"Unregistered handler for command: {command}")
            return True

        return False

    def route_command(self, args: Any) -> bool:
        """
        Route command to appropriate handler

        Args:
            args: Parsed command line arguments

        Returns:
            True if command executed successfully
        """
        try:
            self._command_count += 1

            # Handle special cases
            if not hasattr(args, 'command') or not args.command:
                self._show_help()
                return True

            command = args.command

            if self.verbose:
                self.logger.info(f"Routing command: {command}")
                self.logger.debug(f"Command arguments: {vars(args)}")

            # Check if handler exists
            if command not in self.handlers:
                print(f"❌ Unknown command: {command}")
                print(f"💡 Available commands: {', '.join(sorted(self.handlers.keys()))}")
                print("Use 'mova --help' for more information")
                self._failed_commands += 1
                return False

            # Execute handler
            handler = self.handlers[command]

            try:
                result = handler(args)

                if self.verbose:
                    self.logger.info(f"Command '{command}' completed with result: {result}")

                return bool(result) if result is not None else True

            except Exception as e:
                self.logger.error(f"Command '{command}' failed: {e}")
                print(f"❌ Command execution failed: {e}")

                if self.verbose:
                    import traceback
                    traceback.print_exc()

                self._failed_commands += 1
                return False

        except Exception as e:
            self.logger.error(f"Command routing failed: {e}")
            print(f"❌ Internal error: {e}")
            self._failed_commands += 1
            return False

    def _show_help(self):
        """Show general help information"""
        print_banner(self.version)
        print("🚀 Mova CLI - Professional Communication and Management Tool")
        print()
        print("Available commands:")

        # Group commands by category
        categories = {}
        for cmd, metadata in self.command_metadata.items():
            category = metadata.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'name': cmd,
                'description': metadata.get('description', 'No description available')
            })

        for category, commands in sorted(categories.items()):
            print(f"\n📂 {category.title()}:")
            for cmd_info in sorted(commands, key=lambda x: x['name']):
                print(f"  {cmd_info['name']:12} - {cmd_info['description']}")

        print(f"\nUse 'mova <command> --help' for detailed command information")
        print(f"Use 'mova --version' to show version information")

    def get_available_commands(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available commands with metadata

        Returns:
            Dictionary of commands and their metadata
        """
        return {
            cmd: {
                'handler': handler.__name__ if hasattr(handler, '__name__') else str(handler),
                'metadata': self.command_metadata.get(cmd, {})
            }
            for cmd, handler in self.handlers.items()
        }

    def get_command_stats(self) -> Dict[str, Any]:
        """
        Get command execution statistics

        Returns:
            Statistics dictionary
        """
        return {
            'total_commands': self._command_count,
            'successful_commands': self._command_count - self._failed_commands,
            'failed_commands': self._failed_commands,
            'success_rate': ((self._command_count - self._failed_commands) /
                           max(1, self._command_count)) * 100,
            'registered_handlers': len(self.handlers),
            'version': self.version
        }

    def validate_command_args(self, args: Any) -> bool:
        """
        Validate command arguments

        Args:
            args: Parsed arguments

        Returns:
            True if arguments are valid
        """
        try:
            # Basic validation
            if not hasattr(args, 'command'):
                return False

            # Command-specific validation could be added here
            # For now, basic validation is handled by argument parser

            return True

        except Exception as e:
            self.logger.error(f"Argument validation failed: {e}")
            return False

    def add_middleware(self, middleware: Callable):
        """
        Add middleware for command processing

        Args:
            middleware: Middleware function
        """
        # Middleware support for future extension
        # Could be used for logging, authentication, etc.
        pass

    def get_system_diagnostics(self) -> Dict[str, Any]:
        """
        Get system diagnostics information

        Returns:
            System diagnostics dictionary
        """
        try:
            diagnostics = {
                'router_info': {
                    'version': self.version,
                    'verbose': self.verbose,
                    'handlers_count': len(self.handlers),
                    'command_stats': self.get_command_stats()
                },
                'system_info': get_system_info(),
                'available_commands': list(self.handlers.keys())
            }

            return diagnostics

        except Exception as e:
            self.logger.error(f"Failed to get system diagnostics: {e}")
            return {'error': str(e)}

    def test_handlers(self) -> Dict[str, Any]:
        """
        Test all registered handlers

        Returns:
            Test results dictionary
        """
        test_results = {
            'total_handlers': len(self.handlers),
            'tested_handlers': 0,
            'successful_tests': 0,
            'failed_tests': [],
            'handler_status': {}
        }

        for cmd, handler in self.handlers.items():
            try:
                test_results['tested_handlers'] += 1

                # Basic test - check if handler is callable
                if callable(handler):
                    test_results['successful_tests'] += 1
                    test_results['handler_status'][cmd] = 'available'
                else:
                    test_results['failed_tests'].append({
                        'command': cmd,
                        'error': 'Handler is not callable'
                    })
                    test_results['handler_status'][cmd] = 'not_callable'

            except Exception as e:
                test_results['failed_tests'].append({
                    'command': cmd,
                    'error': str(e)
                })
                test_results['handler_status'][cmd] = 'error'

        return test_results

    def __str__(self) -> str:
        return f"CommandRouter(v{self.version}, handlers={len(self.handlers)})"

    def __repr__(self) -> str:
        return f"<CommandRouter: {self.version}, {len(self.handlers)} handlers, {self._command_count} commands processed>"
