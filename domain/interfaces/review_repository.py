"""Review repository interface"""

from abc import ABC, abstractmethod
from typing import Optional, List


class IReviewRepository(ABC):
    """Interface for review repository"""
    
    @abstractmethod
    def save(self, review: dict) -> int:
        """
        Save a new review.
        
        Args:
            review: dict with keys: product_id, user_id, rating, comment, created_at
        
        Returns:
            Review ID
        """
        pass
    
    @abstractmethod
    def find_by_id(self, review_id: int) -> Optional[dict]:
        """Find review by ID"""
        pass
    
    @abstractmethod
    def find_by_product_id(self, product_id: int) -> List[dict]:
        """Get all reviews for a product"""
        pass
    
    @abstractmethod
    def find_by_user_and_product(self, user_id: int, product_id: int) -> Optional[dict]:
        """Check if user already reviewed a product"""
        pass
    
    @abstractmethod
    def update(self, review_id: int, rating: int, comment: str) -> None:
        """Update a review"""
        pass
    
    @abstractmethod
    def delete(self, review_id: int) -> None:
        """Delete a review"""
        pass
