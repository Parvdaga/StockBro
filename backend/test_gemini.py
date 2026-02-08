from phi.model.google import Gemini
from app.config import settings
from phi.llm.message import Message # Import Message class
import logging

# Basic logging setup to avoid "no handler" errors
logging.basicConfig(level=logging.INFO)

print("Gemini attributes:", dir(Gemini))

try:
    print("Trying with id='gemini-1.5-flash'...")
    model = Gemini(id="gemini-1.5-flash", api_key=settings.GOOGLE_API_KEY)
    
    # Correct usage: pass a list of Message objects
    messages = [Message(role="user", content="Hello")]
    response = model.response(messages)
    
    print("Response with id:", response.content) # Access content attribute
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error with id: {e}")

try:
    print("Trying with model='gemini-1.5-flash' (deprecated param)...")
    # Some versions might allow 'model' but 'id' is standard in 2.x
    model = Gemini(id="gemini-1.5-flash", api_key=settings.GOOGLE_API_KEY)
    messages = [Message(role="user", content="Hi there")]
    response = model.response(messages)
    print("Response with model:", response.content)
except Exception as e:
    print(f"Error with model: {e}")
