"""Base domain event"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DomainEvent:
    """Base class for all domain events"""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
