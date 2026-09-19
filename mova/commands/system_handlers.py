"""
⚙️ System Command Handlers - Shell, Health, and Services Management

Command handlers for system-related operations extracted from monolithic mova.py
with enhanced functionality and comprehensive system integration.
"""

import json
import subprocess
import time
from typing import Any, Dict, Optional, List
from datetime import datetime

from ..cli.utils import make_request, detect_service_name


def handle_shell_command(args: Any) -> bool:
    """
    Handle shell command execution

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        command = args.cmd
        timeout = getattr(args, 'timeout', 30)
        async_exec = getattr(args, 'async', False)

        print(f"🔧 Executing shell command: {command}")
        print(f"⏱️ Timeout: {timeout}s")
        if async_exec:
            print("🔄 Mode: Asynchronous")

        # Prepare command data
        command_data = {
            'command': command,
            'timeout': timeout,
            'async': async_exec,
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        # Send command to server
        response = make_request("POST", "/api/shell", command_data, server=args.server)

        # Handle response
        if response.get('success', False):
            print("✅ Command executed successfully")

            # Display output if available
            if 'output' in response:
                output = response['output']
                if output.strip():
                    print("📤 Output:")
                    print("-" * 40)
                    print(output)
                    print("-" * 40)

            # Display execution info
            if 'execution_time' in response:
                print(f"⏱️ Execution time: {response['execution_time']:.2f}s")

            if 'exit_code' in response:
                exit_code = response['exit_code']
                if exit_code == 0:
                    print(f"✅ Exit code: {exit_code}")
                else:
                    print(f"⚠️ Exit code: {exit_code}")

            if async_exec and 'job_id' in response:
                print(f"🆔 Job ID: {response['job_id']}")
                print("💡 Use this ID to check job status later")

            return True
        else:
            print("❌ Command execution failed")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ Shell command error: {e}")
        return False


def handle_health_command(args: Any) -> bool:
    """
    Handle health check command

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        detailed = getattr(args, 'detailed', False)
        check_services = getattr(args, 'services', False)

        print("🏥 Mova Server Health Check")
        print("-" * 35)

        # Basic health check
        try:
            start_time = time.time()
            response = make_request("GET", "/api/health", server=args.server)
            response_time = (time.time() - start_time) * 1000

            if response.get('status') == 'healthy':
                print("✅ Server Status: Healthy")
                print(f"⚡ Response Time: {response_time:.1f}ms")

                if detailed:
                    _display_detailed_health(response)

                if check_services:
                    _check_service_health(args)

                return True
            else:
                print("❌ Server Status: Unhealthy")
                if 'message' in response:
                    print(f"💥 Issue: {response['message']}")
                return False

        except Exception as e:
            print("❌ Server Status: Offline")
            print(f"💥 Connection Error: {e}")
            print("💡 Make sure the Mova server is running")
            return False

    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def handle_services_command(args: Any) -> bool:
    """
    Handle services management command

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        action = getattr(args, 'services_action', None)

        if action == 'list':
            return _handle_services_list(args)
        elif action == 'enable':
            return _handle_services_enable(args)
        elif action == 'disable':
            return _handle_services_disable(args)
        elif action == 'status':
            return _handle_services_status(args)
        else:
            print(f"❌ Unknown services action: {action}")
            print("💡 Available actions: list, enable, disable, status")
            return False

    except Exception as e:
        print(f"❌ Services command error: {e}")
        return False


def handle_security_command(args: Any) -> bool:
    """
    Handle security management command

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        action = getattr(args, 'security_action', None)

        if action == 'acl':
            return _handle_security_acl(args)
        elif action == 'cors':
            return _handle_security_cors(args)
        else:
            print(f"❌ Unknown security action: {action}")
            print("💡 Available actions: acl, cors")
            return False

    except Exception as e:
        print(f"❌ Security command error: {e}")
        return False


def _display_detailed_health(response: Dict) -> None:
    """Display detailed health information"""
    print("\n📊 Detailed Health Information:")

    # Server info
    if 'server_info' in response:
        server_info = response['server_info']
        print(f"🖥️  Server Version: {server_info.get('version', 'Unknown')}")
        print(f"🐍 Python Version: {server_info.get('python_version', 'Unknown')}")
        print(f"⏰ Uptime: {server_info.get('uptime', 'Unknown')}")

    # System resources
    if 'system_resources' in response:
        resources = response['system_resources']
        print(f"🧠 Memory Usage: {resources.get('memory_percent', 'Unknown')}%")
        print(f"💾 CPU Usage: {resources.get('cpu_percent', 'Unknown')}%")
        print(f"💿 Disk Usage: {resources.get('disk_percent', 'Unknown')}%")

    # Database status
    if 'database' in response:
        db_status = response['database']
        db_icon = "✅" if db_status.get('connected', False) else "❌"
        print(f"{db_icon} Database: {'Connected' if db_status.get('connected', False) else 'Disconnected'}")

    # External services
    if 'external_services' in response:
        ext_services = response['external_services']
        print(f"\n🌐 External Services:")
        for service, status in ext_services.items():
            service_icon = "✅" if status else "❌"
            print(f"  {service_icon} {service}: {'Available' if status else 'Unavailable'}")


