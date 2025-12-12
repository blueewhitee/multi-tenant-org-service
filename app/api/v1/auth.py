from fastapi import APIRouter, Request
from app.models.auth import AdminLogin, Token
from app.services.auth_service import AuthService
from app.main import limiter

router = APIRouter()

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, login_data: AdminLogin):
    """
    Admin Login.
    """
    org = await AuthService.authenticate_admin(login_data)
    
    access_token = AuthService.create_access_token(
        data={"sub": org["admin_email"], "org_name": org["organization_name"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}
