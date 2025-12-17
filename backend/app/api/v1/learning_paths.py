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
    """Determine the status of a module based on progress and prerequisites"""
    node_id = node["node_id"]
    completion = progress_map.get(node_id, 0)

    if completion >= 100:
        return "completed"
    elif completion > 0:
        return "in_progress"
    elif previous_completed:
        return "available"
    else:
        return "locked"


@router.get("/")
async def get_learning_paths(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get all available learning paths with progress"""
    paths = []

    for path_id, path_def in PATH_DEFINITIONS.items():
        # Get nodes for this path
        nodes = await get_nodes_by_prefix(db, path_def["node_prefixes"])
        node_ids = [n["node_id"] for n in nodes]

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
            "in_progress_count": progress_data["in_progress_count"]
        })

    return {"paths": paths}


@router.get("/{path_id}")
async def get_learning_path_detail(
    path_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed information about a specific learning path with modules"""
    # Validate path exists
    if path_id not in PATH_DEFINITIONS:
        raise HTTPException(status_code=404, detail="Learning path not found")

    path_def = PATH_DEFINITIONS[path_id]

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
