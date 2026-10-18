from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "KICKDIARY API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./kickdiary.db"
    
    # Keamanan & JWT
    SECRET_KEY: str = "kickdiary_secret_jwt_key_2026_ippl_secure_super_safe"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Google AI Gemini
    GEMINI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
