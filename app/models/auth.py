from pydantic import BaseModel, EmailStr, Field

class AdminLogin(BaseModel):
    email: EmailStr = Field(..., description="Admin email")
    password: str = Field(..., description="Admin password")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    org_name: str | None = None
