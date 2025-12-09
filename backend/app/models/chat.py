from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class MessageContext(BaseModel):
    """Message context"""
    current_exercise: Optional[str] = None
    mode: str = "teaching"  # teaching, grading, hint, onboarding


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str  # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context: Optional[MessageContext] = None


class ChatLogInDB(BaseModel):
    """Chat log in database"""
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    session_id: str
    node_id: Optional[str] = None
    messages: List[ChatMessage] = []
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ChatMessageRequest(BaseModel):
    """Chat message request"""
    message: str
    context: Optional[Dict[str, Any]] = {}


class ChatAction(BaseModel):
    """Action for UI"""
    type: str  # show_content, show_exercise, navigate
    data: Dict[str, Any] = {}


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    response: str
    mode: str = "explanation"
    actions: List[ChatAction] = []
    next_step: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    messages: List[ChatMessage]
