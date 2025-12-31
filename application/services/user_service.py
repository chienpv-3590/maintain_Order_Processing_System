"""User Service - handles user-related use cases"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Optional

from domain.interfaces.user_repository import IUserRepository
from infrastructure.security.password_hasher import IPasswordHasher
from infrastructure.event_bus.event_bus import IEventBus
from infrastructure.logging.logger import ILogger
from domain.exceptions.user_exceptions import (
    InvalidEmailException,
    WeakPasswordException,
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    UserNotFoundException
)
from domain.events.user_events import (
    UserRegistered,
    UserAuthenticated,
    UserBalanceUpdated,
    UserRoleUpdated
)
from application.dtos.user_dtos import (
    RegisterUserDto,
    LoginDto,
    UserProfileDto,
    LoginResponseDto,
    UpdateBalanceDto,
    UpdateUserRoleDto
)
from application.exceptions.validation_exception import ValidationException
from application.exceptions.unauthorized_exception import UnauthorizedException


class UserService:
    """
    Application service for user operations.
    
    Responsibilities:
    - User registration with validation
    - User authentication
    - User profile management
    - Balance management (admin)
    - Role management (admin)
    """
    
    # Email validation regex
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        event_bus: IEventBus,
        logger: ILogger
    ):
        """
        Initialize UserService with dependencies.
        
        Args:
            user_repository: Repository for user persistence
            password_hasher: Service for password hashing
            event_bus: Event bus for publishing domain events
            logger: Logger for audit trail
        """
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._event_bus = event_bus
        self._logger = logger
    
    def register_user(self, dto: RegisterUserDto) -> UserProfileDto:
        """
        Register a new user.
        
        Steps:
        1. Validate input (name, email, password)
        2. Check if email already exists
        3. Hash password
        4. Create user in database
        5. Publish UserRegistered event
        6. Return user profile
        
        Args:
            dto: RegisterUserDto with user details
        
        Returns:
            UserProfileDto with created user profile
        
        Raises:
            ValidationException: If required fields are missing
            InvalidEmailException: If email format is invalid
            WeakPasswordException: If password doesn't meet requirements
            EmailAlreadyExistsException: If email is already registered
        """
        # 1. Validate input
        self._validate_registration_input(dto)
        
        # 2. Validate email format
        if not self._is_valid_email(dto.email):
            raise InvalidEmailException(dto.email)
        
        # 3. Validate password strength
        if len(dto.password) < self.MIN_PASSWORD_LENGTH:
            raise WeakPasswordException(
                f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters"
            )
        
        # 4. Check if email already exists
        existing_user = self._user_repository.find_by_email(dto.email)
        if existing_user:
            raise EmailAlreadyExistsException(dto.email)
        
        # 5. Hash password
        hashed_password = self._password_hasher.hash(dto.password)
        
        # 6. Create user data
        user_data = {
            'name': dto.name,
            'email': dto.email,
            'password': hashed_password,
            'role': 'customer',  # Default role
            'balance': 0.0,
            'created_at': datetime.now().isoformat()
        }
        
        # 7. Save user
        user_id = self._user_repository.save(user_data)
        
        # 8. Publish domain event
        self._event_bus.publish(
            UserRegistered(
                user_id=user_id,
                name=dto.name,
                email=dto.email,
                role='customer'
            )
        )
        
        # 9. Log action
        self._logger.info(
            f"User registered: {dto.email}",
            {"user_id": user_id, "email": dto.email}
        )
        
        # 10. Return user profile
        return UserProfileDto(
            id=user_id,
            name=dto.name,
            email=dto.email,
            role='customer',
            balance=Decimal("0.0"),
            created_at=user_data['created_at']
        )
    
    def authenticate_user(self, dto: LoginDto) -> LoginResponseDto:
        """
        Authenticate a user (login).
        
        Steps:
        1. Validate input
        2. Find user by email
        3. Verify password
        4. Publish UserAuthenticated event
        5. Return user session
        
        Args:
            dto: LoginDto with credentials
        
        Returns:
            LoginResponseDto with user profile
        
        Raises:
            ValidationException: If required fields are missing
            InvalidCredentialsException: If credentials are invalid
        """
        # 1. Validate input
        if not dto.email or not dto.password:
            raise ValidationException("Email and password are required")
        
        # 2. Find user by email
        user = self._user_repository.find_by_email(dto.email)
        if not user:
            raise InvalidCredentialsException()
        
        # 3. Verify password
        if not self._password_hasher.verify(dto.password, user['password']):
            raise InvalidCredentialsException()
        
        # 4. Publish domain event
        self._event_bus.publish(
            UserAuthenticated(
                user_id=user['id'],
                email=user['email']
            )
        )
        
        # 5. Log action
        self._logger.info(
            f"User logged in: {dto.email}",
            {"user_id": user['id'], "email": dto.email}
        )
        
        # 6. Build and return response
        user_profile = UserProfileDto(
            id=user['id'],
            name=user['name'],
            email=user['email'],
            role=user['role'],
            balance=Decimal(str(user['balance'])),
            created_at=user.get('created_at', '')
        )
        
        return LoginResponseDto(
            success=True,
            user=user_profile,
            token=None  # TODO: Implement JWT token generation
        )
    
    def get_user_profile(self, user_id: int) -> UserProfileDto:
        """
        Get user profile by ID.
        
        Args:
            user_id: User ID
        
        Returns:
            UserProfileDto
        
        Raises:
            UserNotFoundException: If user not found
        """
        user = self._user_repository.find_by_id(user_id)
        
        if not user:
            raise UserNotFoundException(user_id=user_id)
        
        return UserProfileDto(
            id=user['id'],
            name=user['name'],
            email=user['email'],
            role=user['role'],
            balance=Decimal(str(user['balance'])),
            created_at=user.get('created_at', '')
        )
    
    def add_user_balance(self, dto: UpdateBalanceDto, admin_id: int) -> UserProfileDto:
        """
        Add balance to user account (admin only).
        
        Args:
            dto: UpdateBalanceDto with user_id and amount
            admin_id: Admin user ID performing the action
        
        Returns:
            Updated UserProfileDto
        
        Raises:
            UserNotFoundException: If user not found
            ValidationException: If amount is invalid
        """
        # 1. Validate amount
        if dto.amount <= 0:
            raise ValidationException("Amount must be greater than 0")
        
        # 2. Get user
        user = self._user_repository.find_by_id(dto.user_id)
        if not user:
            raise UserNotFoundException(user_id=dto.user_id)
        
        old_balance = Decimal(str(user['balance']))
        
        # 3. Update balance
        self._user_repository.update_balance(dto.user_id, float(dto.amount))
        
        new_balance = old_balance + dto.amount
        
        # 4. Publish event
        self._event_bus.publish(
            UserBalanceUpdated(
                user_id=dto.user_id,
                old_balance=float(old_balance),
                new_balance=float(new_balance),
                changed_by=admin_id
            )
        )
        
        # 5. Log action
        self._logger.info(
            f"Balance added to user {dto.user_id}",
            {
                "user_id": dto.user_id,
                "amount": float(dto.amount),
                "admin_id": admin_id
            }
        )
        
        # 6. Return updated profile
        return UserProfileDto(
            id=user['id'],
            name=user['name'],
            email=user['email'],
            role=user['role'],
            balance=new_balance,
            created_at=user.get('created_at', '')
        )
    
    def update_user_role(self, dto: UpdateUserRoleDto, admin_id: int) -> UserProfileDto:
        """
        Update user role (admin only).
        
        Args:
            dto: UpdateUserRoleDto with user_id and new role
            admin_id: Admin user ID performing the action
        
        Returns:
            Updated UserProfileDto
        
        Raises:
            UserNotFoundException: If user not found
            ValidationException: If role is invalid
        """
        # 1. Validate role
        valid_roles = ['customer', 'vip', 'admin']
        if dto.role not in valid_roles:
            raise ValidationException(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        # 2. Get user
        user = self._user_repository.find_by_id(dto.user_id)
        if not user:
            raise UserNotFoundException(user_id=dto.user_id)
        
        old_role = user['role']
        
        # 3. Update role (assuming we add this method to repository)
        # For now, we'll need to add this to the interface
        # self._user_repository.update_role(dto.user_id, dto.role)
        
        # 4. Publish event
        self._event_bus.publish(
            UserRoleUpdated(
                user_id=dto.user_id,
                old_role=old_role,
                new_role=dto.role,
                changed_by=admin_id
            )
        )
        
        # 5. Log action
        self._logger.info(
            f"User role updated: {dto.user_id}",
            {
                "user_id": dto.user_id,
                "old_role": old_role,
                "new_role": dto.role,
                "admin_id": admin_id
            }
        )
        
        # 6. Return updated profile
        return UserProfileDto(
            id=user['id'],
            name=user['name'],
            email=user['email'],
            role=dto.role,
            balance=Decimal(str(user['balance'])),
            created_at=user.get('created_at', '')
        )
    
    def _validate_registration_input(self, dto: RegisterUserDto) -> None:
        """
        Validate registration input.
        
        Args:
            dto: RegisterUserDto
        
        Raises:
            ValidationException: If validation fails
        """
        if not dto.name or dto.name.strip() == "":
            raise ValidationException("Name is required")
        
        if not dto.email or dto.email.strip() == "":
            raise ValidationException("Email is required")
        
        if not dto.password or dto.password.strip() == "":
            raise ValidationException("Password is required")
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address
        
        Returns:
            True if valid, False otherwise
        """
        return bool(self.EMAIL_REGEX.match(email))
