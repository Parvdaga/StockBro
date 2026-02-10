import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # App Settings
    PROJECT_NAME: str = "StockBro Backend"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ]
    
    # LLM API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    PHIDATA_API_KEY: Optional[str] = os.getenv("PHI_API_KEY")
    
    # Stock Market APIs
    GROWW_API_KEY: Optional[str] = os.getenv("GROWW_API_KEY")
    GROWW_API_SECRET: Optional[str] = os.getenv("GROWW_API_SECRET")
    GROWW_USER_ID: Optional[str] = os.getenv("GROWW_USER_ID")
    
    # News APIs
    GNEWS_API_KEY: Optional[str] = os.getenv("GNEWS_API_KEY")
    
    # Supabase (Database & Auth)
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")

settings = Settings()
