"""
🚀 Mova CLI - Main Entry Point

Main CLI application entry point that orchestrates all modular CLI components
extracted from monolithic mova.py with enhanced functionality and architecture.
"""

import sys
import os
from typing import Optional

from .argument_parser import MovaArgumentParser
from .command_router import CommandRouter
from .utils import detect_service_name

# Import all command handlers
from ..commands.log_handlers import (
    handle_log_command,
    handle_info_command,
    handle_warning_command,
    handle_error_command,
    handle_watch_logs_command
)
from ..commands.voice_handlers import (
    handle_voice_command,
    handle_audio_command
)
from ..commands.system_handlers import (
    handle_shell_command,
    handle_health_command,
    handle_services_command,
    handle_security_command
)
from ..commands.web_handlers import (
    handle_rss_command,
    handle_watch_command,
    handle_server_command
)
from ..commands.content_handlers import (
    handle_content_command,
    handle_upload_command,
    handle_download_command
)


class MovaCLI:
    """
    Main Mova CLI application class

    Orchestrates argument parsing, command routing, and execution
    with comprehensive error handling and extensible architecture.
    """

    def __init__(self):
        """Initialize CLI components"""
        self.parser = MovaArgumentParser()
        self.router = CommandRouter()
        self._register_handlers()

    def _register_handlers(self):
        """Register all command handlers with the router"""
        # Log commands
        self.router.register_handler('logs', handle_log_command)
        self.router.register_handler('info', handle_info_command)
        self.router.register_handler('warning', handle_warning_command)
        self.router.register_handler('error', handle_error_command)

        # Voice commands
        self.router.register_handler('voice', handle_voice_command)
        self.router.register_handler('audio', handle_audio_command)

        # System commands
        self.router.register_handler('shell', handle_shell_command)
        self.router.register_handler('health', handle_health_command)
        self.router.register_handler('services', handle_services_command)
        self.router.register_handler('security', handle_security_command)

        # Web commands
        self.router.register_handler('rss', handle_rss_command)
        self.router.register_handler('watch', handle_watch_command)
        self.router.register_handler('server', handle_server_command)

        # Content commands
        self.router.register_handler('content', handle_content_command)
        self.router.register_handler('upload', handle_upload_command)
        self.router.register_handler('download', handle_download_command)

        # Special handlers for direct log commands
        self.router.register_handler('list', lambda args: handle_log_command(args))
        self.router.register_handler('watch_logs', handle_watch_logs_command)

    def run(self, args: Optional[list] = None) -> int:
        """
        Run the CLI application

        Args:
            args: Command line arguments (defaults to sys.argv[1:])

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            # Parse arguments
            if args is None:
                args = sys.argv[1:]

            parsed_args = self.parser.parse_args(args)

            # Handle special cases
            if hasattr(parsed_args, 'version') and parsed_args.version:
                self._show_version()
                return 0

            if hasattr(parsed_args, 'verbose') and parsed_args.verbose:
                self._show_environment()

            # Route and execute command
            success = self.router.route_command(parsed_args)

            return 0 if success else 1

        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user")
            return 130
        except Exception as e:
            self._handle_error(e, parsed_args if 'parsed_args' in locals() else None)
            return 1

    def _show_version(self):
        """Show version information"""
        print("🚀 Mova CLI - Advanced Voice System")
        print("Version: 2.0.0 (Modular)")
        print("Architecture: Distributed Microservices")
        print("Components: TTS, STT, Audio, Voice UI, Web Services")
        print("Repository: https://github.com/yourusername/mova")

    def _show_environment(self):
        """Show environment information in verbose mode"""
        print("🔍 Environment Information:")
        print(f"   Service: {detect_service_name()}")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   Platform: {sys.platform}")
        print(f"   Working Dir: {os.getcwd()}")
        print("-" * 40)

    def _handle_error(self, error: Exception, args=None):
        """Handle CLI errors with appropriate user feedback"""
        error_msg = str(error)

        # Determine error type and provide appropriate feedback
        if "Connection" in error_msg or "Server" in error_msg:
            print("❌ Server Connection Error")
            print("💡 Make sure the Mova server is running:")
            print("   - Check server status with: mova health")
            print("   - Start server if needed")

        elif "Permission" in error_msg or "Access" in error_msg:
            print("❌ Permission Error")
            print("💡 Check file/directory permissions")

        elif "File" in error_msg and "not found" in error_msg:
            print("❌ File Not Found")
            print("💡 Verify the file path and try again")

        else:
            print(f"❌ CLI Error: {error_msg}")

        # Show debug info in verbose mode
        if args and hasattr(args, 'verbose') and args.verbose:
            print(f"\n🐛 Debug Info:")
            print(f"   Error Type: {type(error).__name__}")
            print(f"   Command: {getattr(args, 'command', 'Unknown')}")

            import traceback
            print(f"   Traceback:\n{traceback.format_exc()}")


def main():
    """
    Main CLI entry point function

    This function is called when the CLI is executed directly
    or via console scripts in setup.py
    """
    cli = MovaCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


def create_cli_instance():
    """
    Factory function to create CLI instance

    Useful for testing and integration purposes
    """
    return MovaCLI()


# Quick command functions for backwards compatibility
def quick_command(command: str, *args) -> bool:
    """
    Execute a quick command programmatically

    Args:
        command: Command to execute
        *args: Additional arguments

    Returns:
        True if successful
    """
    try:
        cli = MovaCLI()
        cmd_args = [command] + list(args)
        exit_code = cli.run(cmd_args)
        return exit_code == 0
    except Exception:
        return False


def health_check() -> bool:
    """Quick health check function"""
    return quick_command('health')


def get_logs(limit: int = 10) -> bool:
    """Quick log retrieval function"""
    return quick_command('logs', 'list', '--limit', str(limit))


def start_voice_interface() -> bool:
    """Quick voice interface start function"""
    return quick_command('voice', 'start')


# Allow direct execution
if __name__ == '__main__':
    main()
