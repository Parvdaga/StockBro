from app.agents.master_agent import master_agent
from app.config import settings

print("--- Debugging Master Agent ---")
print(f"Mistral/Groq/OpenAI/Gemini API Key present: {bool(settings.GOOGLE_API_KEY)}")
print(f"Groww Key present: {bool(settings.GROWW_API_KEY)}")

try:
    print("Attempting to run agent...")
    # Run a simple query that DOES NOT require tools first to test LLM
    response = master_agent.print_response("Hello, who are you?", stream=False)
    print("LLM Response Success.")
    
    # Run a query that DOES require tools to test Groww
    print("\nAttempting tool call...")
    response = master_agent.print_response("What is the price of RELIANCE?", stream=False)
    print("Tool Response Success.")

except Exception as e:
    print("CRITICAL ERROR CAUGHT:")
    import traceback
    traceback.print_exc()
