import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextlib import asynccontextmanager
from app.config import get_settings
from app.db.mongodb import connect_to_mongodb, close_mongodb_connection
from app.db.redis import connect_to_redis, close_redis_connection
from app.api.v1 import api_router

settings = get_settings()

# CORS: hardcoded so Vercel frontend always works (no dependency on env)
CORS_ORIGINS_LIST = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://techerbot.vercel.app",
    "https://teacherbot.vercel.app",
]
CORS_ORIGIN_REGEX = re.compile(r"^https://[\w-]+\.vercel\.app$")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    await connect_to_mongodb()
    try:
        await connect_to_redis()
    except Exception as e:
        print(f"⚠️ Redis optional: {e}")
    print(f"🚀 {settings.APP_NAME} started")
    yield
    # Shutdown
    await close_mongodb_connection()
    try:
        await close_redis_connection()
    except Exception:
        pass
    print(f"👋 {settings.APP_NAME} stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

def _origin_allowed(origin: str | None) -> bool:
    if not origin:
        return False
    if origin in CORS_ORIGINS_LIST:
        return True
    return bool(CORS_ORIGIN_REGEX.fullmatch(origin))


class EarlyOptionsMiddleware(BaseHTTPMiddleware):
    """Respond to OPTIONS (preflight) immediately with 200 and CORS headers so preflight always passes even if app is cold or DB is down."""

    async def dispatch(self, request: Request, call_next):
        if request.method != "OPTIONS":
            return await call_next(request)
        origin = request.headers.get("origin") or ""
        headers = {
            "Access-Control-Max-Age": "600",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Expose-Headers": "*",
        }
        if _origin_allowed(origin):
            headers["Access-Control-Allow-Origin"] = origin
        return Response(status_code=200, headers=headers)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS_LIST,
    allow_origin_regex=r"^https://[\w-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Run first (added last): handle OPTIONS before any other middleware/lifespan so preflight always gets 200
app.add_middleware(EarlyOptionsMiddleware)

# Include API routes
app.include_router(api_router, prefix="/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
