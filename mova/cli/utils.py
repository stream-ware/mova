"""
🔧 CLI Utilities - Core Helper Functions

Professional utility functions extracted from monolithic mova.py
for service detection, HTTP requests, time parsing, and log formatting.
"""

import os
import re
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


# Configuration
DEFAULT_SERVER = "http://localhost:8094"


def detect_service_name() -> str:
    """
    Intelligent service name detection based on context

    Returns:
        Service name with detection method prefix
    """
    try:
        # Get current working directory
        cwd = os.getcwd()
        cwd_path = Path(cwd)

        # 1. Check if we are in a Git repository
        try:
            git_result = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                                      capture_output=True, text=True, timeout=5)
            if git_result.returncode == 0:
                git_root = Path(git_result.stdout.strip())
                # Use Git repository name as service name
                service_name = git_root.name
                if service_name and service_name != '.':
                    return f"git:{service_name}"
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # 2. Check if we are in a directory with characteristic files
        characteristic_files = {
            'package.json': 'nodejs',
            'requirements.txt': 'python',
            'Cargo.toml': 'rust',
            'go.mod': 'golang',
            'pom.xml': 'java',
            'docker-compose.yml': 'docker',
            'Dockerfile': 'docker',
            '.env': 'env'
        }

        for file_name, tech in characteristic_files.items():
            if (cwd_path / file_name).exists():
                return f"{tech}:{cwd_path.name}"

        # 3. Check parent directory name (project)
        if cwd_path.name and cwd_path.name not in ['.', '/', 'home']:
            return f"dir:{cwd_path.name}"

        # 4. Check parent directory if current is 'src', 'app', etc.
        if cwd_path.name in ['src', 'app', 'lib', 'cli', 'server']:
            parent = cwd_path.parent
            if parent.name and parent.name not in ['.', '/', 'home']:
                return f"proj:{parent.name}"

        # 5. Use username and last directory
        username = os.getenv('USER', os.getenv('USERNAME', 'user'))
        return f"{username}:{cwd_path.name}"

    except Exception:
        # Fallback - use directory name or unknown
        try:
            cwd = os.getcwd()
            dir_name = os.path.basename(cwd)
            return dir_name if dir_name else "unknown"
        except:
            return "unknown"


def make_request(method: str, endpoint: str, data: Optional[Dict] = None,
                server: str = DEFAULT_SERVER) -> Dict[str, Any]:
    """
    Make HTTP request to Mova server

    Args:
        method: HTTP method (GET, POST)
        endpoint: API endpoint
        data: Request data
        server: Server URL

    Returns:
        Response JSON data

    Raises:
        SystemExit: On connection or HTTP errors
    """
    url = f"{server}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, params=data or {})
        elif method.upper() == "POST":
            response = requests.post(url, json=data or {})
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        print(f"❌ Błąd: Nie można połączyć się z serwerem Mova na {server}")
        print(f"💡 Upewnij się, że serwer jest uruchomiony: make server")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Błąd HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Błąd: {str(e)}")
        sys.exit(1)


def parse_time_duration(duration: str) -> Optional[float]:
    """
    Parse duration string like '5m', '1h', '30s' into minutes

    Args:
        duration: Duration string (e.g., '30s', '5m', '1h')

    Returns:
        Duration in minutes or None if invalid

    Raises:
        ValueError: For invalid duration format
    """
    if not duration:
        return None

    # Handle bare numbers (assume minutes)
    if duration.isdigit():
        return float(duration)

    match = re.match(r'^(\d+)([smh])$', duration)
    if not match:
        raise ValueError("Invalid duration format. Use: 30s, 5m, 1h or bare number for minutes")

    value, unit = match.groups()
    multipliers = {'s': 1/60, 'm': 1, 'h': 60}
    return int(value) * multipliers[unit]


def format_log_output(logs: List[Dict], full_messages: bool = False) -> None:
    """
    Format and print logs with color coding and proper structure

    Args:
        logs: List of log entries
        full_messages: Whether to show full messages
    """
    if not logs:
        print("📭 Brak logów do wyświetlenia")
        return

    print(f"📊 Znaleziono {len(logs)} logów:")
    print("-" * 80)

    for log in logs:
        timestamp = log.get('timestamp', '')
        level = log.get('level', 'info').upper()
        service = log.get('service', 'unknown')
        message = log.get('message', '')

        # Color coding for levels
        level_colors = {
            'ERROR': '🔴',
            'WARNING': '🟡',
            'INFO': '🔵',
            'DEBUG': '⚪'
        }

        icon = level_colors.get(level, '📝')

        if full_messages:
            # Display full message with line breaks for long messages
            print(f"{icon} [{timestamp[:19]}] {level:7} | {service}")
            print(f"    📄 Treść: {message}")
            print("-" * 60)
        else:
            # Standard display with potential truncation
            display_message = message[:100] + "..." if len(message) > 100 else message
            print(f"{icon} [{timestamp[:19]}] {level:7} | {service:10} | {display_message}")


