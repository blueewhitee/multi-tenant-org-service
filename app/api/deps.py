from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.models.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/admin/login")

async def get_current_admin(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        org_name: str = payload.get("org_name")
        if email is None or org_name is None:
            raise credentials_exception
        token_data = TokenData(email=email, org_name=org_name)
    except JWTError:
        raise credentials_exception
    return token_data
