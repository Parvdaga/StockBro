"""
News Agent — fetches Indian stock market news via NewsData.io API
"""
from phi.agent import Agent
from app.config import settings
from app.agents.shared_model import get_model
from app.integrations.newsdata import NewsDataClient
import asyncio
import concurrent.futures

# Initialize shared client
_news_client = NewsDataClient()

# Thread pool for running async code from sync context
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def _run_async(coro):
    """Run an async coroutine from a sync context, even if an event loop is running."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an existing event loop (e.g. FastAPI)
        # Run in a new thread with its own event loop
        def _thread_run():
            return asyncio.run(coro)
        future = _executor.submit(_thread_run)
        return future.result(timeout=15)
    else:
        # No running loop — safe to use asyncio.run
        return asyncio.run(coro)


def get_stock_news(query: str) -> str:
    """
    Search for the latest Indian stock market news on a given topic.
    
    Args:
        query (str): Topic to search for (e.g., 'Reliance Industries', 
                     'Indian stock market', 'NIFTY', 'banking sector')
    
    Returns:
        str: Formatted summary of top news articles with titles, sources, and URLs.
    """
    if not _news_client.enabled:
        return "News search is not available (NEWSDATA_API_KEY not configured)."

    try:
        articles = _run_async(_news_client.search_news(query=query, max_results=5))

        if not articles:
            return f"No recent news found for '{query}'."

        lines = [f"📰 **Latest News: {query}**\n"]
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", "Unknown")
            url = article.get("url", "")
            published = article.get("published_at", "")[:16]
            description = article.get("description", "")
            if description and len(description) > 150:
                 description = description[:150] + "..."

            lines.append(f"**{i}. {title}**")
            lines.append(f"   📅 {published} | 📌 {source}")
            if description:
                lines.append(f"   {description}")
            lines.append(f"   🔗 [Read more]({url})")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching news: {str(e)}"


def get_market_headlines() -> str:
    """
    Get top Indian business/market headlines.
    
    Returns:
        str: Top 5 Indian business headlines with sources and links.
    """
    if not _news_client.enabled:
        return "News headlines not available (NEWSDATA_API_KEY not configured)."

    try:
        articles = _run_async(_news_client.get_top_headlines(category="business", max_results=5))

        if not articles:
            return "No business headlines available right now."

        lines = ["📰 **Top Indian Business Headlines**\n"]
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", "Unknown")
            url = article.get("url", "")
            lines.append(f"**{i}. {title}**")
            lines.append(f"   📌 {source} | 🔗 [Read]({url})")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching headlines: {str(e)}"


# Create the News Agent  
news_agent = Agent(
    name="News Agent",
    role="Indian Stock Market News Reporter",
    model=get_model(),
    tools=[get_stock_news, get_market_headlines],
    instructions=[
        "You are a specialist in Indian stock market news.",
        "Use 'get_stock_news' to search for news about specific stocks, companies, or market topics.",
        "Use 'get_market_headlines' to get the latest Indian business/market headlines.",
        "When asked about a stock, search for news about that company.",
        "When asked about market overview, get business headlines.",
        "Summarize the key points from the articles and provide source links.",
        "Focus on Indian market news and sentiments.",
    ],
    show_tool_calls=True,
    markdown=True,
)
