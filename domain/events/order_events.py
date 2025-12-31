"""Order domain events"""

from dataclasses import dataclass
from domain.events.base import DomainEvent


@dataclass
class OrderCreated(DomainEvent):
    """Event raised when an order is created"""
    order_id: int
    user_id: int
    total: float
    status: str


@dataclass
class OrderPaid(DomainEvent):
    """Event raised when an order is paid"""
    order_id: int
    payment_method: str
    amount: float


@dataclass
class OrderStatusUpdated(DomainEvent):
    """Event raised when order status changes"""
    order_id: int
    old_status: str
    new_status: str
    updated_by: int


@dataclass
class OrderCancelled(DomainEvent):
    """Event raised when order is cancelled"""
    order_id: int
    cancelled_by: int
    reason: str


@dataclass
class OrderShipped(DomainEvent):
    """Event raised when order is shipped"""
    order_id: int
    shipping_address: str
    tracking_number: str


@dataclass
class OrderDelivered(DomainEvent):
    """Event raised when order is delivered"""
    order_id: int
    delivered_at: str
