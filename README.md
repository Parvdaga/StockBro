# StockBro AI 📈

An AI-powered stock analysis assistant for the **Indian stock market** (NSE/BSE). Chat with StockBro to get real-time stock prices, market news, candlestick charts, and analyst-style insights — all powered by LLMs and live data.

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit (Python) |
| Backend API | FastAPI (Python) |
| LLM | Groq (Llama 3.3-70b) / Gemini fallback |
| Stock Data | Groww API (live prices + historical OHLCV) |
| News | NewsData.io (Indian stock market news) |
| Database & Auth | Supabase (PostgreSQL + Auth) |
| Visualization | Plotly (candlestick & line charts) |
| Agent Framework | Phidata (multi-agent orchestration) |

## ⚙️ Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/Parvdaga/StockBro.git
cd StockBro
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
cp .env.example .env           # Then fill in your API keys
```

### 3. Configure `.env`

| Variable | Source | Required |
|----------|--------|----------|
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) | ✅ |
| `NEWSDATA_API_KEY` | [newsdata.io](https://newsdata.io/) | ✅ |
| `SUPABASE_URL` | Supabase dashboard | ✅ |
| `SUPABASE_ANON_KEY` | Supabase dashboard | ✅ |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase dashboard | ✅ |
| `GROWW_API_KEY` | Groww SDK (optional) | ❌ |
| `GOOGLE_API_KEY` | Google AI Studio (Gemini fallback) | ❌ |

See [backend/.env.example](backend/.env.example) for all variables with defaults.

### 4. Run

```bash
# Terminal 1 — Backend
cd backend
uvicorn main:app --reload

# Terminal 2 — Frontend
cd ..
python -m streamlit run streamlit_app/main.py
```

- Backend: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- Frontend: [http://localhost:8501](http://localhost:8501)

## 📊 Features

### 💬 Chat with StockBro
Ask about any Indian stock — get structured responses with price data, insights, and disclaimers.

### 📈 Market Dashboard
Search any NSE stock to see live prices, candlestick charts, and recent news side by side.

### 📋 Watchlists
Create and manage personal stock watchlists (saved in Supabase).

### 🔄 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/chat/` | Chat with AI analyst |
| `GET /api/v1/stocks/{symbol}` | Live stock price |
| `GET /api/v1/stocks/trending` | Trending Indian stocks |
| `GET /api/v1/charts/{symbol}/history?duration=3M` | Historical OHLCV for charting |
| `GET /api/v1/news/search?q=topic` | Search news articles |
| `GET /api/v1/news/headlines` | Top business headlines |

## 🧪 Testing

```bash
cd backend

# Unit tests (mocked — no API keys needed)
python -m pytest tests/unit/ -v

# Integration tests (requires running backend + valid keys)
python -m pytest tests/integration/ -v
```

## 📁 Project Structure

```
StockBro/
├── backend/
│   ├── main.py                     # FastAPI entry point
│   ├── requirements.txt
│   ├── .env.example                # All env vars documented
│   ├── app/
│   │   ├── config.py               # Settings + cache/rate-limit config
│   │   ├── integrations/
│   │   │   ├── cache.py            # TTL cache utility
│   │   │   ├── retry.py            # Exponential backoff
│   │   │   ├── newsdata.py         # NewsData.io client (cached, retried)
│   │   │   └── groww.py            # Groww client (live + historical + cached)
│   │   ├── agents/
│   │   │   ├── shared_model.py     # Groq/Gemini LLM selection
│   │   │   ├── master_agent.py     # Main AI orchestrator
│   │   │   ├── finance_agent.py    # Stock price tools
│   │   │   └── news_agent.py       # News tools
│   │   ├── api/v1/
│   │   │   ├── router.py           # Route aggregator
│   │   │   ├── chat.py             # Chat endpoint
│   │   │   ├── stocks.py           # Stock data endpoints
│   │   │   ├── news.py             # News proxy endpoint
│   │   │   ├── charts.py           # Chart data endpoint
│   │   │   ├── auth.py             # Authentication
│   │   │   └── watchlist.py        # Watchlist CRUD
│   │   └── schemas/
│   │       ├── stock.py            # StockData, ChartDataPoint, ChartDataResponse
│   │       └── chat.py             # ChatRequest, ChatResponse, ChartConfig
│   └── tests/
│       ├── unit/                   # Mocked unit tests
│       └── integration/            # Live integration tests
├── streamlit_app/
│   ├── main.py                     # Streamlit frontend
│   └── requirements.txt
└── README.md
```

## 📚 Related Research

| Title | Summary |
|-------|---------|
| AI-Driven Financial Advisory: The Rise of Robo-Advisors | Examines AI-powered robo-advisors' impact on financial services |
| An AI Analyst Made 30 Years of Stock Picks (Stanford) | AI analyst outperformed 93% of mutual fund managers over 30 years |
| Leveraging AI Multi-Agent Systems in Financial Analysis | Multi-agent AI integration in financial analytics |
| Large Language Models in Equity Markets | LLMs for sentiment mining and detecting market anomalies |

## ⚠️ Disclaimer

StockBro AI outputs are **not financial advice**. Always consult professionals and conduct your own research before making investment decisions. Models may produce errors, outdated responses, or biased interpretations.
