from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    google_api_key: SecretStr
    gemini_model: str = "gemini-3-flash"
    workspace_root: str = "./workspace"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()