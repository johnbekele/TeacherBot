from fastapi import APIRouter
from app.api.v1 import auth, nodes, exercises, progress, chat, onboarding, user_context, learning_session

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(nodes.router)
api_router.include_router(exercises.router)
api_router.include_router(progress.router)
api_router.include_router(chat.router)
api_router.include_router(onboarding.router)
api_router.include_router(user_context.router)
api_router.include_router(learning_session.router)
