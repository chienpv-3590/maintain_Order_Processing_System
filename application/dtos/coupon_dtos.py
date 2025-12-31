"""Coupon Data Transfer Objects"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateCouponDto:
    """DTO for creating a coupon"""
    code: str
    discount_percentage: int  # 0-100
    max_uses: int


@dataclass
class CouponDto:
    """DTO for coupon response"""
    code: str
    discount_percentage: int
    used_count: int
    max_uses: int
    is_valid: bool


@dataclass
class ValidateCouponDto:
    """DTO for validating a coupon"""
    code: str
    order_amount: Optional[float] = None
