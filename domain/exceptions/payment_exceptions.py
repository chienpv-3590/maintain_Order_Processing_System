"""Payment domain exceptions"""


class PaymentException(Exception):
    """Base exception for payment domain"""
    pass


class InsufficientBalanceException(PaymentException):
    """Raised when user has insufficient balance"""
    
    def __init__(self, required: float, available: float):
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient balance. Required: ${required:.2f}, Available: ${available:.2f}"
        )


class PaymentFailedException(PaymentException):
    """Raised when payment processing fails"""
    pass


class InvalidPaymentMethodException(PaymentException):
    """Raised when payment method is invalid"""
    
    def __init__(self, method: str):
        super().__init__(f"Invalid payment method: {method}")
