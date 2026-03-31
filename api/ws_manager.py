"""
WebSocket Manager — Handles multiple client connections and event broadcasting.
"""

import asyncio
import json
import time
from typing import Set, Dict, Any
from fastapi import WebSocket
from simulation.event_bus import event_bus


class ConnectionManager:
    """Manages WebSocket connections and broadcasts events."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._registered = False

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

        # Register broadcast callback with event bus (once)
        if not self._registered:
            event_bus.subscribe_all(self._broadcast_event)
            self._registered = True

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected client."""
        self.active_connections.discard(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def _broadcast_event(self, event):
        """Broadcast an event to all connected clients."""
        if not self.active_connections:
            return

        message = json.dumps(event.to_dict(), default=str)
        disconnected = set()

        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)

        # Clean up dead connections
        for conn in disconnected:
            self.active_connections.discard(conn)

    async def send_personal(self, websocket: WebSocket, data: dict):
        """Send a message to a specific client."""
        try:
            await websocket.send_json(data)
        except Exception:
            self.disconnect(websocket)

    @property
    def client_count(self):
        return len(self.active_connections)


# Global connection manager instance
ws_manager = ConnectionManager()