def format_log_entry(log_entry: Dict, format_type: str = 'standard') -> str:
    """
    Format single log entry based on format type

    Args:
        log_entry: Log entry dictionary
        format_type: Format type ('standard', 'compact', 'detailed')

    Returns:
        Formatted log string
    """
    timestamp = log_entry.get('timestamp', '')
    level = log_entry.get('level', 'info').upper()
    service = log_entry.get('service', 'unknown')
    message = log_entry.get('message', '')

    # Level icons
    level_colors = {
        'ERROR': '🔴',
        'WARNING': '🟡',
        'INFO': '🔵',
        'DEBUG': '⚪'
    }
    icon = level_colors.get(level, '📝')

    if format_type == 'compact':
        return f"{icon} {timestamp[:16]} {level[:4]} {service[:8]} {message[:60]}"
    elif format_type == 'detailed':
        return (f"{icon} [{timestamp}] {level:8} | {service:12} |\n"
                f"    📄 Message: {message}\n"
                f"    🏷️  Metadata: {json.dumps({k: v for k, v in log_entry.items() if k not in ['timestamp', 'level', 'service', 'message']}, separators=(',', ':'))}")
    else:  # standard
        display_message = message[:100] + "..." if len(message) > 100 else message
        return f"{icon} [{timestamp[:19]}] {level:7} | {service:10} | {display_message}"


def prepare_log_for_tts(log_entry: Dict) -> str:
    """
    Prepare log entry for text-to-speech - extract key information

    Args:
        log_entry: Log entry dictionary

    Returns:
        TTS-ready text string
    """
    try:
        # Basic log fields
        level = log_entry.get('level', 'info').upper()
        message = log_entry.get('message', '').strip()
        service = log_entry.get('service', '')

        # Truncate and clean message for TTS
        if len(message) > 200:
            message = message[:200] + "..."

        # Remove special characters and formatting that might interfere with TTS
        message = message.replace('\n', ' ').replace('\t', ' ')
        message = ' '.join(message.split())  # Normalize whitespace

        # Build TTS text
        tts_parts = []

        # Add log level
        if level in ['ERROR', 'CRITICAL']:
            tts_parts.append(f"Alert {level}")
        elif level == 'WARNING':
            tts_parts.append("Warning")
        elif level == 'INFO':
            tts_parts.append("Info")
        else:
            tts_parts.append(f"Log {level}")

        # Add service if available
        if service:
            tts_parts.append(f"from {service}")

        # Add main message
        if message:
            tts_parts.append(f": {message}")

        return ' '.join(tts_parts)

    except Exception as e:
        # Fallback - basic message
        return f"Log entry: {log_entry.get('message', 'No message')}"


def should_speak_message(tts_text: str, message_cache: Dict, cache_timeout: int = 300) -> bool:
    """
    Check if message should be spoken by TTS (intelligent deduplication)

    Args:
        tts_text: Text to be spoken
        message_cache: Cache of recently spoken messages
        cache_timeout: Cache timeout in seconds (default: 5 minutes)

    Returns:
        True if message should be spoken
    """
    try:
        import hashlib

        # Create message hash for duplicate identification
        message_hash = hashlib.md5(tts_text.encode('utf-8')).hexdigest()
        current_time = time.time()

        # Check if message was already spoken recently
        if message_hash in message_cache:
            last_spoken_time = message_cache[message_hash]
            if current_time - last_spoken_time < cache_timeout:
                # Message was spoken within cache_timeout seconds
                return False

        # Mark message as spoken
        message_cache[message_hash] = current_time

        # Clean old entries from cache (older than cache_timeout)
        expired_hashes = [h for h, t in message_cache.items() if current_time - t > cache_timeout]
        for hash_to_remove in expired_hashes:
            del message_cache[hash_to_remove]

        return True

    except Exception as e:
        # In case of error, allow message to be spoken
        print(f"⚠️ Błąd deduplikacji TTS: {e}")
        return True


def validate_server_url(server: str) -> str:
    """
    Validate and normalize server URL

    Args:
        server: Server URL

    Returns:
        Normalized server URL

    Raises:
        ValueError: For invalid URL format
    """
    if not server:
        return DEFAULT_SERVER

    # Add http:// if no protocol specified
    if not server.startswith(('http://', 'https://')):
        server = f"http://{server}"

    # Remove trailing slash
    server = server.rstrip('/')

    # Basic URL validation
    if not re.match(r'https?://[^\s/$.?#].[^\s]*$', server):
        raise ValueError(f"Invalid server URL format: {server}")

    return server


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for diagnostics

    Returns:
        System information dictionary
    """
    try:
        import platform

        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0],
            'hostname': platform.node(),
            'current_directory': os.getcwd(),
            'user': os.getenv('USER', os.getenv('USERNAME', 'unknown')),
            'service_name': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def print_banner(version: str = "2.0.0"):
    """
    Print Mova CLI banner

    Args:
        version: CLI version
    """
    banner = f"""
    ╔══════════════════════════════════════╗
    ║            🚀 MOVA CLI {version:6}         ║
    ║    Professional Modular Interface    ║
    ╚══════════════════════════════════════╝
    """
    print(banner)


def cleanup_temp_files(temp_dir: Optional[str] = None):
    """
    Clean up temporary files created by CLI operations

    Args:
        temp_dir: Specific temp directory to clean
    """
    try:
        import tempfile
        import shutil

        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        else:
            # Clean system temp files with mova prefix
            system_temp = tempfile.gettempdir()
            for item in os.listdir(system_temp):
                if item.startswith('mova_'):
                    item_path = os.path.join(system_temp, item)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                    except Exception:
                        pass  # Ignore cleanup errors

    except Exception as e:
        # Don't fail on cleanup errors
        pass
