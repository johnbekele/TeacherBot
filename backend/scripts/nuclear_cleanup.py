"""
Nuclear Database Cleanup - Complete Reset
Deletes ALL content except hardcoded nodes
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "myteacher")

# Keep only these hardcoded nodes
KEEP_NODES = ["python-basics", "bash-scripting", "terraform-basics"]
KEEP_EXERCISES = ["python-hello-world", "bash-echo"]


async def nuclear_cleanup():
    """Complete database reset - keep only hardcoded content"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    print("💣 NUCLEAR CLEANUP - Resetting to factory state...")
    print("=" * 60)

    # 1. Delete ALL nodes except hardcoded ones
    result = await db.learning_nodes.delete_many({
        "node_id": {"$nin": KEEP_NODES}
    })
    print(f"✅ Deleted {result.deleted_count} non-hardcoded nodes")

    # 2. Delete ALL exercises except hardcoded ones
    result = await db.exercises.delete_many({
        "exercise_id": {"$nin": KEEP_EXERCISES}
    })
    print(f"✅ Deleted {result.deleted_count} non-hardcoded exercises")

    # 3. Delete ALL learning content
    result = await db.learning_content.delete_many({})
    print(f"✅ Deleted {result.deleted_count} learning content documents")

    # 4. Delete ALL course content
    result = await db.course_content.delete_many({})
    print(f"✅ Deleted {result.deleted_count} course content documents")

    # 5. Delete ALL learning paths
    result = await db.learning_paths.delete_many({})
    print(f"✅ Deleted {result.deleted_count} learning paths")

    # 6. Delete ALL user progress
    result = await db.user_progress.delete_many({})
    print(f"✅ Deleted {result.deleted_count} user progress entries")

    # 7. Delete ALL exercise attempts
    result = await db.exercise_attempts.delete_many({})
    print(f"✅ Deleted {result.deleted_count} exercise attempts")

    # 8. Delete ALL chat messages
    result = await db.chat_messages.delete_many({})
    print(f"✅ Deleted {result.deleted_count} chat messages")

    # 9. Delete ALL learning sessions
    result = await db.learning_sessions.delete_many({})
    print(f"✅ Deleted {result.deleted_count} learning sessions")

    # 10. Delete ALL user profiles (reset weak points)
    result = await db.user_profiles.delete_many({})
    print(f"✅ Deleted {result.deleted_count} user profiles")

    print("=" * 60)
    print("✨ NUCLEAR CLEANUP COMPLETE - Database reset to factory state!")
    print("\n📊 Final state:")

    nodes_count = await db.learning_nodes.count_documents({})
    exercises_count = await db.exercises.count_documents({})
    content_count = await db.learning_content.count_documents({})
    course_content_count = await db.course_content.count_documents({})
    chat_count = await db.chat_messages.count_documents({})

    print(f"   - Learning nodes: {nodes_count}")
    print(f"   - Exercises: {exercises_count}")
    print(f"   - Learning content: {content_count}")
    print(f"   - Course content: {course_content_count}")
    print(f"   - Chat messages: {chat_count}")

    # List remaining nodes
    nodes = await db.learning_nodes.find(
        {},
        {"node_id": 1, "title": 1, "_id": 0}
    ).to_list(length=100)

    if nodes:
        print("\n📚 Remaining hardcoded nodes:")
        for node in nodes:
            print(f"   - {node['node_id']}: {node['title']}")

    exercises = await db.exercises.find(
        {},
        {"exercise_id": 1, "title": 1, "_id": 0}
    ).to_list(length=100)

    if exercises:
        print("\n🎯 Remaining hardcoded exercises:")
        for ex in exercises:
            print(f"   - {ex['exercise_id']}: {ex['title']}")

    client.close()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will delete ALL user data and AI-generated content!")
    print("   Only hardcoded nodes and exercises will remain.")
    print("\n   Press Ctrl+C to cancel, or wait 3 seconds to proceed...")

    import time
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    print("\n   Starting cleanup...\n")
    asyncio.run(nuclear_cleanup())
