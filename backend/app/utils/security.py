from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Strictly verifies a password using bcrypt.
    No plain-text fallback allowed.
    """
    if not hashed_password or not plain_password:
        return False
    
    # Strip potential padding from MS SQL
    plain_password = plain_password.strip()
    hashed_password = hashed_password.strip()

    # LOGGING FOR DEBUGGING (Development only/Securely masked in logs)
    # We log the first 10 chars of hash to verify source vs destination
    import logging
    logging.getLogger(__name__).info(f"🔍 Security Check - Stored Hash: {hashed_password[:10]}... | Provided password starts with: {plain_password[:2]}...")

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logging.getLogger(__name__).error(f"❌ Verification Error: {str(e)}")
        return False

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
