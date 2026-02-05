import os
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
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    PHIDATA_API_KEY: str = os.getenv("PHI_API_KEY")
    
    # Angel One SmartAPI (Indian Market)
    ANGEL_API_KEY: str = os.getenv("ANGEL_API_KEY")
    ANGEL_CLIENT_CODE: str = os.getenv("ANGEL_CLIENT_CODE")
    ANGEL_PASSWORD: str = os.getenv("ANGEL_PASSWORD")
    ANGEL_TOTP_KEY: str = os.getenv("ANGEL_TOTP_KEY")
    
    # Optional tools
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")

settings = Settings()
