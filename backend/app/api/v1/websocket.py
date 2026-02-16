"""WebSocket connection manager - bridges Redis PubSub events to frontend clients."""

import asyncio
import json
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.logging import get_logger
from app.orchestration.event_bus import EventBus

logger = get_logger("api.websocket")

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections per project, bridging Redis PubSub to clients."""

    def __init__(self):
        # project_id -> list of connected WebSocket clients
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # project_id -> asyncio.Task for Redis subscriber
        self._subscriber_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, project_id: str) -> None:
        """Accept a new WebSocket connection and start project event subscription."""
        await websocket.accept()

        if project_id not in self.active_connections:
            self.active_connections[project_id] = []

        self.active_connections[project_id].append(websocket)
        logger.info(f"WebSocket connected: project={project_id}, total={len(self.active_connections[project_id])}")

        # Start Redis subscriber for this project if not already running
        if project_id not in self._subscriber_tasks or self._subscriber_tasks[project_id].done():
            self._subscriber_tasks[project_id] = asyncio.create_task(
                self._subscribe_to_events(project_id)
            )

    async def disconnect(self, websocket: WebSocket, project_id: str) -> None:
        """Remove a WebSocket connection."""
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)
            logger.info(f"WebSocket disconnected: project={project_id}, remaining={len(self.active_connections[project_id])}")

            # Stop subscriber if no more connections for this project
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
                if project_id in self._subscriber_tasks:
                    self._subscriber_tasks[project_id].cancel()
                    del self._subscriber_tasks[project_id]

    async def broadcast_to_project(self, project_id: str, message: dict) -> None:
        """Send a message to all WebSocket clients subscribed to a project."""
        connections = self.active_connections.get(project_id, [])
        dead_connections = []

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        # Clean up dead connections
        for dead in dead_connections:
            await self.disconnect(dead, project_id)

    async def _subscribe_to_events(self, project_id: str) -> None:
        """Subscribe to Redis PubSub events for a project and broadcast to WebSocket clients."""
        event_bus = EventBus()
        try:
            async for event in event_bus.subscribe(project_id):
                await self.broadcast_to_project(project_id, event)
        except asyncio.CancelledError:
            logger.info(f"Event subscription cancelled for project {project_id}")
        except Exception as e:
            logger.error(f"Event subscription error for project {project_id}: {e}")


# Singleton connection manager
manager = ConnectionManager()


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for real-time project event streaming."""
    await manager.connect(websocket, project_id)

    try:
        while True:
            # Listen for client messages (subscribe/unsubscribe/ping)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")

                if action == "ping":
                    await websocket.send_json({"type": "pong"})

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        await manager.disconnect(websocket, project_id)
