"""User domain exceptions"""


class UserException(Exception):
    """Base exception for user domain"""
    pass


class InvalidEmailException(UserException):
    """Raised when email format is invalid"""
    
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Invalid email format: {email}")


class WeakPasswordException(UserException):
    """Raised when password doesn't meet requirements"""
    
    def __init__(self, message: str = "Password must be at least 8 characters"):
        super().__init__(message)


class EmailAlreadyExistsException(UserException):
    """Raised when email is already registered"""
    
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email already exists: {email}")


class InvalidCredentialsException(UserException):
    """Raised when login credentials are invalid"""
    
    def __init__(self):
        super().__init__("Invalid email or password")


class UserNotFoundException(UserException):
    """Raised when user is not found"""
    
    def __init__(self, user_id: int = None, email: str = None):
        if user_id:
            super().__init__(f"User with ID {user_id} not found")
        elif email:
            super().__init__(f"User with email {email} not found")
        else:
            super().__init__("User not found")
