"""Payment Service - handles payment processing"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from domain.interfaces.payment_repository import IPaymentRepository
from domain.interfaces.user_repository import IUserRepository
from domain.interfaces.order_repository import IOrderRepository
from domain.exceptions.payment_exceptions import (
    InsufficientBalanceException,
    PaymentFailedException,
    InvalidPaymentMethodException
)
from application.dtos.payment_dtos import (
    ProcessPaymentDto,
    PaymentDto,
    RefundPaymentDto
)
from application.exceptions.resource_not_found_exception import ResourceNotFoundException
from infrastructure.logging.logger import ILogger
from infrastructure.event_bus.event_bus import IEventBus


class PaymentService:
    """
    Application service for payment operations.
    
    Responsibilities:
    - Process payments
    - Handle refunds
    - Payment method validation
    """
    
    VALID_PAYMENT_METHODS = ['balance', 'credit_card', 'paypal']
    
    def __init__(
        self,
        payment_repository: IPaymentRepository,
        user_repository: IUserRepository,
        order_repository: IOrderRepository,
        event_bus: IEventBus,
        logger: ILogger
    ):
        """
        Initialize PaymentService with dependencies.
        
        Args:
            payment_repository: Repository for payment persistence
            user_repository: Repository for user data
            order_repository: Repository for order data
            event_bus: Event bus for publishing events
            logger: Logger for audit trail
        """
        self._payment_repository = payment_repository
        self._user_repository = user_repository
        self._order_repository = order_repository
        self._event_bus = event_bus
        self._logger = logger
    
    def process_payment(self, dto: ProcessPaymentDto) -> PaymentDto:
        """
        Process a payment.
        
        Args:
            dto: ProcessPaymentDto with payment details
        
        Returns:
            PaymentDto with payment result
        
        Raises:
            InvalidPaymentMethodException: If payment method is invalid
            InsufficientBalanceException: If balance payment fails
            ResourceNotFoundException: If user or order not found
        """
        # Validate payment method
        if dto.payment_method not in self.VALID_PAYMENT_METHODS:
            raise InvalidPaymentMethodException(dto.payment_method)
        
        # Get user
        user = self._user_repository.find_by_id(dto.user_id)
        if not user:
            raise ResourceNotFoundException("User", dto.user_id)
        
        # Get order
        order = self._order_repository.find_by_id(dto.order_id)
        if not order:
            raise ResourceNotFoundException("Order", dto.order_id)
        
        # Process based on payment method
        if dto.payment_method == 'balance':
            return self._process_balance_payment(dto, user)
        elif dto.payment_method == 'credit_card':
            return self._process_credit_card_payment(dto)
        elif dto.payment_method == 'paypal':
            return self._process_paypal_payment(dto)
    
    def _process_balance_payment(self, dto: ProcessPaymentDto, user: dict) -> PaymentDto:
        """Process payment using user balance"""
        user_balance = Decimal(str(user['balance']))
        
        if user_balance < dto.amount:
            raise InsufficientBalanceException(
                required=float(dto.amount),
                available=float(user_balance)
            )
        
        # Deduct balance
        self._user_repository.update_balance(dto.user_id, -float(dto.amount))
        
        # Create payment record
        payment_data = {
            'order_id': dto.order_id,
            'amount': float(dto.amount),
            'method': 'balance',
            'status': 'completed',
            'transaction_id': f'BAL-{dto.order_id}-{int(datetime.now().timestamp())}',
            'created_at': datetime.now().isoformat()
        }
        
        payment_id = self._payment_repository.save(payment_data)
        
        # Update order status
        self._order_repository.update_status(dto.order_id, 'paid')
        
        self._logger.info(
            f"Balance payment processed for order {dto.order_id}",
            {"order_id": dto.order_id, "amount": float(dto.amount), "user_id": dto.user_id}
        )
        
        return PaymentDto(
            id=payment_id,
            order_id=dto.order_id,
            amount=dto.amount,
            method='balance',
            status='completed',
            transaction_id=payment_data['transaction_id'],
            created_at=payment_data['created_at']
        )
    
    def _process_credit_card_payment(self, dto: ProcessPaymentDto) -> PaymentDto:
        """Process credit card payment (mock implementation)"""
        # In production, integrate with payment gateway (Stripe, etc.)
        
        payment_data = {
            'order_id': dto.order_id,
            'amount': float(dto.amount),
            'method': 'credit_card',
            'status': 'pending',
            'transaction_id': f'CC-{dto.order_id}-{int(datetime.now().timestamp())}',
            'created_at': datetime.now().isoformat()
        }
        
        payment_id = self._payment_repository.save(payment_data)
        
        self._logger.info(
            f"Credit card payment initiated for order {dto.order_id}",
            {"order_id": dto.order_id, "amount": float(dto.amount)}
        )
        
        return PaymentDto(
            id=payment_id,
            order_id=dto.order_id,
            amount=dto.amount,
            method='credit_card',
            status='pending',
            transaction_id=payment_data['transaction_id'],
            created_at=payment_data['created_at']
        )
    
    def _process_paypal_payment(self, dto: ProcessPaymentDto) -> PaymentDto:
        """Process PayPal payment (mock implementation)"""
        # In production, integrate with PayPal API
        
        payment_data = {
            'order_id': dto.order_id,
            'amount': float(dto.amount),
            'method': 'paypal',
            'status': 'pending',
            'transaction_id': f'PP-{dto.order_id}-{int(datetime.now().timestamp())}',
            'created_at': datetime.now().isoformat()
        }
        
        payment_id = self._payment_repository.save(payment_data)
        
        self._logger.info(
            f"PayPal payment initiated for order {dto.order_id}",
            {"order_id": dto.order_id, "amount": float(dto.amount)}
        )
        
        return PaymentDto(
            id=payment_id,
            order_id=dto.order_id,
            amount=dto.amount,
            method='paypal',
            status='pending',
            transaction_id=payment_data['transaction_id'],
            created_at=payment_data['created_at']
        )
    
    def get_payment_by_order_id(self, order_id: int) -> Optional[PaymentDto]:
        """Get payment by order ID"""
        payment = self._payment_repository.find_by_order_id(order_id)
        
        if not payment:
            return None
        
        return PaymentDto(
            id=payment['id'],
            order_id=payment['order_id'],
            amount=Decimal(str(payment['amount'])),
            method=payment['method'],
            status=payment['status'],
            transaction_id=payment.get('transaction_id'),
            created_at=payment['created_at']
        )
    
    def refund_payment(self, dto: RefundPaymentDto) -> PaymentDto:
        """
        Refund a payment (admin only).
        
        Args:
            dto: RefundPaymentDto
        
        Returns:
            Updated PaymentDto
        
        Raises:
            ResourceNotFoundException: If payment not found
        """
        payment = self._payment_repository.find_by_id(dto.payment_id)
        if not payment:
            raise ResourceNotFoundException("Payment", dto.payment_id)
        
        # Update payment status
        self._payment_repository.update_status(dto.payment_id, 'refunded')
        
        # If balance payment, refund to user balance
        if payment['method'] == 'balance':
            order = self._order_repository.find_by_id(payment['order_id'])
            if order:
                refund_amount = dto.amount if dto.amount else Decimal(str(payment['amount']))
                self._user_repository.update_balance(order['user_id'], float(refund_amount))
        
        self._logger.info(
            f"Payment refunded: {dto.payment_id}",
            {"payment_id": dto.payment_id, "amount": float(dto.amount) if dto.amount else payment['amount']}
        )
        
        updated_payment = self._payment_repository.find_by_id(dto.payment_id)
        
        return PaymentDto(
            id=updated_payment['id'],
            order_id=updated_payment['order_id'],
            amount=Decimal(str(updated_payment['amount'])),
            method=updated_payment['method'],
            status='refunded',
            transaction_id=updated_payment.get('transaction_id'),
            created_at=updated_payment['created_at']
        )
