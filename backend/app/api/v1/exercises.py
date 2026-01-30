from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional
from bson import ObjectId
from app.dependencies import get_db, get_current_user_id
from app.models.exercise import (
    ExerciseResponse,
    ExerciseSubmit,
    ExerciseResultResponse,
    ExerciseAttemptInDB
)

router = APIRouter(prefix="/exercises", tags=["Exercises"])


# ========================================
# ADAPTIVE PROGRESSION HELPER FUNCTIONS
# ========================================

def categorize_submission_outcome(
    score: int,
    passed: bool,
    weak_points: list,
    user_profile: dict
) -> str:
    """
    Categorize submission outcome for adaptive progression

    Returns:
        "perfect" - Score >= 90, no weak points
        "passed_with_weaknesses" - Score >= 70, but has weak points
        "needs_remediation" - Score < 70, multiple weak points
        "failed" - Score < 50
    """
    if score >= 90 and not weak_points:
        return "perfect"
    elif score >= 70:
        if len(weak_points) > 2:
            return "needs_remediation"
        return "passed_with_weaknesses"
    elif score >= 50:
        return "needs_remediation"
    else:
        return "failed"


async def get_next_node_in_path(db: AsyncIOMotorDatabase, current_node_id: str) -> Optional[dict]:
    """Get the next node in the learning path sequence"""
    # Extract path_id from node_id (e.g., "python-variables" -> "python")
    path_id = current_node_id.split("-")[0] if "-" in current_node_id else current_node_id

    # Get all nodes in this path, sorted by order
    nodes = await db.learning_nodes.find(
        {"node_id": {"$regex": f"^{path_id}"}}
    ).sort("node_id", 1).to_list(length=100)

    if not nodes:
        return None

    # Find current node index
    try:
        current_idx = next(i for i, node in enumerate(nodes) if node["node_id"] == current_node_id)
        if current_idx < len(nodes) - 1:
            return nodes[current_idx + 1]
    except StopIteration:
        pass

    return None


async def get_node_exercises(db: AsyncIOMotorDatabase, node_id: str) -> list:
    """Get all exercises for a node from course_content or exercises collection"""
    # First try course_content (pre-generated)
    content = await db.course_content.find_one({"node_id": node_id})
    if content and content.get("exercises"):
        return content["exercises"]

    # Fallback to exercises collection
    exercises = await db.exercises.find({"node_id": node_id}).to_list(length=100)
    return exercises


async def generate_remedial_exercise(
    db: AsyncIOMotorDatabase,
    user_id: str,
    node_id: str,
    weak_points: list,
    difficulty: str = "beginner"
) -> str:
    """
    Generate a targeted remedial exercise focusing on weak points

    Returns: exercise_id of generated exercise
    """
    from app.ai.content_generator import generate_targeted_exercise

    weak_point_topics = [wp for wp in weak_points if isinstance(wp, str)]

    try:
        exercise = await generate_targeted_exercise(
            db=db,
            user_id=user_id,
            node_id=node_id,
            focus_topics=weak_point_topics,
            difficulty=difficulty,
            context="remedial"
        )

        # Store in exercises collection
        await db.exercises.insert_one(exercise)

        print(f"✅ Generated remedial exercise: {exercise['exercise_id']}")
        return exercise["exercise_id"]

    except Exception as e:
        print(f"❌ Failed to generate remedial exercise: {e}")
        # Fallback: return a basic exercise for this node
        fallback = await db.exercises.find_one({"node_id": node_id, "difficulty": "beginner"})
        return fallback["exercise_id"] if fallback else None


