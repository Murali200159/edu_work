from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password by checking if the stored value is a bcrypt hash or plain text.
    Handles potential whitespace padding from MS SQL Server and type safety.
    """
    if not hashed_password or not plain_password:
        return False
    
    # Strip whitespace to handle input errors and DB padding (NVARCHAR)
    plain_password = plain_password.strip()
    hashed_password = hashed_password.strip()
        
    # Standard bcrypt hashes start with '$2b$', '$2a$', etc.
    if hashed_password.startswith('$2'):
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # Fallback to direct comparison if verification fails due to format mismatch
            return plain_password == hashed_password
            
    # Legacy data case: direct plain-text comparison
    return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
