from phi.model.google import Gemini
from app.config import settings
import logging

# Basic logging setup to avoid "no handler" errors
logging.basicConfig(level=logging.INFO)

print("Gemini attributes:", dir(Gemini))

try:
    print("Trying with id='gemini-1.5-flash'...")
    model = Gemini(id="gemini-1.5-flash", api_key=settings.GOOGLE_API_KEY)
    response = model.response("Hello")
    print("Response with id:", response)
except Exception as e:
    print(f"Error with id: {e}")

try:
    print("Trying with model='gemini-1.5-flash'...")
    # Some versions use 'model'
    model = Gemini(model="gemini-1.5-flash", api_key=settings.GOOGLE_API_KEY)
    response = model.response("Hello")
    print("Response with model:", response)
except Exception as e:
    print(f"Error with model: {e}")
