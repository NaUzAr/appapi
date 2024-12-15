# app/auth.py

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from .schemas import Token
from .models import User
from sqlalchemy.orm import Session
from .dependencies import get_db
from passlib.context import CryptContext
import re

load_dotenv()

# Static Bearer Token untuk login dan register
STATIC_BEARER_TOKEN = os.getenv("STATIC_BEARER_TOKEN")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_static_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != STATIC_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token tidak valid atau tidak diizinkan",
        )
    return credentials.credentials

def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
    """
    Mengautentikasi pengguna berdasarkan identifier yang dapat berupa username atau email.
    """
    # Deteksi apakah identifier adalah email
    if re.match(r'[^@]+@[^@]+\.[^@]+', identifier):
        user = db.query(User).filter(User.email == identifier).first()
    else:
        user = db.query(User).filter(User.username == identifier).first()
    
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tidak dapat memverifikasi kredensial",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        identifier: str = payload.get("sub")
        if identifier is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Deteksi apakah identifier adalah email
    if re.match(r'[^@]+@[^@]+\.[^@]+', identifier):
        user = db.query(User).filter(User.email == identifier).first()
    else:
        user = db.query(User).filter(User.username == identifier).first()
    if user is None:
        raise credentials_exception
    return user
