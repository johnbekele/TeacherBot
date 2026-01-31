"""
Chat API endpoints for AI tutor interactions
"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional, List
import json
import re

from app.dependencies import get_db, get_current_user_id
from app.ai.agents.tutor_agent import TutorAgent
from app.ai.agents.hint_agent import HintAgent
from app.ai.chat_service import ChatService
from app.config import get_settings

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


def should_use_orchestrator(message: str, context_type: str) -> bool:
    """
    Determine if message should use LearningOrchestrator (with tools)
    vs TutorAgent (no tools) using fast pattern matching.

    OPTIMIZED: Removed expensive AI API call, uses regex patterns only.
    Returns True if tools are likely needed for this message.
    """
    # NEVER use orchestrator for Q&A-only contexts (instant content flow)
    if context_type in ["learning_qa", "exercise_qa"]:
        print(f"💬 Q&A-only context ({context_type}), using TutorAgent")
        return False

    # Always use orchestrator for these contexts
    if context_type in ["planning", "learning_session", "onboarding"]:
        return True

    message_lower = message.lower()

    # Fast keyword checks (no regex needed for simple patterns)
    tool_keywords = [
        "create", "generate", "make", "build", "show me",
        "exercise", "quiz", "practice", "challenge",
        "execute", "run", "demo", "example",
        "want to learn", "teach me", "learn about",
        "help me learn", "learning plan", "learning path"
    ]

    if any(kw in message_lower for kw in tool_keywords):
        print(f"🎯 Tool keywords detected, using orchestrator")
        return True

    # Regex patterns for more complex matches
    tool_patterns = [
        r"create.*path", r"give me.*exercise", r"let.*practice",
        r"show.*how.*works", r"can you.*demonstrate"
    ]

    if any(re.search(pattern, message_lower) for pattern in tool_patterns):
        print(f"🎯 Tool pattern matched, using orchestrator")
        return True

    # Q&A patterns - use simpler TutorAgent
    qa_patterns = [
        r"^what (is|are|does)", r"^how (do|does|can|to)",
        r"^why (is|are|do|does)", r"^when (do|does|should)",
        r"^can you explain", r"^explain", r"difference between",
        r"\?$"  # Questions ending with ?
    ]

    if any(re.search(pattern, message_lower) for pattern in qa_patterns):
        print(f"💬 Q&A pattern detected, using TutorAgent")
        return False

    # Default: use orchestrator for safety (tools available if needed)
    return True


class ChatMessageRequest(BaseModel):
    message: str
    context_type: Optional[str] = "general"  # "exercise", "node", "general"
    context_id: Optional[str] = None
    user_code: Optional[str] = None


class HintRequest(BaseModel):
    exercise_id: str
    hint_level: int
    user_code: Optional[str] = ""


@router.post("/message")
async def send_chat_message(
    request: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Send a message to the AI tutor with intelligent routing"""

    # Debug logging
    print(f"📥 Received message with context_type='{request.context_type}', message='{request.message[:50]}...'")

    # Auto-detect planning context from message
    if request.context_type == "general":
        planning_patterns = [
            r"i want to learn", r"teach me", r"create.*path",
            r"learn about", r"i need to learn", r"show me how"
        ]

        for pattern in planning_patterns:
            if re.search(pattern, request.message, re.IGNORECASE):
                original = request.context_type
                request.context_type = "planning"
                print(f"🔄 AUTO-DETECTED: Changed context '{original}' → 'planning' based on message content")
                break

    # Determine if we need tools (LearningOrchestrator) or simple Q&A (TutorAgent)
    use_orchestrator = should_use_orchestrator(request.message, request.context_type)
    print(f"🔍 Routing decision: use_orchestrator={use_orchestrator}")

    # ROUTE 1: Use LearningOrchestrator with tools
    if use_orchestrator:
        from app.ai.agents.learning_orchestrator import LearningOrchestrator
        from app.ai.tool_registry import ToolRegistry
        from app.ai.prompts.system_prompts import get_system_prompt

        orchestrator = LearningOrchestrator(db)
        chat_service = ChatService(db)

        # Get or create session
        session_id = await chat_service.get_or_create_session(
            user_id=user_id,
            context_type=request.context_type,
            context_id=request.context_id or "general"
        )

        # Initialize tool registry with session context
        tool_registry = ToolRegistry(db, user_id, session_id)

        # Load user profile with weak points for adaptive teaching
        user_profile = await db.user_profiles.find_one({"user_id": user_id})

        # Enforce onboarding for new users - profile enables personalized learning
        if not user_profile and request.context_type == "planning":
            print("⚠️ User has no profile, redirecting to onboarding first")
            request.context_type = "onboarding"

        weak_points_info = ""
        if user_profile and user_profile.get("weak_points"):
            weak_topics = [wp.get("topic", "") for wp in user_profile["weak_points"][-5:]]
            if weak_topics:
                weak_points_info = f"\n\nUSER'S WEAK POINTS (target these in exercises):\n- " + "\n- ".join(weak_topics)

        # Choose system prompt based on context
        if request.context_type == "onboarding":
            system_prompt = get_system_prompt("onboarding")
            print(f"✅ ROUTING: Selected ONBOARDING prompt for context_type='{request.context_type}'")
        elif request.context_type == "planning":
            system_prompt = get_system_prompt("planning")
            print(f"✅ ROUTING: Selected PLANNING prompt for context_type='{request.context_type}'")
        else:
            system_prompt = get_system_prompt("learning_orchestrator")
            system_prompt += weak_points_info  # Add weak points context
            print(f"✅ ROUTING: Selected LEARNING_ORCHESTRATOR prompt for context_type='{request.context_type}'")


        # Build context data
        context_data = {}
        if request.user_code:
            context_data["user_code"] = request.user_code

        if request.context_id:
            if request.context_type == "exercise":
                exercise = await db.exercises.find_one({"exercise_id": request.context_id})
                if exercise:
                    context_data["exercise"] = exercise
            elif request.context_type == "node":
                node = await db.learning_nodes.find_one({"node_id": request.context_id})
                if node:
                    context_data["node"] = node

        # Send message with tools enabled
        # Use balanced model for planning AND onboarding (both need good tool use)
        model_tier = "balanced" if request.context_type in ["planning", "onboarding"] else "fast"

        response = await chat_service.send_message(
            user_id=user_id,
            session_id=session_id,
            message=request.message,
            system_prompt=system_prompt,
            context_data=context_data if context_data else None,
            tools=tool_registry.get_tool_definitions(),
            tool_executor=tool_registry.execute_tool,
            model_tier=model_tier
        )

        print(f"🔧 Used LearningOrchestrator (tools enabled, model={model_tier}) for context={request.context_type}: {request.message[:50]}...")
        return response

    # ROUTE 2: Use simple TutorAgent (no tools) for pure Q&A
    else:
        tutor = TutorAgent(db)

        # Build context data if provided
        context_data = None
        if request.user_code:
            context_data = {"user_code": request.user_code}

        # If we have a context_id, fetch relevant details
        if request.context_id:
            if request.context_type == "exercise":
                exercise = await db.exercises.find_one({"exercise_id": request.context_id})
                if exercise:
                    context_data = context_data or {}
                    context_data["exercise"] = exercise
            elif request.context_type == "node":
                node = await db.learning_nodes.find_one({"node_id": request.context_id})
                if node:
                    context_data = context_data or {}
                    context_data["node"] = node
            # For learning_qa context, include current learning content
            elif request.context_type == "learning_qa":
                # Fetch pre-generated content for this node
                content = await db.course_content.find_one({
                    "node_id": request.context_id,
                    "user_id": user_id
                })
                if content:
                    context_data = context_data or {}
                    # Include lecture content (summary) for context
                    lecture = content.get("lecture", {})
                    context_data["learning_content"] = {
                        "title": lecture.get("title", ""),
                        "summary": lecture.get("summary", ""),
                        "topics_covered": [s.get("heading") for s in lecture.get("sections", [])]
                    }
                # Also get node info
                node = await db.learning_nodes.find_one({"node_id": request.context_id})
                if node:
                    context_data = context_data or {}
                    context_data["node"] = node

        response = await tutor.ask_question(
            user_id=user_id,
            question=request.message,
            context_type=request.context_type,
            context_id=request.context_id,
            context_data=context_data,
        )

        print(f"💬 Used TutorAgent (simple Q&A) for: {request.message[:50]}...")
        return response


