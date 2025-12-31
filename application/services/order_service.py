"""Order Service - handles order creation and management use cases"""

import json
from datetime import datetime
from decimal import Decimal
from typing import List

from domain.interfaces.order_repository import IOrderRepository
from domain.interfaces.product_repository import IProductRepository
from domain.interfaces.coupon_repository import ICouponRepository
from domain.interfaces.user_repository import IUserRepository
from domain.exceptions.order_exceptions import (
    EmptyOrderException,
    InvalidShippingAddressException,
    InsufficientStockException
)
from domain.exceptions.product_exceptions import ProductNotFoundException
from application.exceptions.resource_not_found_exception import (
    CouponNotFoundException,
    CouponExpiredException
)
from application.exceptions.unauthorized_exception import NotAuthenticatedException
from application.dtos.order_dtos import (
    CreateOrderDto,
    OrderSummaryDto,
    OrderBreakdownDto,
    OrderItemResponseDto
)


class OrderService:
    """
    Application service for order operations.
    
    Responsibilities:
    - Orchestrate order creation workflow
    - Validate stock availability
    - Apply coupons and calculate totals
    - Coordinate with payment service
    - Manage transactions
    """
    
    # Constants
    TAX_RATE = Decimal("0.1")
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        product_repository: IProductRepository,
        coupon_repository: ICouponRepository,
        user_repository: IUserRepository
    ):
        """
        Initialize OrderService with dependencies.
        
        Args:
            order_repository: Repository for order persistence
            product_repository: Repository for product data
            coupon_repository: Repository for coupon data
            user_repository: Repository for user data
        """
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._coupon_repository = coupon_repository
        self._user_repository = user_repository
    
    def create_order(self, dto: CreateOrderDto) -> OrderSummaryDto:
        """
        Create a new order.
        
        Steps:
        1. Validate user is authenticated
        2. Validate order has items and shipping address
        3. Validate product availability and reserve stock
        4. Apply coupon if provided
        5. Calculate tax and total
        6. Process payment if VIP user with balance
        7. Save order
        8. Return order summary
        
        Args:
            dto: CreateOrderDto with order details
        
        Returns:
            OrderSummaryDto with order summary
        
        Raises:
            NotAuthenticatedException: If user_id is not provided
            EmptyOrderException: If order has no items
            InvalidShippingAddressException: If shipping address is missing
            ProductNotFoundException: If product doesn't exist
            InsufficientStockException: If product stock is insufficient
            CouponNotFoundException: If coupon code is invalid
            CouponExpiredException: If coupon has reached usage limit
        """
        # 1. Validate user authentication
        if not dto.user_id:
            raise NotAuthenticatedException()
        
        # 2. Validate order data
        if not dto.items or len(dto.items) == 0:
            raise EmptyOrderException()
        
        if not dto.shipping_address or dto.shipping_address.strip() == "":
            raise InvalidShippingAddressException()
        
        # 3. Validate products and calculate subtotal
        order_items = []
        subtotal = Decimal("0")
        
        for item_dto in dto.items:
            # Fetch product
            product = self._product_repository.find_by_id(item_dto.product_id)
            if not product:
                raise ProductNotFoundException(item_dto.product_id)
            
            # Check stock availability
            if product['stock'] < item_dto.quantity:
                raise InsufficientStockException(
                    product['name'],
                    product['stock'],
                    item_dto.quantity
                )
            
            # Calculate item subtotal
            item_price = Decimal(str(product['price']))
            item_subtotal = item_price * item_dto.quantity
            subtotal += item_subtotal
            
            # Reserve stock (decrease)
            self._product_repository.update_stock(
                item_dto.product_id,
                -item_dto.quantity
            )
            
            # Build order item
            order_items.append({
                'product_id': product['id'],
                'name': product['name'],
                'price': float(item_price),
                'quantity': item_dto.quantity,
                'subtotal': float(item_subtotal)
            })
        
        # 4. Apply coupon discount
        discount = Decimal("0")
        if dto.coupon_code:
            coupon = self._coupon_repository.find_by_code(dto.coupon_code)
            
            if not coupon:
                raise CouponNotFoundException(dto.coupon_code)
            
            # Check if coupon is still valid
            if coupon['used'] >= coupon['max_uses']:
                raise CouponExpiredException(dto.coupon_code)
            
            # Calculate discount
            discount_percentage = Decimal(str(coupon['discount']))
            discount = subtotal * (discount_percentage / Decimal("100"))
            
            # Increment coupon usage
            self._coupon_repository.increment_usage(dto.coupon_code)
        
        # 5. Calculate tax
        taxable_amount = subtotal - discount
        tax = taxable_amount * self.TAX_RATE
        
        # 6. Calculate final total
        final_total = subtotal - discount + tax
        
        # 7. Determine payment status and process payment for VIP users
        user = self._user_repository.find_by_id(dto.user_id)
        payment_status = "pending_payment"
        
        if user and user['role'] == 'vip':
            user_balance = Decimal(str(user['balance']))
            if user_balance >= final_total:
                # Deduct from balance
                self._user_repository.update_balance(
                    dto.user_id,
                    -float(final_total)
                )
                payment_status = "paid_with_balance"
        
        # 8. Generate order ID (simple counter-based approach)
        # In production, use database auto-increment or UUID
        order_id = self._generate_order_id()
        
        # 9. Save order
        order_data = {
            'id': order_id,
            'user_id': dto.user_id,
            'items': json.dumps(order_items),
            'total': float(final_total),
            'status': payment_status,
            'created_at': datetime.now().isoformat(),
            'shipping_address': dto.shipping_address
        }
        
        saved_order_id = self._order_repository.save(order_data)
        
        # 10. Build and return summary
        breakdown = OrderBreakdownDto(
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=final_total
        )
        
        return OrderSummaryDto(
            success=True,
            order_id=saved_order_id,
            total=final_total,
            status=payment_status,
            breakdown=breakdown
        )
    
    def _generate_order_id(self) -> int:
        """
        Generate a new order ID.
        
        Note: This is a simple implementation. In production:
        - Use database auto-increment
        - Use UUID for distributed systems
        - Use a dedicated ID generation service
        
        Returns:
            New order ID
        """
        # Simple implementation: use timestamp-based ID
        return int(datetime.now().timestamp() * 1000)
    
    def get_order_by_id(self, order_id: int, user_id: int, is_admin: bool = False) -> dict:
        """
        Get order by ID.
        
        Args:
            order_id: Order ID to fetch
            user_id: Current user ID
            is_admin: Whether current user is admin
        
        Returns:
            Order details
        
        Raises:
            ResourceNotFoundException: If order not found
            UnauthorizedException: If user doesn't own the order and is not admin
        """
        order = self._order_repository.find_by_id(order_id)
        
        if not order:
            from application.exceptions.resource_not_found_exception import ResourceNotFoundException
            raise ResourceNotFoundException("Order", order_id)
        
        # Check authorization
        if not is_admin and order['user_id'] != user_id:
            from application.exceptions.unauthorized_exception import UnauthorizedException
            raise UnauthorizedException("You don't have permission to view this order")
        
        return order
    
    def get_user_orders(self, user_id: int) -> List[dict]:
        """
        Get all orders for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of orders
        """
        return self._order_repository.find_by_user_id(user_id)
    
    def get_all_orders(self) -> List[dict]:
        """
        Get all orders (admin only).
        
        Returns:
            List of all orders
        """
        return self._order_repository.find_all()
    
    def update_order_status(self, order_id: int, new_status: str) -> None:
        """
        Update order status (admin only).
        
        Args:
            order_id: Order ID
            new_status: New status value
        
        Raises:
            ResourceNotFoundException: If order not found
        """
        order = self._order_repository.find_by_id(order_id)
        
        if not order:
            from application.exceptions.resource_not_found_exception import ResourceNotFoundException
            raise ResourceNotFoundException("Order", order_id)
        
        # Validate status
        valid_statuses = [
            "pending_payment", "paid", "processing", 
            "shipped", "delivered", "cancelled"
        ]
        
        if new_status not in valid_statuses:
            from application.exceptions.validation_exception import ValidationException
            raise ValidationException(f"Invalid status: {new_status}")
        
        self._order_repository.update_status(order_id, new_status)
