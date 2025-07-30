# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    n8n_api_base_url: str
    n8n_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
