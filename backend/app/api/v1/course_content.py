"""
Course Content API endpoints
Retrieves pre-generated course content (lectures + exercises) from database

INSTANT LOADING: Content is pre-generated and served step-by-step without AI orchestration.
AI is only used for:
1. Grading exercise submissions
2. Answering Q&A in chat
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from pydantic import BaseModel

from app.dependencies import get_db, get_current_user_id

router = APIRouter()


# Request/Response models
class StartLearningRequest(BaseModel):
    """Request to start learning a node"""
    node_id: str


class StepResponse(BaseModel):
    """Response for a single learning step"""
    step_number: int
    total_steps: int
    step_type: str  # "lecture_section" or "exercise"
    content: dict
    has_next: bool
    has_previous: bool


@router.get("/content/{node_id}")
async def get_node_content(
    node_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get pre-generated lecture content for a node
    Falls back to on-demand generation if not found

    Args:
        node_id: Node identifier (e.g., "python-variables")
        user_id: Current user ID (from auth)
        db: MongoDB database connection

    Returns:
        {
            "lecture": {title, introduction, sections, summary},
            "exercise_ids": ["ex1", "ex2", ...],
            "generated": bool (whether content was pre-generated),
            "node_id": str
        }
    """
    # Try to get pre-generated content
    content = await db.course_content.find_one({
        "node_id": node_id,
        "user_id": user_id
    })

    # If content exists, track access and return
    if content:
        # Update access tracking
        await db.course_content.update_one(
            {"_id": content["_id"]},
            {
                "$set": {"last_accessed": datetime.utcnow()},
                "$inc": {"access_count": 1}
            }
        )

        return {
            "lecture": content["lecture"],
            "exercise_ids": [ex["exercise_id"] for ex in content.get("exercises", [])],
            "generated": True,
            "node_id": node_id
        }

    # Content not found - fallback to on-demand generation
    print(f"⚠️ Content not found for {node_id}, generating on-demand")

    try:
        from app.ai.content_generator import generate_single_node_content

        content = await generate_single_node_content(db, user_id, node_id)

        return {
            "lecture": content["lecture"],
            "exercise_ids": [ex["exercise_id"] for ex in content.get("exercises", [])],
            "generated": False,  # Indicate on-demand generation
            "node_id": node_id
        }

    except Exception as e:
        print(f"❌ Failed to generate content for {node_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load or generate content for node: {node_id}"
        )


