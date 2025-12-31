"""Product domain exceptions"""


class ProductException(Exception):
    """Base exception for product domain"""
    pass


class ProductNotFoundException(ProductException):
    """Raised when product is not found"""
    
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product with ID {product_id} not found")


class InvalidPriceException(ProductException):
    """Raised when product price is invalid"""
    
    def __init__(self):
        super().__init__("Product price must be greater than 0")


class InvalidStockException(ProductException):
    """Raised when stock quantity is invalid"""
    
    def __init__(self):
        super().__init__("Stock quantity cannot be negative")
