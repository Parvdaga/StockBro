from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.googlesearch import GoogleSearch

# We can use Phidata's built-in DuckDuckGo tool
news_agent = Agent(
    name="News Agent",
    role="News Reporter",
    tools=[DuckDuckGo()],
    instructions=[
        "Search for the latest news on the given topic.",
        "Summarize the key points from the top 3-5 articles.",
        "Provide links to the sources."
    ],
    show_tool_calls=True,
    markdown=True,
)
