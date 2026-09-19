"""
🔌 Mova Component Base Interface

Standard interface that all Mova components must implement.
Provides consistent lifecycle management and plugin architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

class MovaComponent(ABC):
    """
    Base interface for all Mova ecosystem components.

    Every Mova component (mova-core, movatalk, movaweb, etc.)
    implements this interface for consistent management.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        """Initialize component with basic metadata"""
        self.name = name
        self.version = version
        self.logger = logging.getLogger(f"mova.{name}")
        self._initialized = False
        self._running = False
        self._config = {}

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize component with configuration.

        Args:
            config: Component-specific configuration dictionary

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def start(self) -> bool:
        """
        Start component services and background tasks.

        Returns:
            True if startup successful, False otherwise
        """
        pass

    @abstractmethod
    def stop(self) -> bool:
        """
        Stop component services and cleanup resources.

        Returns:
            True if shutdown successful, False otherwise
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Return current component health status.

        Returns:
            Dictionary with health information:
            - status: 'healthy', 'degraded', 'unhealthy'
            - details: Additional status information
            - metrics: Performance metrics if available
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of capabilities this component provides.

        Returns:
            List of capability identifiers (e.g., ['tts', 'stt', 'audio_management'])
        """
        pass

    # Standard lifecycle properties
    @property
    def is_initialized(self) -> bool:
        """Check if component is initialized"""
        return self._initialized

    @property
    def is_running(self) -> bool:
        """Check if component is running"""
        return self._running

    @property
    def config(self) -> Dict[str, Any]:
        """Get current component configuration"""
        return self._config.copy()

    # Helper methods for common operations
    def log_info(self, message: str) -> None:
        """Log info message with component context"""
        self.logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str) -> None:
        """Log error message with component context"""
        self.logger.error(f"[{self.name}] {message}")

    def log_warning(self, message: str) -> None:
        """Log warning message with component context"""
        self.logger.warning(f"[{self.name}] {message}")


class MovaPlugin:
    """
    Base class for Mova plugins.

    Plugins extend component functionality without modifying core code.
    """

    def __init__(self, name: str, component_type: str):
        self.name = name
        self.component_type = component_type
        self.logger = logging.getLogger(f"mova.plugin.{name}")

    @abstractmethod
    def install(self, component: MovaComponent) -> bool:
        """Install plugin into component"""
        pass

    @abstractmethod
    def uninstall(self, component: MovaComponent) -> bool:
        """Remove plugin from component"""
        pass

    @abstractmethod
    def get_plugin_info(self) -> Dict[str, Any]:
        """Return plugin metadata and capabilities"""
        pass


class MovaRegistry:
    """
    Central registry for components and plugins.

    Manages component lifecycle and plugin installation.
    """

    def __init__(self):
        self._components: Dict[str, MovaComponent] = {}
        self._plugins: Dict[str, MovaPlugin] = {}
        self.logger = logging.getLogger("mova.registry")

    def register_component(self, component: MovaComponent) -> bool:
        """Register a new component"""
        try:
            self._components[component.name] = component
            self.logger.info(f"Registered component: {component.name} v{component.version}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register component {component.name}: {e}")
            return False

    def get_component(self, name: str) -> Optional[MovaComponent]:
        """Get component by name"""
        return self._components.get(name)

    def list_components(self) -> List[str]:
        """List all registered component names"""
        return list(self._components.keys())

    def register_plugin(self, plugin: MovaPlugin) -> bool:
        """Register a new plugin"""
        try:
            self._plugins[plugin.name] = plugin
            self.logger.info(f"Registered plugin: {plugin.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register plugin {plugin.name}: {e}")
            return False

    def install_plugin(self, plugin_name: str, component_name: str) -> bool:
        """Install plugin into component"""
        plugin = self._plugins.get(plugin_name)
        component = self._components.get(component_name)

        if not plugin or not component:
            self.logger.error(f"Plugin {plugin_name} or component {component_name} not found")
            return False

        return plugin.install(component)


# Global registry instance
registry = MovaRegistry()
