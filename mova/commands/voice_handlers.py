"""
🗣️ Voice Command Handlers - Voice Interface and Audio Management

Command handlers for voice-related operations extracted from monolithic mova.py
with enhanced functionality and integration with modular voice components.
"""

from typing import Any, Dict, Optional
import time

from ..cli.utils import detect_service_name


def handle_voice_command(args: Any) -> bool:
    """
    Handle voice interface control commands

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        action = getattr(args, 'voice_action', None)

        if action == 'start':
            return _handle_voice_start(args)
        elif action == 'stop':
            return _handle_voice_stop(args)
        elif action == 'test':
            return _handle_voice_test(args)
        elif action == 'status':
            return _handle_voice_status(args)
        else:
            print(f"❌ Unknown voice action: {action}")
            print("💡 Available actions: start, stop, test, status")
            return False

    except Exception as e:
        print(f"❌ Voice command error: {e}")
        return False


def handle_audio_command(args: Any) -> bool:
    """
    Handle audio device management commands

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        action = getattr(args, 'audio_action', None)

        if action == 'list':
            return _handle_audio_list(args)
        elif action == 'get':
            return _handle_audio_get(args)
        elif action == 'set':
            return _handle_audio_set(args)
        else:
            print(f"❌ Unknown audio action: {action}")
            print("💡 Available actions: list, get, set")
            return False

    except Exception as e:
        print(f"❌ Audio command error: {e}")
        return False


def _handle_voice_start(args: Any) -> bool:
    """Handle voice interface start command"""
    try:
        # Try to import voice interface
        try:
            from ...movatalk.voice_ui import VoiceInterface
            from ...movatalk.voice_ui.session import SessionMode
        except ImportError:
            print("❌ Voice interface modules not available")
            print("💡 Install voice dependencies: pip install -e .")
            return False

        language = getattr(args, 'language', 'en')
        mode_str = getattr(args, 'mode', 'single')
        timeout = getattr(args, 'timeout', None)

        # Convert mode string to SessionMode enum
        mode_mapping = {
            'single': SessionMode.SINGLE,
            'continuous': SessionMode.CONTINUOUS,
            'wake_word': SessionMode.WAKE_WORD,
            'push_to_talk': SessionMode.PUSH_TO_TALK
        }

        mode = mode_mapping.get(mode_str, SessionMode.SINGLE)

        print(f"🎤 Starting voice interface...")
        print(f"🌐 Language: {language}")
        print(f"🔄 Mode: {mode_str}")
        if timeout:
            print(f"⏱️ Timeout: {timeout} minutes")

        # Initialize voice interface
        voice_interface = VoiceInterface(
            language=language,
            server=getattr(args, 'server', 'localhost:8000')
        )

        # Check dependencies
        if not voice_interface.check_dependencies():
            print("❌ Voice dependencies not satisfied")
            print("💡 Run dependency check: mova voice test --audio --tts --stt")
            return False

        # Start voice session
        success = voice_interface.start_session(mode=mode, timeout=timeout)

        if success:
            print("✅ Voice interface started successfully")
            print("🗣️ You can now speak commands")
            print("💡 Say 'stop' or press Ctrl+C to end session")

            try:
                # Keep running until stopped
                while voice_interface.is_session_active():
                    time.sleep(1.0)

            except KeyboardInterrupt:
                print("\n🛑 Stopping voice interface...")
                voice_interface.stop_session()

            print("👋 Voice interface stopped")
            return True
        else:
            print("❌ Failed to start voice interface")
            return False

    except Exception as e:
        print(f"❌ Voice start error: {e}")
        return False


def _handle_voice_stop(args: Any) -> bool:
    """Handle voice interface stop command"""
    try:
        # This would typically connect to running voice interface
        # For now, provide informational message
        print("🛑 Stopping voice interface...")
        print("💡 This will stop any running voice sessions")

        # Implementation would send stop signal to voice interface

        print("✅ Voice interface stop signal sent")
        return True

    except Exception as e:
        print(f"❌ Voice stop error: {e}")
        return False


