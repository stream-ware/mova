"""
🌐 Web Command Handlers - RSS, Watch, and Web Server Management

Command handlers for web-related operations extracted from monolithic mova.py
with enhanced functionality and real-time monitoring capabilities.
"""

import json
import time
import threading
import signal
import sys
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urlparse

from ..cli.utils import make_request, detect_service_name, format_log_output


class WatchMonitor:
    """Real-time monitoring for watch commands"""

    def __init__(self):
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()

    def start(self, watch_func, *args, **kwargs):
        """Start monitoring in separate thread"""
        if self.running:
            return False

        self.running = True
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._monitor_loop,
            args=(watch_func, *args),
            kwargs=kwargs,
            daemon=True
        )
        self.thread.start()
        return True

    def stop(self):
        """Stop monitoring"""
        if not self.running:
            return

        self.running = False
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _monitor_loop(self, watch_func, *args, **kwargs):
        """Main monitoring loop"""
        while self.running and not self.stop_event.is_set():
            try:
                watch_func(*args, **kwargs)
                # Wait with interrupt capability
                if self.stop_event.wait(timeout=kwargs.get('interval', 5)):
                    break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                if self.stop_event.wait(timeout=2):
                    break


# Global watch monitor instance
_watch_monitor = WatchMonitor()


def handle_rss_command(args: Any) -> bool:
    """
    Handle RSS feed management command

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        action = getattr(args, 'rss_action', None)

        if action == 'start':
            return _handle_rss_start(args)
        elif action == 'stop':
            return _handle_rss_stop(args)
        elif action == 'status':
            return _handle_rss_status(args)
        elif action == 'add':
            return _handle_rss_add(args)
        elif action == 'remove':
            return _handle_rss_remove(args)
        elif action == 'list':
            return _handle_rss_list(args)
        elif action == 'fetch':
            return _handle_rss_fetch(args)
        else:
            print(f"❌ Unknown RSS action: {action}")
            print("💡 Available actions: start, stop, status, add, remove, list, fetch")
            return False

    except Exception as e:
        print(f"❌ RSS command error: {e}")
        return False


def handle_watch_command(args: Any) -> bool:
    """
    Handle watch/monitoring command

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        watch_type = getattr(args, 'watch_type', 'logs')
        interval = getattr(args, 'interval', 5)

        print(f"👁️  Starting real-time monitoring: {watch_type}")
        print(f"⏱️  Update interval: {interval}s")
        print("💡 Press Ctrl+C to stop monitoring")
        print("-" * 50)

        # Setup signal handler for graceful exit
        def signal_handler(sig, frame):
            print(f"\n🛑 Stopping monitor...")
            _watch_monitor.stop()
            print("✅ Monitor stopped")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Determine watch function based on type
        if watch_type == 'logs':
            watch_func = _watch_logs
        elif watch_type == 'health':
            watch_func = _watch_health
        elif watch_type == 'services':
            watch_func = _watch_services
        elif watch_type == 'rss':
            watch_func = _watch_rss
        else:
            print(f"❌ Unknown watch type: {watch_type}")
            print("💡 Available types: logs, health, services, rss")
            return False

        # Start monitoring
        success = _watch_monitor.start(watch_func, args, interval=interval)
        if not success:
            print("❌ Failed to start monitoring (already running?)")
            return False

        # Keep main thread alive
        try:
            while _watch_monitor.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            _watch_monitor.stop()

        return True

    except Exception as e:
        print(f"❌ Watch command error: {e}")
        _watch_monitor.stop()
        return False


