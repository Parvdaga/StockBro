from phi.agent import Agent
from phi.model.groq import Groq
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage
from app.config import settings
from app.agents.finance_agent import finance_agent
from app.agents.news_agent import news_agent

from phi.model.google import Gemini

# Determine LLM Provider
# Priority: Groq > OpenAI > Gemini (to avoid Gemini deprecation warnings)
def get_model():
    """
    Get the LLM model based on available API keys.
    Priority order: Groq (fastest, no deprecation) > OpenAI > Gemini
    """
    if settings.GROQ_API_KEY:
        print("🚀 Using Groq model: llama-3.3-70b-versatile")
        return Groq(id="llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY)
    elif settings.OPENAI_API_KEY:
        print("🤖 Using OpenAI model: gpt-4o")
        return OpenAIChat(model="gpt-4o", api_key=settings.OPENAI_API_KEY)
    elif settings.GOOGLE_API_KEY:
        print("⚠️  Using Gemini (may have deprecation warnings)")
        return Gemini(id="gemini-2.0-flash", api_key=settings.GOOGLE_API_KEY)
    else:
        raise ValueError(
            "No LLM API key found. Please set GROQ_API_KEY, OPENAI_API_KEY, "
            "or GOOGLE_API_KEY in your .env file."
        )


# Database Storage for Memory
storage = None
if settings.DB_URL:
    # Use SqlAgentStorage which works with SQLite/Postgres
    # Note: For SQLite, url format is sqlite:///...
    db_url = settings.DB_URL
    if "sqlite+aiosqlite" in db_url:
         # Agent storage needs sync driver for now (usually)
         db_url = db_url.replace("sqlite+aiosqlite", "sqlite")
    
    storage = SqlAgentStorage(table_name="agent_memory", db_url=db_url)

master_agent = Agent(
    name="StockBro",
    role="Financial Advisor & Team Lead",
    model=get_model(),
    team=[finance_agent, news_agent],
    storage=storage,
    add_history_to_messages=True,
    num_history_responses=5,
    instructions=[
        "You are 'StockBro', a helpful and polite financial advisor.",
        "Coordinate with your team (Finance Agent and News Agent) to answer user queries.",
        "If the user asks about a stock price, delegate to Finance Agent.",
        "If the user asks for news, delegate to News Agent.",
        "Always synthesize the information into a clear, helpful response.",
        "If asked about yourself, say you are StockBro, powered by AI."
    ],
    markdown=True,
)
