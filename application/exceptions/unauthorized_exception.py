"""Authorization exceptions"""


class UnauthorizedException(Exception):
    """Raised when user is not authorized to perform action"""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message)


class NotAuthenticatedException(UnauthorizedException):
    """Raised when user is not authenticated"""
    
    def __init__(self):
        super().__init__("User must be logged in")
