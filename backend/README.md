# StockBro Backend ⚙️

The backend is the core engine of StockBro, built with **FastAPI**. It handles:
- **API Endpoints**: Chat, Stocks, News, Watchlists.
- **AI Agents**: Orchestrates LLMs (Groq/Gemini) with Phidata.
- **Data Fetching**: Integrates with Groww (Stocks) and NewsData.io (News).
- **Database**: Manages user data and watchlists in Supabase.

## 🚀 Setup & Run

### 1. Prerequisites
- Python 3.10+
- API Keys (Groq, Supabase, etc. - see below).

### 2. Installation

Navigate to the `backend` directory:

```bash
cd backend
python -m venv venv
# Activate venv:
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configuration

Duplicate `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | For the primary LLM (Llama 3). |
| `SUPABASE_URL` | Database URL. |
| `SUPABASE_SERVICE_ROLE_KEY` | Admin key for backend operations. |
| `GROWW_API_KEY` | Optional (if using Groww SDK). |
| `NEWSDATA_API_KEY` | For fetching news. |

### 4. Run the Server

From the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

- **API Docs**: `http://localhost:8000/api/v1/docs`
- **Health Check**: `http://localhost:8000/health`

## 🧪 Testing

We have a verification script to check if the backend is healthy:

```bash
python scripts/verify_backend.py
```

This will run a series of tests against the running server.

## 📁 Structure

- `app/main.py`: Application entry point.
- `app/api/`: API route handlers (Chat, Stocks, etc.).
- `app/agents/`: AI capabilities.
- `app/integrations/`: External API clients.
- `app/core/`: Configuration and database connection.
