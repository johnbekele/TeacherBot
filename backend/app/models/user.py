from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserSettings(BaseModel):
    """User settings"""
    focus_mode: bool = False
    break_reminders: bool = True
    pace_preference: str = "medium"  # slow, medium, fast
    adhd_mode: bool = False


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """User model in database"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    onboarding_completed: bool = False
    settings: UserSettings = Field(default_factory=UserSettings)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserResponse(UserBase):
    """User response model (public)"""
    id: str = Field(alias="_id")
    onboarding_completed: bool
    settings: UserSettings
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True


class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
