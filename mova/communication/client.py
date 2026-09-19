"""
🌐 Mova Communication Client

Lightweight HTTP and WebSocket client for Mova ecosystem communication.
Handles API calls, real-time messaging, and connection management.
"""

import asyncio
import json
import requests
import websockets
from typing import Dict, Any, Optional, Callable, Union
from urllib.parse import urljoin
import logging

from ..mova_logging.logger import get_logger


class MovaClient:
    """
    Unified client for HTTP and WebSocket communication with Mova services.

    Features:
    - HTTP API calls with automatic retry
    - WebSocket real-time communication
    - Connection pooling and management
    - Automatic reconnection on failures
    - Event-driven message handling
    """

    def __init__(self,
                 base_url: str = "http://localhost:8094",
                 websocket_url: Optional[str] = None,
                 timeout: int = 30):
        """
        Initialize Mova client.

        Args:
            base_url: Base URL for HTTP API calls
            websocket_url: WebSocket URL (auto-detected if None)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.websocket_url = websocket_url or self._detect_websocket_url()
        self.timeout = timeout

        self.logger = get_logger("client")
        self.session = requests.Session()
        self.websocket = None
        self.event_handlers = {}

        # Connection state
        self._connected = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5

    def _detect_websocket_url(self) -> str:
        """Auto-detect WebSocket URL from HTTP base URL"""
        if self.base_url.startswith('https://'):
            return self.base_url.replace('https://', 'wss://') + '/ws'
        else:
            return self.base_url.replace('http://', 'ws://') + '/ws'

    # HTTP API Methods

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make GET request to API endpoint.

        Args:
            endpoint: API endpoint (e.g., '/api/logs')
            params: Query parameters

        Returns:
            Response JSON data
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            self.logger.debug("GET request successful",
                            endpoint=endpoint, status_code=response.status_code)

            return response.json() if response.content else {}

        except requests.RequestException as e:
            self.logger.error("GET request failed",
                            endpoint=endpoint, error=str(e))
            raise MovaClientError(f"GET {endpoint} failed: {e}")

    def post(self, endpoint: str, data: Optional[Dict] = None,
             json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make POST request to API endpoint.

        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data

        Returns:
            Response JSON data
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                timeout=self.timeout
            )
            response.raise_for_status()

            self.logger.debug("POST request successful",
                            endpoint=endpoint, status_code=response.status_code)

            return response.json() if response.content else {}

        except requests.RequestException as e:
            self.logger.error("POST request failed",
                            endpoint=endpoint, error=str(e))
            raise MovaClientError(f"POST {endpoint} failed: {e}")

    def health_check(self) -> Dict[str, Any]:
        """Check server health status"""
        try:
            return self.get('/health')
        except MovaClientError:
            return {'status': 'unhealthy', 'error': 'Connection failed'}

    # WebSocket Methods

    async def connect_websocket(self) -> bool:
        """
        Establish WebSocket connection.

        Returns:
            True if connection successful
        """
        try:
            self.websocket = await websockets.connect(
                self.websocket_url,
                timeout=self.timeout
            )
            self._connected = True
            self._reconnect_attempts = 0

            self.logger.info("WebSocket connected", url=self.websocket_url)

            # Start message handling loop
            asyncio.create_task(self._handle_messages())

            return True

        except Exception as e:
            self.logger.error("WebSocket connection failed", error=str(e))
            self._connected = False
            return False

    async def disconnect_websocket(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self._connected = False
            self.logger.info("WebSocket disconnected")

    async def send_message(self, message_type: str, data: Dict[str, Any]) -> bool:
        """
        Send message via WebSocket.

        Args:
            message_type: Type of message ('chat', 'command', etc.)
            data: Message data

        Returns:
            True if message sent successfully
        """
        if not self._connected or not self.websocket:
            self.logger.warning("WebSocket not connected, attempting to connect...")
            if not await self.connect_websocket():
                return False

        message = {
            'type': message_type,
            'timestamp': str(asyncio.get_event_loop().time()),
            'data': data
        }

        try:
            await self.websocket.send(json.dumps(message))
            self.logger.debug("WebSocket message sent", type=message_type)
            return True

        except Exception as e:
            self.logger.error("Failed to send WebSocket message", error=str(e))
            self._connected = False
            return False

    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            async for message_str in self.websocket:
                try:
                    message = json.loads(message_str)
                    message_type = message.get('type', 'unknown')

                    # Trigger registered event handlers
                    if message_type in self.event_handlers:
                        for handler in self.event_handlers[message_type]:
                            try:
                                await handler(message)
                            except Exception as e:
                                self.logger.error("Event handler failed",
                                                type=message_type, error=str(e))

                    self.logger.debug("WebSocket message received", type=message_type)

                except json.JSONDecodeError as e:
                    self.logger.warning("Invalid JSON in WebSocket message", error=str(e))

        except websockets.exceptions.ConnectionClosed:
            self.logger.info("WebSocket connection closed")
            self._connected = False
            await self._attempt_reconnect()

        except Exception as e:
            self.logger.error("WebSocket message handling failed", error=str(e))
            self._connected = False

    async def _attempt_reconnect(self):
        """Attempt to reconnect WebSocket with exponential backoff"""
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")
            return

        wait_time = 2 ** self._reconnect_attempts  # Exponential backoff
        self.logger.info(f"Attempting reconnection in {wait_time} seconds...",
                        attempt=self._reconnect_attempts + 1)

        await asyncio.sleep(wait_time)
        self._reconnect_attempts += 1

        if await self.connect_websocket():
            self.logger.info("Reconnection successful")
        else:
            await self._attempt_reconnect()

    # Event Handling

    def on(self, event_type: str, handler: Callable):
        """
        Register event handler for WebSocket messages.

        Args:
            event_type: Type of event to handle
            handler: Async function to handle the event
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        self.logger.debug("Event handler registered", type=event_type)

    def off(self, event_type: str, handler: Optional[Callable] = None):
        """
        Unregister event handler.

        Args:
            event_type: Type of event
            handler: Specific handler to remove (None = remove all)
        """
        if event_type in self.event_handlers:
            if handler:
                self.event_handlers[event_type].remove(handler)
            else:
                self.event_handlers[event_type] = []

    # Utility Methods

    @property
    def is_connected(self) -> bool:
        """Check if client is connected (HTTP + WebSocket)"""
        try:
            # Check HTTP connection
            health = self.health_check()
            http_ok = health.get('status') != 'unhealthy'

            # WebSocket connection status
            ws_ok = self._connected and self.websocket and not self.websocket.closed

            return http_ok and ws_ok
        except:
            return False

    def close(self):
        """Close all connections and cleanup resources"""
        if self.websocket:
            asyncio.create_task(self.disconnect_websocket())

        self.session.close()
        self.logger.info("Mova client closed")


class MovaClientError(Exception):
    """Exception raised by MovaClient operations"""
    pass
