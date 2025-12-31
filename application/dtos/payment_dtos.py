"""Payment Data Transfer Objects"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class ProcessPaymentDto:
    """DTO for processing payment"""
    order_id: int
    user_id: int
    amount: Decimal
    payment_method: str  # 'balance', 'credit_card', 'paypal'


@dataclass
class PaymentDto:
    """DTO for payment response"""
    id: int
    order_id: int
    amount: Decimal
    method: str
    status: str
    transaction_id: Optional[str]
    created_at: str


@dataclass
class RefundPaymentDto:
    """DTO for refunding payment"""
    payment_id: int
    amount: Optional[Decimal] = None  # None means full refund
