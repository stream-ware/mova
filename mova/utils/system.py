"""
🖥️ System Utilities - System Information and Process Management

Comprehensive system utilities for process management, system monitoring,
and resource information with cross-platform compatibility.
"""

import os
import sys
import psutil
import socket
import platform
import subprocess
from typing import Dict, Any, Optional, List, Tuple, Sequence, Set
import logging


def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information

    Returns:
        Dictionary with system information
    """
    try:
        info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'python_version': platform.python_version(),
            },
            'cpu': {
                'count': psutil.cpu_count(),
                'count_logical': psutil.cpu_count(logical=True),
                'percent': psutil.cpu_percent(interval=1),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used,
                'free': psutil.virtual_memory().free,
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent,
            },
            'network': {
                'hostname': socket.gethostname(),
                'ip_address': get_local_ip(),
            },
            'process': {
                'pid': os.getpid(),
                'ppid': os.getppid(),
                'cwd': os.getcwd(),
                'user': get_current_user(),
            }
        }

        return info

    except Exception as e:
        logging.error(f"Error getting system info: {e}")
        return {}


def get_local_ip() -> str:
    """
    Get local IP address

    Returns:
        Local IP address string
    """
    try:
        # Connect to remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def get_current_user() -> str:
    """
    Get current system user

    Returns:
        Current username
    """
    try:
        return os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
    except Exception:
        return 'unknown'


def check_port_available(port: int, host: str = 'localhost') -> bool:
    """
    Check if port is available for binding

    Args:
        port: Port number to check
        host: Host address to check

    Returns:
        True if port is available
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0  # Port is available if connection fails
    except Exception:
        return False


def find_free_port(start_port: int = 8000, end_port: int = 9000,
                  host: str = 'localhost') -> Optional[int]:
    """
    Find first available port in range

    Args:
        start_port: Starting port number
        end_port: Ending port number
        host: Host address to check

    Returns:
        First available port or None if none found
    """
    try:
        for port in range(start_port, end_port + 1):
            if check_port_available(port, host):
                return port
        return None
    except Exception:
        return None


def get_process_info(pid: Optional[int] = None) -> Dict[str, Any]:
    """
    Get process information

    Args:
        pid: Process ID (defaults to current process)

    Returns:
        Process information dictionary
    """
    try:
        if pid is None:
            pid = os.getpid()

        process = psutil.Process(pid)

        info = {
            'pid': process.pid,
            'ppid': process.ppid(),
            'name': process.name(),
            'status': process.status(),
            'create_time': process.create_time(),
            'cpu_percent': process.cpu_percent(),
            'memory_info': process.memory_info()._asdict(),
            'memory_percent': process.memory_percent(),
            'num_threads': process.num_threads(),
            'cmdline': process.cmdline(),
            'cwd': process.cwd() if hasattr(process, 'cwd') else None,
            'username': process.username() if hasattr(process, 'username') else None,
        }

        return info

    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
        logging.error(f"Error getting process info for PID {pid}: {e}")
        return {}


def kill_process_by_port(port: int, force: bool = False) -> bool:
    """
    Kill process using specified port

    Args:
        port: Port number
        force: Use SIGKILL instead of SIGTERM

    Returns:
        True if process was killed
    """
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.pid:
                try:
                    process = psutil.Process(conn.pid)
                    if force:
                        process.kill()  # SIGKILL
                    else:
                        process.terminate()  # SIGTERM

                    # Wait for process to terminate
                    try:
                        process.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        process.kill()  # Force kill if doesn't terminate

                    logging.info(f"Killed process {conn.pid} using port {port}")
                    return True

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        return False

    except Exception as e:
        logging.error(f"Error killing process on port {port}: {e}")
        return False


def get_disk_usage(path: str = '/') -> Dict[str, Any]:
    """
    Get disk usage information for path

    Args:
        path: Path to check disk usage

    Returns:
        Disk usage information
    """
    try:
        usage = psutil.disk_usage(path)

        return {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0,
            'path': path
        }

    except Exception as e:
        logging.error(f"Error getting disk usage for {path}: {e}")
        return {}


def get_memory_usage() -> Dict[str, Any]:
    """
    Get system memory usage information

    Returns:
        Memory usage information
    """
    try:
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            'virtual': {
                'total': virtual.total,
                'available': virtual.available,
                'percent': virtual.percent,
                'used': virtual.used,
                'free': virtual.free,
                'active': getattr(virtual, 'active', 0),
                'inactive': getattr(virtual, 'inactive', 0),
                'buffers': getattr(virtual, 'buffers', 0),
                'cached': getattr(virtual, 'cached', 0),
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent,
            }
        }

    except Exception as e:
        logging.error(f"Error getting memory usage: {e}")
        return {}


def get_running_processes() -> List[Dict[str, Any]]:
    """
    Get list of running processes

    Returns:
        List of process information dictionaries
    """
    try:
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    except Exception as e:
        logging.error(f"Error getting running processes: {e}")
        return []


def find_processes_by_name(name: str) -> List[Dict[str, Any]]:
    """
    Find processes by name

    Args:
        name: Process name to search for

    Returns:
        List of matching process information
    """
    try:
        matching_processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if name.lower() in proc.info['name'].lower():
                    matching_processes.append(get_process_info(proc.info['pid']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return matching_processes

    except Exception as e:
        logging.error(f"Error finding processes by name '{name}': {e}")
        return []


def run_command(
    command: Sequence[str],
    *,
    allowed_commands: Set[str],
    timeout: int = 30,
) -> Tuple[int, str, str]:
    """
    Run system command and return result

    Args:
        command: Explicit executable and arguments. Shell strings are rejected.
        allowed_commands: Exact executable names permitted by the caller.
        timeout: Command timeout in seconds

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    if isinstance(command, str) or not command:
        return -1, "", "Command must be a non-empty argv sequence"
    argv = list(command)
    if not all(isinstance(item, str) and item for item in argv):
        return -1, "", "Command argv must contain non-empty strings"
    if argv[0] not in allowed_commands:
        return -1, "", f"Command '{argv[0]}' is not allowed"

    process: subprocess.Popen[str] | None = None
    try:
        process = subprocess.Popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr

    except subprocess.TimeoutExpired:
        if process is not None:
            process.kill()
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def is_admin() -> bool:
    """
    Check if running with administrator/root privileges

    Returns:
        True if running as admin/root
    """
    try:
        if sys.platform == 'win32':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


def get_environment_variables(prefix: str = "") -> Dict[str, str]:
    """
    Get environment variables with optional prefix filter

    Args:
        prefix: Optional prefix to filter variables

    Returns:
        Dictionary of environment variables
    """
    try:
        if prefix:
            return {k: v for k, v in os.environ.items() if k.startswith(prefix)}
        else:
            return dict(os.environ)
    except Exception:
        return {}


def set_environment_variable(key: str, value: str) -> bool:
    """
    Set environment variable

    Args:
        key: Environment variable name
        value: Environment variable value

    Returns:
        True if successful
    """
    try:
        os.environ[key] = value
        return True
    except Exception:
        return False
