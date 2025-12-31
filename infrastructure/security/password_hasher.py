"""Password hasher interface"""

from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Interface for password hashing"""
    
    @abstractmethod
    def hash(self, password: str) -> str:
        """
        Hash a password.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        pass
    
    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            password: Plain text password
            hashed: Hashed password
        
        Returns:
            True if password matches, False otherwise
        """
        pass
