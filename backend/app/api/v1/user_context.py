"""
User Context API endpoints - Comprehensive user information management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional

from app.dependencies import get_db, get_current_user_id
from app.models.user_context import (
    UserContextCreate,
    UserContextResponse,
    EducationBackground,
    WorkExperience,
    LearningContext,
    CareerGoals,
    PersonalContext
)

router = APIRouter(prefix="/user-context", tags=["User Context"])


@router.get("", response_model=dict)
async def get_user_context(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get comprehensive user context"""
    context = await db.user_context.find_one({"user_id": user_id})

    if not context:
        # Return empty context if none exists
        return {
            "user_id": user_id,
            "education": None,
            "work": None,
            "learning": None,
            "career_goals": None,
            "personal": None,
            "free_text_notes": None,
            "exists": False
        }

    # Convert MongoDB document to response format
    return {
        "user_id": user_id,
        "education": context.get("education"),
        "work": context.get("work"),
        "learning": context.get("learning"),
        "career_goals": context.get("career_goals"),
        "personal": context.get("personal"),
        "free_text_notes": context.get("free_text_notes"),
        "created_at": context.get("created_at"),
        "updated_at": context.get("updated_at"),
        "exists": True
    }


@router.put("", response_model=dict)
async def update_user_context(
    context_data: UserContextCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user context (creates if doesn't exist)"""

    # Check if context exists
    existing_context = await db.user_context.find_one({"user_id": user_id})

    # Prepare update data
    update_data = {}
    if context_data.education:
        update_data["education"] = context_data.education.dict(exclude_none=True)
    if context_data.work:
        update_data["work"] = context_data.work.dict(exclude_none=True)
    if context_data.learning:
        update_data["learning"] = context_data.learning.dict(exclude_none=True)
    if context_data.career_goals:
        update_data["career_goals"] = context_data.career_goals.dict(exclude_none=True)
    if context_data.personal:
        update_data["personal"] = context_data.personal.dict(exclude_none=True)
    if context_data.free_text_notes:
        update_data["free_text_notes"] = context_data.free_text_notes

    update_data["updated_at"] = datetime.utcnow()

    if existing_context:
        # Update existing context
        await db.user_context.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    else:
        # Create new context
        update_data["user_id"] = user_id
        update_data["created_at"] = datetime.utcnow()
        await db.user_context.insert_one(update_data)

    return {
        "message": "User context updated successfully",
        "user_id": user_id
    }


@router.patch("/education", response_model=dict)
async def update_education(
    education: EducationBackground,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update only education section"""
    await _ensure_context_exists(db, user_id)

    await db.user_context.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "education": education.dict(exclude_none=True),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Education updated successfully"}


@router.patch("/work", response_model=dict)
async def update_work(
    work: WorkExperience,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update only work experience section"""
    await _ensure_context_exists(db, user_id)

    await db.user_context.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "work": work.dict(exclude_none=True),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Work experience updated successfully"}


@router.patch("/learning", response_model=dict)
async def update_learning(
    learning: LearningContext,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update only learning context section"""
    await _ensure_context_exists(db, user_id)

    await db.user_context.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "learning": learning.dict(exclude_none=True),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Learning context updated successfully"}


@router.patch("/career-goals", response_model=dict)
async def update_career_goals(
    career_goals: CareerGoals,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update only career goals section"""
    await _ensure_context_exists(db, user_id)

    await db.user_context.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "career_goals": career_goals.dict(exclude_none=True),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Career goals updated successfully"}


@router.patch("/personal", response_model=dict)
async def update_personal(
    personal: PersonalContext,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update only personal context section"""
    await _ensure_context_exists(db, user_id)

    await db.user_context.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "personal": personal.dict(exclude_none=True),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Personal context updated successfully"}


@router.post("/notes", response_model=dict)
async def add_note(
    note: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Add or update free-text notes"""
    await _ensure_context_exists(db, user_id)

    await db.user_context.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "free_text_notes": note,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Note added successfully"}


async def _ensure_context_exists(db: AsyncIOMotorDatabase, user_id: str):
    """Ensure user context document exists"""
    existing = await db.user_context.find_one({"user_id": user_id})
    if not existing:
        await db.user_context.insert_one({
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })


async def get_user_context_for_ai(db: AsyncIOMotorDatabase, user_id: str) -> str:
    """
    Get formatted user context for AI prompts
    Returns a comprehensive summary of user information
    """
    context = await db.user_context.find_one({"user_id": user_id})

    if not context:
        return "No detailed user context available yet."

    context_parts = []

    # Education
    if education := context.get("education"):
        edu_text = f"Education: {education.get('highest_degree', 'Unknown')} in {education.get('field_of_study', 'N/A')}"
        if education.get("current_student"):
            edu_text += " (currently studying)"
        context_parts.append(edu_text)

    # Work Experience
    if work := context.get("work"):
        work_text = f"Work: {work.get('current_role', 'N/A')}"
        if years := work.get("years_of_experience"):
            work_text += f" with {years} years of experience"
        work_text += f" in {work.get('industry', 'N/A')}"
        if work.get("technical_background"):
            work_text += " (technical background)"
        context_parts.append(work_text)

    # Learning Context
    if learning := context.get("learning"):
        learn_text = f"Learning: Motivated by {learning.get('learning_motivation', 'N/A')}"
        if time := learning.get("available_time_per_week"):
            learn_text += f", can dedicate {time} hours/week"
        if challenges := learning.get("learning_challenges"):
            learn_text += f", challenges: {', '.join(challenges)}"
        context_parts.append(learn_text)

    # Career Goals
    if goals := context.get("career_goals"):
        goal_text = f"Goals: Targeting {goals.get('target_role', 'N/A')} role"
        if timeline := goals.get("timeline"):
            goal_text += f" within {timeline}"
        if location := goals.get("location_preference"):
            goal_text += f", prefers {location} work"
        context_parts.append(goal_text)

    # Personal Context
    if personal := context.get("personal"):
        personal_text = []
        if age := personal.get("age_range"):
            personal_text.append(f"age {age}")
        if lang := personal.get("native_language"):
            personal_text.append(f"native {lang} speaker")
        if personal_text:
            context_parts.append(f"Personal: {', '.join(personal_text)}")

    # Free text notes
    if notes := context.get("free_text_notes"):
        context_parts.append(f"Additional info: {notes}")

    return " | ".join(context_parts) if context_parts else "Basic user profile available."