async def determine_next_action(
    db: AsyncIOMotorDatabase,
    user_id: str,
    exercise: dict,
    outcome: str,
    weak_points: list
) -> dict:
    """
    Determine what happens next based on submission outcome

    Decision Tree:
    1. outcome == "perfect" → Next node
    2. outcome == "passed_with_weaknesses" → Next exercise in sequence or remedial
    3. outcome == "needs_remediation" → Generate remedial exercise
    4. outcome == "failed" → Retry with hint
    """

    if outcome == "perfect":
        # Advance to next node
        next_node = await get_next_node_in_path(db, exercise["node_id"])
        if next_node:
            return {
                "type": "navigate_to_node",
                "node_id": next_node["node_id"],
                "reason": "Perfect score! Moving to next topic.",
                "message": "🎉 Excellent work! Let's continue to the next topic."
            }
        else:
            return {
                "type": "complete_path",
                "message": "🏆 Congratulations! You've completed this learning path!"
            }

    elif outcome == "passed_with_weaknesses":
        # Check if this is first exercise or subsequent
        node_exercises = await get_node_exercises(db, exercise["node_id"])

        try:
            current_idx = next(i for i, ex in enumerate(node_exercises)
                             if ex.get("exercise_id") == exercise["exercise_id"])

            if current_idx < len(node_exercises) - 1:
                # More exercises in sequence
                next_exercise = node_exercises[current_idx + 1]
                return {
                    "type": "navigate_to_exercise",
                    "exercise_id": next_exercise["exercise_id"],
                    "reason": "Good job! Let's practice more to strengthen your skills.",
                    "message": "✅ Well done! Moving to the next exercise."
                }
        except StopIteration:
            pass

        # Generate remedial exercise for weak points
        remedial_exercise_id = await generate_remedial_exercise(
            db, user_id, exercise["node_id"], weak_points
        )

        if remedial_exercise_id:
            return {
                "type": "navigate_to_exercise",
                "exercise_id": remedial_exercise_id,
                "reason": "Let's address some areas that need practice.",
                "message": "📝 I've created a targeted exercise to help you master these concepts."
            }
        else:
            # Fallback: move to next node
            next_node = await get_next_node_in_path(db, exercise["node_id"])
            if next_node:
                return {
                    "type": "navigate_to_node",
                    "node_id": next_node["node_id"],
                    "reason": "Good progress! Let's move forward.",
                    "message": "✅ Good work! Moving to the next topic."
                }

    elif outcome == "needs_remediation":
        # Generate easier exercise + provide hint
        remedial_exercise_id = await generate_remedial_exercise(
            db, user_id, exercise["node_id"], weak_points, difficulty="beginner"
        )

        if remedial_exercise_id:
            return {
                "type": "navigate_to_exercise",
                "exercise_id": remedial_exercise_id,
                "reason": "Let's practice the fundamentals before moving forward.",
                "message": "💪 Don't worry! Let's break this down with a simpler exercise.",
                "auto_hint": True  # Automatically show first hint
            }

    # Default: failed - retry current exercise
    return {
        "type": "retry",
        "message": "Let's try again! Review the lecture if needed.",
        "show_hint_button": True
    }


