"""User domain events"""

from dataclasses import dataclass
from datetime import datetime
from domain.events.base import DomainEvent


@dataclass
class UserRegistered(DomainEvent):
    """Event raised when a user registers"""
    user_id: int
    name: str
    email: str
    role: str


@dataclass
class UserAuthenticated(DomainEvent):
    """Event raised when a user logs in"""
    user_id: int
    email: str


@dataclass
class UserBalanceUpdated(DomainEvent):
    """Event raised when user balance is updated"""
    user_id: int
    old_balance: float
    new_balance: float
    changed_by: int  # Admin user ID


@dataclass
class UserRoleUpdated(DomainEvent):
    """Event raised when user role is updated"""
    user_id: int
    old_role: str
    new_role: str
    changed_by: int  # Admin user ID
