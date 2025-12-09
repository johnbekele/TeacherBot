"""
Learning Session API
Endpoints for AI-driven dynamic learning
"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional

from app.dependencies import get_db, get_current_user_id
from app.ai.agents.learning_orchestrator import LearningOrchestrator


router = APIRouter(prefix="/learning-session", tags=["Learning Session"])


class ContinueLearningRequest(BaseModel):
    """Request to continue learning session"""
    session_id: str
    message: str


class ExerciseSubmissionEvent(BaseModel):
    """Notification that user submitted an exercise"""
    exercise_id: str
    submission_id: str
    code: str


@router.post("/start/{node_id}")
async def start_learning_session(
    node_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Start AI-driven learning session for a node

    The AI orchestrator takes control and guides the user through learning.
    It may generate intro content, jump straight to an exercise, or ask questions.

    Returns:
        session_id: Chat session ID
        ai_response: AI's initial message
        content_id: ID of generated content (if any)
        exercise_id: ID of generated exercise (if any)
        actions: List of actions for frontend to take
    """
    orchestrator = LearningOrchestrator(db)

    try:
        result = await orchestrator.start_learning_session(user_id, node_id)

        return {
            "session_id": result.get("session_id"),
            "ai_response": result.get("message"),
            "content_id": result.get("content_id"),
            "exercise_id": result.get("exercise_id"),
            "actions": result.get("actions", [])
        }
    except Exception as e:
        print(f"❌ Error starting learning session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/continue")
async def continue_learning(
    request: ContinueLearningRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Continue learning session with user message

    User can ask questions, request custom notes, or interact with AI teacher.
    AI may respond with tools to generate content, exercises, or navigate.

    Returns:
        message: AI's response
        content_id: ID of generated content (if any)
        exercise_id: ID of generated exercise (if any)
        actions: List of actions
    """
    orchestrator = LearningOrchestrator(db)

    try:
        result = await orchestrator.continue_learning(
            user_id=user_id,
            session_id=request.session_id,
            message=request.message
        )

        return {
            "message": result.get("message"),
            "content_id": result.get("content_id"),
            "exercise_id": result.get("exercise_id"),
            "actions": result.get("actions", [])
        }
    except Exception as e:
        print(f"❌ Error continuing learning: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercise-submitted")
async def handle_exercise_submission_ai(
    request: ExerciseSubmissionEvent,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Notify AI that user submitted an exercise

    AI analyzes the submission results and decides:
    - What feedback to provide
    - What the next step should be (next exercise, more content, etc.)
    - Whether to adjust difficulty

    Returns:
        message: AI's feedback and guidance
        navigation: Next step instructions
        actions: List of actions
    """
    from bson import ObjectId

    orchestrator = LearningOrchestrator(db)

    try:
        # Get submission results from database
        attempt = await db.exercise_attempts.find_one({"_id": ObjectId(request.submission_id)})

        if not attempt:
            raise HTTPException(status_code=404, detail="Submission not found")

        # Build test results for AI
        test_results = {
            "score": attempt.get("score", 0),
            "passed": attempt.get("score", 0) >= 70,
            "test_results": attempt.get("test_results", []),
            "feedback": attempt.get("feedback", "")
        }

        # AI analyzes and decides next step
        result = await orchestrator.handle_exercise_submission(
            user_id=user_id,
            exercise_id=request.exercise_id,
            code=request.code,
            test_results=test_results
        )

        # Store AI's response in the attempt
        await db.exercise_attempts.update_one(
            {"_id": ObjectId(request.submission_id)},
            {
                "$set": {
                    "ai_feedback": result.get("message"),
                    "ai_next_step": {
                        "navigation": result.get("actions", []),
                        "exercise_id": result.get("exercise_id"),
                        "content_id": result.get("content_id")
                    }
                }
            }
        )

        return {
            "message": result.get("message"),
            "navigation": result.get("actions"),
            "exercise_id": result.get("exercise_id"),
            "content_id": result.get("content_id")
        }
    except Exception as e:
        print(f"❌ Error handling exercise submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/{content_id}")
async def get_dynamic_content(
    content_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get AI-generated learning content by ID

    Returns the full content document with title, sections, code examples, etc.
    """
    content = await db.learning_content.find_one({
        "content_id": content_id,
        "created_for_user": user_id
    })

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Remove MongoDB _id from response
    content.pop("_id", None)

    return content
