from phi.agent import Agent
from app.config import settings
from app.agents.shared_model import get_model

# Import agents after shared_model to avoid circular imports
from app.agents.finance_agent import finance_agent
from app.agents.news_agent import news_agent


# Note: Agent memory is now managed by Supabase (conversations/messages tables)
# No need for local database storage

master_agent = Agent(
    name="StockBro",
    role="Financial Advisor & Team Lead",
    model=get_model(),
    team=[finance_agent, news_agent],
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
