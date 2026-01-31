from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from pydantic import BaseModel
from app.dependencies import get_db, get_current_user
from app.models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserInDB,
    Token,
    UserSettings
)
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Register a new user"""

    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user_dict = {
        "email": user_data.email,
        "full_name": user_data.full_name,
        "password_hash": get_password_hash(user_data.password),
        "created_at": datetime.utcnow(),
        "last_login": None,
        "onboarding_completed": False,
        "settings": UserSettings().dict()
    }

    result = await db.users.insert_one(user_dict)
    user_id = str(result.inserted_id)

    # Initialize progress state for new user
    progress_state = {
        "user_id": user_id,
        "current_node_id": None,
        "completed_nodes": [],
        "unlocked_nodes": [],
        "node_progress": {},
        "overall_stats": {
            "total_exercises_completed": 0,
            "total_time_spent": 0,
            "success_rate": 0.0,
            "streak_days": 0,
            "last_activity": None
        },
        "updated_at": datetime.utcnow()
    }
    await db.user_progress.insert_one(progress_state)

    return {
        "user_id": user_id,
        "message": "User created successfully"
    }


@router.post("/login", response_model=dict)
async def login(
    credentials: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Login user and return JWT token"""

    # Find user
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]}
    )

    # Prepare user response (use .get to avoid KeyError on legacy docs)
    user_response = {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "onboarding_completed": user.get("onboarding_completed", False)
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (client should discard token)"""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "user_id": str(current_user["_id"]),
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "onboarding_completed": current_user.get("onboarding_completed", False),
        "settings": current_user.get("settings", {}),
        "created_at": current_user.get("created_at"),
        "last_login": current_user.get("last_login")
    }


class ProfileUpdate(BaseModel):
    full_name: str


class SettingsUpdate(BaseModel):
    settings: dict


@router.put("/profile")
async def update_profile(
    data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user profile"""
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"full_name": data.full_name}}
    )
    return {"message": "Profile updated successfully"}


@router.put("/settings")
async def update_settings(
    data: SettingsUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user settings"""
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"settings": data.settings}}
    )
    return {"message": "Settings updated successfully"}
