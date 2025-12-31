"""Coupon Service - handles coupon management"""

from typing import Optional
from decimal import Decimal

from domain.interfaces.coupon_repository import ICouponRepository
from application.dtos.coupon_dtos import (
    CreateCouponDto,
    CouponDto,
    ValidateCouponDto
)
from application.exceptions.resource_not_found_exception import (
    CouponNotFoundException,
    CouponExpiredException
)
from application.exceptions.validation_exception import ValidationException
from infrastructure.logging.logger import ILogger


class CouponService:
    """
    Application service for coupon operations.
    
    Responsibilities:
    - Create and manage coupons
    - Validate coupon usage
    - Track coupon statistics
    """
    
    def __init__(
        self,
        coupon_repository: ICouponRepository,
        logger: ILogger
    ):
        """
        Initialize CouponService.
        
        Args:
            coupon_repository: Repository for coupon persistence
            logger: Logger for audit trail
        """
        self._coupon_repository = coupon_repository
        self._logger = logger
    
    def create_coupon(self, dto: CreateCouponDto, admin_id: int) -> CouponDto:
        """
        Create a new coupon (admin only).
        
        Args:
            dto: CreateCouponDto with coupon details
            admin_id: Admin user ID creating coupon
        
        Returns:
            CouponDto
        
        Raises:
            ValidationException: If validation fails
        """
        # Validate input
        if not dto.code or dto.code.strip() == "":
            raise ValidationException("Coupon code is required")
        
        if dto.discount_percentage < 0 or dto.discount_percentage > 100:
            raise ValidationException("Discount percentage must be between 0 and 100")
        
        if dto.max_uses <= 0:
            raise ValidationException("Max uses must be greater than 0")
        
        # Check if coupon already exists
        existing = self._coupon_repository.find_by_code(dto.code)
        if existing:
            raise ValidationException(f"Coupon code '{dto.code}' already exists")
        
        # Create coupon
        coupon_data = {
            'code': dto.code.upper(),
            'discount': dto.discount_percentage,
            'used': 0,
            'max_uses': dto.max_uses
        }
        
        self._coupon_repository.save(coupon_data)
        
        self._logger.info(
            f"Coupon created: {dto.code}",
            {"code": dto.code, "discount": dto.discount_percentage, "admin_id": admin_id}
        )
        
        return CouponDto(
            code=dto.code.upper(),
            discount_percentage=dto.discount_percentage,
            used_count=0,
            max_uses=dto.max_uses,
            is_valid=True
        )
    
    def validate_coupon(self, dto: ValidateCouponDto) -> CouponDto:
        """
        Validate a coupon code.
        
        Args:
            dto: ValidateCouponDto with coupon code
        
        Returns:
            CouponDto with validation result
        
        Raises:
            CouponNotFoundException: If coupon not found
            CouponExpiredException: If coupon is expired
        """
        coupon = self._coupon_repository.find_by_code(dto.code.upper())
        
        if not coupon:
            raise CouponNotFoundException(dto.code)
        
        # Check if coupon is still valid
        is_valid = coupon['used'] < coupon['max_uses']
        
        if not is_valid:
            raise CouponExpiredException(dto.code)
        
        return CouponDto(
            code=coupon['code'],
            discount_percentage=coupon['discount'],
            used_count=coupon['used'],
            max_uses=coupon['max_uses'],
            is_valid=is_valid
        )
    
    def get_coupon(self, code: str) -> Optional[CouponDto]:
        """
        Get coupon by code.
        
        Args:
            code: Coupon code
        
        Returns:
            CouponDto or None
        """
        coupon = self._coupon_repository.find_by_code(code.upper())
        
        if not coupon:
            return None
        
        return CouponDto(
            code=coupon['code'],
            discount_percentage=coupon['discount'],
            used_count=coupon['used'],
            max_uses=coupon['max_uses'],
            is_valid=coupon['used'] < coupon['max_uses']
        )
    
    def calculate_discount(self, code: str, amount: Decimal) -> Decimal:
        """
        Calculate discount amount for a coupon.
        
        Args:
            code: Coupon code
            amount: Order amount
        
        Returns:
            Discount amount
        
        Raises:
            CouponNotFoundException: If coupon not found
            CouponExpiredException: If coupon expired
        """
        coupon = self._coupon_repository.find_by_code(code.upper())
        
        if not coupon:
            raise CouponNotFoundException(code)
        
        if coupon['used'] >= coupon['max_uses']:
            raise CouponExpiredException(code)
        
        discount_percentage = Decimal(str(coupon['discount']))
        discount_amount = amount * (discount_percentage / Decimal("100"))
        
        return discount_amount
