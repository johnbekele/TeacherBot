"""
Create MongoDB indexes for course_content collection
Run this script to set up database indexes for optimal query performance
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "myteacher")


async def create_indexes():
    """Create all necessary indexes for the course_content collection"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    print("🔧 Creating indexes for course_content collection...")

    # Index 1: path_id + node_id (for fetching specific node content)
    await db.course_content.create_index(
        [("path_id", 1), ("node_id", 1)],
        name="path_node_idx"
    )
    print("✅ Created index: path_node_idx")

    # Index 2: user_id + path_id (for checking user's generated content)
    await db.course_content.create_index(
        [("user_id", 1), ("path_id", 1)],
        name="user_path_idx"
    )
    print("✅ Created index: user_path_idx")

    # Index 3: user_id + node_id (for fetching user's specific node content - most common query)
    await db.course_content.create_index(
        [("user_id", 1), ("node_id", 1)],
        name="user_node_idx",
        unique=True  # One content document per user per node
    )
    print("✅ Created index: user_node_idx (unique)")

    # Index 4: generated_at (for tracking and cleanup)
    await db.course_content.create_index(
        [("generated_at", -1)],
        name="generated_at_idx"
    )
    print("✅ Created index: generated_at_idx")

    # Index 5: last_accessed (for identifying stale content)
    await db.course_content.create_index(
        [("last_accessed", -1)],
        name="last_accessed_idx"
    )
    print("✅ Created index: last_accessed_idx")

    # Also create indexes for exercise_attempts (for next_action queries)
    print("\n🔧 Creating indexes for exercise_attempts collection...")

    await db.exercise_attempts.create_index(
        [("user_id", 1), ("exercise_id", 1), ("timestamp", -1)],
        name="user_exercise_time_idx"
    )
    print("✅ Created index: user_exercise_time_idx")

    # List all indexes
    print("\n📋 All indexes in course_content:")
    indexes = await db.course_content.index_information()
    for idx_name, idx_info in indexes.items():
        print(f"   - {idx_name}: {idx_info['key']}")

    print("\n📋 All indexes in exercise_attempts:")
    indexes = await db.exercise_attempts.index_information()
    for idx_name, idx_info in indexes.items():
        print(f"   - {idx_name}: {idx_info['key']}")

    print("\n🎉 Index creation complete!")

    client.close()


if __name__ == "__main__":
    asyncio.run(create_indexes())
