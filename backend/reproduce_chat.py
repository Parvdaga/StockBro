import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app.agents.master_agent import master_agent

async def main():
    print("Running master agent...")
    try:
        # Run sync first as master_agent.run is sync by default in phi
        response = master_agent.run("Should I buy KOTAK BANK stocks for long term?", stream=False)
        print("Response content:")
        print(response.content)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(str(e) + "\n")
            traceback.print_exc(file=f)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
