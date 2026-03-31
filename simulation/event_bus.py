"""
Event Bus — Publish/Subscribe system for agent-to-agent and agent-to-UI communication.
All system events flow through here and are broadcast via WebSocket.
"""

import asyncio
import time
import uuid
from collections import deque
from typing import Callable, Dict, List, Any, Optional


class Event:
    """Represents a single system event."""
    def __init__(self, event_type: str, payload: dict, source: str = "system"):
        self.id = str(uuid.uuid4())[:8]
        self.event_type = event_type
        self.payload = payload
        self.source = source
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.event_type,
            "payload": self.payload,
            "source": self.source,
            "timestamp": self.timestamp,
        }


# Event type constants
EVENT_DEVICE_DISCOVERED = "device_discovered"
EVENT_DEVICE_UPDATED = "device_updated"
EVENT_THREAT_DETECTED = "threat_detected"
EVENT_ALERT_CREATED = "alert_created"
EVENT_HONEYPOT_DEPLOYED = "honeypot_deployed"
EVENT_HONEYPOT_INTERACTION = "honeypot_interaction"
EVENT_DEVICE_ISOLATED = "device_isolated"
EVENT_DEVICE_RELEASED = "device_released"
EVENT_LOG_ENTRY = "log_entry"
EVENT_AGENT_ACTION = "agent_action"
EVENT_METRIC_UPDATE = "metric_update"
EVENT_SYSTEM_STATE_CHANGE = "system_state_change"
EVENT_ATTACK_STARTED = "attack_started"
EVENT_ATTACK_BLOCKED = "attack_blocked"
EVENT_NETWORK_MAP_UPDATE = "network_map_update"

# System state modes
STATE_MONITORING = "MONITORING"
STATE_ALERT = "ALERT"
STATE_DEFENSE = "DEFENSE"
STATE_LOCKDOWN = "LOCKDOWN"


class EventBus:
    """Central event bus for all system communication."""

    def __init__(self, history_size: int = 500):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._global_subscribers: List[Callable] = []
        self._history: deque = deque(maxlen=history_size)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._system_state = STATE_MONITORING
        self._threat_count = 0
        self._critical_threshold = 3  # auto-escalate after N critical threats

    @property
    def system_state(self):
        return self._system_state

    def set_system_state(self, state: str):
        """Change system-wide operational state."""
        old_state = self._system_state
        self._system_state = state
        # Publish state change event synchronously into queue
        event = Event(EVENT_SYSTEM_STATE_CHANGE, {
            "old_state": old_state,
            "new_state": state,
        }, source="event_bus")
        self._history.append(event)
        # Don't await here — just put in queue
        try:
            self._event_queue.put_nowait(event)
        except asyncio.QueueFull:
            pass

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def subscribe_all(self, callback: Callable):
        """Subscribe to all events (used by WebSocket broadcaster)."""
        self._global_subscribers.append(callback)

    def unsubscribe_all_callback(self, callback: Callable):
        """Remove a global subscriber."""
        if callback in self._global_subscribers:
            self._global_subscribers.remove(callback)

    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        self._history.append(event)
        await self._event_queue.put(event)

    async def publish_new(self, event_type: str, payload: dict, source: str = "system"):
        """Create and publish a new event."""
        event = Event(event_type, payload, source)
        await self.publish(event)
        return event

    async def _process_events(self):
        """Main event processing loop."""
        self._running = True
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=0.5)
                # Auto-escalate system state based on threats
                if event.event_type == EVENT_THREAT_DETECTED:
                    severity = event.payload.get("severity", "low")
                    if severity in ("critical", "high"):
                        self._threat_count += 1
                        if self._threat_count >= self._critical_threshold and self._system_state == STATE_MONITORING:
                            self.set_system_state(STATE_ALERT)
                        elif self._threat_count >= self._critical_threshold * 2 and self._system_state == STATE_ALERT:
                            self.set_system_state(STATE_DEFENSE)

                # Notify type-specific subscribers
                if event.event_type in self._subscribers:
                    for callback in self._subscribers[event.event_type]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event)
                            else:
                                callback(event)
                        except Exception as e:
                            print(f"[EventBus] Subscriber error: {e}")

                # Notify global subscribers (WebSocket broadcast)
                for callback in self._global_subscribers:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                    except Exception as e:
                        print(f"[EventBus] Global subscriber error: {e}")

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[EventBus] Processing error: {e}")

    async def start(self):
        """Start the event processing loop."""
        asyncio.create_task(self._process_events())

    def stop(self):
        """Stop event processing."""
        self._running = False

    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Get event history, optionally filtered by type."""
        events = list(self._history)
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return [e.to_dict() for e in events[-limit:]]

    def get_stats(self) -> dict:
        """Get event bus statistics."""
        type_counts = {}
        for event in self._history:
            type_counts[event.event_type] = type_counts.get(event.event_type, 0) + 1
        return {
            "total_events": len(self._history),
            "queue_size": self._event_queue.qsize(),
            "subscriber_count": sum(len(s) for s in self._subscribers.values()),
            "global_subscribers": len(self._global_subscribers),
            "system_state": self._system_state,
            "event_type_counts": type_counts,
        }


# Global event bus instance
event_bus = EventBus()
