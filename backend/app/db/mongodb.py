from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

settings = get_settings()


class MongoDB:
    """MongoDB connection manager"""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongodb():
    """Connect to MongoDB"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]
    print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongodb_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("✅ Closed MongoDB connection")


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return mongodb.db
