"""
📝 Argument Parser - Modular CLI Argument Processing

Professional argument parsing system extracted from monolithic mova.py
with comprehensive command structure and validation.
"""

import argparse
from typing import Any, Dict, List, Optional
from .utils import DEFAULT_SERVER


class MovaArgumentParser:
    """
    Professional argument parser for Mova CLI

    Features:
    - Modular command structure
    - Comprehensive argument validation
    - Help system integration
    - Extensible subcommand support
    - Type checking and defaults

    Extracted from original mova.py for modular architecture.
    """

    def __init__(self, version: str = "2.0.0"):
        """
        Initialize Mova argument parser

        Args:
            version: CLI version
        """
        self.version = version
        self.parser = self._create_main_parser()
        self.subparsers = self.parser.add_subparsers(dest='command')
        self._setup_commands()

    def _create_main_parser(self) -> argparse.ArgumentParser:
        """Create main argument parser"""
        parser = argparse.ArgumentParser(
            description='Mova CLI - Professional Communication and Management Tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  mova shell 'ls -la'                    # Execute shell command
  mova list error --last 1h              # List errors from last hour
  mova info "Service started"            # Send info log
  mova health                           # Check server health
  mova watch error --interval 5         # Watch error logs
  mova services list                    # List available services
  mova voice start --language en        # Start voice interface
  mova audio list --test               # List and test audio devices

For more information, visit: https://github.com/mova-project
            """
        )

        # Global options
        parser.add_argument(
            '--server',
            type=str,
            default=DEFAULT_SERVER,
            help='Mova server address (default: %(default)s)'
        )
        parser.add_argument(
            '--version',
            action='version',
            version=f'Mova CLI {self.version}'
        )
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        parser.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Suppress non-essential output'
        )

        return parser

    def _setup_commands(self):
        """Setup all CLI commands and subcommands"""
        self._setup_shell_command()
        self._setup_list_command()
        self._setup_log_commands()
        self._setup_http_command()
        self._setup_health_command()
        self._setup_watch_command()
        self._setup_services_command()
        self._setup_security_command()
        self._setup_voice_command()
        self._setup_audio_command()
        self._setup_rss_command()

    def _setup_shell_command(self):
        """Setup shell command parser"""
        shell_parser = self.subparsers.add_parser(
            'shell',
            help='Execute shell command remotely',
            description='Execute shell commands on remote systems via Mova server'
        )
        shell_parser.add_argument(
            'cmd',
            type=str,
            help='Shell command to execute'
        )
        shell_parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Command timeout in seconds (default: %(default)s)'
        )
        shell_parser.add_argument(
            '--async',
            action='store_true',
            help='Execute command asynchronously'
        )

    def _setup_list_command(self):
        """Setup list command parser"""
        list_parser = self.subparsers.add_parser(
            'list',
            help='List logs and events',
            description='Retrieve and display logs with filtering options'
        )
        list_parser.add_argument(
            'level',
            type=str,
            choices=['error', 'warning', 'info', 'debug', 'all'],
            help='Log level to filter'
        )
        list_parser.add_argument(
            '--last',
            type=str,
            help='Time period (e.g., 5m, 1h, 30s, or bare number for minutes)'
        )
        list_parser.add_argument(
            '--service',
            type=str,
            help='Filter by service name'
        )
        list_parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum number of logs (default: %(default)s)'
        )
        list_parser.add_argument(
            '--format',
            choices=['standard', 'compact', 'detailed', 'json', 'ndjson'],
            default='standard',
            help='Output format (default: %(default)s)'
        )
        list_parser.add_argument(
            '--tts',
            action='store_true',
            help='Enable text-to-speech for log reading'
        )

    def _setup_log_commands(self):
        """Setup logging commands (info, warning, error)"""
        # Info command
        info_parser = self.subparsers.add_parser(
            'info',
            help='Send info log message',
            description='Send informational log message to Mova server'
        )
        info_parser.add_argument(
            'message',
            type=str,
            help='Log message content'
        )
        info_parser.add_argument(
            '--service',
            type=str,
            help='Service name (auto-detected if not provided)'
        )

        # Warning command
        warning_parser = self.subparsers.add_parser(
            'warning',
            help='Send warning log message',
            description='Send warning log message to Mova server'
        )
        warning_parser.add_argument(
            'message',
            type=str,
            help='Warning message content'
        )
        warning_parser.add_argument(
            '--service',
            type=str,
            help='Service name (auto-detected if not provided)'
        )
        warning_parser.add_argument(
            '--mqtt-broker',
            type=str,
            help='MQTT broker address for alerts'
        )
        warning_parser.add_argument(
            '--mqtt-topic',
            type=str,
            help='MQTT topic for alerts'
        )

        # Error command
        error_parser = self.subparsers.add_parser(
            'error',
            help='Send error log message',
            description='Send error log message to Mova server'
        )
        error_parser.add_argument(
            'message',
            type=str,
            help='Error message content'
        )
        error_parser.add_argument(
            '--service',
            type=str,
            help='Service name (auto-detected if not provided)'
        )

    def _setup_http_command(self):
        """Setup HTTP command parser"""
        http_parser = self.subparsers.add_parser(
            'http',
            help='Execute JavaScript in browser',
            description='Execute JavaScript code in remote browser via Mova server'
        )
        http_parser.add_argument(
            'address',
            type=str,
            help='Target host address (localhost, IP, or domain)'
        )
        http_parser.add_argument(
            'js_code',
            type=str,
            help='JavaScript code to execute'
        )
        http_parser.add_argument(
            '--port',
            type=int,
            default=8094,
            help='Server port (default: %(default)s)'
        )

    def _setup_health_command(self):
        """Setup health command parser"""
        health_parser = self.subparsers.add_parser(
            'health',
            help='Check server health status',
            description='Perform health check on Mova server and services'
        )
        health_parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed health information'
        )
        health_parser.add_argument(
            '--services',
            action='store_true',
            help='Include service health status'
        )

    def _setup_watch_command(self):
        """Setup watch command parser"""
        watch_parser = self.subparsers.add_parser(
            'watch',
            help='Monitor logs in real-time',
            description='Continuously monitor logs with live updates'
        )
        watch_parser.add_argument(
            'level',
            choices=['info', 'warning', 'error', 'debug', 'all'],
            help='Log level to monitor'
        )
        watch_parser.add_argument(
            '--service',
            type=str,
            help='Filter by service name'
        )
        watch_parser.add_argument(
            '--interval',
            type=int,
            default=2,
            help='Refresh interval in seconds (default: %(default)s)'
        )
        watch_parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Number of logs to display (default: %(default)s)'
        )
        watch_parser.add_argument(
            '--follow',
            action='store_true',
            help='Show only new logs (like tail -f)'
        )
        watch_parser.add_argument(
            '--full',
            action='store_true',
            help='Show full messages without truncation'
        )
        watch_parser.add_argument(
            '--tts',
            action='store_true',
            help='Enable text-to-speech for new logs'
        )
        watch_parser.add_argument(
            '--format',
            choices=['standard', 'compact', 'detailed'],
            default='standard',
            help='Output format (default: %(default)s)'
        )

    def _setup_services_command(self):
        """Setup services management command"""
        services_parser = self.subparsers.add_parser(
            'services',
            help='Manage system services',
            description='Manage integrated system services via Mova'
        )
        services_subparsers = services_parser.add_subparsers(dest='services_action')

        # services list
        list_parser = services_subparsers.add_parser(
            'list',
            help='List available services'
        )
        list_parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed service information'
        )

        # services enable/disable
        enable_parser = services_subparsers.add_parser(
            'enable',
            help='Enable service monitoring'
        )
        enable_parser.add_argument(
            'service_name',
            type=str,
            help='Service name to enable'
        )

        disable_parser = services_subparsers.add_parser(
            'disable',
            help='Disable service monitoring'
        )
        disable_parser.add_argument(
            'service_name',
            type=str,
            help='Service name to disable'
        )

        # services status
        status_parser = services_subparsers.add_parser(
            'status',
            help='Check service status'
        )
        status_parser.add_argument(
            'service_name',
            type=str,
            nargs='?',
            help='Specific service name (optional)'
        )

    def _setup_security_command(self):
        """Setup security management command"""
        security_parser = self.subparsers.add_parser(
            'security',
            help='Manage security settings',
            description='Configure and manage security policies'
        )
        security_subparsers = security_parser.add_subparsers(dest='security_action')

        # security acl
        acl_parser = security_subparsers.add_parser(
            'acl',
            help='Manage Access Control Lists'
        )
        acl_subparsers = acl_parser.add_subparsers(dest='acl_action')

        acl_list_parser = acl_subparsers.add_parser('list', help='List ACL rules')

        acl_add_parser = acl_subparsers.add_parser('add', help='Add ACL rule')
        acl_add_parser.add_argument('--ip', required=True, help='IP address or range')
        acl_add_parser.add_argument('--action', choices=['allow', 'deny'], required=True)
        acl_add_parser.add_argument('--description', help='Rule description')

        # security cors
        cors_parser = security_subparsers.add_parser(
            'cors',
            help='Manage CORS policies'
        )
        cors_subparsers = cors_parser.add_subparsers(dest='cors_action')

        cors_list_parser = cors_subparsers.add_parser('list', help='List CORS policies')

        cors_add_parser = cors_subparsers.add_parser('add', help='Add CORS policy')
        cors_add_parser.add_argument('--origin', required=True, help='Allowed origin')
        cors_add_parser.add_argument('--methods', nargs='+', help='Allowed methods')
        cors_add_parser.add_argument('--headers', nargs='+', help='Allowed headers')

    def _setup_voice_command(self):
        """Setup voice interface command"""
        voice_parser = self.subparsers.add_parser(
            'voice',
            help='Voice interface control',
            description='Control voice recognition and text-to-speech interface'
        )
        voice_subparsers = voice_parser.add_subparsers(dest='voice_action')

        # voice start
        start_parser = voice_subparsers.add_parser(
            'start',
            help='Start voice interface'
        )
        start_parser.add_argument(
            '--language',
            choices=['en', 'pl', 'de', 'es', 'fr'],
            default='en',
            help='Interface language (default: %(default)s)'
        )
        start_parser.add_argument(
            '--mode',
            choices=['single', 'continuous', 'wake_word', 'push_to_talk'],
            default='single',
            help='Voice interaction mode (default: %(default)s)'
        )
        start_parser.add_argument(
            '--timeout',
            type=float,
            help='Session timeout in minutes'
        )

        # voice stop
        voice_subparsers.add_parser(
            'stop',
            help='Stop voice interface'
        )

        # voice test
        test_parser = voice_subparsers.add_parser(
            'test',
            help='Test voice components'
        )
        test_parser.add_argument(
            '--tts',
            action='store_true',
            help='Test text-to-speech'
        )
        test_parser.add_argument(
            '--stt',
            action='store_true',
            help='Test speech-to-text'
        )
        test_parser.add_argument(
            '--audio',
            action='store_true',
            help='Test audio devices'
        )

        # voice status
        voice_subparsers.add_parser(
            'status',
            help='Show voice interface status'
        )

    def _setup_audio_command(self):
        """Setup audio device management command"""
        audio_parser = self.subparsers.add_parser(
            'audio',
            help='Audio device management',
            description='Manage audio input/output devices for voice interface'
        )
        audio_subparsers = audio_parser.add_subparsers(dest='audio_action')

        # audio list
        list_parser = audio_subparsers.add_parser(
            'list',
            help='List audio devices'
        )
        list_parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed device information'
        )
        list_parser.add_argument(
            '--test',
            action='store_true',
            help='Test devices during listing'
        )

        # audio get
        get_parser = audio_subparsers.add_parser(
            'get',
            help='Get current audio devices'
        )
        get_parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information'
        )

        # audio set
        set_parser = audio_subparsers.add_parser(
            'set',
            help='Set audio devices'
        )
        set_subparsers = set_parser.add_subparsers(dest='audio_set_action')

        auto_parser = set_subparsers.add_parser(
            'auto',
            help='Auto-configure audio devices'
        )
        auto_parser.add_argument(
            '--test',
            action='store_true',
            help='Test devices after configuration'
        )
        auto_parser.add_argument(
            '--save',
            action='store_true',
            help='Save configuration permanently'
        )

    def _setup_rss_command(self):
        """Setup RSS processing command"""
        rss_parser = self.subparsers.add_parser(
            'rss',
            help='RSS feed processing',
            description='Process and analyze RSS feeds'
        )
        rss_parser.add_argument(
            'url',
            nargs='?',
            help='RSS feed URL (optional if default configured)'
        )
        rss_parser.add_argument(
            '--output',
            choices=['summary', 'full', 'json'],
            default='summary',
            help='Output format (default: %(default)s)'
        )
        rss_parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of items (default: %(default)s)'
        )
        rss_parser.add_argument(
            '--tts',
            action='store_true',
            help='Read items with text-to-speech'
        )

    def parse_args(self, args: Optional[List[str]] = None) -> Any:
        """
        Parse command line arguments

        Args:
            args: Arguments to parse (None for sys.argv)

        Returns:
            Parsed arguments namespace
        """
        parsed_args = self.parser.parse_args(args)

        # Post-processing validation
        self._validate_args(parsed_args)

        return parsed_args

    def _validate_args(self, args: Any):
        """
        Validate parsed arguments

        Args:
            args: Parsed arguments namespace

        Raises:
            argparse.ArgumentError: For invalid argument combinations
        """
        # Validate server URL
        if hasattr(args, 'server') and args.server:
            from .utils import validate_server_url
            try:
                args.server = validate_server_url(args.server)
            except ValueError as e:
                self.parser.error(str(e))

        # Validate mutually exclusive options
        if hasattr(args, 'verbose') and hasattr(args, 'quiet'):
            if args.verbose and args.quiet:
                self.parser.error("--verbose and --quiet are mutually exclusive")

        # Validate time duration format
        if hasattr(args, 'last') and args.last:
            from .utils import parse_time_duration
            try:
                parse_time_duration(args.last)
            except ValueError as e:
                self.parser.error(f"Invalid --last format: {e}")

        # Validate timeout values
        if hasattr(args, 'timeout') and args.timeout is not None:
            if args.timeout <= 0:
                self.parser.error("Timeout must be greater than 0")

        # Validate limit values
        if hasattr(args, 'limit') and args.limit is not None:
            if args.limit <= 0:
                self.parser.error("Limit must be greater than 0")

    def print_help(self):
        """Print help message"""
        self.parser.print_help()

    def get_subcommands(self) -> List[str]:
        """
        Get list of available subcommands

        Returns:
            List of subcommand names
        """
        return list(self.subparsers.choices.keys())

    def add_custom_command(self, name: str, **kwargs) -> argparse.ArgumentParser:
        """
        Add custom command to parser

        Args:
            name: Command name
            **kwargs: Additional arguments for add_parser

        Returns:
            Subparser for the command
        """
        return self.subparsers.add_parser(name, **kwargs)