def _check_service_health(args: Any) -> None:
    """Check health of individual services"""
    try:
        print(f"\n🔍 Checking Service Health...")

        response = make_request("GET", "/api/services/health", server=args.server)
        services = response.get('services', {})

        if not services:
            print("📭 No services found")
            return

        for service_name, service_info in services.items():
            status = service_info.get('status', 'unknown')
            last_check = service_info.get('last_check', 'Never')

            if status == 'healthy':
                icon = "✅"
            elif status == 'warning':
                icon = "⚠️"
            elif status == 'error':
                icon = "❌"
            else:
                icon = "❓"

            print(f"  {icon} {service_name}: {status.title()} (Last check: {last_check})")

    except Exception as e:
        print(f"⚠️ Service health check failed: {e}")


def _handle_services_list(args: Any) -> bool:
    """Handle services list command"""
    try:
        detailed = getattr(args, 'detailed', False)

        print("📋 Available Services")
        print("-" * 25)

        try:
            # Try to import service manager
            from ...config_manager import ServiceManager

            service_manager = ServiceManager()
            services = service_manager.get_available_services()

            if not services:
                print("📭 No services configured")
                return True

            for service_name, service_info in services.items():
                status = service_info.get('status', 'unknown')
                enabled = service_info.get('enabled', False)

                # Status icons
                status_icon = "✅" if status == 'running' else "❌" if status == 'stopped' else "❓"
                enabled_icon = "🟢" if enabled else "🔴"

                print(f"{status_icon} {service_name}")
                print(f"   Status: {status.title()}")
                print(f"   Enabled: {enabled_icon} {'Yes' if enabled else 'No'}")

                if detailed:
                    print(f"   Type: {service_info.get('type', 'Unknown')}")
                    print(f"   Description: {service_info.get('description', 'No description')}")
                    if 'last_restart' in service_info:
                        print(f"   Last Restart: {service_info['last_restart']}")

                print()

            return True

        except ImportError:
            print("❌ Service manager not available")
            print("💡 This feature requires the service management module")
            return False

    except Exception as e:
        print(f"❌ Services list error: {e}")
        return False


