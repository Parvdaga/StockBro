import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.agents.shared_model import get_model
from phi.agent import Agent

def test_groq():
    print("Testing Groq...")
    try:
        model = get_model()
        agent = Agent(model=model, markdown=True)
        response = agent.run("Hi", stream=False)
        print("Response:", response.content)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_groq()
