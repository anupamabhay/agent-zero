"""
Configuration management using Pydantic Settings.
Handles environment variables and defaults.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application Settings."""
    google_api_key: str
    gemini_model: str = "gemini-2.5-pro"
    workspace_root: str = "./workspace_data"
    
    class Config:
        env_file = ".env"

settings = Settings()
