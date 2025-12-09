"""
User Learning Profile Model
Stores onboarding data, learning preferences, and weak points
"""
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class WeakPoint(BaseModel):
    """Specific area where user struggles"""
    topic: str  # e.g., "function_declaration", "loops", "algorithmic_thinking"
    description: str
    identified_at: datetime
    occurrences: int = 1
    exercises_failed: List[str] = []


class LearningPreferences(BaseModel):
    """User's learning preferences from onboarding"""
    preferred_pace: str = "moderate"  # slow, moderate, fast
    learning_style: str = "mixed"  # visual, hands-on, reading, mixed
    adhd_accommodations: bool = False
    break_reminders: bool = False
    focus_mode: bool = False


class UserProfile(BaseModel):
    """Complete user learning profile"""
    user_id: str

    # Onboarding data
    experience_level: str  # beginner, intermediate, advanced
    background: str  # Previous programming experience
    learning_goals: List[str]  # What they want to achieve
    available_time: str  # hours per week
    specific_interests: List[str]  # Specific tools/topics they mentioned

    # Learning preferences
    preferences: LearningPreferences

    # Performance tracking
    weak_points: List[WeakPoint] = []
    strong_areas: List[str] = []

    # Progress metrics
    total_exercises_completed: int = 0
    total_exercises_failed: int = 0
    average_score: float = 0.0

    # Session history
    last_active: datetime
    created_at: datetime
    updated_at: datetime


class UserProfileInDB(UserProfile):
    """User profile as stored in database"""
    pass
