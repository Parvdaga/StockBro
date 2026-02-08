import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # App Settings
    PROJECT_NAME: str = "StockBro Backend"
    API_V1_STR: str = "/api/v1"
    
    # Database
    # Ensure DB_URL is set in .env. Example: postgresql+asyncpg://user:pass@host:port/dbname
    DB_URL: str = os.getenv("DB_URL", "sqlite+aiosqlite:///./stockbro.db")
    
    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    PHIDATA_API_KEY: Optional[str] = os.getenv("PHI_API_KEY")
    
    # Groww API (Indian Market)
    GROWW_API_KEY: Optional[str] = os.getenv("GROWW_API_KEY")
    GROWW_API_SECRET: Optional[str] = os.getenv("GROWW_API_SECRET")
    GROWW_USER_ID: Optional[str] = os.getenv("GROWW_USER_ID")
    
    # Optional tools
    GNEWS_API_KEY: Optional[str] = os.getenv("GNEWS_API_KEY")

settings = Settings()
