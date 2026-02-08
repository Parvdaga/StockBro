import google.generativeai as genai
from app.config import settings
import os

api_key = settings.GOOGLE_API_KEY
if not api_key:
    # try loading from .env manually just in case
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("No GOOGLE_API_KEY found.")
    exit()

print(f"Key: {api_key[:5]}...")
genai.configure(api_key=api_key)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
