"""Payment repository interface"""

from abc import ABC, abstractmethod
from typing import Optional, List


class IPaymentRepository(ABC):
    """Interface for payment repository"""
    
    @abstractmethod
    def save(self, payment: dict) -> int:
        """
        Save a new payment record.
        
        Args:
            payment: dict with keys: order_id, amount, method, status, 
                    transaction_id, created_at
        
        Returns:
            Payment ID
        """
        pass
    
    @abstractmethod
    def find_by_id(self, payment_id: int) -> Optional[dict]:
        """Find payment by ID"""
        pass
    
    @abstractmethod
    def find_by_order_id(self, order_id: int) -> Optional[dict]:
        """Find payment by order ID"""
        pass
    
    @abstractmethod
    def update_status(self, payment_id: int, status: str) -> None:
        """Update payment status"""
        pass
