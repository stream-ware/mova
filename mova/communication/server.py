"""
Mova Server - WebSocket i HTTP Server dla komunikacji
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..mova_logging.logger import MovaLogger
from ..config.manager import ConfigManager


@dataclass
class ClientConnection:
    """Informacje o połączeniu klienta"""
    id: str
    websocket: WebSocket
    connected_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MovaServer:
    """
    Mova Server - Centralny serwer komunikacyjny dla ecosystem

    Zapewnia:
    - WebSocket connections dla real-time komunikacji
    - HTTP API endpoints
    - Client management i heartbeat monitoring
    - Message routing między komponentami
    """

    def __init__(self,
                 host: str = "localhost",
                 port: int = 8080,
                 name: str = "mova-server"):

        self.host = host
        self.port = port
        self.name = name

        # Logging i config
        self.logger = MovaLogger(f"mova.server.{name}")
        self.config = ConfigManager()

        # FastAPI app
        self.app = FastAPI(title="Mova Server", version="1.0.0")

        # WebSocket connections
        self.active_connections: Dict[str, ClientConnection] = {}

        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}

        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup routes
        self._setup_routes()

        self.logger.info(f"Mova Server initialized on {host}:{port}")

    def _setup_routes(self):
        """Setup HTTP i WebSocket routes"""

        @self.app.get("/")
        async def root():
            return {
                "message": "Mova Server Running",
                "version": "1.0.0",
                "active_connections": len(self.active_connections)
            }

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "connections": len(self.active_connections)
            }

        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            await self.handle_websocket_connection(websocket, client_id)

    async def handle_websocket_connection(self, websocket: WebSocket, client_id: str):
        """Obsługuje połączenie WebSocket"""

        await websocket.accept()

        # Create connection object
        connection = ClientConnection(
            id=client_id,
            websocket=websocket,
            last_heartbeat=datetime.now()
        )

        self.active_connections[client_id] = connection
        self.logger.info(f"Client {client_id} connected via WebSocket")

        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)

                # Update heartbeat
                connection.last_heartbeat = datetime.now()

                # Route message
                await self.route_message(client_id, message)

        except WebSocketDisconnect:
            self.logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            self.logger.error(f"WebSocket error for {client_id}: {e}")
        finally:
            # Clean up connection
            if client_id in self.active_connections:
                del self.active_connections[client_id]

    async def route_message(self, client_id: str, message: Dict[str, Any]):
        """Routuje wiadomość do odpowiedniego handlera"""

        message_type = message.get('type', 'unknown')

        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            try:
                response = await handler(client_id, message)
                if response:
                    await self.send_to_client(client_id, response)
            except Exception as e:
                self.logger.error(f"Handler error for {message_type}: {e}")
                await self.send_error_to_client(client_id, str(e))
        else:
            self.logger.warning(f"No handler for message type: {message_type}")

    def register_message_handler(self, message_type: str, handler: Callable):
        """Rejestruje handler dla typu wiadomości"""
        self.message_handlers[message_type] = handler
        self.logger.info(f"Registered handler for message type: {message_type}")

    async def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Wysyła wiadomość do klienta"""

        if client_id in self.active_connections:
            connection = self.active_connections[client_id]
            try:
                await connection.websocket.send_text(json.dumps(message))
            except Exception as e:
                self.logger.error(f"Failed to send to {client_id}: {e}")
                # Remove dead connection
                if client_id in self.active_connections:
                    del self.active_connections[client_id]

    async def send_error_to_client(self, client_id: str, error_message: str):
        """Wysyła error do klienta"""

        error_response = {
            'type': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }

        await self.send_to_client(client_id, error_response)

    async def broadcast_message(self, message: Dict[str, Any], exclude_client: str = None):
        """Broadcastuje wiadomość do wszystkich klientów"""

        message_json = json.dumps(message)

        for client_id, connection in self.active_connections.items():
            if client_id != exclude_client:
                try:
                    await connection.websocket.send_text(message_json)
                except Exception as e:
                    self.logger.error(f"Broadcast failed to {client_id}: {e}")

    async def start_server(self):
        """Uruchamia serwer"""

        self.logger.info(f"Starting Mova Server on {self.host}:{self.port}")

        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )

        server = uvicorn.Server(config)
        await server.serve()

    def get_connection_info(self) -> Dict[str, Any]:
        """Zwraca informacje o połączeniach"""

        return {
            'active_connections': len(self.active_connections),
            'clients': [
                {
                    'id': conn.id,
                    'connected_at': conn.connected_at.isoformat(),
                    'last_heartbeat': conn.last_heartbeat.isoformat() if conn.last_heartbeat else None,
                    'metadata': conn.metadata
                }
                for conn in self.active_connections.values()
            ],
            'registered_handlers': list(self.message_handlers.keys())
        }


# Default handlers
async def handle_ping(client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """Default ping handler"""
    return {
        'type': 'pong',
        'timestamp': datetime.now().isoformat(),
        'client_id': client_id
    }


async def handle_heartbeat(client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """Default heartbeat handler"""
    return {
        'type': 'heartbeat_ack',
        'timestamp': datetime.now().isoformat()
    }


def create_default_server(host: str = "localhost", port: int = 8080) -> MovaServer:
    """Tworzy serwer z domyślnymi handlers"""

    server = MovaServer(host=host, port=port)

    # Register default handlers
    server.register_message_handler('ping', handle_ping)
    server.register_message_handler('heartbeat', handle_heartbeat)

    return server
