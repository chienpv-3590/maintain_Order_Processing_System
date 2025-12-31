"""User repository interface"""

from abc import ABC, abstractmethod
from typing import Optional


class IUserRepository(ABC):
    """Interface for user repository"""
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[dict]:
        """Find user by ID
        
        Returns:
            dict with keys: id, name, email, role, balance
            None if not found
        """
        pass
    
    @abstractmethod
    def update_balance(self, user_id: int, amount: float) -> None:
        """Update user balance by adding/subtracting amount
        
        Args:
            user_id: User ID
            amount: Amount to change (negative to deduct)
        """
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email"""
        pass
    
    @abstractmethod
    def save(self, user: dict) -> int:
        """Save a new user
        
        Returns:
            User ID
        """
        pass