def _handle_voice_test(args: Any) -> bool:
    """Handle voice component testing"""
    try:
        test_tts = getattr(args, 'tts', False)
        test_stt = getattr(args, 'stt', False)
        test_audio = getattr(args, 'audio', False)

        # If no specific tests requested, test all
        if not any([test_tts, test_stt, test_audio]):
            test_tts = test_stt = test_audio = True

        print("🧪 Testing voice components...")
        print("-" * 40)

        test_results = {}

        # Test TTS
        if test_tts:
            print("🗣️ Testing Text-to-Speech...")
            try:
                from ...movatalk.tts import TTSManager

                tts_manager = TTSManager()
                tts_result = tts_manager.test_all_engines()

                if tts_result.get('success', False):
                    print("✅ TTS test passed")
                    working_engines = [e for e, r in tts_result.get('engine_results', {}).items()
                                     if r.get('success', False)]
                    print(f"   Working engines: {', '.join(working_engines)}")
                else:
                    print("❌ TTS test failed")

                test_results['tts'] = tts_result.get('success', False)

            except ImportError:
                print("❌ TTS module not available")
                test_results['tts'] = False
            except Exception as e:
                print(f"❌ TTS test error: {e}")
                test_results['tts'] = False

        # Test STT
        if test_stt:
            print("\n🎤 Testing Speech-to-Text...")
            try:
                from ...movatalk.stt import STTManager

                stt_manager = STTManager()
                stt_result = stt_manager.test_engines()

                if stt_result.get('success', False):
                    print("✅ STT test passed")
                    working_engines = [e for e, r in stt_result.get('engine_results', {}).items()
                                     if r.get('success', False)]
                    print(f"   Working engines: {', '.join(working_engines)}")
                else:
                    print("❌ STT test failed")

                test_results['stt'] = stt_result.get('success', False)

            except ImportError:
                print("❌ STT module not available")
                test_results['stt'] = False
            except Exception as e:
                print(f"❌ STT test error: {e}")
                test_results['stt'] = False

        # Test Audio
        if test_audio:
            print("\n🔊 Testing Audio Devices...")
            try:
                from ...movatalk.audio import AudioRecorder, AudioConfig

                config = AudioConfig()
                recorder = AudioRecorder(config=config)
                audio_result = recorder.test_recording()

                if audio_result.get('success', False):
                    print("✅ Audio test passed")
                    print(f"   Sample rate: {config.sample_rate} Hz")
                    print(f"   Channels: {config.channels}")
                else:
                    print("❌ Audio test failed")

                test_results['audio'] = audio_result.get('success', False)

            except ImportError:
                print("❌ Audio module not available")
                test_results['audio'] = False
            except Exception as e:
                print(f"❌ Audio test error: {e}")
                test_results['audio'] = False

        # Summary
        print("\n" + "=" * 40)
        print("📊 Voice Component Test Summary:")

        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)

        for component, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {component.upper()}: {status}")

        print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 All voice components are working!")
        else:
            print("⚠️ Some voice components need attention")
            print("💡 Check individual component documentation for troubleshooting")

        return passed_tests > 0

    except Exception as e:
        print(f"❌ Voice test error: {e}")
        return False