@router.get("/exercises/{node_id}")
async def get_node_exercises(
    node_id: str,
    difficulty: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get pre-generated exercises for a node, optionally filtered by difficulty

    Args:
        node_id: Node identifier
        difficulty: Optional filter ("beginner", "intermediate", "advanced")
        user_id: Current user ID
        db: MongoDB database connection

    Returns:
        {
            "exercises": [
                {
                    exercise_id, title, description, prompt, difficulty,
                    starter_code, test_cases, hints
                }
            ],
            "node_id": str,
            "count": int
        }
    """
    # Try to get pre-generated content
    content = await db.course_content.find_one({
        "node_id": node_id,
        "user_id": user_id
    })

    # If no pre-generated content, try to fetch exercises from exercises collection
    if not content:
        # Check if exercises exist in exercises collection
        query = {"node_id": node_id}
        if difficulty:
            query["difficulty"] = difficulty

        cursor = db.exercises.find(query, {"_id": 0})
        exercises = await cursor.to_list(length=20)

        if not exercises:
            # No exercises at all - return empty
            print(f"⚠️ No exercises found for {node_id}")
            return {
                "exercises": [],
                "node_id": node_id,
                "count": 0
            }

        return {
            "exercises": exercises,
            "node_id": node_id,
            "count": len(exercises),
            "source": "exercises_collection"
        }

    # Pre-generated content exists
    exercises = content.get("exercises", [])

    # Filter by difficulty if specified
    if difficulty:
        exercises = [ex for ex in exercises if ex.get("difficulty") == difficulty]

    # Track access
    await db.course_content.update_one(
        {"_id": content["_id"]},
        {
            "$set": {"last_accessed": datetime.utcnow()},
            "$inc": {"access_count": 1}
        }
    )

    return {
        "exercises": exercises,
        "node_id": node_id,
        "count": len(exercises),
        "source": "course_content"
    }


@router.get("/status/{path_id}")
async def get_content_generation_status(
    path_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Check if content has been generated for a learning path

    Args:
        path_id: Learning path identifier
        user_id: Current user ID
        db: MongoDB database connection

    Returns:
        {
            "path_id": str,
            "generated": bool,
            "nodes_with_content": int,
            "total_nodes": int,
            "completion_percentage": int,
            "generated_at": datetime (if applicable)
        }
    """
    # Count total nodes in path
    total_nodes = await db.learning_nodes.count_documents({
        "node_id": {"$regex": f"^{path_id}"}
    })

    # Count nodes with generated content
    nodes_with_content = await db.course_content.count_documents({
        "path_id": path_id,
        "user_id": user_id
    })

    # Get generation timestamp if available
    sample_content = await db.course_content.find_one(
        {"path_id": path_id, "user_id": user_id},
        {"generated_at": 1}
    )

    completion_percentage = (nodes_with_content / total_nodes * 100) if total_nodes > 0 else 0

    return {
        "path_id": path_id,
        "generated": nodes_with_content > 0,
        "nodes_with_content": nodes_with_content,
        "total_nodes": total_nodes,
        "completion_percentage": round(completion_percentage),
        "generated_at": sample_content.get("generated_at").isoformat() if sample_content and sample_content.get("generated_at") else None
    }


@router.post("/regenerate/{node_id}")
async def regenerate_node_content(
    node_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Regenerate content for a specific node
    Useful for refreshing outdated content or fixing issues

    Args:
        node_id: Node to regenerate content for
        user_id: Current user ID
        db: MongoDB database connection

    Returns:
        {
            "success": bool,
            "message": str,
            "node_id": str
        }
    """
    try:
        from app.ai.content_generator import generate_single_node_content

        print(f"🔄 Regenerating content for {node_id}")

        # Delete existing content
        await db.course_content.delete_one({
            "node_id": node_id,
            "user_id": user_id
        })

        # Generate new content
        content = await generate_single_node_content(db, user_id, node_id)

        return {
            "success": True,
            "message": f"Content regenerated for {node_id}",
            "node_id": node_id,
            "exercises_count": len(content.get("exercises", []))
        }

    except Exception as e:
        print(f"❌ Failed to regenerate content for {node_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate content: {str(e)}"
        )


# ============================================================================
# INSTANT STEP-BY-STEP CONTENT API
# Pre-generated content served without AI orchestration
# ============================================================================


def build_steps_from_content(content: dict) -> List[dict]:
    """
    Build a flat list of steps from pre-generated content.

    Steps are structured as:
    1. Introduction section
    2-N. Lecture sections (Core Concepts, Examples, Common Mistakes, etc.)
    N+1. Summary section
    N+2 onwards. Exercises (beginner, intermediate, advanced)

    Returns list of step objects with type and content.
    """
    steps = []
    lecture = content.get("lecture", {})
    exercises = content.get("exercises", [])

    # Step 1: Introduction
    if lecture.get("introduction"):
        steps.append({
            "step_type": "lecture_section",
            "section_name": "introduction",
            "title": lecture.get("title", "Introduction"),
            "content": {
                "heading": "Introduction",
                "body": lecture["introduction"],
                "code_examples": []
            }
        })

    # Steps 2-N: Lecture sections
    for idx, section in enumerate(lecture.get("sections", [])):
        steps.append({
            "step_type": "lecture_section",
            "section_name": f"section_{idx + 1}",
            "title": section.get("heading", f"Section {idx + 1}"),
            "content": {
                "heading": section.get("heading", ""),
                "body": section.get("body", ""),
                "code_examples": section.get("code_examples", [])
            }
        })

    # Summary section
    if lecture.get("summary"):
        steps.append({
            "step_type": "lecture_section",
            "section_name": "summary",
            "title": "Summary & Key Takeaways",
            "content": {
                "heading": "Summary & Key Takeaways",
                "body": lecture["summary"],
                "code_examples": [],
                "next_steps": lecture.get("next_steps", "Ready to practice!")
            }
        })

    # Exercises (after all lecture content)
    for idx, exercise in enumerate(exercises):
        steps.append({
            "step_type": "exercise",
            "section_name": f"exercise_{idx + 1}",
            "title": exercise.get("title", f"Exercise {idx + 1}"),
            "content": {
                "exercise_id": exercise.get("exercise_id"),
                "title": exercise.get("title"),
                "description": exercise.get("description", ""),
                "prompt": exercise.get("prompt", ""),
                "difficulty": exercise.get("difficulty", "beginner"),
                "starter_code": exercise.get("starter_code", ""),
                "hints": exercise.get("hints", []),
                # NOTE: Solution is NOT included - used only for AI grading
            }
        })

    return steps


@router.post("/start/{node_id}")
async def start_learning_node(
    node_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Start learning a node - returns first step of pre-generated content.

    If content doesn't exist, generates it on-demand (with loading indicator).
    Subsequent calls return instantly from pre-generated content.

    Returns:
        {
            "node_id": str,
            "node_title": str,
            "total_steps": int,
            "current_step": 1,
            "step": { step content },
            "has_next": bool,
            "content_ready": bool  # False if generating on-demand
        }
    """
    # Get node metadata
    node = await db.learning_nodes.find_one({"node_id": node_id})
    if not node:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

    # Try to get pre-generated content
    content = await db.course_content.find_one({
        "node_id": node_id,
        "user_id": user_id
    })

    # If no content, generate on-demand
    if not content:
        print(f"⚡ No pre-generated content for {node_id}, generating now...")

        try:
            from app.ai.content_generator import generate_single_node_content
            content = await generate_single_node_content(db, user_id, node_id)
        except Exception as e:
            print(f"❌ Content generation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate learning content. Please try again."
            )

    # Build steps from content
    steps = build_steps_from_content(content)

    if not steps:
        raise HTTPException(
            status_code=500,
            detail="Content exists but no steps could be built."
        )

    # Track access
    await db.course_content.update_one(
        {"node_id": node_id, "user_id": user_id},
        {
            "$set": {"last_accessed": datetime.utcnow()},
            "$inc": {"access_count": 1}
        }
    )

    # Initialize/update user progress
    await db.user_progress.update_one(
        {"user_id": user_id, "node_id": node_id},
        {
            "$setOnInsert": {
                "user_id": user_id,
                "node_id": node_id,
                "started_at": datetime.utcnow(),
                "completion_percentage": 0,
                "exercises_completed": 0
            },
            "$set": {"last_accessed": datetime.utcnow()}
        },
        upsert=True
    )

    # Return first step
    first_step = steps[0]
    return {
        "node_id": node_id,
        "node_title": node.get("title", node_id),
        "total_steps": len(steps),
        "current_step": 1,
        "step": first_step,
        "has_next": len(steps) > 1,
        "has_previous": False,
        "content_ready": True
    }


@router.get("/step/{node_id}/{step_number}")
async def get_learning_step(
    node_id: str,
    step_number: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get a specific step of the learning content.

    Step numbers are 1-indexed.

    Returns:
        {
            "node_id": str,
            "total_steps": int,
            "current_step": int,
            "step": { step content },
            "has_next": bool,
            "has_previous": bool
        }
    """
    # Get pre-generated content
    content = await db.course_content.find_one({
        "node_id": node_id,
        "user_id": user_id
    })

    if not content:
        raise HTTPException(
            status_code=404,
            detail="Content not found. Please start learning this node first."
        )

    # Build steps
    steps = build_steps_from_content(content)
    total_steps = len(steps)

    # Validate step number
    if step_number < 1 or step_number > total_steps:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step number. Must be between 1 and {total_steps}"
        )

    # Get requested step (convert to 0-indexed)
    step_idx = step_number - 1
    current_step = steps[step_idx]

    # Update progress based on step completed
    # Lecture steps contribute to completion %, exercises are tracked separately
    lecture_steps = [s for s in steps if s["step_type"] == "lecture_section"]
    lecture_count = len(lecture_steps)

    if current_step["step_type"] == "lecture_section" and lecture_count > 0:
        # Calculate progress based on lecture sections viewed
        lecture_step_idx = next(
            (i for i, s in enumerate(lecture_steps) if s == current_step),
            0
        )
        lecture_progress = min(100, int(((lecture_step_idx + 1) / lecture_count) * 50))

        await db.user_progress.update_one(
            {"user_id": user_id, "node_id": node_id},
            {
                "$max": {"completion_percentage": lecture_progress},
                "$set": {"last_accessed": datetime.utcnow()}
            }
        )

    return {
        "node_id": node_id,
        "total_steps": total_steps,
        "current_step": step_number,
        "step": current_step,
        "has_next": step_number < total_steps,
        "has_previous": step_number > 1
    }


@router.get("/all-steps/{node_id}")
async def get_all_steps(
    node_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get all steps for a node - useful for building navigation/table of contents.

    Returns lightweight step metadata (not full content).

    Returns:
        {
            "node_id": str,
            "total_steps": int,
            "steps": [
                { "step_number": 1, "step_type": "lecture_section", "title": "Introduction" },
                ...
            ]
        }
    """
    # Get pre-generated content
    content = await db.course_content.find_one({
        "node_id": node_id,
        "user_id": user_id
    })

    if not content:
        raise HTTPException(
            status_code=404,
            detail="Content not found. Please start learning this node first."
        )

    # Build steps
    steps = build_steps_from_content(content)

    # Return lightweight metadata
    step_metadata = []
    for idx, step in enumerate(steps):
        step_metadata.append({
            "step_number": idx + 1,
            "step_type": step["step_type"],
            "title": step["title"],
            "section_name": step["section_name"]
        })

    return {
        "node_id": node_id,
        "total_steps": len(steps),
        "steps": step_metadata
    }


@router.post("/complete-exercise/{node_id}/{exercise_id}")
async def mark_exercise_completed(
    node_id: str,
    exercise_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Mark an exercise as completed and update progress.

    Called after AI grades submission as passing.

    Returns:
        {
            "success": bool,
            "node_progress": int,
            "exercises_completed": int,
            "total_exercises": int,
            "node_completed": bool
        }
    """
    # Get content to count total exercises
    content = await db.course_content.find_one({
        "node_id": node_id,
        "user_id": user_id
    })

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    exercises = content.get("exercises", [])
    total_exercises = len(exercises)

    # Get current progress
    progress = await db.user_progress.find_one({
        "user_id": user_id,
        "node_id": node_id
    })

    current_completed = progress.get("exercises_completed", 0) if progress else 0

    # Increment exercises completed
    new_completed = min(current_completed + 1, total_exercises)

    # Calculate total progress (50% lecture + 50% exercises)
    exercise_progress = int((new_completed / total_exercises) * 50) if total_exercises > 0 else 0
    lecture_progress = progress.get("completion_percentage", 0) if progress else 0
    # Keep lecture progress contribution (capped at 50%)
    lecture_contribution = min(lecture_progress, 50)
    total_progress = min(100, lecture_contribution + exercise_progress)

    # Check if node is completed
    node_completed = total_progress >= 100

    # Update progress
    update_data = {
        "exercises_completed": new_completed,
        "completion_percentage": total_progress,
        "last_accessed": datetime.utcnow()
    }

    if node_completed:
        update_data["completed_at"] = datetime.utcnow()

    await db.user_progress.update_one(
        {"user_id": user_id, "node_id": node_id},
        {"$set": update_data},
        upsert=True
    )

    return {
        "success": True,
        "node_progress": total_progress,
        "exercises_completed": new_completed,
        "total_exercises": total_exercises,
        "node_completed": node_completed
    }
