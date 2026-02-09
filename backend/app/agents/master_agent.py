from phi.agent import Agent
from phi.storage.agent.sqlite import SqlAgentStorage
from app.config import settings
from app.agents.shared_model import get_model

# Import agents after shared_model to avoid circular imports
from app.agents.finance_agent import finance_agent
from app.agents.news_agent import news_agent


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
    add_history_to_messages=False,  # Disabled to fix AttributeError - history managed by chat service
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
