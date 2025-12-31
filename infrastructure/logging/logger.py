"""Logger interface"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ILogger(ABC):
    """Interface for logging"""
    
    @abstractmethod
    def info(self, message: str, context: Optional[dict] = None) -> None:
        """Log info message"""
        pass
    
    @abstractmethod
    def error(self, message: str, exception: Optional[Exception] = None, context: Optional[dict] = None) -> None:
        """Log error message"""
        pass
    
    @abstractmethod
    def warning(self, message: str, context: Optional[dict] = None) -> None:
        """Log warning message"""
        pass
    
    @abstractmethod
    def debug(self, message: str, context: Optional[dict] = None) -> None:
        """Log debug message"""
        pass
