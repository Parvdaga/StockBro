import os
import sys
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.agents.finance_agent import finance_agent
from app.agents.news_agent import news_agent

async def test_finance():
    print("\n--- Testing Finance Agent ---")
    try:
        response = finance_agent.run("What is the price of RELIANCE?", stream=False)
        print("Finance Response:", response.content)
    except Exception as e:
        print(f"Finance Agent Error: {e}")
        import traceback
        traceback.print_exc()

async def test_news():
    print("\n--- Testing News Agent ---")
    try:
        response = news_agent.run("News about Reliance Industries", stream=False)
        print("News Response:", response.content)
    except Exception as e:
        print(f"News Agent Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_finance()
    await test_news()

if __name__ == "__main__":
    asyncio.run(main())
