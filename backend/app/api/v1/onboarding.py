"""
Onboarding API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from app.dependencies import get_db, get_current_user_id
from app.ai.agents.tutor_agent import TutorAgent
from app.ai.prompts.system_prompts import get_system_prompt

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class AssessmentQuestion(BaseModel):
    question: str
    options: List[str]
    category: str  # "experience", "goals", "learning_style", "technical"


class AssessmentAnswer(BaseModel):
    question_index: int
    answer: str


class AssessmentSubmission(BaseModel):
    answers: List[AssessmentAnswer]
    free_text_goals: Optional[str] = None


class LearningPathResponse(BaseModel):
    recommended_level: str  # "beginner", "intermediate", "advanced"
    starting_nodes: List[str]
    estimated_duration_weeks: int
    personalized_message: str
    settings: dict


@router.get("/questions")
async def get_assessment_questions():
    """Get onboarding assessment questions"""
    questions = [
        {
            "question": "What's your experience with programming?",
            "options": [
                "Complete beginner - I've never written code",
                "Some experience - I've done basic tutorials",
                "Intermediate - I can write simple programs",
                "Advanced - I'm comfortable with multiple languages",
            ],
            "category": "experience",
        },
        {
            "question": "Have you worked with DevOps tools before?",
            "options": [
                "Never heard of DevOps",
                "I know what it is but haven't used tools",
                "I've used a few tools (Docker, Git, etc.)",
                "I have professional DevOps experience",
            ],
            "category": "technical",
        },
        {
            "question": "What's your primary goal?",
            "options": [
                "Learn programming from scratch",
                "Understand DevOps concepts and tools",
                "Prepare for a DevOps role",
                "Improve existing DevOps skills",
            ],
            "category": "goals",
        },
        {
            "question": "How do you learn best?",
            "options": [
                "Step-by-step with lots of practice",
                "Quick explanations, then hands-on",
                "Deep dives with detailed theory",
                "Real-world projects and challenges",
            ],
            "category": "learning_style",
        },
        {
            "question": "How much time can you dedicate per week?",
            "options": [
                "1-2 hours (slow and steady)",
                "3-5 hours (consistent progress)",
                "6-10 hours (focused learning)",
                "10+ hours (intensive bootcamp style)",
            ],
            "category": "time_commitment",
        },
    ]
    return {"questions": questions}


@router.post("/assess", response_model=LearningPathResponse)
async def submit_assessment(
    submission: AssessmentSubmission,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Submit assessment answers and get personalized learning path"""

    # Analyze answers
    experience_level = _determine_experience_level(submission.answers)
    learning_pace = _determine_learning_pace(submission.answers)
    focus_area = _determine_focus_area(submission.answers)

    # Get recommended nodes based on assessment
    recommended_nodes = await _get_recommended_nodes(
        db, experience_level, focus_area
    )

    # Generate personalized message with AI
    tutor = TutorAgent(db)
    assessment_summary = _summarize_assessment(submission.answers)

    ai_response = await tutor.ask_question(
        user_id=user_id,
        question=f"Based on this assessment: {assessment_summary}\nGoals: {submission.free_text_goals or 'General DevOps learning'}\nProvide a brief, encouraging personalized message (2-3 sentences) about their learning journey.",
        context_type="onboarding",
    )

    # Determine estimated duration
    duration_weeks = _calculate_duration(experience_level, learning_pace)

    # Configure user settings based on assessment
    settings = {
        "pace_preference": learning_pace,
        "adhd_mode": True,  # Enable by default for better UX
        "break_reminders": True,
        "focus_mode": False,
    }

    # Update user profile
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "onboarding_completed": True,
                "experience_level": experience_level,
                "learning_pace": learning_pace,
                "focus_area": focus_area,
                "settings": settings,
            }
        },
    )

    # Create initial user context from assessment
    from datetime import datetime

    initial_context = {
        "user_id": user_id,
        "learning": {
            "learning_motivation": focus_area,
            "preferred_learning_style": _get_learning_style_from_answers(submission.answers),
            "available_time_per_week": _get_time_commitment_from_answers(submission.answers),
        },
        "free_text_notes": submission.free_text_goals or "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Check if context already exists
    existing_context = await db.user_context.find_one({"user_id": user_id})
    if not existing_context:
        await db.user_context.insert_one(initial_context)
    else:
        # Update learning section only
        await db.user_context.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "learning": initial_context["learning"],
                    "free_text_notes": initial_context["free_text_notes"],
                    "updated_at": datetime.utcnow()
                }
            }
        )

    return LearningPathResponse(
        recommended_level=experience_level,
        starting_nodes=[str(node["_id"]) for node in recommended_nodes],
        estimated_duration_weeks=duration_weeks,
        personalized_message=ai_response["message"],
        settings=settings,
    )


