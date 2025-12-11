from fastapi import APIRouter, status, Depends, HTTPException
from app.models.org import OrgCreate, OrgResponse, OrgUpdate
from app.services.org_service import OrganizationService
from app.api.deps import get_current_admin
from app.models.auth import TokenData

router = APIRouter()

@router.post("/create", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(org_in: OrgCreate):
    """
    Create a new organization.
    """
    return await OrganizationService.create_organization(org_in)

@router.get("/get", response_model=OrgResponse)
async def get_organization(organization_name: str):
    """
    Get organization details.
    """
    org = await OrganizationService.get_organization(organization_name)
    return OrgResponse(
        organization_name=org["organization_name"],
        collection_name=org["collection_name"]
    )

@router.put("/update", response_model=OrgResponse)
async def update_organization(
    org_in: OrgUpdate,
    current_admin: TokenData = Depends(get_current_admin)
):
    """
    Update organization. Protected route.
    If name changes, performs data migration.
    """
    # Logic: Can only update OWN org? Or any if 'admin' implies super-admin?
    # Prompt says: "Update Organization Service... Implement update_organization(old_name, new_data)"
    # The route takes OrgUpdate.
    # Where do we get old_name?
    # Usually from the token (current_admin.org_name)
    
    # Verify the admin is updating their own org? 
    # Or is this a super-admin system? 
    # "Multi-tenant Organization Management Service".
    # Requirement 5: "Check if JWT payload contains Admin ID and Org ID".
    # It implies the admin belongs to an org.
    # So they should likely update THEIR OWN org.
    
    # Let's derive old_name from current_admin.org_name
    old_name = current_admin.org_name
    
    # Security check:
    # If the user tries to rename their org, the 'old_name' is what's in the token.
    # We pass that to the service.
    
    return await OrganizationService.update_organization(old_name, org_in)

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    organization_name: str,
    current_admin: TokenData = Depends(get_current_admin)
):
    """
    Delete organization. Protected route.
    """
    # Ensure admin can only delete their own org?
    # Or matches requirement: "Only authenticated Admins can delete."
    
    # If the param organization_name is different from token's org_name, reject?
    if organization_name != current_admin.org_name:
         raise HTTPException(status_code=403, detail="Not authorized to delete this organization")
         
    await OrganizationService.delete_organization(organization_name)
    return None
