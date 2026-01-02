"""
B1Z KODLAB - Configuration
Powered by MiniMax-M2
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    MINIMAX_API_KEY: str = ""
    MINIMAX_API_BASE: str = "https://api.minimax.chat/v1"
    MINIMAX_MODEL: str = "MiniMax-M2"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://modulllm.com",
    ]

    # B1Z Platform
    PLATFORM_NAME: str = "B1Z KODLAB"
    MAX_CODE_LENGTH: int = 100000
    AI_TIMEOUT: int = 30

    # 11 Theme Configuration
    PARALLEL_AI_COUNT: int = 11  # 11 Akıl Harmanları
    DAILY_CHALLENGE_POINTS: int = 111
    MASTERY_POINTS: int = 1111

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
