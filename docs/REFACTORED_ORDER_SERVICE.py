"""
REFACTORED OrderService - Improved version following best practices

Key improvements:
1. Extract methods for SRP
2. Add Unit of Work pattern
3. Move business logic to domain
4. Add domain events
5. Strategy pattern for payment
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from domain.interfaces.order_repository import IOrderRepository
from domain.interfaces.product_repository import IProductRepository
from domain.interfaces.coupon_repository import ICouponRepository
from domain.interfaces.user_repository import IUserRepository
from domain.interfaces.unit_of_work import IUnitOfWork
from domain.services.pricing_service import PricingService
from domain.services.inventory_service import InventoryService
from domain.events.order_events import OrderCreated
from infrastructure.event_bus.event_bus import IEventBus
from application.dtos.order_dtos import CreateOrderDto, OrderSummaryDto
from application.strategies.payment_strategy import PaymentStrategyFactory


class ImprovedOrderService:
    """
    Refactored OrderService with better separation of concerns.
    
    Changes:
    - Extracted calculation logic to domain services
    - Added Unit of Work for transaction management
    - Added event bus for domain events
    - Reduced method complexity
    """
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        product_repository: IProductRepository,
        coupon_repository: ICouponRepository,
        user_repository: IUserRepository,
        pricing_service: PricingService,  # New: Domain service
        inventory_service: InventoryService,  # New: Domain service
        unit_of_work: IUnitOfWork,  # New: Transaction management
        event_bus: IEventBus,  # New: Event publishing
        payment_strategy_factory: PaymentStrategyFactory  # New: Payment strategy
    ):
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._coupon_repository = coupon_repository
        self._user_repository = user_repository
        self._pricing_service = pricing_service
        self._inventory_service = inventory_service
        self._unit_of_work = unit_of_work
        self._event_bus = event_bus
        self._payment_strategy_factory = payment_strategy_factory
    
    def create_order(self, dto: CreateOrderDto) -> OrderSummaryDto:
        """
        Create order with transaction safety.
        
        Improvements:
        - Wrapped in transaction (Unit of Work)
        - Extracted validation
        - Extracted calculation
        - Publishes domain events
        """
        # Begin transaction
        with self._unit_of_work:
            # 1. Validate input
            self._validate_order_input(dto)
            
            # 2. Reserve inventory (with rollback on failure)
            reservation = self._inventory_service.reserve_items(dto.items)
            
            # 3. Calculate pricing (domain logic)
            pricing = self._pricing_service.calculate_order_pricing(
                items=reservation.items,
                coupon_code=dto.coupon_code
            )
            
            # 4. Process payment
            user = self._user_repository.find_by_id(dto.user_id)
            payment_strategy = self._payment_strategy_factory.get_strategy(user)
            payment_result = payment_strategy.process(pricing.total, user)
            
            # 5. Create order entity
            order_id = self._create_order_entity(
                dto=dto,
                pricing=pricing,
                payment_status=payment_result.status
            )
            
            # 6. Publish domain event
            event = OrderCreated(
                order_id=order_id,
                user_id=dto.user_id,
                total=float(pricing.total),
                items=reservation.items
            )
            self._event_bus.publish(event)
            
            # 7. Commit transaction
            self._unit_of_work.commit()
            
            return OrderSummaryDto(
                success=True,
                order_id=order_id,
                total=pricing.total,
                status=payment_result.status,
                breakdown=pricing.breakdown
            )
    
    def _validate_order_input(self, dto: CreateOrderDto) -> None:
        """Validate order input (extracted for clarity)"""
        from domain.exceptions.order_exceptions import (
            EmptyOrderException,
            InvalidShippingAddressException
        )
        from application.exceptions.unauthorized_exception import NotAuthenticatedException
        
        if not dto.user_id:
            raise NotAuthenticatedException()
        
        if not dto.items or len(dto.items) == 0:
            raise EmptyOrderException()
        
        if not dto.shipping_address or dto.shipping_address.strip() == "":
            raise InvalidShippingAddressException()
    
    def _create_order_entity(
        self,
        dto: CreateOrderDto,
        pricing,
        payment_status: str
    ) -> int:
        """Create and save order entity"""
        order_data = {
            'user_id': dto.user_id,
            'items': json.dumps([item.to_dict() for item in pricing.items]),
            'total': float(pricing.total),
            'status': payment_status,
            'created_at': datetime.now().isoformat(),
            'shipping_address': dto.shipping_address
        }
        
        return self._order_repository.save(order_data)


# =====================================================
# SUPPORTING CLASSES
# =====================================================


class PricingService:
    """
    Domain Service for pricing calculations.
    
    Benefits:
    - Business logic in domain layer
    - Reusable across services
    - Easy to test in isolation
    """
    
    TAX_RATE = Decimal("0.1")
    
    def __init__(self, coupon_repository: ICouponRepository):
        self._coupon_repository = coupon_repository
    
    def calculate_order_pricing(self, items: List, coupon_code: Optional[str] = None):
        """Calculate complete pricing with tax and discounts"""
        # Calculate subtotal
        subtotal = sum(
            Decimal(str(item['price'])) * item['quantity']
            for item in items
        )
        
        # Apply coupon
        discount = self._calculate_discount(subtotal, coupon_code)
        
        # Calculate tax
        taxable_amount = subtotal - discount
        tax = taxable_amount * self.TAX_RATE
        
        # Final total
        total = subtotal - discount + tax
        
        return PricingResult(
            items=items,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total
        )
    
    def _calculate_discount(self, subtotal: Decimal, coupon_code: Optional[str]) -> Decimal:
        """Calculate discount amount"""
        if not coupon_code:
            return Decimal("0")
        
        from application.exceptions.resource_not_found_exception import (
            CouponNotFoundException,
            CouponExpiredException
        )
        
        coupon = self._coupon_repository.find_by_code(coupon_code)
        if not coupon:
            raise CouponNotFoundException(coupon_code)
        
        if coupon['used'] >= coupon['max_uses']:
            raise CouponExpiredException(coupon_code)
        
        discount_percentage = Decimal(str(coupon['discount']))
        discount = subtotal * (discount_percentage / Decimal("100"))
        
        # Increment usage
        self._coupon_repository.increment_usage(coupon_code)
        
        return discount


class InventoryService:
    """
    Domain Service for inventory management.
    
    Benefits:
    - Encapsulates stock reservation logic
    - Can implement pessimistic locking
    - Handles rollback on transaction failure
    """
    
    def __init__(self, product_repository: IProductRepository):
        self._product_repository = product_repository
    
    def reserve_items(self, items):
        """Reserve inventory for order"""
        from domain.exceptions.product_exceptions import ProductNotFoundException
        from domain.exceptions.order_exceptions import InsufficientStockException
        
        reserved_items = []
        
        for item_dto in items:
            product = self._product_repository.find_by_id(item_dto.product_id)
            
            if not product:
                raise ProductNotFoundException(item_dto.product_id)
            
            if product['stock'] < item_dto.quantity:
                raise InsufficientStockException(
                    product['name'],
                    product['stock'],
                    item_dto.quantity
                )
            
            # Reserve stock
            self._product_repository.update_stock(
                item_dto.product_id,
                -item_dto.quantity
            )
            
            reserved_items.append({
                'product_id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': item_dto.quantity
            })
        
        return InventoryReservation(reserved_items)


# =====================================================
# VALUE OBJECTS
# =====================================================


class PricingResult:
    """Value object for pricing calculation result"""
    
    def __init__(self, items, subtotal, discount, tax, total):
        self.items = items
        self.subtotal = subtotal
        self.discount = discount
        self.tax = tax
        self.total = total
        
        # Create breakdown DTO
        from application.dtos.order_dtos import OrderBreakdownDto
        self.breakdown = OrderBreakdownDto(
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total
        )


class InventoryReservation:
    """Value object for inventory reservation result"""
    
    def __init__(self, items):
        self.items = items


# =====================================================
# UNIT OF WORK PATTERN
# =====================================================


class IUnitOfWork:
    """
    Interface for Unit of Work pattern.
    
    Benefits:
    - Transaction management
    - Atomic operations
    - Automatic rollback on error
    """
    
    def __enter__(self):
        """Begin transaction"""
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback"""
        if exc_type is not None:
            self.rollback()
        return False
    
    def commit(self):
        """Commit transaction"""
        pass
    
    def rollback(self):
        """Rollback transaction"""
        pass


