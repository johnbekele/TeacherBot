"""
Database Cleanup Script
Removes all AI-generated content and user-specific data to start fresh
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "myteacher")


async def cleanup_database():
    """Remove all AI-generated and user-specific content"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    print("🧹 Starting database cleanup...")
    print("=" * 60)

    # 1. Delete AI-generated learning nodes
    result = await db.learning_nodes.delete_many({"created_by": "ai"})
    print(f"✅ Deleted {result.deleted_count} AI-generated learning nodes")

    # 2. Delete AI-generated exercises
    result = await db.exercises.delete_many({"generated_by_ai": True})
    print(f"✅ Deleted {result.deleted_count} AI-generated exercises")

    # 3. Delete all learning content
    result = await db.learning_content.delete_many({})
    print(f"✅ Deleted {result.deleted_count} learning content documents")

    # 4. Delete all course content (pre-generated)
    result = await db.course_content.delete_many({})
    print(f"✅ Deleted {result.deleted_count} course content documents")

    # 5. Delete user-created learning paths
    result = await db.learning_paths.delete_many({"created_by": "ai"})
    print(f"✅ Deleted {result.deleted_count} AI-generated learning paths")

    # 6. Delete user progress for AI-generated nodes
    # Note: We'll keep progress for hardcoded nodes (python-basics, etc.)
    result = await db.user_progress.delete_many({
        "node_id": {"$regex": "^(go|docker|pulumi|github)"}
    })
    print(f"✅ Deleted {result.deleted_count} user progress entries")

    # 7. Delete exercise attempts for AI-generated exercises
    result = await db.exercise_attempts.delete_many({})
    print(f"✅ Deleted {result.deleted_count} exercise attempts")

    # 8. Clean up chat messages from learning sessions
    result = await db.chat_messages.delete_many({
        "context_type": {"$in": ["learning_session", "planning", "exercise"]}
    })
    print(f"✅ Deleted {result.deleted_count} learning session chat messages")

    # 9. Delete learning sessions
    result = await db.learning_sessions.delete_many({})
    print(f"✅ Deleted {result.deleted_count} learning sessions")

    print("=" * 60)
    print("✨ Database cleanup complete!")
    print("\n📊 Summary of remaining hardcoded content:")

    # Show what's left
    nodes_count = await db.learning_nodes.count_documents({})
    exercises_count = await db.exercises.count_documents({})
    print(f"   - Learning nodes: {nodes_count}")
    print(f"   - Exercises: {exercises_count}")

    # List remaining nodes
    nodes = await db.learning_nodes.find(
        {},
        {"node_id": 1, "title": 1, "_id": 0}
    ).to_list(length=100)

    if nodes:
        print("\n📚 Remaining nodes:")
        for node in nodes:
            print(f"   - {node['node_id']}: {node['title']}")

    client.close()


if __name__ == "__main__":
    asyncio.run(cleanup_database())
