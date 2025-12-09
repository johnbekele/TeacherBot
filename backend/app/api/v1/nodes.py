from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from app.dependencies import get_db, get_current_user_id
from app.models.node import NodeResponse, NodeListItem, NodeProgress

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.get("", response_model=dict)
async def get_nodes(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all learning nodes with user progress"""

    # Build query
    query = {}
    if category:
        query["category"] = category
    if difficulty:
        query["difficulty"] = difficulty

    # Get nodes
    nodes_cursor = db.learning_nodes.find(query)
    nodes = await nodes_cursor.to_list(length=100)

    # Get user progress
    progress = await db.user_progress.find_one({"user_id": user_id})

    # Build response
    node_list = []
    for node in nodes:
        node_id = node["node_id"]

        # Check if locked
        prerequisites = node.get("prerequisites", [])
        completed_nodes = progress.get("completed_nodes", []) if progress else []
        locked = not all(prereq in completed_nodes for prereq in prerequisites)

        # Get progress
        node_progress_data = {}
        if progress:
            node_progress_data = progress.get("node_progress", {}).get(node_id, {})

        node_item = {
            "node_id": node_id,
            "title": node["title"],
            "description": node["description"],
            "difficulty": node["difficulty"],
            "estimated_duration": node["estimated_duration"],
            "prerequisites": prerequisites,
            "locked": locked,
            "completion_status": node_progress_data.get("status", "not_started"),
            "completion_percentage": node_progress_data.get("completion_percentage", 0)
        }
        node_list.append(node_item)

    return {"nodes": node_list}


@router.get("/{node_id}", response_model=dict)
async def get_node_detail(
    node_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get detailed node information with exercises"""

    # Get node
    node = await db.learning_nodes.find_one({"node_id": node_id})
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Get exercises for this node
    exercises_cursor = db.exercises.find({"node_id": node_id})
    exercises = await exercises_cursor.to_list(length=100)

    # Get user progress
    progress = await db.user_progress.find_one({"user_id": user_id})
    node_progress_data = {}
    if progress:
        node_progress_data = progress.get("node_progress", {}).get(node_id, {})

    # Get completed exercises
    completed_exercise_ids = set()
    if progress:
        attempts_cursor = db.exercise_attempts.find({
            "user_id": user_id,
            "exercise_id": {"$in": [ex["exercise_id"] for ex in exercises]},
            "score": {"$gte": 70}  # Passing score
        })
        completed_attempts = await attempts_cursor.to_list(length=1000)
        completed_exercise_ids = {att["exercise_id"] for att in completed_attempts}

    # Build exercise list
    exercise_list = []
    for ex in exercises:
        exercise_list.append({
            "exercise_id": ex["exercise_id"],
            "title": ex["title"],
            "difficulty": ex["difficulty"],
            "completed": ex["exercise_id"] in completed_exercise_ids
        })

    # Build response
    return {
        "node": {
            "node_id": node["node_id"],
            "title": node["title"],
            "description": node["description"],
            "difficulty": node["difficulty"],
            "prerequisites": node.get("prerequisites", []),
            "skills_taught": node.get("skills_taught", []),
            "content": node.get("content", {}),
            "exercises": exercise_list
        },
        "progress": {
            "status": node_progress_data.get("status", "not_started"),
            "completion_percentage": node_progress_data.get("completion_percentage", 0),
            "exercises_completed": len(completed_exercise_ids),
            "exercises_total": len(exercises)
        }
    }


@router.post("/{node_id}/start", response_model=dict)
async def start_node(
    node_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Start a learning node"""

    # Verify node exists
    node = await db.learning_nodes.find_one({"node_id": node_id})
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Update progress
    from datetime import datetime
    await db.user_progress.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "current_node_id": node_id,
                f"node_progress.{node_id}.status": "in_progress",
                f"node_progress.{node_id}.last_accessed": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    # Get first exercise
    first_exercise = await db.exercises.find_one({"node_id": node_id})

    return {
        "message": "Node started",
        "ai_introduction": f"Welcome to {node['title']}! Let's begin your learning journey.",
        "first_exercise": first_exercise["exercise_id"] if first_exercise else None
    }
