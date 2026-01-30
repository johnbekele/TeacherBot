"""
Learning Paths API endpoints
Organizes learning nodes into structured paths with modules
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_db, get_current_user_id

router = APIRouter()


# Learning path definitions with metadata
PATH_DEFINITIONS = {
    "python": {
        "id": "python",
        "title": "Python Mastery",
        "description": "Master Python from basics to advanced concepts",
        "thumbnail": "🐍",
        "color": "#3776AB",
        "node_prefixes": ["python"],
    },
    "go": {
        "id": "go",
        "title": "Go Programming",
        "description": "Learn Go programming from fundamentals to concurrency",
        "thumbnail": "🐹",
        "color": "#00ADD8",
        "node_prefixes": ["go"],
    },
    "javascript": {
        "id": "javascript",
        "title": "Modern JavaScript & TypeScript",
        "description": "Master JavaScript, DOM manipulation, async programming, and TypeScript",
        "thumbnail": "🌐",
        "color": "#F7DF1E",
        "node_prefixes": ["js", "typescript"],
    },
    "infrastructure": {
        "id": "infrastructure",
        "title": "Infrastructure & DevOps",
        "description": "Learn Bash, Docker, Terraform, and infrastructure automation",
        "thumbnail": "🛠️",
        "color": "#FF6F00",
        "node_prefixes": ["bash", "docker", "terraform", "pulumi"],
    }
}


async def get_nodes_by_prefix(db: AsyncIOMotorDatabase, prefixes: List[str]) -> List[Dict]:
    """Get all nodes that match any of the given prefixes"""
    # Build regex pattern to match any prefix
    pattern = "^(" + "|".join(prefixes) + ")"

    cursor = db.learning_nodes.find(
        {"node_id": {"$regex": pattern}},
        {"_id": 0}
    ).sort("created_at", 1)

    nodes = await cursor.to_list(length=100)
    return nodes


async def calculate_path_progress(db: AsyncIOMotorDatabase, user_id: str, node_ids: List[str]) -> Dict:
    """Calculate overall progress for a learning path"""
    if not node_ids:
        return {"progress": 0, "completed_count": 0, "total_count": 0, "in_progress_count": 0}

    # Get user progress for these nodes
    progress_cursor = db.user_progress.find(
        {"user_id": user_id, "node_id": {"$in": node_ids}},
        {"node_id": 1, "completion_percentage": 1, "_id": 0}
    )

    progress_data = await progress_cursor.to_list(length=100)
    progress_map = {p["node_id"]: p["completion_percentage"] for p in progress_data}

    completed_count = sum(1 for nid in node_ids if progress_map.get(nid, 0) >= 100)
    in_progress_count = sum(1 for nid in node_ids if 0 < progress_map.get(nid, 0) < 100)

    overall_progress = sum(progress_map.get(nid, 0) for nid in node_ids) / len(node_ids) if node_ids else 0

    return {
        "progress": round(overall_progress),
        "completed_count": completed_count,
        "total_count": len(node_ids),
        "in_progress_count": in_progress_count
    }


def determine_module_status(node: Dict, progress_map: Dict, previous_completed: bool) -> str:
    """
    Determine the status of a module based on progress and prerequisites

    Enhanced with prerequisite verification to ensure accurate unlocking logic
    """
    node_id = node["node_id"]
    completion = progress_map.get(node_id, 0)

    # Already completed
    if completion >= 100:
        return "completed"

    # In progress
    if completion > 0:
        return "in_progress"

    # Check prerequisites if specified in node
    prerequisites = node.get("prerequisites", [])
    if prerequisites:
        # All prerequisites must be completed
        prereqs_completed = all(
            progress_map.get(prereq_id, 0) >= 100
            for prereq_id in prerequisites
        )
        if not prereqs_completed:
            return "locked"

    # Sequential check: previous node must be completed
    if not previous_completed:
        return "locked"

    return "available"


@router.get("/")
async def get_learning_paths(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get all available learning paths with progress (both hardcoded and user-created)"""
    paths = []

    # 1. Add hardcoded paths (python, go, javascript, infrastructure)
    # BUT only if they have at least one node
    for path_id, path_def in PATH_DEFINITIONS.items():
        # Get nodes for this path
        nodes = await get_nodes_by_prefix(db, path_def["node_prefixes"])
        node_ids = [n["node_id"] for n in nodes]

        # Skip if no nodes exist for this path
        if not node_ids:
            continue

        # Calculate progress
        progress_data = await calculate_path_progress(db, user_id, node_ids)

        paths.append({
            "id": path_def["id"],
            "title": path_def["title"],
            "description": path_def["description"],
            "thumbnail": path_def["thumbnail"],
            "color": path_def["color"],
            "modules_count": progress_data["total_count"],
            "progress": progress_data["progress"],
            "completed_count": progress_data["completed_count"],
            "in_progress_count": progress_data["in_progress_count"],
            "is_hardcoded": True  # Mark as hardcoded (can't be deleted)
        })

    # 2. Add user-created paths from MongoDB
    user_paths_cursor = db.learning_paths.find({"user_id": user_id, "status": "active"})
    user_paths = await user_paths_cursor.to_list(length=100)

    for path_doc in user_paths:
        # Get nodes for this path (using node_prefixes)
        nodes = await get_nodes_by_prefix(db, path_doc.get("node_prefixes", [path_doc["path_id"]]))
        node_ids = [n["node_id"] for n in nodes]

        # Skip if no nodes exist
        if not node_ids:
            continue

        # Calculate progress
        progress_data = await calculate_path_progress(db, user_id, node_ids)

        paths.append({
            "id": path_doc["path_id"],
            "title": path_doc["title"],
            "description": path_doc["description"],
            "thumbnail": path_doc.get("thumbnail", "🎯"),
            "color": path_doc.get("color", "#6366F1"),
            "modules_count": progress_data["total_count"],
            "progress": progress_data["progress"],
            "completed_count": progress_data["completed_count"],
            "in_progress_count": progress_data["in_progress_count"],
            "is_hardcoded": False  # User-created, can be deleted
        })

    return {"paths": paths}


