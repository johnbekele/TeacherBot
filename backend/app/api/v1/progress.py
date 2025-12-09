from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import List, Dict
from bson import ObjectId
from app.dependencies import get_db, get_current_user_id
from app.models.progress import ProgressResponse, StatsResponse

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("", response_model=dict)
async def get_progress(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user progress"""

    progress = await db.user_progress.find_one({"user_id": user_id})

    if not progress:
        # Return empty progress
        return {
            "current_node": None,
            "completed_nodes": [],
            "unlocked_nodes": [],
            "overall_stats": {
                "total_exercises_completed": 0,
                "total_time_spent": 0,
                "success_rate": 0.0,
                "streak_days": 0,
                "last_activity": None
            },
            "node_progress": {}
        }

    return {
        "current_node": progress.get("current_node_id"),
        "completed_nodes": progress.get("completed_nodes", []),
        "unlocked_nodes": progress.get("unlocked_nodes", []),
        "overall_stats": progress.get("overall_stats", {}),
        "node_progress": progress.get("node_progress", {})
    }


@router.get("/stats", response_model=dict)
async def get_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get detailed user statistics"""

    # Get user memory (weaknesses and strengths)
    memory_cursor = db.user_memory.find({"user_id": user_id})
    memories = await memory_cursor.to_list(length=100)

    strengths = []
    weaknesses = []

    for mem in memories:
        if mem["memory_type"] == "strength":
            strengths.append({
                "concept": mem["concept"],
                "proficiency": 100 - (mem.get("severity", 1) * 10)
            })
        elif mem["memory_type"] in ["weakness", "confusion"]:
            weaknesses.append({
                "concept": mem["concept"],
                "confusion_count": mem.get("frequency", 1)
            })

    # Get learning patterns
    progress = await db.user_progress.find_one({"user_id": user_id})
    settings = {}
    if progress:
        user = await db.users.find_one({"_id": user_id})
        if user:
            settings = user.get("settings", {})

    learning_patterns = {
        "best_time_of_day": None,  # TODO: Calculate from activity logs
        "average_session_length": 45,  # TODO: Calculate from sessions
        "preferred_pace": settings.get("pace_preference", "medium")
    }

    return {
        "strengths": strengths[:10],  # Top 10
        "weaknesses": weaknesses[:10],  # Top 10
        "learning_patterns": learning_patterns
    }


@router.get("/dashboard", response_model=dict)
async def get_dashboard_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get comprehensive dashboard statistics"""

    # Get all user attempts
    attempts = await db.attempts.find({"user_id": user_id}).to_list(length=1000)

    # Calculate overall stats
    total_attempts = len(attempts)
    passed_attempts = len([a for a in attempts if a.get("score", 0) >= 70])
    success_rate = (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0

    # Get unique exercises completed
    completed_exercises = set()
    for attempt in attempts:
        if attempt.get("score", 0) >= 70:
            completed_exercises.add(attempt["exercise_id"])

    # Calculate streak
    streak_days = await _calculate_streak(db, user_id)

    # Get progress by difficulty
    exercises_by_difficulty = await _get_exercises_by_difficulty(db, attempts)

    # Get weekly activity (last 7 days)
    weekly_activity = await _get_weekly_activity(db, user_id)

    # Get recent achievements
    recent_nodes = await _get_completed_nodes(db, user_id)

    # Time spent (estimated from attempts)
    total_time_minutes = len(attempts) * 15  # Rough estimate: 15 min per attempt

    return {
        "overview": {
            "exercises_completed": len(completed_exercises),
            "total_attempts": total_attempts,
            "success_rate": round(success_rate, 1),
            "streak_days": streak_days,
            "total_time_hours": round(total_time_minutes / 60, 1),
            "nodes_completed": len(recent_nodes),
        },
        "exercises_by_difficulty": exercises_by_difficulty,
        "weekly_activity": weekly_activity,
        "recent_nodes": recent_nodes[:5],
    }


async def _calculate_streak(db: AsyncIOMotorDatabase, user_id: str) -> int:
    """Calculate current learning streak in days"""
    # Get attempts sorted by date
    attempts = await db.attempts.find({"user_id": user_id}).sort("created_at", -1).to_list(length=100)

    if not attempts:
        return 0

    # Check consecutive days
    streak = 0
    current_date = datetime.utcnow().date()

    for attempt in attempts:
        attempt_date = attempt.get("created_at", datetime.utcnow()).date()

        # Check if this attempt is within the streak
        if attempt_date == current_date or attempt_date == current_date - timedelta(days=1):
            streak += 1
            current_date = attempt_date - timedelta(days=1)
        else:
            break

    return min(streak, 365)  # Cap at 365 days


async def _get_exercises_by_difficulty(db: AsyncIOMotorDatabase, attempts: List[Dict]) -> Dict:
    """Get exercise completion by difficulty level"""
    difficulty_stats = {
        "beginner": {"completed": 0, "total": 0},
        "intermediate": {"completed": 0, "total": 0},
        "advanced": {"completed": 0, "total": 0},
    }

    # Get exercise details for all attempts
    exercise_ids = list(set(a["exercise_id"] for a in attempts))
    exercises = await db.exercises.find({"_id": {"$in": [ObjectId(eid) for eid in exercise_ids]}}).to_list(length=100)

    exercise_difficulty = {str(e["_id"]): e.get("difficulty", "beginner") for e in exercises}

    for attempt in attempts:
        difficulty = exercise_difficulty.get(attempt["exercise_id"], "beginner")
        if difficulty in difficulty_stats:
            difficulty_stats[difficulty]["total"] += 1
            if attempt.get("score", 0) >= 70:
                difficulty_stats[difficulty]["completed"] += 1

    return difficulty_stats


async def _get_weekly_activity(db: AsyncIOMotorDatabase, user_id: str) -> List[Dict]:
    """Get activity for last 7 days"""
    activity = []
    today = datetime.utcnow().date()

    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())

        count = await db.attempts.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": start, "$lte": end}
        })

        activity.append({
            "date": date.isoformat(),
            "day": date.strftime("%a"),
            "exercises": count
        })

    return activity


async def _get_completed_nodes(db: AsyncIOMotorDatabase, user_id: str) -> List[Dict]:
    """Get recently completed nodes"""
    progress = await db.user_progress.find_one({"user_id": user_id})

    if not progress or not progress.get("completed_nodes"):
        return []

    # Get node details
    node_ids = [ObjectId(nid) for nid in progress["completed_nodes"][:5]]
    nodes = await db.learning_nodes.find({"_id": {"$in": node_ids}}).to_list(length=5)

    return [
        {
            "id": str(node["_id"]),
            "title": node["title"],
            "difficulty": node["difficulty"],
        }
        for node in nodes
    ]
