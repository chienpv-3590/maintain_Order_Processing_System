"""Validation exceptions"""


class ValidationException(Exception):
    """Raised when validation fails"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
