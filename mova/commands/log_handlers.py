"""
📊 Log Command Handlers - Professional Logging Operations

Command handlers for log-related operations extracted from monolithic mova.py
with enhanced functionality and modular architecture.
"""

import json
import time
import os
from datetime import datetime
from typing import Any, Dict, Optional

from ..cli.utils import (
    make_request,
    detect_service_name,
    parse_time_duration,
    format_log_entry,
    prepare_log_for_tts,
    should_speak_message
)


def handle_list_command(args: Any) -> bool:
    """
    Handle list command for retrieving logs

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        # Prepare request parameters
        params = {
            'level': args.level,
            'limit': args.limit
        }

        # Add service filter if specified
        if hasattr(args, 'service') and args.service:
            params['service'] = args.service
        else:
            # Auto-detect service name
            params['service'] = detect_service_name()

        # Add time filter if specified
        if hasattr(args, 'last') and args.last:
            duration_minutes = parse_time_duration(args.last)
            if duration_minutes:
                params['since'] = duration_minutes

        # Make request to server
        response = make_request("GET", "/api/logs", params, server=args.server)
        logs = response.get('logs', [])

        if not logs:
            print("📭 No logs found matching criteria")
            return True

        # Format output based on requested format
        format_type = getattr(args, 'format', 'standard')

        if format_type == 'json':
            print(json.dumps(logs, indent=2, ensure_ascii=False))
        elif format_type == 'ndjson':
            for log in logs:
                print(json.dumps(log, ensure_ascii=False, separators=(',', ':')))
        else:
            # Standard, compact, or detailed format
            for log in logs:
                formatted_log = format_log_entry(log, format_type)
                print(formatted_log)

        # TTS output if requested
        if hasattr(args, 'tts') and args.tts:
            _handle_tts_output(logs, args)

        print(f"\n📊 Displayed {len(logs)} logs")
        return True

    except Exception as e:
        print(f"❌ Error retrieving logs: {e}")
        return False


def handle_watch_command(args: Any) -> bool:
    """
    Handle watch command for real-time log monitoring

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        print(f"📖 Mova Log Reader - Level: {args.level} | Mode: WATCH")
        print(f"🔄 Refresh interval: {args.interval}s")
        if hasattr(args, 'service') and args.service:
            print(f"🏷️  Service filter: {args.service}")
        print("Press Ctrl+C to stop")
        print("-" * 80)

        last_timestamp = None
        tts_message_cache = {}
        tts_cache_timeout = 300  # 5 minutes

        # Initialize TTS if requested
        tts_interface = None
        if hasattr(args, 'tts') and args.tts:
            tts_interface = _initialize_tts_interface()

        while True:
            try:
                # Clear screen (optional)
                if hasattr(os, 'system'):
                    os.system('clear' if os.name == 'posix' else 'cls')

                print(f"📖 Mova Log Reader - Level: {args.level} | Mode: WATCH")
                print(f"⏰ Last update: {datetime.now().strftime('%H:%M:%S')}")
                if hasattr(args, 'service') and args.service:
                    print(f"🏷️  Service: {args.service}")
                print("-" * 80)

                # Fetch logs
                count, new_timestamp = _fetch_and_display_logs(args, last_timestamp, tts_interface, tts_message_cache, tts_cache_timeout)

                if new_timestamp:
                    last_timestamp = new_timestamp

                print(f"\n📊 Found {count} logs")
                print(f"🔄 Next update in {args.interval}s... (Ctrl+C to stop)")

                time.sleep(args.interval)

            except KeyboardInterrupt:
                print(f"\n👋 Stopped log monitoring")
                break

        return True

    except Exception as e:
        print(f"❌ Error in watch mode: {e}")
        return False


