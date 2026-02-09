from phi.model.groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
try:
    llm = Groq(id="llama-3.3-70b-versatile", api_key=api_key)
    print("Methods:", dir(llm))
    try:
        from phi.model.message import Message
        print("Invoking with Message object...")
        response = llm.invoke([Message(role="user", content="Hello")])
        print("Response:", response)
    except Exception as e:
        print("Error invoking with Message:", e)
        
    try:
        print("Invoking with dict...")
        response = llm.invoke([{"role": "user", "content": "Hello"}])
        print("Response:", response)
    except Exception as e:
        print("Error invoking with dict:", e)

except Exception as e:
    print("Error initializing Groq:", e)
