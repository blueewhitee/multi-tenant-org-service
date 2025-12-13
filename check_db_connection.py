import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check_connection():
    print(f"Testing connection to: {settings.MONGO_URL.split('@')[-1]}")  # masking credentials
    try:
        client = AsyncIOMotorClient(settings.MONGO_URL)
        # Force a connection verification
        await client.admin.command('ping')
        print("SUCCESS: Connected to MongoDB Atlas!")
    except Exception as e:
        print(f"FAILED: Could not connect to MongoDB. Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_connection())
