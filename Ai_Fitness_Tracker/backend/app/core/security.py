from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
import hashlib
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Derive encryption key from SECRET_KEY
def get_fernet():
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))

def encrypt_totp_secret(secret: str) -> str:
    f = get_fernet()
    return f.encrypt(secret.encode()).decode()

def decrypt_totp_secret(encrypted_secret: str) -> str:
    f = get_fernet()
    return f.decrypt(encrypted_secret.encode()).decode()

def hash_password(password: str) -> str:
    # Truncate to 72 bytes to avoid bcrypt error
    return pwd_context.hash(password[:72])

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password[:72], hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
