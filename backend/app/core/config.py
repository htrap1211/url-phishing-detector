"""
Configuration settings for the application.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "URL Phishing Detector"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./phishing_detector.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # API Keys
    GOOGLE_SAFE_BROWSING_API_KEY: Optional[str] = None
    VIRUSTOTAL_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    API_KEY_HEADER: str = "X-API-Key"
    ALLOWED_ORIGINS: list = ["http://localhost:4200", "chrome-extension://*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # ML Model
    MODEL_PATH: str = "../models/trained/model_v1.0.0.pkl"
    SCALER_PATH: str = "../models/trained/scaler_v1.0.0.pkl"
    MODEL_VERSION: str = "v1.0.0"
    
    # Features
    USE_MOCK_APIS: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
