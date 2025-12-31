"""User Data Transfer Objects"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class RegisterUserDto:
    """DTO for user registration"""
    name: str
    email: str
    password: str


@dataclass
class LoginDto:
    """DTO for user login"""
    email: str
    password: str


@dataclass
class UserProfileDto:
    """DTO for user profile response"""
    id: int
    name: str
    email: str
    role: str
    balance: Decimal
    created_at: str


@dataclass
class LoginResponseDto:
    """DTO for login response"""
    success: bool
    user: UserProfileDto
    token: Optional[str] = None  # For future JWT implementation


@dataclass
class UpdateBalanceDto:
    """DTO for updating user balance (admin only)"""
    user_id: int
    amount: Decimal


@dataclass
class UpdateUserRoleDto:
    """DTO for updating user role (admin only)"""
    user_id: int
    role: str