@router.get("/{exercise_id}", response_model=dict)
async def get_exercise(
    exercise_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get exercise details - checks both exercises and course_content collections"""

    exercise = await db.exercises.find_one({"exercise_id": exercise_id})

    # If not found in exercises collection, check course_content
    if not exercise:
        # Extract node_id from exercise_id (e.g., "python-basics-ex1" -> "python-basics")
        # Exercise IDs are formatted as "{node_id}-ex{number}"
        parts = exercise_id.rsplit("-ex", 1)
        if len(parts) == 2:
            node_id = parts[0]

            # Search in course_content for this user
            content = await db.course_content.find_one({
                "node_id": node_id,
                "user_id": user_id
            })

            if content and content.get("exercises"):
                # Find the specific exercise in the pre-generated content
                for ex in content["exercises"]:
                    if ex.get("exercise_id") == exercise_id:
                        exercise = ex
                        # Add node_id if missing
                        exercise["node_id"] = node_id
                        # Infer type from node_id
                        if "python" in node_id:
                            exercise["type"] = "python"
                        elif "js" in node_id or "javascript" in node_id:
                            exercise["type"] = "javascript"
                        else:
                            exercise["type"] = "python"  # default
                        break

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # Get user's attempt history
    attempts = await db.exercise_attempts.find({
        "user_id": user_id,
        "exercise_id": exercise_id
    }).to_list(length=100)

    best_score = 0
    if attempts:
        best_score = max(att.get("score", 0) for att in attempts)

    return {
        "exercise": {
            "exercise_id": exercise.get("exercise_id", exercise_id),
            "title": exercise.get("title", "Exercise"),
            "description": exercise.get("description", ""),
            "prompt": exercise.get("prompt", ""),
            "starter_code": exercise.get("starter_code", ""),
            "type": exercise.get("type", "python"),
            "difficulty": exercise.get("difficulty", "beginner")
        },
        "user_progress": {
            "attempts": len(attempts),
            "best_score": best_score,
            "completed": best_score >= 70
        }
    }


@router.post("/{exercise_id}/submit", response_model=dict)
async def submit_exercise(
    exercise_id: str,
    submission: ExerciseSubmit,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Submit exercise code for AI assessment with interactive feedback"""

    # Verify exercise exists - check both collections
    exercise = await db.exercises.find_one({"exercise_id": exercise_id})

    # If not found, check course_content
    if not exercise:
        parts = exercise_id.rsplit("-ex", 1)
        if len(parts) == 2:
            node_id = parts[0]
            content = await db.course_content.find_one({
                "node_id": node_id,
                "user_id": user_id
            })
            if content and content.get("exercises"):
                for ex in content["exercises"]:
                    if ex.get("exercise_id") == exercise_id:
                        exercise = ex
                        exercise["node_id"] = node_id
                        if "python" in node_id:
                            exercise["type"] = "python"
                        elif "js" in node_id or "javascript" in node_id:
                            exercise["type"] = "javascript"
                        else:
                            exercise["type"] = "python"
                        break

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    # Count attempts
    attempt_count = await db.exercise_attempts.count_documents({
        "user_id": user_id,
        "exercise_id": exercise_id
    })

    # Import AI Grading Service and Learning Orchestrator
    from app.services.ai_grading_service import grade_exercise
    from app.ai.agents.learning_orchestrator import LearningOrchestrator

    orchestrator = LearningOrchestrator(db)

    # AI-powered grading with Claude Sonnet
    print(f"🎓 Grading submission for exercise: {exercise['title']}")

    grading_result = await grade_exercise(
        exercise=exercise,
        student_code=submission.code,
        expected_solution=exercise.get('solution')
    )

    score = grading_result['score']
    passed = grading_result['passed']

    print(f"📊 Score: {score}/100 ({'PASSED' if passed else 'NEEDS WORK'})")

    # Prepare test results
    test_results = {
        "score": score,
        "passed": passed,
        "test_results": [{
            "test_id": "ai_assessment",
            "passed": passed,
            "error_message": "" if passed else "Code needs improvement"
        }]
    }

    # Create attempt record with detailed AI grading
    attempt = {
        "user_id": user_id,
        "exercise_id": exercise_id,
        "attempt_number": attempt_count + 1,
        "submitted_code": submission.code,
        "execution_result": {"status": "ai_graded", "grader": grading_result.get("graded_by", "ai_sonnet")},
        "test_results": test_results["test_results"],
        "score": score,
        "feedback": grading_result["feedback"]["summary"],
        "ai_comments": {
            "strengths": grading_result["feedback"]["strengths"],
            "improvements": grading_result["feedback"]["improvements"],
            "specific_issues": grading_result["feedback"].get("specific_issues", []),
            "next_steps": grading_result["next_steps"]
        },
        "grading_breakdown": grading_result["breakdown"],
        "submitted_at": datetime.utcnow(),
        "graded_at": datetime.utcnow()
    }

    result = await db.exercise_attempts.insert_one(attempt)
    submission_id = str(result.inserted_id)

    # Analyze code for weak points
    weak_points = []
    code_lower = submission.code.lower()

    # Check for common weak points
    if 'def ' not in code_lower and 'function ' not in code_lower:
        weak_points.append("function_declaration")
    if 'for ' not in code_lower and 'while ' not in code_lower:
        weak_points.append("loops")
    if 'if ' not in code_lower:
        weak_points.append("conditionals")
    if 'class ' in code_lower and 'def __init__' not in code_lower:
        weak_points.append("class_initialization")
    if not passed:
        weak_points.append("algorithmic_thinking")

    # Update user profile with weak points
    if weak_points:
        for wp in weak_points:
            # Try to update existing weak point
            result = await db.user_profiles.update_one(
                {
                    "user_id": user_id,
                    "weak_points.topic": wp
                },
                {
                    "$inc": {"weak_points.$.occurrences": 1},
                    "$push": {"weak_points.$.exercises_failed": exercise_id},
                    "$set": {"weak_points.$.last_seen": datetime.utcnow()}
                }
            )

            # If weak point doesn't exist, create it
            if result.matched_count == 0:
                await db.user_profiles.update_one(
                    {"user_id": user_id},
                    {
                        "$push": {
                            "weak_points": {
                                "topic": wp,
                                "description": f"Struggles with {wp.replace('_', ' ')}",
                                "identified_at": datetime.utcnow(),
                                "occurrences": 1,
                                "exercises_failed": [exercise_id],
                                "last_seen": datetime.utcnow()
                            }
                        }
                    },
                    upsert=True
                )

    # Update stats
    await db.user_profiles.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "total_exercises_completed": 1,
                "total_exercises_failed": 0 if passed else 1
            },
            "$set": {"last_active": datetime.utcnow()}
        },
        upsert=True
    )

    # ========================================
    # ADAPTIVE PROGRESSION - Determine Next Action
    # ========================================

    # Get user profile for categorization
    user_profile = await db.user_profiles.find_one({"user_id": user_id}) or {}

    # Categorize submission outcome
    outcome = categorize_submission_outcome(
        score=score,
        passed=passed,
        weak_points=weak_points,
        user_profile=user_profile
    )

    print(f"📊 Submission outcome: {outcome}")

    # Determine next action based on outcome
    next_action = await determine_next_action(
        db=db,
        user_id=user_id,
        exercise=exercise,
        outcome=outcome,
        weak_points=weak_points
    )

    print(f"🚀 Next action: {next_action.get('type')} - {next_action.get('message')}")

    # Update attempt document with outcome and next_action
    await db.exercise_attempts.update_one(
        {"_id": ObjectId(submission_id)},
        {
            "$set": {
                "outcome": outcome,
                "next_action": next_action
            }
        }
    )

    # Now send to Learning Orchestrator for interactive feedback in chat
    try:
        await orchestrator.handle_exercise_submission(
            user_id=user_id,
            exercise_id=exercise_id,
            code=submission.code,
            test_results=test_results
        )
        print(f"✅ Sent submission to AI orchestrator for interactive feedback")
        if weak_points:
            print(f"📊 Identified weak points: {', '.join(weak_points)}")
    except Exception as e:
        print(f"⚠️ AI orchestrator feedback failed: {e}")
        # Don't fail the submission, just log it

    return {
        "submission_id": submission_id,
        "status": "completed",
        "message": "Code submitted! Check the AI chat panel for detailed interactive feedback.",
        "score": score,
        "passed": passed,
        "outcome": outcome,
        "next_action": next_action  # Include next action for frontend auto-progression
    }


