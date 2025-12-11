from fastapi import APIRouter
from app.models.auth import AdminLogin, Token
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(login_data: AdminLogin):
    """
    Admin Login.
    """
    org = await AuthService.authenticate_admin(login_data)
    
    access_token = AuthService.create_access_token(
        data={"sub": org["admin_email"], "org_name": org["organization_name"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}
