# StockBro Backend

FastAPI backend for the StockBro AI-powered stock analysis application.

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** installed
- **Groq API Key** (free) - [Get it here](https://console.groq.com/keys)

### Setup & Run

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   
   Copy `.env.example` to `.env` and add your API keys:
   ```ini
   GROQ_API_KEY=your_groq_api_key_here
   DB_URL=sqlite+aiosqlite:///./stockbro.db
   ```

3. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Verify it's running:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/api/v1/docs
   - Health: http://localhost:8000/health

## 📋 API Keys

### Required
- **GROQ_API_KEY** - Free tier available at [console.groq.com](https://console.groq.com/keys)

### Optional
- **GOOGLE_API_KEY** - Fallback LLM provider
- **GROWW_API_KEY** - For Indian stock market data
- **FINNHUB_API_KEY** - For global stock data
- **GNEWS_API_KEY** - For financial news

> **Note:** Supabase is **not required**. The backend works perfectly with SQLite for development.

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── agents/          # AI agents (finance, news, master)
│   │   ├── finance_agent.py
│   │   ├── news_agent.py
│   │   ├── master_agent.py
│   │   └── shared_model.py
│   ├── api/v1/          # API endpoints
│   │   ├── auth.py      # Authentication
│   │   ├── chat.py      # AI chat
│   │   ├── stocks.py    # Stock data
│   │   └── watchlist.py # User watchlists
│   ├── db/              # Database models
│   ├── services/        # Business logic
│   └── config.py        # Configuration
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## 🔧 Available Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Create account
- `POST /api/v1/auth/login` - Login

### Chat
- `POST /api/v1/chat/` - Chat with AI assistant
- `GET /api/v1/chat/conversations` - Get chat history

### Stocks
- `GET /api/v1/stocks/{symbol}` - Get stock data
- `GET /api/v1/stocks/search` - Search stocks

### Watchlist
- `GET /api/v1/watchlist/` - Get user watchlist
- `POST /api/v1/watchlist/` - Add to watchlist
- `DELETE /api/v1/watchlist/{symbol}` - Remove from watchlist

## 🛠️ Troubleshooting

### Port Already in Use
```powershell
# Windows: Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

### ModuleNotFoundError
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### AttributeError: 'dict' object has no attribute 'role'
This has been fixed in the current version. If you encounter this:
- Ensure `add_history_to_messages=False` in `app/agents/master_agent.py`
- Restart the server

### GROQ_API_KEY not set
Get a free API key from [console.groq.com](https://console.groq.com/keys) and add to `.env`:
```ini
GROQ_API_KEY=gsk_your_key_here
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Or using PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

## 💾 Database

- **Development:** SQLite (default, no setup required)
- **Production:** PostgreSQL/Supabase supported

The database schema is automatically created on first run.

## 📚 Documentation

Interactive API documentation (Swagger UI) is available at:
- http://localhost:8000/api/v1/docs

## 🤖 AI Features

StockBro uses a multi-agent architecture powered by **Groq**:
- **Master Agent** - Coordinates team and manages conversations
- **Finance Agent** - Provides stock analysis and market data
- **News Agent** - Fetches and analyzes financial news

All agents use the **llama-3.3-70b-versatile** model by default.

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS enabled for frontend (configurable in `config.py`)

## 📝 Environment Variables

See [`.env.example`](file:///.env.example) for all available configuration options and [SETUP.md](file:///SETUP.md) for detailed setup instructions.
