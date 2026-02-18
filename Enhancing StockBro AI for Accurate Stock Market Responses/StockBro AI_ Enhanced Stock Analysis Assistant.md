# StockBro AI: Enhanced Stock Analysis Assistant

StockBro AI is an intelligent financial advisor specializing in the Indian stock market. This project enhances its capabilities to provide high-quality, accurate responses to a wide range of stock-related inquiries, including IPOs, long-term investments, intraday trading, futures and options, and domain-specific questions. It integrates real-time data, improved natural language processing (NLP), and cost-effective API management.

## Key Enhancements

### 1. Input Handling & NLP

- **Improved Query Understanding**: The `query_router.py` has been significantly enhanced to better parse and understand various types of stock-related queries. It now uses more robust natural language processing (NLP) techniques to identify keywords and user intent.
- **Nickname Matching**: The system can now recognize common stock nicknames (e.g., "HDFC" for "HDFCBANK", "Reliance" for "RELIANCE") and map them to their official symbols, improving user experience.
- **Intent Prioritization**: The intent detection logic has been refined to prioritize specific financial queries (e.g., price requests) over general educational queries when a stock symbol is explicitly mentioned.

### 2. Data Source Integration

- **Groww API Integration**: The `groww.py` integration has been strengthened to retrieve the most current stock values. It includes:
    - **Enhanced Caching**: Implemented `TTLCache` with `stale_window` to serve slightly older data when rate limits are hit, ensuring continuous service.
    - **Request Coalescing**: Concurrent requests for the same data are now coalesced into a single upstream call, reducing API calls and improving efficiency.
    - **Robust Error Handling**: Improved error handling and retry mechanisms for API calls.
- **NewsData.io API**: The `newsdata.py` client now includes more explicit rate-limiting handling and caching strategies to comply with free-tier usage (180 requests/day, 30 requests/hour).

### 3. Response Generation

- **Structured Responses**: The AI model is trained to provide structured responses that address user queries in detail, leveraging templates for common questions (e.g., F&O basics, intraday plans, IPO overviews).
- **Fallback Mechanism**: The enhanced caching and rate-limiting logic in `groww.py` and `newsdata.py` acts as a fallback, allowing the AI to provide relevant information even when real-time API calls are temporarily unavailable.

### 4. Real-Time Functionality

- **Auto-Refresh in Streamlit**: The `streamlit_app/main.py` now includes an auto-refresh mechanism, allowing the frontend to periodically fetch updated data and refresh stock graphs and information without manual intervention. This is set to a `REFRESH_INTERVAL` of 10 seconds.
- **Visual Elements**: The Streamlit application continues to utilize Plotly for interactive charts and graphs, representing stock performance over time.

### 5. Domain-Specific Knowledge

- **Knowledge Base (`knowledge_base.py`)**: A new module `knowledge_base.py` has been introduced to store and retrieve information on common stock market terms (IPO, F&O, LTP, Market Cap), notable stocks in various sectors (Banking, IT, Defense, Automobile, Energy, Pharma, Consumer), and investment strategies. This provides a static, reliable source of information.
- **Integration with Master Agent**: The `master_agent.py` now leverages this knowledge base to provide educational content and sector-specific stock lists, enhancing the AI's ability to answer domain-specific questions.

## Setup and Configuration

To run StockBro AI, you need to set up the backend and frontend components.

### Prerequisites

- Python 3.9+
- `pip` (Python package installer)
- Git
- Supabase account (for authentication and conversation history)
- Groww API Key (optional, for official SDK integration, though web scraping is used for free tier)
- NewsData.io API Key (for financial news)

### 1. Clone the Repository

```bash
git clone https://github.com/Parvdaga/StockBro.git
cd StockBro
```

### 2. Backend Setup

Navigate to the `backend` directory:

```bash
cd backend
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```
SUPABASE_URL="YOUR_SUPABASE_URL"
SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"
SUPABASE_SERVICE_ROLE_KEY="YOUR_SUPABASE_SERVICE_ROLE_KEY" # Used for backend operations

# Optional: For Groww API SDK (if you have access)
GROWW_API_KEY="YOUR_GROWW_API_KEY"

