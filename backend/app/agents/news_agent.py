"""
News Agent — fetches Indian stock market news via GNews API
"""
from phi.agent import Agent
from app.config import settings
from app.agents.shared_model import get_model
import requests


GNEWS_SEARCH_URL = "https://gnews.io/api/v4/search"
GNEWS_HEADLINES_URL = "https://gnews.io/api/v4/top-headlines"


def get_stock_news(query: str) -> str:
    """
    Search for the latest Indian stock market news on a given topic.
    
    Args:
        query (str): Topic to search for (e.g., 'Reliance Industries', 
                     'Indian stock market', 'NIFTY', 'banking sector')
    
    Returns:
        str: Formatted summary of top news articles with titles, sources, and URLs.
    """
    api_key = settings.GNEWS_API_KEY
    if not api_key:
        return "News search is not available (GNEWS_API_KEY not configured)."

    try:
        params = {
            "q": query,
            "lang": "en",
            "country": "in",
            "max": 5,
            "token": api_key,
        }
        response = requests.get(GNEWS_SEARCH_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            return f"Error fetching news: HTTP {response.status_code}"

        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return f"No recent news found for '{query}'."

        lines = [f"📰 **Latest News: {query}**\n"]
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", {}).get("name", "Unknown")
            url = article.get("url", "")
            published = article.get("publishedAt", "")[:10]  # date only
            description = article.get("description", "")[:150]

            lines.append(f"**{i}. {title}**")
            lines.append(f"   📅 {published} | 📌 {source}")
            if description:
                lines.append(f"   {description}...")
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
    api_key = settings.GNEWS_API_KEY
    if not api_key:
        return "News headlines not available (GNEWS_API_KEY not configured)."

    try:
        params = {
            "category": "business",
            "lang": "en",
            "country": "in",
            "max": 5,
            "token": api_key,
        }
        response = requests.get(GNEWS_HEADLINES_URL, params=params, timeout=10)

        if response.status_code != 200:
            return f"Error fetching headlines: HTTP {response.status_code}"

        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return "No business headlines available right now."

        lines = ["📰 **Top Indian Business Headlines**\n"]
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", {}).get("name", "Unknown")
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