def handle_server_command(args: Any) -> bool:
    """
    Handle web server management command

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        action = getattr(args, 'server_action', None)

        if action == 'start':
            return _handle_server_start(args)
        elif action == 'stop':
            return _handle_server_stop(args)
        elif action == 'restart':
            return _handle_server_restart(args)
        elif action == 'status':
            return _handle_server_status(args)
        elif action == 'config':
            return _handle_server_config(args)
        else:
            print(f"❌ Unknown server action: {action}")
            print("💡 Available actions: start, stop, restart, status, config")
            return False

    except Exception as e:
        print(f"❌ Server command error: {e}")
        return False


def _handle_rss_start(args: Any) -> bool:
    """Handle RSS server start"""
    try:
        port = getattr(args, 'port', 8095)

        print(f"🚀 Starting RSS server on port {port}")

        start_data = {
            'port': port,
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/rss/start", start_data, server=args.server)

        if response.get('success', False):
            print("✅ RSS server started successfully")
            server_url = response.get('server_url', f'http://localhost:{port}')
            print(f"🌐 RSS server URL: {server_url}")

            if 'feeds_count' in response:
                print(f"📡 Active feeds: {response['feeds_count']}")

            return True
        else:
            print("❌ Failed to start RSS server")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ RSS start error: {e}")
        return False


def _handle_rss_stop(args: Any) -> bool:
    """Handle RSS server stop"""
    try:
        print("🛑 Stopping RSS server")

        stop_data = {
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/rss/stop", stop_data, server=args.server)

        if response.get('success', False):
            print("✅ RSS server stopped successfully")
            return True
        else:
            print("❌ Failed to stop RSS server")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ RSS stop error: {e}")
        return False


def _handle_rss_status(args: Any) -> bool:
    """Handle RSS server status"""
    try:
        print("📊 RSS Server Status")
        print("-" * 25)

        response = make_request("GET", "/api/rss/status", server=args.server)

        status = response.get('status', 'unknown')

        if status == 'running':
            print("🟢 Status: Running")

            if 'port' in response:
                print(f"🌐 Port: {response['port']}")

            if 'uptime' in response:
                print(f"⏱️ Uptime: {response['uptime']}")

            if 'feeds_count' in response:
                print(f"📡 Active feeds: {response['feeds_count']}")

            if 'last_update' in response:
                print(f"🔄 Last update: {response['last_update']}")

            # Display feed details if available
            if 'feeds' in response:
                feeds = response['feeds']
                if feeds:
                    print(f"\n📋 Feed Details:")
                    for i, feed in enumerate(feeds, 1):
                        name = feed.get('name', f'Feed {i}')
                        url = feed.get('url', 'Unknown URL')
                        last_check = feed.get('last_check', 'Never')

                        print(f"  {i}. {name}")
                        print(f"     URL: {url}")
                        print(f"     Last check: {last_check}")

        elif status == 'stopped':
            print("🔴 Status: Stopped")
        else:
            print(f"❓ Status: {status}")

        return True

    except Exception as e:
        print(f"❌ RSS status error: {e}")
        return False


def _handle_rss_add(args: Any) -> bool:
    """Handle adding RSS feed"""
    try:
        name = args.feed_name
        url = args.feed_url

        print(f"➕ Adding RSS feed: {name}")
        print(f"🔗 URL: {url}")

        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            print("❌ Invalid URL format")
            return False

        feed_data = {
            'name': name,
            'url': url,
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/rss/feeds", feed_data, server=args.server)

        if response.get('success', False):
            print("✅ RSS feed added successfully")

            if 'feed_id' in response:
                print(f"🆔 Feed ID: {response['feed_id']}")

            return True
        else:
            print("❌ Failed to add RSS feed")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ RSS add error: {e}")
        return False


def _handle_rss_remove(args: Any) -> bool:
    """Handle removing RSS feed"""
    try:
        feed_identifier = args.feed_id

        print(f"➖ Removing RSS feed: {feed_identifier}")

        remove_data = {
            'feed_id': feed_identifier,
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("DELETE", f"/api/rss/feeds/{feed_identifier}", remove_data, server=args.server)

        if response.get('success', False):
            print("✅ RSS feed removed successfully")
            return True
        else:
            print("❌ Failed to remove RSS feed")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ RSS remove error: {e}")
        return False


def _handle_rss_list(args: Any) -> bool:
    """Handle listing RSS feeds"""
    try:
        detailed = getattr(args, 'detailed', False)

        print("📋 RSS Feeds")
        print("-" * 15)

        response = make_request("GET", "/api/rss/feeds", server=args.server)
        feeds = response.get('feeds', [])

        if not feeds:
            print("📭 No RSS feeds configured")
            return True

        for i, feed in enumerate(feeds, 1):
            name = feed.get('name', f'Feed {i}')
            url = feed.get('url', 'Unknown URL')
            status = feed.get('status', 'unknown')

            # Status icon
            if status == 'active':
                icon = "🟢"
            elif status == 'error':
                icon = "❌"
            elif status == 'disabled':
                icon = "🔴"
            else:
                icon = "❓"

            print(f"{i}. {icon} {name}")

            if detailed:
                print(f"   URL: {url}")
                print(f"   Status: {status}")

                if 'last_check' in feed:
                    print(f"   Last check: {feed['last_check']}")

                if 'items_count' in feed:
                    print(f"   Items: {feed['items_count']}")

                if 'last_error' in feed and feed['last_error']:
                    print(f"   Last error: {feed['last_error']}")

                print()
            else:
                print(f"   {url}")

        return True

    except Exception as e:
        print(f"❌ RSS list error: {e}")
        return False


def _handle_rss_fetch(args: Any) -> bool:
    """Handle fetching RSS feeds"""
    try:
        feed_id = getattr(args, 'feed_id', None)

        if feed_id:
            print(f"🔄 Fetching RSS feed: {feed_id}")
        else:
            print("🔄 Fetching all RSS feeds")

        fetch_data = {
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        if feed_id:
            fetch_data['feed_id'] = feed_id

        endpoint = f"/api/rss/fetch/{feed_id}" if feed_id else "/api/rss/fetch"
        response = make_request("POST", endpoint, fetch_data, server=args.server)

        if response.get('success', False):
            print("✅ RSS feeds fetched successfully")

            if 'feeds_updated' in response:
                print(f"📊 Feeds updated: {response['feeds_updated']}")

            if 'new_items' in response:
                print(f"📄 New items: {response['new_items']}")

            return True
        else:
            print("❌ Failed to fetch RSS feeds")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ RSS fetch error: {e}")
        return False


def _handle_server_start(args: Any) -> bool:
    """Handle web server start"""
    try:
        port = getattr(args, 'port', 8094)
        host = getattr(args, 'host', 'localhost')

        print(f"🚀 Starting web server")
        print(f"🌐 Host: {host}")
        print(f"🔌 Port: {port}")

        start_data = {
            'host': host,
            'port': port,
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/server/start", start_data, server=args.server)

        if response.get('success', False):
            print("✅ Web server started successfully")
            server_url = response.get('server_url', f'http://{host}:{port}')
            print(f"🌍 Server URL: {server_url}")
            return True
        else:
            print("❌ Failed to start web server")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ Server start error: {e}")
        return False


def _handle_server_stop(args: Any) -> bool:
    """Handle web server stop"""
    try:
        print("🛑 Stopping web server")

        stop_data = {
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/server/stop", stop_data, server=args.server)

        if response.get('success', False):
            print("✅ Web server stopped successfully")
            return True
        else:
            print("❌ Failed to stop web server")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ Server stop error: {e}")
        return False


def _handle_server_restart(args: Any) -> bool:
    """Handle web server restart"""
    try:
        print("🔄 Restarting web server")

        # Stop first
        if not _handle_server_stop(args):
            print("⚠️ Stop failed, attempting restart anyway")

        # Wait a moment
        time.sleep(2)

        # Start again
        return _handle_server_start(args)

    except Exception as e:
        print(f"❌ Server restart error: {e}")
        return False


def _handle_server_status(args: Any) -> bool:
    """Handle web server status"""
    try:
        print("📊 Web Server Status")
        print("-" * 25)

        response = make_request("GET", "/api/server/status", server=args.server)

        status = response.get('status', 'unknown')

        if status == 'running':
            print("🟢 Status: Running")

            if 'host' in response:
                print(f"🌐 Host: {response['host']}")

            if 'port' in response:
                print(f"🔌 Port: {response['port']}")

            if 'uptime' in response:
                print(f"⏱️ Uptime: {response['uptime']}")

            if 'requests_count' in response:
                print(f"📊 Requests served: {response['requests_count']}")

            if 'active_connections' in response:
                print(f"🔗 Active connections: {response['active_connections']}")

        elif status == 'stopped':
            print("🔴 Status: Stopped")
        else:
            print(f"❓ Status: {status}")

        return True

    except Exception as e:
        print(f"❌ Server status error: {e}")
        return False


def _handle_server_config(args: Any) -> bool:
    """Handle web server configuration"""
    try:
        config_action = getattr(args, 'config_action', 'show')

        if config_action == 'show':
            print("⚙️ Web Server Configuration")
            print("-" * 35)

            response = make_request("GET", "/api/server/config", server=args.server)
            config = response.get('config', {})

            if not config:
                print("📭 No configuration available")
                return True

            for key, value in config.items():
                print(f"{key}: {value}")

            return True
        else:
            print(f"❌ Unknown config action: {config_action}")
            return False

    except Exception as e:
        print(f"❌ Server config error: {e}")
        return False


def _watch_logs(args: Any, **kwargs) -> None:
    """Watch logs in real-time"""
    try:
        # Clear screen
        print("\033[2J\033[H", end="")

        print(f"👁️  Watching Logs - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)

        response = make_request("GET", "/api/logs/recent", {'limit': 10}, server=args.server)
        logs = response.get('logs', [])

        if logs:
            for log_entry in logs:
                formatted_log = format_log_output(log_entry)
                print(formatted_log)
        else:
            print("📭 No recent logs")

    except Exception as e:
        print(f"❌ Watch logs error: {e}")


def _watch_health(args: Any, **kwargs) -> None:
    """Watch system health in real-time"""
    try:
        # Clear screen
        print("\033[2J\033[H", end="")

        print(f"🏥 System Health - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 40)

        response = make_request("GET", "/api/health", server=args.server)

        if response.get('status') == 'healthy':
            print("✅ Overall Status: Healthy")

            # Show resource usage if available
            if 'system_resources' in response:
                resources = response['system_resources']
                cpu = resources.get('cpu_percent', 'N/A')
                memory = resources.get('memory_percent', 'N/A')
                disk = resources.get('disk_percent', 'N/A')

                print(f"💾 CPU: {cpu}%")
                print(f"🧠 Memory: {memory}%")
                print(f"💿 Disk: {disk}%")

        else:
            print("❌ Overall Status: Unhealthy")
            if 'message' in response:
                print(f"💥 Issue: {response['message']}")

    except Exception as e:
        print(f"❌ Watch health error: {e}")


def _watch_services(args: Any, **kwargs) -> None:
    """Watch services in real-time"""
    try:
        # Clear screen
        print("\033[2J\033[H", end="")

        print(f"⚙️  Services Status - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 45)

        response = make_request("GET", "/api/services/status", server=args.server)
        services = response.get('services', {})

        if services:
            for service_name, service_info in services.items():
                status = service_info.get('status', 'unknown')

                if status == 'running':
                    icon = "🟢"
                elif status == 'stopped':
                    icon = "🔴"
                elif status == 'error':
                    icon = "❌"
                else:
                    icon = "❓"

                print(f"{icon} {service_name}: {status.title()}")
        else:
            print("📭 No services found")

    except Exception as e:
        print(f"❌ Watch services error: {e}")


def _watch_rss(args: Any, **kwargs) -> None:
    """Watch RSS feeds in real-time"""
    try:
        # Clear screen
        print("\033[2J\033[H", end="")

        print(f"📡 RSS Feeds Status - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)

        response = make_request("GET", "/api/rss/status", server=args.server)

        # Server status
        server_status = response.get('status', 'unknown')
        if server_status == 'running':
            print("🟢 RSS Server: Running")
        else:
            print("🔴 RSS Server: Stopped")

        # Feed status
        if 'feeds' in response:
            feeds = response['feeds']
            if feeds:
                print(f"\n📋 Feeds ({len(feeds)}):")
                for feed in feeds:
                    name = feed.get('name', 'Unknown')
                    status = feed.get('status', 'unknown')
                    last_update = feed.get('last_update', 'Never')

                    if status == 'active':
                        icon = "🟢"
                    elif status == 'error':
                        icon = "❌"
                    else:
                        icon = "❓"

                    print(f"  {icon} {name} (Updated: {last_update})")
            else:
                print("\n📭 No feeds configured")

    except Exception as e:
        print(f"❌ Watch RSS error: {e}")
