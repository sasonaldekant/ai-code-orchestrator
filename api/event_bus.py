
import asyncio
import logging
import json
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    LOG = "log"
    THOUGHT = "thought"
    PLAN = "plan"
    MILESTONE = "milestone"
    TASK = "task"
    ARTIFACT = "artifact"
    WARNING = "warning"
    ERROR = "error"
    DONE = "done"
    INFO = "info"

@dataclass
class Event:
    type: str
    content: Any
    agent: str = "System"
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))

class EventBus:
    """
    Simple in-memory event bus for broadcasting orchestration events to SSE clients.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = set()
            cls._instance.history = [] # Keep recent history for new connections
        return cls._instance

    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        self.history.append(event)
        if len(self.history) > 1000: # Limit history size
            self.history.pop(0)
            
        # Log to console as well for debugging
        if event.type == EventType.ERROR:
            logger.error(f"[{event.agent}] {event.content}")
        elif event.type == EventType.THOUGHT:
            logger.info(f"[{event.agent}] 🤔 {event.content}")
        else:
            logger.info(f"[{event.agent}] {event.content}")

        # Broadcast to queues
        to_remove = []
        for q in self.subscribers:
            try:
                await q.put(event)
            except Exception:
                to_remove.append(q)
        
        for q in to_remove:
            self.subscribers.remove(q)

    def subscribe(self) -> asyncio.Queue:
        """Subscribe to the event stream."""
        q = asyncio.Queue()
        self.subscribers.add(q)
        
        # Replay recent history (optional, or just latest state)
        # For simplicity, we won't replay everything to avoid flooding,
        # but a real system might need state hydration.
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self.subscribers:
            self.subscribers.remove(q)

# Global instance
bus = EventBus()
