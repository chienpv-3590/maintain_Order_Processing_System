"""Product Data Transfer Objects"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class CreateProductDto:
    """DTO for creating a product"""
    name: str
    price: Decimal
    stock: int
    category: str


@dataclass
class UpdateProductDto:
    """DTO for updating a product"""
    product_id: int
    name: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    category: Optional[str] = None


@dataclass
class ProductDto:
    """DTO for product response"""
    id: int
    name: str
    price: Decimal
    stock: int
    category: str


@dataclass
class ProductSearchDto:
    """DTO for product search"""
    query: str
    category: Optional[str] = None


@dataclass
class UpdateStockDto:
    """DTO for updating product stock"""
    product_id: int
    quantity: int  # Positive to add, negative to subtract
