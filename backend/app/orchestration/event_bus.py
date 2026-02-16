"""Redis PubSub event bus for real-time event distribution."""

from __future__ import annotations
import json
from typing import Any, AsyncGenerator, Callable

import redis.asyncio as aioredis

from app.core.logging import get_logger
from app.db.redis import get_redis
from app.orchestration.events import Event

logger = get_logger("orchestration.event_bus")


class EventBus:
    """Redis PubSub-based event bus for distributing agent and system events."""

    CHANNEL_PREFIX = "aiden:events"

    def __init__(self, redis_client: aioredis.Redis | None = None):
        self._redis = redis_client

    @property
    def redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = get_redis()
        return self._redis

    def _channel_for_project(self, project_id: str) -> str:
        return f"{self.CHANNEL_PREFIX}:{project_id}"

    async def publish(self, event_type: str, data: dict, project_id: str | None = None) -> None:
        """Publish an event to the project's channel."""
        pid = project_id or data.get("project_id", "global")
        channel = self._channel_for_project(pid)

        message = {
            "event_type": event_type,
            "project_id": pid,
            "data": data,
        }

        await self.redis.publish(channel, json.dumps(message, default=str))
        logger.debug(f"Published {event_type} to {channel}")

    async def publish_event(self, event: Event) -> None:
        """Publish a structured Event object."""
        await self.publish(
            event_type=event.event_type,
            data={
                "execution_id": event.execution_id,
                "agent_name": event.agent_name,
                "timestamp": event.timestamp,
                **event.data,
            },
            project_id=event.project_id,
        )

    async def subscribe(self, project_id: str) -> AsyncGenerator[dict, None]:
        """Subscribe to events for a specific project. Yields parsed event dicts."""
        channel = self._channel_for_project(project_id)
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)

        logger.info(f"Subscribed to channel: {channel}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        yield data
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in event: {message['data']}")
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    async def subscribe_all(self) -> AsyncGenerator[dict, None]:
        """Subscribe to all AIDEN events (for admin monitoring)."""
        pattern = f"{self.CHANNEL_PREFIX}:*"
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe(pattern)

        try:
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    try:
                        data = json.loads(message["data"])
                        yield data
                    except json.JSONDecodeError:
                        pass
        finally:
            await pubsub.punsubscribe(pattern)
            await pubsub.close()
