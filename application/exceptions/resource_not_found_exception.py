"""Resource not found exceptions"""


class ResourceNotFoundException(Exception):
    """Raised when a resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: any):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} with ID {resource_id} not found")


class CouponNotFoundException(ResourceNotFoundException):
    """Raised when coupon is not found"""
    
    def __init__(self, code: str):
        self.code = code
        super().__init__("Coupon", code)


class CouponExpiredException(Exception):
    """Raised when coupon has been fully used"""
    
    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Coupon '{code}' has reached its usage limit")