@router.get("/{exercise_id}/result/{submission_id}", response_model=dict)
async def get_exercise_result(
    exercise_id: str,
    submission_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get exercise grading result"""

    attempt = await db.exercise_attempts.find_one({
        "_id": ObjectId(submission_id),
        "user_id": user_id,
        "exercise_id": exercise_id
    })

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    # Determine status
    status_value = "completed" if attempt.get("graded_at") else "grading"

    # Get exercise for hints
    exercise = await db.exercises.find_one({"exercise_id": exercise_id})
    hints_available = len(exercise.get("hints", [])) if exercise else 0

    return {
        "submission_id": str(attempt["_id"]),
        "status": status_value,
        "score": attempt.get("score", 0),
        "passed": attempt.get("score", 0) >= 70,
        "test_results": attempt.get("test_results", []),
        "feedback": attempt.get("feedback", ""),
        "next_step": "Continue to next exercise" if attempt.get("score", 0) >= 70 else "Review feedback and try again",
        "hints_available": hints_available
    }


@router.post("/{exercise_id}/hint", response_model=dict)
async def get_hint(
    exercise_id: str,
    hint_number: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a hint for an exercise"""

    exercise = await db.exercises.find_one({"exercise_id": exercise_id})
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    hints = exercise.get("hints", [])
    if hint_number < 1 or hint_number > len(hints):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid hint number"
        )

    hint = hints[hint_number - 1]

    return {
        "hint": hint["text"],
        "hints_remaining": len(hints) - hint_number
    }
