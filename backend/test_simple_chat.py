import os
import sys
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.agents.master_agent import master_agent

async def main():
    print("Running master agent with simple query...")
    try:
        response = master_agent.run("Hi, who are you?", stream=False)
        print("Response content:")
        print(response.content)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
