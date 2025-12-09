from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis
from bson import ObjectId
from app.db.mongodb import get_database
from app.db.redis import get_redis
from app.utils.security import decode_access_token
from app.models.user import TokenData

security = HTTPBearer()


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency for database access"""
    return await get_database()


async def get_redis_client() -> Redis:
    """Dependency for Redis access"""
    return await get_redis()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    token_data: TokenData = decode_access_token(token)

    if token_data is None:
        raise credentials_exception

    # Get user from database (convert string ID to ObjectId)
    try:
        user = await db.users.find_one({"_id": ObjectId(token_data.user_id)})
    except Exception:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Lightweight dependency to get just user_id from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    token_data: TokenData = decode_access_token(token)

    if token_data is None:
        raise credentials_exception

    return token_data.user_id