# =====================================================
# PAYMENT STRATEGY PATTERN
# =====================================================


class PaymentStrategy:
    """Base strategy for payment processing"""
    
    def process(self, amount: Decimal, user: dict):
        """Process payment"""
        raise NotImplementedError


class VIPBalancePaymentStrategy(PaymentStrategy):
    """Payment strategy for VIP users using balance"""
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    def process(self, amount: Decimal, user: dict):
        user_balance = Decimal(str(user['balance']))
        
        if user_balance >= amount:
            self._user_repository.update_balance(user['id'], -float(amount))
            return PaymentResult(status='paid_with_balance', success=True)
        
        return PaymentResult(status='pending_payment', success=False)


class StandardPaymentStrategy(PaymentStrategy):
    """Payment strategy for standard users"""
    
    def process(self, amount: Decimal, user: dict):
        return PaymentResult(status='pending_payment', success=True)


class PaymentStrategyFactory:
    """Factory for creating payment strategies"""
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    def get_strategy(self, user: dict) -> PaymentStrategy:
        """Get appropriate payment strategy based on user"""
        if user and user.get('role') == 'vip':
            return VIPBalancePaymentStrategy(self._user_repository)
        return StandardPaymentStrategy()


class PaymentResult:
    """Value object for payment result"""
    
    def __init__(self, status: str, success: bool):
        self.status = status
        self.success = success
