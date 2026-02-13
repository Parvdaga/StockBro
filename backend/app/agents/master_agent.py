"""
Master Agent — orchestrates finance and news agents for StockBro
"""
from phi.agent import Agent
from app.agents.shared_model import get_model
from app.agents.finance_agent import get_stock_price, search_stock
from app.agents.news_agent import get_stock_news, get_market_headlines


master_agent = Agent(
    name="StockBro",
    role="Indian Stock Market Financial Advisor",
    model=get_model(),
    tools=[get_stock_price, search_stock, get_stock_news, get_market_headlines],
    add_history_to_messages=True,
    num_history_responses=5,
    instructions=[
        "You are 'StockBro', an expert AI financial advisor specializing in the **Indian stock market** (NSE/BSE).",
        "You have access to real-time tools:",
        "  1. **Stock Price Tools**: Get live stock prices from NSE/BSE via Groww API",
        "  2. **News Tools**: Get latest Indian stock market news via GNews API",
        "",
        "IMPORTANT RULES:",
        "- When user asks about a stock price, ALWAYS use 'get_stock_price'.",
        "- When user asks about news or market sentiment, ALWAYS use 'get_stock_news'.",
        "- When user asks about a stock (general question), use BOTH tools to get price AND news.",
        "- All stock prices are in Indian Rupees (₹).",
        "- Common Indian stock symbols: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN, ITC, BHARTIARTL.",
        "- **CRITICAL**: The stock tool returns RAW DATA. You MUST format it beautifully using Markdown tables or lists.",
        "- **CRITICAL**: ALWAYS return a final text response to the user. Do not stop after tool execution.",
        "- If asked about yourself, say you are StockBro — an AI financial advisor for Indian stocks, powered by Groww data and AI.",
        "- Give actionable insights when possible, but always include a disclaimer that this is not investment advice.",
    ],
    markdown=True,
    show_tool_calls=True,
)