def _determine_experience_level(answers: List[AssessmentAnswer]) -> str:
    """Determine user's experience level from answers"""
    # Find programming experience answer
    prog_answer = next((a for a in answers if a.question_index == 0), None)
    if not prog_answer:
        return "beginner"

    answer_lower = prog_answer.answer.lower()
    if "complete beginner" in answer_lower or "never written" in answer_lower:
        return "beginner"
    elif "advanced" in answer_lower or "multiple languages" in answer_lower:
        return "advanced"
    else:
        return "intermediate"


def _determine_learning_pace(answers: List[AssessmentAnswer]) -> str:
    """Determine preferred learning pace"""
    time_answer = next((a for a in answers if a.question_index == 4), None)
    if not time_answer:
        return "medium"

    answer_lower = time_answer.answer.lower()
    if "1-2 hours" in answer_lower:
        return "slow"
    elif "10+ hours" in answer_lower or "intensive" in answer_lower:
        return "fast"
    else:
        return "medium"


def _determine_focus_area(answers: List[AssessmentAnswer]) -> str:
    """Determine user's primary focus area"""
    goal_answer = next((a for a in answers if a.question_index == 2), None)
    if not goal_answer:
        return "general"

    answer_lower = goal_answer.answer.lower()
    if "from scratch" in answer_lower:
        return "programming_basics"
    elif "devops concepts" in answer_lower:
        return "devops_fundamentals"
    elif "devops role" in answer_lower:
        return "job_preparation"
    else:
        return "skill_improvement"


async def _get_recommended_nodes(
    db: AsyncIOMotorDatabase, experience_level: str, focus_area: str
) -> List[dict]:
    """Get recommended starting nodes based on assessment"""
    # Build query based on experience level
    query = {}

    if experience_level == "beginner":
        query["difficulty"] = "beginner"
        query["prerequisites"] = {"$size": 0}
    elif experience_level == "intermediate":
        query["difficulty"] = {"$in": ["beginner", "intermediate"]}
    else:
        query["difficulty"] = {"$in": ["intermediate", "advanced"]}

    # Get nodes matching criteria
    nodes = await db.learning_nodes.find(query).limit(3).to_list(length=3)

    # If not enough nodes, get any beginner nodes
    if len(nodes) < 2:
        nodes = await db.learning_nodes.find({"difficulty": "beginner"}).limit(3).to_list(length=3)

    return nodes


def _calculate_duration(experience_level: str, learning_pace: str) -> int:
    """Calculate estimated duration in weeks"""
    base_duration = {
        "beginner": 12,
        "intermediate": 8,
        "advanced": 6,
    }

    pace_multiplier = {
        "slow": 1.5,
        "medium": 1.0,
        "fast": 0.7,
    }

    duration = base_duration.get(experience_level, 10) * pace_multiplier.get(
        learning_pace, 1.0
    )
    return int(duration)


def _summarize_assessment(answers: List[AssessmentAnswer]) -> str:
    """Create a summary of assessment answers for AI"""
    summary_parts = []
    for answer in answers:
        summary_parts.append(f"Q{answer.question_index + 1}: {answer.answer}")
    return " | ".join(summary_parts)


def _get_learning_style_from_answers(answers: List[AssessmentAnswer]) -> str:
    """Extract learning style from assessment answers"""
    # Find learning style answer (question index 3)
    style_answer = next((a for a in answers if a.question_index == 3), None)
    if not style_answer:
        return "balanced"

    answer_lower = style_answer.answer.lower()
    if "step-by-step" in answer_lower or "practice" in answer_lower:
        return "hands_on_incremental"
    elif "quick" in answer_lower:
        return "fast_paced"
    elif "deep" in answer_lower or "theory" in answer_lower:
        return "theoretical_comprehensive"
    elif "real-world" in answer_lower or "projects" in answer_lower:
        return "project_based"
    else:
        return "balanced"


def _get_time_commitment_from_answers(answers: List[AssessmentAnswer]) -> int:
    """Extract time commitment from assessment answers"""
    # Find time commitment answer (question index 4)
    time_answer = next((a for a in answers if a.question_index == 4), None)
    if not time_answer:
        return 5

    answer_lower = time_answer.answer.lower()
    if "1-2 hours" in answer_lower:
        return 2
    elif "3-5 hours" in answer_lower:
        return 4
    elif "6-10 hours" in answer_lower:
        return 8
    elif "10+" in answer_lower:
        return 15
    else:
        return 5
