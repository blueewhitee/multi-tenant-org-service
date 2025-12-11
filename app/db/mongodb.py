from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

class DatabaseManager:
    client: AsyncIOMotorClient = None

    def __init__(self):
        self.client = None

    async def connect(self):
        """Establish connection to MongoDB."""
        logging.info("Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        logging.info("Connected to MongoDB.")

    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            logging.info("Closing MongoDB connection...")
            self.client.close()
            logging.info("MongoDB connection closed.")

    def get_master_database(self) -> AsyncIOMotorDatabase:
        """Return the master database instance."""
        if not self.client:
             raise RuntimeError("Database not initialized. Call connect() first.")
        return self.client[settings.MONGO_DB_NAME]

    def get_tenant_collection_name(self, org_name: str) -> str:
        """Generate sanitized collection name for a tenant."""
        # Simple sanitization: lowercase and replace spaces with underscores. 
        # In production, use stricter regex.
        sanitized_name = "".join(c for c in org_name if c.isalnum() or c in [' ', '_', '-']).strip().replace(' ', '_').lower()
        return f"org_{sanitized_name}"

    def get_tenant_collection(self, org_name: str):
        """Return the specific collection for an organization."""
        if not self.client:
             raise RuntimeError("Database not initialized.")
        # Note: All tenant collections are in the same physical DB as master or a separate one? 
        # Requirement says: "Each organization gets its own dynamic MongoDB collection."
        # Usually implies same DB, different collection. 
        # But if we want physical isolation (separate DBs), we'd do self.client[org_db_name].
        # Architecture constraints say: "Data for an organization must be stored in a collection named org_{sanitized_org_name}."
        # This implies it's in a database. Let's assume it's the SAME database as master for simplicity unless specified otherwise,
        # OR we can have a dedicated DB for tenants. 
        # User Rule: "Master Database (master_metadata)" vs "Dynamic Tenant Collections". 
        # Let's keep them in the same DB defined by MONGO_DB_NAME to start, or separate?
        # The prompt says: "Master Database ('master_metadata')"
        # Let's assume all collections live in the DB defined by MONGO_DB_NAME for now 
        # OR we could make it `self.client[settings.MONGO_DB_NAME][collection_name]`.
        
        collection_name = self.get_tenant_collection_name(org_name)
        return self.client[settings.MONGO_DB_NAME][collection_name]

db = DatabaseManager()
