from fastapi import HTTPException, status
from app.db.mongodb import db
from app.models.org import OrgCreate, OrgUpdate, OrgResponse
from app.services.auth_service import AuthService
from datetime import datetime, timezone
from app.core.logging import get_logger

logger = get_logger(__name__)

class OrganizationService:
    
    @staticmethod
    async def create_organization(data: OrgCreate) -> OrgResponse:
        """
        Creates a new organization.
        
        Steps:
        1. Check if org name exists in Master DB.
        2. Hash password.
        3. Create metadata in Master DB.
        4. Initialize dynamic collection with dummy doc.
        """
        logger.info(f"Creating organization: {data.organization_name}")
        master_db = db.get_master_database()
        organizations_collection = master_db["organizations"]
        
        # 1. Check for duplicate organization name
        existing_org = await organizations_collection.find_one({"organization_name": data.organization_name})
        if existing_org:
            logger.warning(f"Organization creation failed: '{data.organization_name}' already exists.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this name already exists"
            )
            
        # 2. Hash the admin password
        hashed_password = AuthService.get_password_hash(data.password)
        
        # 3. Create metadata document
        collection_name = db.get_tenant_collection_name(data.organization_name)
        new_org_doc = {
            "organization_name": data.organization_name,
            "admin_email": data.email,
            "hashed_password": hashed_password,
            "collection_name": collection_name,
            "created_at": datetime.now(timezone.utc)
        }
        
        result = await organizations_collection.insert_one(new_org_doc)
        
        # 4. Programmatically insert a dummy document to initialize the collection
        tenant_collection = db.get_tenant_collection(data.organization_name)
        await tenant_collection.insert_one({
            "type": "init_dummy_doc", 
            "message": "Collection initialized", 
            "created_at": datetime.now(timezone.utc)
        })
        
        logger.info(f"Organization '{data.organization_name}' created successfully with collection '{collection_name}'")
        
        return OrgResponse(
            organization_name=data.organization_name,
            collection_name=collection_name
        )

    @staticmethod
    async def get_organization(org_name: str) -> dict:
        master_db = db.get_master_database()
        org = await master_db["organizations"].find_one({"organization_name": org_name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return org

    @staticmethod
    async def delete_organization(org_name: str):
        logger.info(f"Deleting organization: {org_name}")
        master_db = db.get_master_database()
        org_collection = master_db["organizations"]
        
        # Verify existence
        org = await org_collection.find_one({"organization_name": org_name})
        if not org:
             logger.warning(f"Delete failed: Organization '{org_name}' not found")
             raise HTTPException(status_code=404, detail="Organization not found")

        # Delete from Master DB
        await org_collection.delete_one({"organization_name": org_name})
        
        # Drop the dynamic collection
        # We need to get the collection object then drop it.
        # Motor/Pymongo expects dropping via the database object usually or collection.drop()
        tenant_collection = db.get_tenant_collection(org_name)
        await tenant_collection.drop()
        logger.info(f"Organization '{org_name}' and its collection deleted.")

    @staticmethod
    async def update_organization(old_name: str, data: OrgUpdate) -> OrgResponse:
        master_db = db.get_master_database()
        org_collection = master_db["organizations"]
        
        current_org = await org_collection.find_one({"organization_name": old_name})
        if not current_org:
            raise HTTPException(status_code=404, detail="Organization not found")
            
        new_name = data.organization_name
        new_email = data.email
        new_password = data.password # Should be hashed if changed
        
        # If name changes, we have a migration scenario
        if new_name != old_name:
            logger.info(f"Migrating organization data from '{old_name}' to '{new_name}'")
            # a. Check if new name exists
            if await org_collection.find_one({"organization_name": new_name}):
                logger.error(f"Migration failed: Target name '{new_name}' already exists")
                raise HTTPException(status_code=400, detail="New organization name already exists")
            
            # b. Create NEW collection (dummy insert)
            new_collection_name = db.get_tenant_collection_name(new_name)
            new_tenant_collection = db.get_tenant_collection(new_name)
            
            # c. Migration: Fetch all docs from OLD and insert to NEW
            old_tenant_collection = db.get_tenant_collection(old_name)
            
            # Use async iteration to copy documents
            # Note: insert_many might be better for bulk, but let's do simple loop for safety unless large dataset
            # For assignment, this is fine.
            docs_to_move = []
            async for doc in old_tenant_collection.find({}):
                docs_to_move.append(doc)
            
            if docs_to_move:
                await new_tenant_collection.insert_many(docs_to_move)
            else:
                 # Ensure collection is created even if empty (unlikely due to init doc)
                 await new_tenant_collection.insert_one({"type": "init_dummy_doc_migrated"})

            # d. Update Master DB metadata
            hashed_password = AuthService.get_password_hash(new_password)
            
            await org_collection.update_one(
                {"organization_name": old_name},
                {"$set": {
                    "organization_name": new_name,
                    "admin_email": new_email,
                    "hashed_password": hashed_password,
                    "collection_name": new_collection_name
                }}
            )
            
            # e. Drop OLD collection
            await old_tenant_collection.drop()
            
            logger.info(f"Migration complete: '{old_name}' -> '{new_name}'")
            
            return OrgResponse(
                organization_name=new_name,
                collection_name=new_collection_name
            )
        
        else:
            # Just simple update of fields (email, password)
            hashed_password = AuthService.get_password_hash(new_password)
            await org_collection.update_one(
                {"organization_name": old_name},
                {"$set": {
                    "admin_email": new_email,
                    "hashed_password": hashed_password
                }}
            )
            return OrgResponse(
                organization_name=old_name,
                collection_name=current_org["collection_name"]
            )
