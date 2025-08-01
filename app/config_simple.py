# Simple config for direct imports
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.n8n_api_base_url = os.getenv("N8N_API_BASE_URL")
        self.n8n_api_key = os.getenv("N8N_API_KEY")

settings = Settings()