def handle_info_command(args: Any) -> bool:
    """
    Handle info command for sending info logs

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        # Prepare log data
        log_data = {
            'level': 'info',
            'message': args.message,
            'service': getattr(args, 'service', None) or detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        # Send log to server
        response = make_request("POST", "/api/logs", log_data, server=args.server)

        print(f"✅ Info log sent successfully")
        print(f"📝 Message: {args.message}")
        print(f"🏷️  Service: {log_data['service']}")

        return True

    except Exception as e:
        print(f"❌ Error sending info log: {e}")
        return False


def handle_warning_command(args: Any) -> bool:
    """
    Handle warning command for sending warning logs

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        # Prepare log data
        log_data = {
            'level': 'warning',
            'message': args.message,
            'service': getattr(args, 'service', None) or detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        # Add MQTT configuration if provided
        if hasattr(args, 'mqtt_broker') and args.mqtt_broker:
            log_data['mqtt_broker'] = args.mqtt_broker

        if hasattr(args, 'mqtt_topic') and args.mqtt_topic:
            log_data['mqtt_topic'] = args.mqtt_topic

        # Send log to server
        response = make_request("POST", "/api/logs", log_data, server=args.server)

        print(f"⚠️  Warning log sent successfully")
        print(f"📝 Message: {args.message}")
        print(f"🏷️  Service: {log_data['service']}")

        if 'mqtt_broker' in log_data:
            print(f"📡 MQTT Broker: {log_data['mqtt_broker']}")
        if 'mqtt_topic' in log_data:
            print(f"📢 MQTT Topic: {log_data['mqtt_topic']}")

        return True

    except Exception as e:
        print(f"❌ Error sending warning log: {e}")
        return False


def handle_error_command(args: Any) -> bool:
    """
    Handle error command for sending error logs

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        # Prepare log data
        log_data = {
            'level': 'error',
            'message': args.message,
            'service': getattr(args, 'service', None) or detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        # Send log to server
        response = make_request("POST", "/api/logs", log_data, server=args.server)

        print(f"🔴 Error log sent successfully")
        print(f"📝 Message: {args.message}")
        print(f"🏷️  Service: {log_data['service']}")

        return True

    except Exception as e:
        print(f"❌ Error sending error log: {e}")
        return False


def _fetch_and_display_logs(args: Any, since_timestamp: Optional[str] = None,
                           tts_interface: Optional[Any] = None,
                           tts_message_cache: Optional[Dict] = None,
                           tts_cache_timeout: int = 300) -> tuple:
    """
    Fetch and display logs with optional TTS

    Args:
        args: Command arguments
        since_timestamp: Timestamp for filtering new logs
        tts_interface: TTS interface for voice output
        tts_message_cache: Cache for TTS deduplication
        tts_cache_timeout: TTS cache timeout

    Returns:
        Tuple of (log_count, latest_timestamp)
    """
    try:
        # Prepare request parameters
        params = {
            'level': args.level,
            'limit': getattr(args, 'limit', 20)
        }

        # Add service filter
        if hasattr(args, 'service') and args.service:
            params['service'] = args.service

        # Add time filter
        if hasattr(args, 'last') and args.last:
            duration_minutes = parse_time_duration(args.last)
            if duration_minutes:
                params['since'] = duration_minutes
        elif since_timestamp:
            params['since_timestamp'] = since_timestamp

        # Make request
        response = make_request("GET", "/api/logs", params, server=args.server)
        logs = response.get('logs', [])

        if not logs:
            return 0, None

        # Find latest timestamp
        latest_timestamp = None
        for log in logs:
            log_timestamp = log.get('timestamp')
            if log_timestamp and (not latest_timestamp or log_timestamp > latest_timestamp):
                latest_timestamp = log_timestamp

        # Display logs
        format_type = getattr(args, 'format', 'standard')

        for log in logs:
            formatted_log = format_log_entry(log, format_type)
            print(formatted_log)

            # TTS output
            if tts_interface and hasattr(args, 'tts') and args.tts:
                try:
                    tts_text = prepare_log_for_tts(log)
                    if tts_text and tts_message_cache is not None:
                        if should_speak_message(tts_text, tts_message_cache, tts_cache_timeout):
                            print(f"🗣️  TTS: {tts_text[:50]}{'...' if len(tts_text) > 50 else ''}")
                            tts_interface.speak(tts_text)
                            time.sleep(0.5)
                except Exception as e:
                    print(f"❌ TTS Error: {e}")

        return len(logs), latest_timestamp

    except Exception as e:
        print(f"❌ Error fetching logs: {e}")
        return 0, None


def _handle_tts_output(logs: list, args: Any):
    """
    Handle TTS output for logs

    Args:
        logs: List of log entries
        args: Command arguments
    """
    try:
        tts_interface = _initialize_tts_interface()

        if tts_interface:
            # Create summary for multiple logs
            if len(logs) > 1:
                summary = f"Found {len(logs)} log entries of level {args.level}"
                if hasattr(args, 'service') and args.service:
                    summary += f" for service {args.service}"

                tts_interface.speak(summary)
                time.sleep(1.0)

            # Read individual logs (limit to prevent overload)
            tts_cache = {}
            for log in logs[:5]:  # Limit to first 5 logs
                tts_text = prepare_log_for_tts(log)
                if tts_text and should_speak_message(tts_text, tts_cache, 60):
                    tts_interface.speak(tts_text)
                    time.sleep(0.5)

    except Exception as e:
        print(f"❌ TTS Error: {e}")


def _initialize_tts_interface():
    """
    Initialize TTS interface for voice output

    Returns:
        TTS interface or None
    """
    try:
        # Try to import and initialize TTS
        from ...movatalk.tts import TTSManager

        tts_manager = TTSManager()
        if tts_manager.initialize():
            return tts_manager

        return None

    except ImportError:
        print("⚠️ TTS not available - voice output disabled")
        return None
    except Exception as e:
        print(f"⚠️ TTS initialization failed: {e}")
        return None
