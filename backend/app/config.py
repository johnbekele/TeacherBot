from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "MyTeacher API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "myteacher"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0

    # Vector DB
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = ""
    PINECONE_INDEX_NAME: str = "myteacher-memory"

    # AI
    ANTHROPIC_API_KEY: str = ""

    # Sandbox
    SANDBOX_TIMEOUT: int = 30  # seconds
    SANDBOX_MEMORY_LIMIT: str = "256m"
    SANDBOX_CPU_LIMIT: str = "0.5"
    MAX_CODE_LENGTH: int = 10000
    MAX_OUTPUT_SIZE: int = 10240  # 10KB

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    EXERCISE_SUBMIT_LIMIT: int = 10
    CHAT_MESSAGE_LIMIT: int = 5

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
