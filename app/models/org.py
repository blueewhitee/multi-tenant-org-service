from pydantic import BaseModel, EmailStr, Field, ConfigDict

class OrgCreate(BaseModel):
    organization_name: str = Field(..., min_length=1, description="Name of the organization")
    email: EmailStr = Field(..., description="Admin email for the organization")
    password: str = Field(..., min_length=8, description="Admin password")

class OrgUpdate(BaseModel):
    organization_name: str = Field(..., min_length=1, description="New name of the organization")
    email: EmailStr = Field(..., description="New admin email")
    password: str = Field(..., min_length=8, description="New admin password")

class OrgResponse(BaseModel):
    organization_name: str
    collection_name: str
    
    model_config = ConfigDict(from_attributes=True)
