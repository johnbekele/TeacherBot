from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class NodeContent(BaseModel):
    """Node content structure"""
    introduction: str
    concepts: List[str]
    practical_applications: List[str]


class NodeBase(BaseModel):
    """Base node model"""
    node_id: str = Field(..., description="Unique identifier like 'terraform-basics'")
    title: str
    description: str
    category: str  # terraform, pulumi, python, bash, ansible
    difficulty: str  # beginner, intermediate, advanced
    estimated_duration: int  # minutes
    prerequisites: List[str] = []  # array of node_ids
    skills_taught: List[str] = []
    status: str = "available"  # available, locked, deprecated


class NodeCreate(NodeBase):
    """Node creation model"""
    content: NodeContent


class NodeInDB(NodeBase):
    """Node model in database"""
    id: Optional[str] = Field(alias="_id", default=None)
    content: NodeContent
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class NodeProgress(BaseModel):
    """Node progress for a user"""
    status: str = "not_started"  # not_started, in_progress, completed
    completion_percentage: int = 0
    exercises_completed: int = 0
    exercises_total: int = 0
    time_spent: int = 0  # minutes
    last_accessed: Optional[datetime] = None


class NodeResponse(NodeBase):
    """Node response model"""
    id: str = Field(alias="_id")
    content: NodeContent
    locked: bool = False
    progress: Optional[NodeProgress] = None

    class Config:
        populate_by_name = True


class NodeListItem(BaseModel):
    """Simplified node for list views"""
    node_id: str
    title: str
    description: str
    difficulty: str
    estimated_duration: int
    prerequisites: List[str]
    locked: bool = False
    completion_status: str = "not_started"
    completion_percentage: int = 0
