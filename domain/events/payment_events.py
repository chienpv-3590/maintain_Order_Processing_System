"""Payment domain events"""

from dataclasses import dataclass
from domain.events.base import DomainEvent


@dataclass
class PaymentInitiated(DomainEvent):
    """Event raised when payment is initiated"""
    payment_id: int
    order_id: int
    amount: float
    method: str


@dataclass
class PaymentCompleted(DomainEvent):
    """Event raised when payment is completed"""
    payment_id: int
    order_id: int
    amount: float
    transaction_id: str


@dataclass
class PaymentFailed(DomainEvent):
    """Event raised when payment fails"""
    payment_id: int
    order_id: int
    reason: str


@dataclass
class PaymentRefunded(DomainEvent):
    """Event raised when payment is refunded"""
    payment_id: int
    order_id: int
    amount: float
    refunded_by: int