def _handle_services_enable(args: Any) -> bool:
    """Handle service enable command"""
    try:
        service_name = args.service_name

        print(f"🟢 Enabling service: {service_name}")

        # Prepare service data
        service_data = {
            'service': service_name,
            'action': 'enable',
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/services/manage", service_data, server=args.server)

        if response.get('success', False):
            print(f"✅ Service '{service_name}' enabled successfully")
            if 'message' in response:
                print(f"💬 {response['message']}")
            return True
        else:
            print(f"❌ Failed to enable service '{service_name}'")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ Service enable error: {e}")
        return False


def _handle_services_disable(args: Any) -> bool:
    """Handle service disable command"""
    try:
        service_name = args.service_name

        print(f"🔴 Disabling service: {service_name}")

        # Prepare service data
        service_data = {
            'service': service_name,
            'action': 'disable',
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/services/manage", service_data, server=args.server)

        if response.get('success', False):
            print(f"✅ Service '{service_name}' disabled successfully")
            if 'message' in response:
                print(f"💬 {response['message']}")
            return True
        else:
            print(f"❌ Failed to disable service '{service_name}'")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ Service disable error: {e}")
        return False


def _handle_services_status(args: Any) -> bool:
    """Handle service status command"""
    try:
        service_name = getattr(args, 'service_name', None)

        if service_name:
            print(f"📊 Status for service: {service_name}")
        else:
            print("📊 Status for all services")

        print("-" * 30)

        # Prepare status request
        params = {}
        if service_name:
            params['service'] = service_name

        response = make_request("GET", "/api/services/status", params, server=args.server)
        services = response.get('services', {})

        if not services:
            print("📭 No services found")
            return True

        for svc_name, svc_status in services.items():
            status = svc_status.get('status', 'unknown')
            uptime = svc_status.get('uptime', 'Unknown')
            pid = svc_status.get('pid', 'Unknown')

            # Status icon
            if status == 'running':
                icon = "🟢"
            elif status == 'stopped':
                icon = "🔴"
            elif status == 'error':
                icon = "❌"
            else:
                icon = "❓"

            print(f"{icon} {svc_name}")
            print(f"   Status: {status.title()}")
            print(f"   Uptime: {uptime}")
            print(f"   PID: {pid}")

            if 'memory_usage' in svc_status:
                print(f"   Memory: {svc_status['memory_usage']} MB")

            if 'cpu_usage' in svc_status:
                print(f"   CPU: {svc_status['cpu_usage']}%")

            print()

        return True

    except Exception as e:
        print(f"❌ Service status error: {e}")
        return False


def _handle_security_acl(args: Any) -> bool:
    """Handle ACL security management"""
    try:
        acl_action = getattr(args, 'acl_action', None)

        if acl_action == 'list':
            return _handle_acl_list(args)
        elif acl_action == 'add':
            return _handle_acl_add(args)
        else:
            print(f"❌ Unknown ACL action: {acl_action}")
            print("💡 Available actions: list, add")
            return False

    except Exception as e:
        print(f"❌ ACL management error: {e}")
        return False


def _handle_security_cors(args: Any) -> bool:
    """Handle CORS security management"""
    try:
        cors_action = getattr(args, 'cors_action', None)

        if cors_action == 'list':
            return _handle_cors_list(args)
        elif cors_action == 'add':
            return _handle_cors_add(args)
        else:
            print(f"❌ Unknown CORS action: {cors_action}")
            print("💡 Available actions: list, add")
            return False

    except Exception as e:
        print(f"❌ CORS management error: {e}")
        return False


def _handle_acl_list(args: Any) -> bool:
    """Handle ACL rules listing"""
    try:
        print("🛡️ Access Control List Rules")
        print("-" * 35)

        response = make_request("GET", "/api/security/acl", server=args.server)
        rules = response.get('rules', [])

        if not rules:
            print("📭 No ACL rules configured")
            return True

        for i, rule in enumerate(rules, 1):
            ip = rule.get('ip', 'Unknown')
            action = rule.get('action', 'unknown')
            description = rule.get('description', 'No description')

            action_icon = "✅" if action == 'allow' else "❌" if action == 'deny' else "❓"

            print(f"{i}. {action_icon} {ip}")
            print(f"   Action: {action.title()}")
            print(f"   Description: {description}")
            print()

        return True

    except Exception as e:
        print(f"❌ ACL list error: {e}")
        return False


def _handle_acl_add(args: Any) -> bool:
    """Handle adding ACL rule"""
    try:
        ip = args.ip
        action = args.action
        description = getattr(args, 'description', f"ACL rule for {ip}")

        print(f"🛡️ Adding ACL rule")
        print(f"   IP: {ip}")
        print(f"   Action: {action}")
        print(f"   Description: {description}")

        rule_data = {
            'ip': ip,
            'action': action,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/security/acl", rule_data, server=args.server)

        if response.get('success', False):
            print("✅ ACL rule added successfully")
            return True
        else:
            print("❌ Failed to add ACL rule")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ ACL add error: {e}")
        return False


def _handle_cors_list(args: Any) -> bool:
    """Handle CORS policies listing"""
    try:
        print("🌐 CORS Policies")
        print("-" * 20)

        response = make_request("GET", "/api/security/cors", server=args.server)
        policies = response.get('policies', [])

        if not policies:
            print("📭 No CORS policies configured")
            return True

        for i, policy in enumerate(policies, 1):
            origin = policy.get('origin', 'Unknown')
            methods = policy.get('methods', [])
            headers = policy.get('headers', [])

            print(f"{i}. 🌍 {origin}")
            print(f"   Methods: {', '.join(methods) if methods else 'None'}")
            print(f"   Headers: {', '.join(headers) if headers else 'None'}")
            print()

        return True

    except Exception as e:
        print(f"❌ CORS list error: {e}")
        return False


def _handle_cors_add(args: Any) -> bool:
    """Handle adding CORS policy"""
    try:
        origin = args.origin
        methods = getattr(args, 'methods', ['GET', 'POST'])
        headers = getattr(args, 'headers', ['Content-Type'])

        print(f"🌐 Adding CORS policy")
        print(f"   Origin: {origin}")
        print(f"   Methods: {', '.join(methods)}")
        print(f"   Headers: {', '.join(headers)}")

        policy_data = {
            'origin': origin,
            'methods': methods,
            'headers': headers,
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/security/cors", policy_data, server=args.server)

        if response.get('success', False):
            print("✅ CORS policy added successfully")
            return True
        else:
            print("❌ Failed to add CORS policy")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ CORS add error: {e}")
        return False
