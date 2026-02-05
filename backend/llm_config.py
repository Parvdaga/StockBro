import os
from phi.llm.groq import Groq
from phi.llm.openai import OpenAIChat
from phi.llm.gemini import Gemini
from dotenv import load_dotenv

load_dotenv()

def get_llm(provider="groq", model="llama3-70b-8192"):
    """
    Factory function to get the LLM instance based on provider.
    """
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found.")
        return Groq(model=model, api_key=api_key)
    
    elif provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
             print("Warning: GOOGLE_API_KEY not found.")
        return Gemini(model=model, api_key=api_key)

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        return OpenAIChat(model=model, api_key=api_key)
    
    else:
        # Fallback or default
        return Groq(model="llama3-70b-8192")
