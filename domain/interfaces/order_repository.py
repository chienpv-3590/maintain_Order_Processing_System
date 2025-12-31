"""Order repository interface"""

from abc import ABC, abstractmethod
from typing import Optional, List


class IOrderRepository(ABC):
    """Interface for order repository"""
    
    @abstractmethod
    def save(self, order: dict) -> int:
        """Save a new order
        
        Args:
            order: dict with keys: id, user_id, items (json), total, status, 
                   created_at, shipping_address
        
        Returns:
            Order ID
        """
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[dict]:
        """Find order by ID
        
        Returns:
            dict or None if not found
        """
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[dict]:
        """Get all orders for a user"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[dict]:
        """Get all orders (admin only)"""
        pass
    
    @abstractmethod
    def update_status(self, order_id: int, status: str) -> None:
        """Update order status"""
        pass