@router.post("/hint")
async def get_hint(
    request: HintRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get a progressive hint for an exercise"""
    hint_agent = HintAgent(db)

    # Get user's attempt count for this exercise
    attempts = await db.attempts.count_documents(
        {"user_id": user_id, "exercise_id": request.exercise_id}
    )

    try:
        hint = await hint_agent.generate_hint(
            user_id=user_id,
            exercise_id=request.exercise_id,
            hint_level=request.hint_level,
            user_code=request.user_code,
            previous_attempts=attempts,
        )
        return hint
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get chat history for a session"""
    chat_service = ChatService(db)

    # Verify session belongs to user
    session = await db.chat_sessions.find_one({"_id": session_id})
    if not session or session["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    history = await chat_service.get_session_history(session_id)

    # Convert ObjectIds to strings for JSON serialization
    for msg in history:
        if "_id" in msg:
            msg["_id"] = str(msg["_id"])

    return {"session_id": session_id, "messages": history}


@router.get("/sessions")
async def get_user_sessions(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    limit: int = 10,
):
    """Get user's recent chat sessions"""
    sessions = (
        await db.chat_sessions.find({"user_id": user_id})
        .sort("updated_at", -1)
        .limit(limit)
        .to_list(length=limit)
    )

    # Convert ObjectIds to strings
    for session in sessions:
        session["_id"] = str(session["_id"])

    return {"sessions": sessions}


@router.post("/sessions/{session_id}/close")
async def close_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Close a chat session"""
    # Verify session belongs to user
    session = await db.chat_sessions.find_one({"_id": session_id})
    if not session or session["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    chat_service = ChatService(db)
    await chat_service.close_session(session_id)

    return {"message": "Session closed", "session_id": session_id}
