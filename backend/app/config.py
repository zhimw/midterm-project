from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    llm_provider: str = "openai"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 5
    
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
