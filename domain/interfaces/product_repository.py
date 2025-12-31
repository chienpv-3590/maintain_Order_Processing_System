"""Product repository interface"""

from abc import ABC, abstractmethod
from typing import Optional, List


class IProductRepository(ABC):
    """Interface for product repository"""
    
    @abstractmethod
    def find_by_id(self, product_id: int) -> Optional[dict]:
        """Find product by ID
        
        Returns:
            dict with keys: id, name, price, stock, category
            None if not found
        """
        pass
    
    @abstractmethod
    def update_stock(self, product_id: int, quantity_change: int) -> None:
        """Update product stock by adding/subtracting quantity
        
        Args:
            product_id: Product ID
            quantity_change: Amount to change (negative to decrease)
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[dict]:
        """Get all products"""
        pass
    
    @abstractmethod
    def save(self, product: dict) -> int:
        """Save a new product
        
        Returns:
            Product ID
        """
        pass
