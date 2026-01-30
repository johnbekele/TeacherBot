from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

settings = get_settings()


class MongoDB:
    """MongoDB connection manager with optimized pooling"""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongodb():
    """Connect to MongoDB with optimized connection pooling"""
    mongodb.client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        # Connection pool settings for better performance
        maxPoolSize=50,           # Max connections in pool
        minPoolSize=10,           # Keep minimum connections ready
        maxIdleTimeMS=30000,      # Close idle connections after 30s
        serverSelectionTimeoutMS=5000,  # Fast fail if server unavailable
        connectTimeoutMS=10000,   # Connection timeout
        socketTimeoutMS=20000,    # Socket timeout
        retryWrites=True,         # Auto-retry failed writes
        w="majority"              # Write concern
    )
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]

    # Create indexes for better query performance
    await create_indexes(mongodb.db)

    print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME} (poolSize: 10-50)")


async def create_indexes(db: AsyncIOMotorDatabase):
    """Create database indexes for optimal query performance"""
    try:
        # User progress indexes
        await db.user_progress.create_index([("user_id", 1), ("node_id", 1)])
        await db.user_progress.create_index([("user_id", 1), ("status", 1)])

        # Chat indexes
        await db.chat_sessions.create_index([("user_id", 1), ("is_active", 1)])
        await db.chat_sessions.create_index([("user_id", 1), ("updated_at", -1)])
        await db.chat_messages.create_index([("session_id", 1), ("created_at", -1)])

        # Exercise indexes
        await db.exercises.create_index("node_id")
        await db.exercises.create_index("exercise_id", unique=True)
        await db.exercise_attempts.create_index([("user_id", 1), ("exercise_id", 1)])
        await db.exercise_attempts.create_index([("user_id", 1), ("score", -1)])

        # Content indexes
        await db.course_content.create_index([("node_id", 1), ("user_id", 1)])
        await db.course_content.create_index([("path_id", 1), ("user_id", 1)])
        await db.learning_content.create_index([("created_for_user", 1)])

        # Learning nodes indexes
        await db.learning_nodes.create_index("node_id", unique=True)
        await db.learning_nodes.create_index("status")

        # User profile indexes
        await db.user_profiles.create_index("user_id", unique=True)

        # Learning paths
        await db.learning_paths.create_index([("user_id", 1), ("path_id", 1)])

        print("✅ Database indexes created")
    except Exception as e:
        print(f"⚠️ Index creation error (may already exist): {e}")


async def close_mongodb_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("✅ Closed MongoDB connection")


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return mongodb.db
