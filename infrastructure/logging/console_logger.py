"""Console logger implementation"""

from datetime import datetime
from typing import Optional
from infrastructure.logging.logger import ILogger


class ConsoleLogger(ILogger):
    """Simple console logger implementation"""
    
    def info(self, message: str, context: Optional[dict] = None) -> None:
        """Log info message to console"""
        timestamp = datetime.now().isoformat()
        ctx = f" | Context: {context}" if context else ""
        print(f"[{timestamp}] INFO: {message}{ctx}")
    
    def error(self, message: str, exception: Optional[Exception] = None, context: Optional[dict] = None) -> None:
        """Log error message to console"""
        timestamp = datetime.now().isoformat()
        exc = f" | Exception: {exception}" if exception else ""
        ctx = f" | Context: {context}" if context else ""
        print(f"[{timestamp}] ERROR: {message}{exc}{ctx}")
    
    def warning(self, message: str, context: Optional[dict] = None) -> None:
        """Log warning message to console"""
        timestamp = datetime.now().isoformat()
        ctx = f" | Context: {context}" if context else ""
        print(f"[{timestamp}] WARNING: {message}{ctx}")
    
    def debug(self, message: str, context: Optional[dict] = None) -> None:
        """Log debug message to console"""
        timestamp = datetime.now().isoformat()
        ctx = f" | Context: {context}" if context else ""
        print(f"[{timestamp}] DEBUG: {message}{ctx}")


class NullLogger(ILogger):
    """Null logger for testing (does nothing)"""
    
    def info(self, message: str, context: Optional[dict] = None) -> None:
        pass
    
    def error(self, message: str, exception: Optional[Exception] = None, context: Optional[dict] = None) -> None:
        pass
    
    def warning(self, message: str, context: Optional[dict] = None) -> None:
        pass
    
    def debug(self, message: str, context: Optional[dict] = None) -> None:
        pass
