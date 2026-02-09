from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.googlesearch import GoogleSearch
from app.agents.shared_model import get_model

# Use shared Groq/Gemini model to avoid OpenAI default
news_agent = Agent(
    name="News Agent",
    role="News Reporter",
    model=get_model(),  # Use shared model
    tools=[DuckDuckGo()],
    instructions=[
        "Search for the latest news on the given topic.",
        "Summarize the key points from the top 3-5 articles.",
        "Provide links to the sources."
    ],
    show_tool_calls=True,
    markdown=True,
)
