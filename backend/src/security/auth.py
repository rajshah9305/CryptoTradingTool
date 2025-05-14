import jwt
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class SecurityService:
    def __init__(self):
        self.JWT_SECRET = os.environ.get("JWT_SECRET")
        if not self.JWT_SECRET:
            raise ValueError("JWT_SECRET is not set in environment variables")
        self.JWT_EXPIRY = "1h"
        self.REFRESH_TOKEN_EXPIRY = "7d"

    async def hash_password(self, password: str) -> str:
        """Hash a password using Argon2id-like strong hashing (simplified version using hashlib)"""
        salt = secrets.token_bytes(16)
        # In production, use a proper Argon2id implementation like argon2-cffi
        # This is a simplified version for compatibility
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt, 
            100000  # Iterations
        )
        return f"{salt.hex()}${hash_obj.hex()}"

    async def verify_password(self, stored_hash: str, password: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt_hex, hash_hex = stored_hash.split('$')
            salt = bytes.fromhex(salt_hex)
            
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode('utf-8'), 
                salt, 
                100000  # Same iterations as used for hashing
            )
            
            return hash_obj.hex() == hash_hex
        except Exception:
            return False

    def _get_expiry_datetime(self, expiry_str: str) -> datetime:
        """Convert expiry string like '1h', '7d' to datetime"""
        unit = expiry_str[-1]
        value = int(expiry_str[:-1])
        
        if unit == 'h':
            return datetime.utcnow() + timedelta(hours=value)
        elif unit == 'd':
            return datetime.utcnow() + timedelta(days=value)
        else:
            raise ValueError(f"Unsupported expiry format: {expiry_str}")

    def generate_tokens(self, user: Dict[str, Any]) -> Dict[str, str]:
        """Generate access and refresh tokens for a user"""
        access_token_expiry = self._get_expiry_datetime(self.JWT_EXPIRY)
        refresh_token_expiry = self._get_expiry_datetime(self.REFRESH_TOKEN_EXPIRY)
        
        access_token = jwt.encode(
            {
                "userId": str(user["id"]),
                "roles": user.get("roles", []),
                "exp": int(access_token_expiry.timestamp())
            },
            self.JWT_SECRET,
            algorithm="HS256"
        )
        
        refresh_token = jwt.encode(
            {
                "userId": str(user["id"]),
                "tokenVersion": user.get("tokenVersion", 0),
                "exp": int(refresh_token_expiry.timestamp())
            },
            self.JWT_SECRET,
            algorithm="HS256"
        )
        
        return {"accessToken": access_token, "refreshToken": refresh_token}

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a JWT token and return its payload if valid"""
        try:
            return jwt.decode(token, self.JWT_SECRET, algorithms=["HS256"])
        except:
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate a new access token from a refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.JWT_SECRET, algorithms=["HS256"])
            access_token_expiry = self._get_expiry_datetime(self.JWT_EXPIRY)
            
            return jwt.encode(
                {
                    "userId": payload["userId"],
                    "roles": payload.get("roles", []),
                    "exp": int(access_token_expiry.timestamp())
                },
                self.JWT_SECRET,
                algorithm="HS256"
            )
        except:
            return None
