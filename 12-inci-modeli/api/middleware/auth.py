"""
JWT Authentication System for 12. İnci Modeli
Secure user authentication with JWT tokens
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import secrets

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()


# ============================================
# Password Hashing
# ============================================

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# JWT Token Functions
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ============================================
# API Key Functions
# ============================================

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """Verify API key (we can hash these too for extra security)"""
    return api_key == stored_hash  # Simple comparison for now


# ============================================
# FastAPI Dependencies
# ============================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> dict:
    """
    Get current user from JWT token
    Use as dependency in protected routes
    """
    token = credentials.credentials

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Get user from database
        from models.database import User
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_current_premium_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get current premium user"""
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    return current_user


# ============================================
# Authentication Schemas (Pydantic)
# ============================================

from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None


# ============================================
# To add to main.py
# ============================================

"""
Add these endpoints to main.py:

@app.post("/api/v1/auth/register", response_model=Token)
async def register(user_data: UserRegister, db = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing:
        raise HTTPException(400, "User already exists")

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        api_key=generate_api_key()
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token({"sub": user.id, "username": user.username})
    refresh_token = create_refresh_token({"sub": user.id})

    return Token(access_token=access_token, refresh_token=refresh_token)

@app.post("/api/v1/auth/login", response_model=Token)
async def login(credentials: UserLogin, db = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Generate tokens
    access_token = create_access_token({"sub": user.id, "username": user.username})
    refresh_token = create_refresh_token({"sub": user.id})

    return Token(access_token=access_token, refresh_token=refresh_token)

@app.get("/api/v1/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_premium": current_user.is_premium,
        "api_calls_count": current_user.api_calls_count,
        "api_calls_limit": current_user.api_calls_limit
    }

# Protected endpoint example
@app.post("/api/v1/emotion/analyze-protected")
async def analyze_protected(
    request: EmotionAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    # Check rate limit
    if current_user.api_calls_count >= current_user.api_calls_limit:
        raise HTTPException(429, "API call limit exceeded")

    # Increment counter
    current_user.api_calls_count += 1
    db.commit()

    # ... rest of emotion analysis logic
"""
