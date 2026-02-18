# StockBro AI Enhancement: API Research & Technical Requirements

## 1. Groww Trade API (Python SDK)
The Groww Trade API provides professional-grade access to Indian market data.

### Key Features:
- **REST APIs**: For order placement, portfolio management, and historical data.
- **WebSocket (GrowwFeed)**: Essential for real-time updates. The `GrowwFeed` class in the `growwapi` module supports subscribing to specific instrument IDs for live price streams.
- **Instrument Search**: Supports lookup of NSE/BSE instruments.

### Implementation Strategy:
- **Transition**: Move from scraping-style web APIs to the official SDK (`growwapi`).
- **Real-time**: Implement a WebSocket manager in the backend to maintain a connection to Groww and push updates to the frontend.
- **Rate Limiting**: The SDK requires an API key. We must implement a strict token-bucket limiter to stay within free-tier bounds (if applicable) or handle 429 errors gracefully.

## 2. NewsData.io API
NewsData.io is used for financial news and historical news data.

### Constraints (Free Tier):
- **Daily Limit**: ~200 credits per day.
- **Rate Limit**: 30 credits per 15 minutes.
- **Credits**: Each request consumes credits. Multiple articles in one response are cost-effective.

### Optimization:
- **Caching**: Increase TTL for news to 30-60 minutes as news doesn't change every second.
- **Batching**: Fetch top headlines once and cache them globally to serve multiple users.
- **Fallback**: If rate-limited, serve the most recent cached news or provide a "Market Overview" based on static domain knowledge.

## 3. Real-time Functionality
To achieve "real-time" without overwhelming APIs:
- **Backend**: Use `FastAPI` WebSockets to broadcast data.
- **Frontend**: Streamlit's native support for real-time is limited (requires re-running). We will use a combination of `st.empty()` for updates or a custom HTML/JS component for smoother charts.
- **Polling vs WebSockets**: WebSockets are preferred for efficiency. If WebSockets are blocked, fall back to 5-second polling.

## 4. Domain Knowledge Base
- **Static Layer**: A JSON/Markdown file containing definitions for F&O, IPO, and common sectors (Defense, IT, Banking).
- **Dynamic Layer**: Use the `search_stock` tool to augment the knowledge base with current market leaders.

## 5. NLP Enhancements
- **Intent Recognition**: Use a small LLM (like `gpt-4.1-nano`) or a structured prompt to classify queries into: `TRADE`, `ANALYZE`, `NEWS`, `EDUCATION`, `IPO`.
- **Keyword Mapping**: Expand the current `QueryRouter` with more robust regex and fuzzy matching for Indian stock nicknames (e.g., "Reliance" -> "RELIANCE", "HDFC" -> "HDFCBANK").
