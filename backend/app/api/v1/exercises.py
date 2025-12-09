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
from app.services.grading_service import grade_exercise

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.get("/{exercise_id}", response_model=dict)
async def get_exercise(
    exercise_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get exercise details"""

    exercise = await db.exercises.find_one({"exercise_id": exercise_id})
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
            "exercise_id": exercise["exercise_id"],
            "title": exercise["title"],
            "description": exercise["description"],
            "prompt": exercise["prompt"],
            "starter_code": exercise.get("starter_code", ""),
            "type": exercise["type"],
            "difficulty": exercise["difficulty"]
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

    # Verify exercise exists
    exercise = await db.exercises.find_one({"exercise_id": exercise_id})
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
        "passed": passed
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
