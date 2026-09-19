"""
Unit Tests for Mova Core Components
Tests for basic communication, logging, and configuration functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from mova.communication.client import MovaClient
from mova.communication.server import MovaServer
from mova.mova_logging.logger import MovaLogger
from mova.config.manager import ConfigManager
from mova.base import MovaComponent
from mova.security.acl_manager import ACLManager, SecurityLevel, SecurityPolicy
from mova.utils.helpers import format_timestamp, parse_duration


class TestMovaClient:
    """Tests for MovaClient communication"""

    @pytest.fixture
    def client(self):
        return MovaClient(base_url="http://localhost:8080")

    def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.base_url == "http://localhost:8080"
        assert client.session is not None

    def test_client_get_request(self, client):
        """Test GET request functionality"""
        response = Mock(content=b"{}", status_code=200)
        response.json.return_value = {"status": "ok"}
        with patch.object(client.session, "get", return_value=response) as mock_get:
            result = client.get("/test")
        assert result == {"status": "ok"}
        mock_get.assert_called_once()

    def test_client_post_request(self, client):
        """Test POST request functionality"""
        response = Mock(content=b"{}", status_code=201)
        response.json.return_value = {"created": True}
        with patch.object(client.session, "post", return_value=response) as mock_post:
            result = client.post("/create", {"data": "test"})
        assert result == {"created": True}
        mock_post.assert_called_once()


class TestMovaLogger:
    """Tests for MovaLogger"""

    def test_logger_initialization(self):
        """Test logger initialization"""
        logger = MovaLogger("test_component")
        assert logger.name == "test_component"
        assert logger.logger is not None

    def test_logger_info_message(self):
        """Test info level logging"""
        logger = MovaLogger("test")

        with patch.object(logger.logger, 'info') as mock_info:
            logger.info("Test message")
            record = mock_info.call_args.args[0]
            assert '"message": "Test message"' in record

    def test_logger_error_message(self):
        """Test error level logging"""
        logger = MovaLogger("test")

        with patch.object(logger.logger, 'error') as mock_error:
            logger.error("Error message")
            record = mock_error.call_args.args[0]
            assert '"message": "Error message"' in record


class TestConfigManager:
    """Tests for ConfigManager"""

    def test_config_manager_initialization(self):
        """Test config manager initialization"""
        config = ConfigManager()
        assert config is not None

    def test_get_config_value(self):
        """Test getting configuration values"""
        with patch.dict('os.environ', {'MOVA_TEST_VAR': 'test_value'}):
            config = ConfigManager()
        assert config.get('test.var') == 'test_value'

    def test_get_config_default(self):
        """Test getting default values"""
        config = ConfigManager()
        value = config.get('NON_EXISTENT_VAR', 'default_value')
        assert value == 'default_value'


class TestMovaComponent:
    """Tests for MovaComponent base class"""

    class TestComponent(MovaComponent):
        """Test implementation of MovaComponent"""

        async def initialize(self, config=None):
            self._config = config or {}
            self._initialized = True
            return True

        async def start(self):
            self._running = True
            return True

        async def stop(self):
            self._running = False
            return True

        def health_check(self):
            return {"status": "healthy", "details": "Test component"}

        def get_capabilities(self):
            return ["test"]

    def test_component_initialization(self):
        """Test component initialization"""
        component = self.TestComponent("test_component")
        assert component.name == "test_component"
        assert hasattr(component, 'logger')
        assert isinstance(component.config, dict)

    @pytest.mark.asyncio
    async def test_component_start_stop(self):
        """Test component lifecycle"""
        component = self.TestComponent("test")

        await component.start()
        assert component.is_running is True

        await component.stop()
        assert component.is_running is False


class TestMovaUtils:
    """Tests for Mova utility functions"""

    def test_format_timestamp(self):
        """Test timestamp formatting"""
        from datetime import datetime
        dt = datetime(2024, 1, 1, 12, 0, 0)

        formatted = format_timestamp(dt)
        assert isinstance(formatted, str)
        assert "2024" in formatted

    def test_parse_duration_seconds(self):
        """Test duration parsing - seconds"""
        duration = parse_duration("30s")
        assert duration == 30.0

    def test_parse_duration_minutes(self):
        """Test duration parsing - minutes"""
        duration = parse_duration("5m")
        assert duration == 300.0

    def test_parse_duration_hours(self):
        """Test duration parsing - hours"""
        duration = parse_duration("2h")
        assert duration == 7200.0

    def test_parse_duration_invalid(self):
        """Test invalid duration parsing"""
        duration = parse_duration("invalid")
        assert duration == 0.0


class TestACLManager:
    """Tests for ACL Manager"""

    @pytest.fixture
    def acl_manager(self):
        """ACL Manager instance"""
        return ACLManager()

    def test_acl_manager_initialization(self, acl_manager):
        """Test ACL manager initialization"""
        assert acl_manager is not None
        assert len(acl_manager.security_policies) > 0
        assert "restricted" in acl_manager.security_policies

    def test_validate_allowed_command(self, acl_manager):
        """Test validating allowed command"""
        allowed, reason = acl_manager.validate_command("echo hello", "test_user")
        assert allowed is True
        assert "allowed" in reason.lower()

    def test_validate_forbidden_command(self, acl_manager):
        """Test validating forbidden command"""
        allowed, reason = acl_manager.validate_command("rm -rf /", "test_user")
        assert allowed is False
        assert "forbidden" in reason.lower()

    def test_validate_unknown_command(self, acl_manager):
        """Test validating unknown command"""
        allowed, reason = acl_manager.validate_command("unknown_cmd", "test_user")
        assert allowed is False
        assert "not in allowed" in reason.lower()

    def test_add_security_policy(self, acl_manager):
        """Test adding custom security policy"""
        custom_policy = SecurityPolicy(
            name="custom",
            level=SecurityLevel.OPEN,
            allowed_commands={"custom_cmd"},
            forbidden_patterns=[]
        )

        result = acl_manager.add_security_policy(custom_policy)
        assert result is True
        assert "custom" in acl_manager.security_policies

    def test_get_security_report(self, acl_manager):
        """Test security report generation"""
        # Generate some audit events
        acl_manager.validate_command("echo test", "user1")
        acl_manager.validate_command("rm -rf /", "user1")

        report = acl_manager.get_security_report()

        assert "security_level" in report
        assert "total_events" in report
        assert "blocked_events" in report
        assert report["total_events"] >= 2


class TestMovaIntegration:
    """Integration tests for Mova components working together"""

    @pytest.mark.asyncio
    async def test_component_with_client(self):
        """Test component using client"""

        class TestIntegrationComponent(MovaComponent):
            async def initialize(self, config=None):
                self._initialized = True
                return True
            async def start(self):
                self._running = True
                return True
            async def stop(self):
                self._running = False
                return True
            def health_check(self):
                return {"status": "healthy"}
            def get_capabilities(self):
                return ["integration_test"]

        component = TestIntegrationComponent("integration_test")
        client = MovaClient("http://localhost:8080")

        await component.start()

        # Component should be able to use client
        assert component.is_running is True
        assert client.base_url == "http://localhost:8080"

        await component.stop()

    def test_logger_with_config(self):
        """Test logger using configuration"""
        config = ConfigManager()
        logger = MovaLogger("config_test")

        # Should work together without issues
        log_level = config.get('LOG_LEVEL', 'INFO')
        assert log_level == 'INFO'

        logger.info(f"Log level set to {log_level}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
