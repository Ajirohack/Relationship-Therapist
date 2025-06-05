"""Authentication and Authorization System"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import sqlite3
import hashlib
import secrets
from enum import Enum

from config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class UserRole(str, Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    subscription_expires: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    token_type: Optional[str] = None

class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self, db_path: str = "relationship_therapist.db"):
        self.db_path = db_path
        self._init_auth_tables()
    
    def _init_auth_tables(self):
        """Initialize authentication tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    hashed_password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    subscription_expires TIMESTAMP,
                    email_verified BOOLEAN DEFAULT 0,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            """)
            
            # Refresh tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_refresh_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_revoked BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES auth_users (id)
                )
            """)
            
            # User sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES auth_users (id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Authentication tables initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize auth tables: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": TokenType.ACCESS})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token"""
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "type": TokenType.REFRESH,
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        }
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        
        # Store refresh token hash in database
        self._store_refresh_token(user_id, encoded_jwt, expire)
        
        return encoded_jwt
    
    def _store_refresh_token(self, user_id: str, token: str, expires_at: datetime):
        """Store refresh token hash in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            token_id = secrets.token_urlsafe(16)
            
            cursor.execute("""
                INSERT INTO auth_refresh_tokens (id, user_id, token_hash, expires_at)
                VALUES (?, ?, ?, ?)
            """, (token_id, user_id, token_hash, expires_at))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store refresh token: {e}")
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute(
                "SELECT id FROM auth_users WHERE email = ? OR username = ?",
                (user_data.email, user_data.username)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email or username already exists"
                )
            
            # Create new user
            user_id = secrets.token_urlsafe(16)
            hashed_password = self.hash_password(user_data.password)
            
            cursor.execute("""
                INSERT INTO auth_users (id, email, username, full_name, hashed_password)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                user_data.email,
                user_data.username,
                user_data.full_name,
                hashed_password
            ))
            
            conn.commit()
            conn.close()
            
            return await self.get_user_by_id(user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for account lockout
            cursor.execute("""
                SELECT failed_login_attempts, locked_until FROM auth_users 
                WHERE email = ?
            """, (email,))
            
            result = cursor.fetchone()
            if result:
                failed_attempts, locked_until = result
                if locked_until and datetime.fromisoformat(locked_until) > datetime.utcnow():
                    raise HTTPException(
                        status_code=status.HTTP_423_LOCKED,
                        detail="Account is temporarily locked due to too many failed login attempts"
                    )
            
            # Get user data
            cursor.execute("""
                SELECT id, email, username, full_name, hashed_password, role, is_active,
                       created_at, last_login, subscription_expires
                FROM auth_users WHERE email = ?
            """, (email,))
            
            user_data = cursor.fetchone()
            if not user_data:
                self._increment_failed_attempts(email)
                return None
            
            user_id, email, username, full_name, hashed_password, role, is_active, created_at, last_login, subscription_expires = user_data
            
            if not self.verify_password(password, hashed_password):
                self._increment_failed_attempts(email)
                return None
            
            if not is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is deactivated"
                )
            
            # Reset failed attempts and update last login
            cursor.execute("""
                UPDATE auth_users 
                SET failed_login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (email,))
            
            conn.commit()
            conn.close()
            
            return User(
                id=user_id,
                email=email,
                username=username,
                full_name=full_name,
                role=UserRole(role),
                is_active=bool(is_active),
                created_at=datetime.fromisoformat(created_at),
                last_login=datetime.fromisoformat(last_login) if last_login else None,
                subscription_expires=datetime.fromisoformat(subscription_expires) if subscription_expires else None
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    def _increment_failed_attempts(self, email: str):
        """Increment failed login attempts and lock account if necessary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE auth_users 
                SET failed_login_attempts = failed_login_attempts + 1
                WHERE email = ?
            """, (email,))
            
            # Lock account after 5 failed attempts for 30 minutes
            cursor.execute("""
                UPDATE auth_users 
                SET locked_until = datetime('now', '+30 minutes')
                WHERE email = ? AND failed_login_attempts >= 5
            """, (email,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to increment failed attempts: {e}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, username, full_name, role, is_active,
                       created_at, last_login, subscription_expires
                FROM auth_users WHERE id = ?
            """, (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if not user_data:
                return None
            
            user_id, email, username, full_name, role, is_active, created_at, last_login, subscription_expires = user_data
            
            return User(
                id=user_id,
                email=email,
                username=username,
                full_name=full_name,
                role=UserRole(role),
                is_active=bool(is_active),
                created_at=datetime.fromisoformat(created_at),
                last_login=datetime.fromisoformat(last_login) if last_login else None,
                subscription_expires=datetime.fromisoformat(subscription_expires) if subscription_expires else None
            )
            
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    async def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("user_id")
            email: str = payload.get("email")
            role: str = payload.get("role")
            token_type: str = payload.get("type")
            
            if user_id is None:
                return None
            
            return TokenData(
                user_id=user_id,
                email=email,
                role=role,
                token_type=token_type
            )
            
        except JWTError:
            return None
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("user_id")
            token_type: str = payload.get("type")
            jti: str = payload.get("jti")
            
            if token_type != TokenType.REFRESH or not user_id:
                return None
            
            # Check if refresh token exists and is not revoked
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            cursor.execute("""
                SELECT id FROM auth_refresh_tokens 
                WHERE user_id = ? AND token_hash = ? AND expires_at > CURRENT_TIMESTAMP AND is_revoked = 0
            """, (user_id, token_hash))
            
            if not cursor.fetchone():
                conn.close()
                return None
            
            conn.close()
            
            # Get user data for new access token
            user = await self.get_user_by_id(user_id)
            if not user:
                return None
            
            # Create new access token
            access_token_data = {
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value
            }
            
            return self.create_access_token(access_token_data)
            
        except JWTError:
            return None
    
    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            cursor.execute("""
                UPDATE auth_refresh_tokens 
                SET is_revoked = 1 
                WHERE token_hash = ?
            """, (token_hash,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke refresh token: {e}")
            return False
    
    async def login(self, login_data: UserLogin) -> Token:
        """Login user and return tokens"""
        user = await self.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value
        }
        
        access_token = self.create_access_token(access_token_data)
        refresh_token = self.create_refresh_token(user.id)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60
        )

# Global auth service instance
auth_service = AuthService()

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = await auth_service.verify_token(credentials.credentials)
    if token_data is None or token_data.token_type != TokenType.ACCESS:
        raise credentials_exception
    
    user = await auth_service.get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(required_role: UserRole):
    """Require specific user role"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

async def require_premium(current_user: User = Depends(get_current_active_user)) -> User:
    """Require premium subscription"""
    if current_user.role == UserRole.USER:
        if not current_user.subscription_expires or current_user.subscription_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Premium subscription required"
            )
    return current_user