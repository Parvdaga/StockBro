"""
Shared model configuration for all agents
This ensures all agents use the same LLM (Groq) and avoid OpenAI defaults
"""
import os
from typing import Optional
from phi.model.groq import Groq
from phi.model.google import Gemini
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_shared_model():
    """
    Get the shared LLM model for all agents.
    Priority order: Groq (free, fast) > Gemini (fallback)
    OpenAI has been removed to avoid quota/billing issues.
    """
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    if GROQ_API_KEY:
        print("Using Groq model: llama-3.3-70b-versatile")
        return Groq(id="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
    elif GOOGLE_API_KEY:
        print("Using Gemini model: gemini-pro")
        return Gemini(id="gemini-pro", api_key=GOOGLE_API_KEY)
    else:
        raise ValueError(
            "No LLM API key found. Please set GROQ_API_KEY or GOOGLE_API_KEY in your .env file. "
            "Get free Groq API key at: https://console.groq.com/keys"
        )

# Create a singleton instance
_shared_model = None

def get_model():
    """Get or create the shared model instance"""
    global _shared_model
    if _shared_model is None:
        _shared_model = get_shared_model()
    return _shared_model
