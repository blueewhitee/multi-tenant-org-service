from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.db.mongodb import db
from app.models.auth import AdminLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    async def authenticate_admin(login_data: AdminLogin) -> Dict[str, Any]:
        """
        Authenticate an admin by email and password.
        Returns the organization document if successful.
        """
        master_db = db.get_master_database()
        org = await master_db["organizations"].find_one({"admin_email": login_data.email})
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not AuthService.verify_password(login_data.password, org["hashed_password"]):
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return org

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        CRITICAL RULE: The payload MUST contain 'sub' (email) and 'org_name'.
        """
        to_encode = data.copy()
        
        # Rule Check: Ensure JWT payload contains sub and org_name
        if "sub" not in to_encode:
            raise ValueError("Token payload must contain 'sub' (admin email)")
        if "org_name" not in to_encode:
            raise ValueError("Token payload must contain 'org_name'")

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
