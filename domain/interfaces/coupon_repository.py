"""Coupon repository interface"""

from abc import ABC, abstractmethod
from typing import Optional


class ICouponRepository(ABC):
    """Interface for coupon repository"""
    
    @abstractmethod
    def find_by_code(self, code: str) -> Optional[dict]:
        """Find coupon by code
        
        Returns:
            dict with keys: code, discount, used, max_uses
            None if not found
        """
        pass
    
    @abstractmethod
    def increment_usage(self, code: str) -> None:
        """Increment coupon usage count"""
        pass
    
    @abstractmethod
    def save(self, coupon: dict) -> None:
        """Save a new coupon"""
        pass
