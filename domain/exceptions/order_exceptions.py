"""Order domain exceptions"""


class OrderException(Exception):
    """Base exception for order domain"""
    pass


class InvalidOrderStateException(OrderException):
    """Raised when order state transition is invalid"""
    pass


class InsufficientStockException(OrderException):
    """Raised when product stock is insufficient"""
    
    def __init__(self, product_name: str, available_stock: int, requested_quantity: int):
        self.product_name = product_name
        self.available_stock = available_stock
        self.requested_quantity = requested_quantity
        super().__init__(
            f"Insufficient stock for {product_name}. "
            f"Available: {available_stock}, Requested: {requested_quantity}"
        )


class EmptyOrderException(OrderException):
    """Raised when trying to create order without items"""
    
    def __init__(self):
        super().__init__("Order must contain at least one item")


class InvalidShippingAddressException(OrderException):
    """Raised when shipping address is invalid"""
    
    def __init__(self):
        super().__init__("Shipping address is required")
