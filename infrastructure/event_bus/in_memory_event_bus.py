"""In-memory event bus implementation"""

from typing import Dict, List, Callable, Type
from infrastructure.event_bus.event_bus import IEventBus


class InMemoryEventBus(IEventBus):
    """
    Simple in-memory event bus implementation.
    
    Events are published synchronously to all subscribed handlers.
    For production, consider using a message queue (RabbitMQ, Redis, etc.)
    """
    
    def __init__(self):
        self._subscribers: Dict[Type, List[Callable]] = {}
    
    def publish(self, event: object) -> None:
        """
        Publish an event to all subscribed handlers.
        
        Args:
            event: Event object to publish
        """
        event_type = type(event)
        
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # Log error but don't stop other handlers
                    print(f"Error in event handler: {e}")
    
    def subscribe(self, event_type: Type, handler: Callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callable to handle the event
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
