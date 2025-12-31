"""Order Data Transfer Objects"""

from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal


@dataclass
class OrderItemDto:
    """DTO for order item input"""
    product_id: int
    quantity: int


@dataclass
class CreateOrderDto:
    """DTO for creating an order"""
    user_id: int
    items: List[OrderItemDto]
    shipping_address: str
    coupon_code: Optional[str] = None


@dataclass
class OrderItemResponseDto:
    """DTO for order item in response"""
    product_id: int
    product_name: str
    price: Decimal
    quantity: int
    subtotal: Decimal


@dataclass
class OrderBreakdownDto:
    """DTO for order price breakdown"""
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal


@dataclass
class OrderDto:
    """DTO for order response"""
    order_id: int
    user_id: int
    items: List[OrderItemResponseDto]
    breakdown: OrderBreakdownDto
    status: str
    shipping_address: str
    created_at: str


@dataclass
class OrderSummaryDto:
    """DTO for order creation summary"""
    success: bool
    order_id: int
    total: Decimal
    status: str
    breakdown: OrderBreakdownDto


@dataclass
class UpdateOrderStatusDto:
    """DTO for updating order status"""
    order_id: int
    new_status: str
    updated_by: int


@dataclass
class CancelOrderDto:
    """DTO for cancelling an order"""
    order_id: int
    user_id: int
    reason: Optional[str] = None