@router.get("/{path_id}")
async def get_learning_path_detail(
    path_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed information about a specific learning path with modules"""
    # Try to get path from hardcoded definitions first
    if path_id in PATH_DEFINITIONS:
        path_def = PATH_DEFINITIONS[path_id]
    else:
        # Try to get user-created path from MongoDB
        path_doc = await db.learning_paths.find_one({"path_id": path_id, "user_id": user_id})
        if not path_doc:
            raise HTTPException(status_code=404, detail="Learning path not found")

        # Convert MongoDB document to path_def format
        path_def = {
            "id": path_doc["path_id"],
            "title": path_doc["title"],
            "description": path_doc["description"],
            "thumbnail": path_doc.get("thumbnail", "🎯"),
            "color": path_doc.get("color", "#6366F1"),
            "node_prefixes": path_doc.get("node_prefixes", [path_doc["path_id"]])
        }

    # Get nodes for this path
    nodes = await get_nodes_by_prefix(db, path_def["node_prefixes"])

    if not nodes:
        raise HTTPException(status_code=404, detail="No modules found for this path")

    # Get user progress for these nodes
    node_ids = [n["node_id"] for n in nodes]
    progress_cursor = db.user_progress.find(
        {"user_id": user_id, "node_id": {"$in": node_ids}},
        {"node_id": 1, "completion_percentage": 1, "exercises_completed": 1, "_id": 0}
    )

    progress_data = await progress_cursor.to_list(length=100)
    progress_map = {p["node_id"]: p["completion_percentage"] for p in progress_data}

    # Build modules list with status
    modules = []
    previous_completed = True  # First module is always available

    for idx, node in enumerate(nodes):
        # Count exercises for this node
        exercises_count = await db.exercises.count_documents({"node_id": node["node_id"]})

        status = determine_module_status(node, progress_map, previous_completed)

        modules.append({
            "id": node["node_id"],
            "title": node["title"],
            "description": node.get("description", ""),
            "difficulty": node.get("difficulty", "beginner"),
            "order": idx + 1,
            "status": status,
            "exercises_count": exercises_count,
            "completion_percentage": progress_map.get(node["node_id"], 0)
        })

        # Update previous_completed for next iteration
        previous_completed = (status == "completed")

    # Calculate overall progress
    progress_data = await calculate_path_progress(db, user_id, node_ids)

    return {
        "id": path_def["id"],
        "title": path_def["title"],
        "description": path_def["description"],
        "color": path_def["color"],
        "thumbnail": path_def["thumbnail"],
        "progress": progress_data["progress"],
        "completed_count": progress_data["completed_count"],
        "total_count": progress_data["total_count"],
        "modules": modules
    }


@router.delete("/{path_id}")
async def delete_learning_path(
    path_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a user-created learning path and all associated content

    NOTE: Hardcoded paths (python, go, javascript, infrastructure) cannot be deleted
    """
    # Check if this is a hardcoded path
    if path_id in PATH_DEFINITIONS:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete hardcoded learning paths. They will be hidden automatically when empty."
        )

    # Check if path exists and belongs to user
    path = await db.learning_paths.find_one({
        "path_id": path_id,
        "user_id": user_id
    })

    if not path:
        raise HTTPException(
            status_code=404,
            detail="Learning path not found or you don't have permission to delete it"
        )

    print(f"🗑️ Deleting learning path: {path_id} for user: {user_id}")

    # Get all nodes for this path
    nodes = await get_nodes_by_prefix(db, path.get("node_prefixes", [path_id]))
    node_ids = [n["node_id"] for n in nodes]

    # Delete all associated content
    if node_ids:
        # Delete nodes
        result = await db.learning_nodes.delete_many({"node_id": {"$in": node_ids}})
        print(f"   Deleted {result.deleted_count} nodes")

        # Delete exercises
        result = await db.exercises.delete_many({"node_id": {"$in": node_ids}})
        print(f"   Deleted {result.deleted_count} exercises")

        # Delete course content
        result = await db.course_content.delete_many({
            "path_id": path_id,
            "user_id": user_id
        })
        print(f"   Deleted {result.deleted_count} course content documents")

        # Delete user progress
        result = await db.user_progress.delete_many({
            "user_id": user_id,
            "node_id": {"$in": node_ids}
        })
        print(f"   Deleted {result.deleted_count} progress entries")

        # Delete exercise attempts
        exercise_ids = [ex["exercise_id"] for ex in await db.exercises.find(
            {"node_id": {"$in": node_ids}},
            {"exercise_id": 1}
        ).to_list(length=1000)]

        if exercise_ids:
            result = await db.exercise_attempts.delete_many({
                "user_id": user_id,
                "exercise_id": {"$in": exercise_ids}
            })
            print(f"   Deleted {result.deleted_count} exercise attempts")

    # Delete the learning path document
    await db.learning_paths.delete_one({"_id": path["_id"]})

    print(f"✅ Learning path {path_id} deleted successfully")

    return {
        "success": True,
        "message": f"Learning path '{path['title']}' and all associated content deleted successfully"
    }
