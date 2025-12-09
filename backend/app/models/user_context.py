"""
User Context Models - Comprehensive user information for AI personalization
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class EducationBackground(BaseModel):
    """User's educational background"""
    highest_degree: Optional[str] = None  # e.g., "High School", "Bachelor's", "Master's"
    field_of_study: Optional[str] = None
    current_student: bool = False
    institution: Optional[str] = None
    graduation_year: Optional[int] = None


class WorkExperience(BaseModel):
    """User's work experience"""
    current_role: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None  # "startup", "small", "medium", "large", "enterprise"
    technical_background: bool = False
    previous_roles: Optional[List[str]] = []


class LearningContext(BaseModel):
    """Learning-related context"""
    learning_motivation: Optional[str] = None  # Career change, skill improvement, curiosity, etc.
    available_time_per_week: Optional[int] = None  # hours
    preferred_learning_times: Optional[List[str]] = []  # "morning", "afternoon", "evening", "night"
    learning_challenges: Optional[List[str]] = []  # ADHD, dyslexia, time constraints, etc.
    previous_learning_experiences: Optional[str] = None
    preferred_learning_style: Optional[str] = None


class CareerGoals(BaseModel):
    """User's career aspirations"""
    target_role: Optional[str] = None
    target_industry: Optional[str] = None
    timeline: Optional[str] = None  # "3 months", "6 months", "1 year", "2+ years"
    salary_expectations: Optional[str] = None
    location_preference: Optional[str] = None  # "remote", "hybrid", "on-site"
    relocation_willing: bool = False


class PersonalContext(BaseModel):
    """Personal life context"""
    age_range: Optional[str] = None  # "18-24", "25-34", "35-44", "45-54", "55+"
    family_status: Optional[str] = None  # "single", "married", "with kids", etc.
    timezone: Optional[str] = None
    native_language: Optional[str] = None
    additional_languages: Optional[List[str]] = []
    hobbies_interests: Optional[List[str]] = []


class UserContextCreate(BaseModel):
    """Create or update user context"""
    education: Optional[EducationBackground] = None
    work: Optional[WorkExperience] = None
    learning: Optional[LearningContext] = None
    career_goals: Optional[CareerGoals] = None
    personal: Optional[PersonalContext] = None
    free_text_notes: Optional[str] = None  # Any additional information user wants to share


class UserContextResponse(BaseModel):
    """User context response"""
    user_id: str
    education: Optional[EducationBackground] = None
    work: Optional[WorkExperience] = None
    learning: Optional[LearningContext] = None
    career_goals: Optional[CareerGoals] = None
    personal: Optional[PersonalContext] = None
    free_text_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserContextInDB(BaseModel):
    """User context as stored in database"""
    user_id: str
    education: Optional[Dict] = None
    work: Optional[Dict] = None
    learning: Optional[Dict] = None
    career_goals: Optional[Dict] = None
    personal: Optional[Dict] = None
    free_text_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