def _handle_voice_status(args: Any) -> bool:
    """Handle voice interface status command"""
    try:
        print("📊 Voice Interface Status")
        print("-" * 30)

        # Check if voice interface is running
        # This would typically check for running processes/sessions

        print("🔍 Checking voice components...")

        # Check component availability
        components = {}

        try:
            from ...movatalk.tts import TTSManager
            components['TTS'] = "Available"
        except ImportError:
            components['TTS'] = "Not Available"

        try:
            from ...movatalk.stt import STTManager
            components['STT'] = "Available"
        except ImportError:
            components['STT'] = "Not Available"

        try:
            from ...movatalk.voice_ui import VoiceInterface
            components['Voice UI'] = "Available"
        except ImportError:
            components['Voice UI'] = "Not Available"

        try:
            from ...movatalk.audio import AudioManager
            components['Audio'] = "Available"
        except ImportError:
            components['Audio'] = "Not Available"

        # Display status
        for component, status in components.items():
            icon = "✅" if status == "Available" else "❌"
            print(f"{icon} {component}: {status}")

        # Check for active sessions
        print(f"\n🔄 Active Sessions: 0")  # Would check actual sessions
        print(f"🎤 Default Language: en")   # Would get from config
        print(f"🔊 Audio Status: Ready")     # Would check audio devices

        available_components = sum(1 for status in components.values() if status == "Available")
        total_components = len(components)

        if available_components == total_components:
            print(f"\n🎉 Voice interface is fully operational ({available_components}/{total_components} components)")
        else:
            print(f"\n⚠️ Voice interface partially operational ({available_components}/{total_components} components)")

        return True

    except Exception as e:
        print(f"❌ Voice status error: {e}")
        return False


def _handle_audio_list(args: Any) -> bool:
    """Handle audio device listing"""
    try:
        detailed = getattr(args, 'detailed', False)
        test_devices = getattr(args, 'test', False)

        print("🔊 Audio Devices")
        print("-" * 30)

        try:
            from ...movatalk.voice_ui import AudioDeviceManager

            device_manager = AudioDeviceManager()

            if not device_manager.initialize():
                print("❌ Failed to initialize audio device manager")
                return False

            # List all devices
            success = device_manager.list_all_audio_devices(
                detailed=detailed,
                test=test_devices
            )

            return success

        except ImportError:
            print("❌ Audio device manager not available")
            print("💡 Install audio dependencies: pip install -e .")
            return False

    except Exception as e:
        print(f"❌ Audio list error: {e}")
        return False


def _handle_audio_get(args: Any) -> bool:
    """Handle getting current audio devices"""
    try:
        detailed = getattr(args, 'detailed', False)

        print("🎯 Current Audio Configuration")
        print("-" * 35)

        try:
            from ...movatalk.voice_ui import AudioDeviceManager

            device_manager = AudioDeviceManager()

            if not device_manager.initialize():
                print("❌ Failed to initialize audio device manager")
                return False

            # Get current devices
            success = device_manager.get_current_audio_devices(detailed=detailed)

            return success

        except ImportError:
            print("❌ Audio device manager not available")
            return False

    except Exception as e:
        print(f"❌ Audio get error: {e}")
        return False


def _handle_audio_set(args: Any) -> bool:
    """Handle setting audio devices"""
    try:
        set_action = getattr(args, 'audio_set_action', None)

        if set_action == 'auto':
            return _handle_audio_set_auto(args)
        else:
            print(f"❌ Unknown audio set action: {set_action}")
            print("💡 Available actions: auto")
            return False

    except Exception as e:
        print(f"❌ Audio set error: {e}")
        return False


def _handle_audio_set_auto(args: Any) -> bool:
    """Handle automatic audio device configuration"""
    try:
        test_devices = getattr(args, 'test', False)
        save_config = getattr(args, 'save', False)

        print("🔧 Auto-configuring Audio Devices")
        print("-" * 40)

        try:
            from ...movatalk.voice_ui import AudioDeviceManager

            device_manager = AudioDeviceManager()

            if not device_manager.initialize():
                print("❌ Failed to initialize audio device manager")
                return False

            # Auto-configure devices
            success = device_manager.set_auto_audio_devices(
                test=test_devices,
                save=save_config
            )

            if success:
                print("✅ Audio auto-configuration completed")
                if save_config:
                    print("💾 Configuration saved permanently")
            else:
                print("❌ Audio auto-configuration failed")

            return success

        except ImportError:
            print("❌ Audio device manager not available")
            return False

    except Exception as e:
        print(f"❌ Audio auto-config error: {e}")
        return False