# Required for NewsData.io integration
NEWSDATA_API_KEY="YOUR_NEWSDATA_API_KEY"
```

- **Supabase**: Follow the Supabase documentation to set up a new project. Apply the `schema.sql` located in `backend/app/db/schema.sql` to your Supabase database. This sets up tables for profiles, watchlists, conversations, and messages.
- **NewsData.io**: Obtain a free API key from [NewsData.io](https://newsdata.io/).

#### Run the Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be accessible at `http://localhost:8000`.

### 3. Frontend Setup (Streamlit)

Open a new terminal and navigate to the `streamlit_app` directory:

```bash
cd streamlit_app
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Run the Frontend

```bash
streamlit run main.py
```

The Streamlit application will open in your web browser, usually at `http://localhost:8501`.

## Usage

1.  **Login**: Use your Supabase credentials to log in to the Streamlit application. If you don't have an account, you can create one via Supabase or use test credentials if configured.
2.  **Chat with StockBro**: Enter your stock-related queries in the chat input. Examples:
    -   "What is the current price of Reliance?"
    -   "Show me the latest news for TCS."
    -   "Explain F&O basics."
    -   "Give me an intraday plan for HDFCBANK."
    -   "What are the top defense stocks?"
    -   "Show me the chart for INFY for the last 3 months."
3.  **Market Overview**: Explore trending stocks and market headlines.
4.  **Watchlist**: Manage your personalized stock watchlists.

## Code Review Notes and Recommendations

### General

-   **Modularity**: The project structure is generally modular, separating concerns into `agents`, `integrations`, `schemas`, and `services`.
-   **Asynchronous Operations**: Effective use of `asyncio` and `httpx.AsyncClient` for non-blocking I/O operations, which is crucial for performance in API-heavy applications.

### Backend (`backend/`)

-   **`app/agents/master_agent.py`**: The master agent effectively orchestrates calls to specialized agents based on user intent. The addition of `get_sector_stocks` and `explain_term` tools enhances its capabilities.
-   **`app/agents/query_router.py`**: The NLP enhancements, including nickname matching and refined intent prioritization, significantly improve query understanding. Further expansion of `KNOWN_SYMBOLS` and `NICKNAMES` could improve coverage.
-   **`app/integrations/groww.py`**: The implementation of `TTLCache` with `stale_window` and `RequestCoalescer` is excellent for managing API rate limits and improving responsiveness. The fallback to stale data on rate limits or network errors is a robust solution for free-tier usage.
-   **`app/integrations/newsdata.py`**: Similar to `groww.py`, the caching and rate-limiting logic is well-implemented. Consider adding more granular control over news categories if the free tier allows.
-   **`app/core/knowledge_base.py`**: This new module provides a solid foundation for domain-specific knowledge. It can be expanded with more terms, sectors, and even basic investment principles.
-   **Testing**: Unit tests for `query_router.py` have been added, which is a good practice. Expanding test coverage to other critical modules (e.g., `groww.py`, `newsdata.py` integrations) would further improve code quality and reliability.

### Frontend (`streamlit_app/`)

-   **User Interface**: The Streamlit UI is clean and functional. The custom CSS styling enhances the visual appeal.
-   **Real-time Data**: The auto-refresh mechanism is a practical solution for simulating real-time updates within Streamlit's architecture. For truly real-time, low-latency updates, a more advanced frontend framework with WebSocket support (e.g., React with a dedicated WebSocket client) might be considered in the future, but the current approach is effective for the given constraints.
-   **Error Handling**: Frontend error messages are user-friendly, guiding the user when data is unavailable or API calls fail.

## Future Improvements

-   **Advanced NLP**: Explore more sophisticated NLP models for sentiment analysis of news articles and more nuanced intent recognition.
-   **Portfolio Management**: Enhance the watchlist and portfolio features with more detailed analytics and tracking.
-   **User Feedback Loop**: Implement a more formal feedback mechanism within the application to collect user interactions and improve AI responses.
-   **Scalability**: For higher loads, consider deploying the FastAPI backend with a production-ready ASGI server (e.g., Gunicorn) and optimizing database queries.
-   **Alternative Data Sources**: Research and integrate additional free-tier data sources for redundancy and broader coverage, especially for historical data and fundamental analysis.
