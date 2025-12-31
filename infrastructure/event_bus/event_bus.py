"""Event bus interface"""

from abc import ABC, abstractmethod
from typing import Callable, Type


class IEventBus(ABC):
    """Interface for event bus"""
    
    @abstractmethod
    def publish(self, event: object) -> None:
        """
        Publish an event.
        
        Args:
            event: Event object to publish
        """
        pass
    
    @abstractmethod
    def subscribe(self, event_type: Type, handler: Callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callable to handle the event
        """
        pass
