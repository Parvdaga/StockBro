
import asyncio
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

async def test_groq():
    print("Testing Groq Integration...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables!")
        return
    
    print(f"✅ Found GROQ_API_KEY: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        from phi.model.groq import Groq
        llm = Groq(id="llama3-70b-8192", api_key=api_key)
        print("✅ Initialized Groq LLM client")
        
        print("Sending test message...")
        response = llm.invoke([{"role": "user", "content": "Hello, are you working?"}])
        print(f"✅ Response received: {response}")
        
    except Exception as e:
        print(f"❌ Error testing Groq: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_groq())
