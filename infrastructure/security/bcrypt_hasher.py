"""Bcrypt password hasher implementation"""

import hashlib
from infrastructure.security.password_hasher import IPasswordHasher


class MD5PasswordHasher(IPasswordHasher):
    """
    MD5 password hasher (NOT RECOMMENDED FOR PRODUCTION).
    
    This is a simple implementation for backwards compatibility with the old system.
    In production, use BcryptPasswordHasher or Argon2PasswordHasher.
    """
    
    def hash(self, password: str) -> str:
        """
        Hash password using MD5.
        
        Args:
            password: Plain text password
        
        Returns:
            MD5 hash
        """
        return hashlib.md5(password.encode()).hexdigest()
    
    def verify(self, password: str, hashed: str) -> bool:
        """
        Verify password against MD5 hash.
        
        Args:
            password: Plain text password
            hashed: MD5 hash
        
        Returns:
            True if matches, False otherwise
        """
        return self.hash(password) == hashed


class BcryptPasswordHasher(IPasswordHasher):
    """
    Bcrypt password hasher (RECOMMENDED FOR PRODUCTION).
    
    Note: Requires bcrypt library: pip install bcrypt
    """
    
    def __init__(self):
        try:
            import bcrypt
            self._bcrypt = bcrypt
        except ImportError:
            raise ImportError(
                "bcrypt library is required. Install with: pip install bcrypt"
            )
    
    def hash(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Bcrypt hash
        """
        salt = self._bcrypt.gensalt()
        hashed = self._bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify(self, password: str, hashed: str) -> bool:
        """
        Verify password against bcrypt hash.
        
        Args:
            password: Plain text password
            hashed: Bcrypt hash
        
        Returns:
            True if matches, False otherwise
        """
        return self._bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
