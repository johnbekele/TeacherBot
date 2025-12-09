from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId


class NodeProgressDetail(BaseModel):
    """Progress for a specific node"""
    status: str = "not_started"  # not_started, in_progress, completed
    completion_percentage: int = 0
    exercises_completed: int = 0
    exercises_total: int = 0
    time_spent: int = 0  # minutes
    last_accessed: Optional[datetime] = None


class OverallStats(BaseModel):
    """Overall user statistics"""
    total_exercises_completed: int = 0
    total_time_spent: int = 0  # minutes
    success_rate: float = 0.0
    streak_days: int = 0
    last_activity: Optional[datetime] = None


class ProgressStateInDB(BaseModel):
    """User progress state in database"""
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str = Field(..., unique=True)
    current_node_id: Optional[str] = None
    completed_nodes: List[str] = []
    unlocked_nodes: List[str] = []
    node_progress: Dict[str, NodeProgressDetail] = {}
    overall_stats: OverallStats = Field(default_factory=OverallStats)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ProgressResponse(BaseModel):
    """Progress response"""
    current_node: Optional[str] = None
    completed_nodes: List[str] = []
    unlocked_nodes: List[str] = []
    overall_stats: OverallStats
    node_progress: Dict[str, NodeProgressDetail] = {}


class Strength(BaseModel):
    """User strength"""
    concept: str
    proficiency: int  # 0-100


class Weakness(BaseModel):
    """User weakness"""
    concept: str
    confusion_count: int


class LearningPatterns(BaseModel):
    """User learning patterns"""
    best_time_of_day: Optional[str] = None
    average_session_length: int = 0  # minutes
    preferred_pace: str = "medium"


class StatsResponse(BaseModel):
    """Detailed stats response"""
    strengths: List[Strength] = []
    weaknesses: List[Weakness] = []
    learning_patterns: LearningPatterns
