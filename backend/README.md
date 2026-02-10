# StockBro Backend

> 🚀 **AI-Powered Stock Analysis Platform** - FastAPI backend with Supabase authentication and multi-agent AI system

A sophisticated backend system for stock market analysis, powered by AI agents and real-time market data from Groww API.

---

## 📑 Table of Contents

- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start-5-minutes)
- [Detailed Setup Guide](#-detailed-setup-guide)
- [Configuration](#-configuration)
- [Running the Server](#-running-the-server)
- [Testing Your Setup](#-testing-your-setup)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Development Tips](#-development-tips)

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your computer:

### Required Software

1. **Python 3.10 or higher**
   - Download from: https://www.python.org/downloads/
   - **Important**: During installation, check "Add Python to PATH"
   - Verify installation:
     ```bash
     python --version
     # Should show: Python 3.10.x or higher
     ```

2. **pip** (Python package manager)
   - Usually comes with Python
   - Verify installation:
     ```bash
     pip --version
     # Should show: pip 21.x or higher
     ```

3. **Git** (optional, for version control)
   - Download from: https://git-scm.com/downloads

### Required API Keys

You'll need to sign up for these **free** API keys:

1. **Groq API Key** (Required for AI features)
   - Sign up: https://console.groq.com/keys
   - Click "Create API Key"
   - Copy and save your key (starts with `gsk_`)

2. **Supabase Account** (Required for database & auth)
   - Sign up: https://supabase.com
   - Create a new project
   - Get your credentials from Project Settings → API

3. **Groww API** (Required for Indian stock data)
   - Sign up at Groww and get API credentials
   - You'll need: API Key, API Secret, and User ID

4. **Google Gemini API** (Optional, as backup AI)
   - Get from: https://makersuite.google.com/app/apikey

5. **GNews API** (Optional, for news features)
   - Get from: https://gnews.io/

---

## ⚡ Quick Start (5 Minutes)

If you're experienced with Python, here's the express setup:

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# 5. Edit .env and add your API keys

# 6. Run the server
uvicorn main:app --reload
```

Visit http://localhost:8000/api/v1/docs to see the API documentation!

---

## 🔧 Detailed Setup Guide

Follow these steps if you're new to Python or backend development:

### Step 1: Download the Project

If you have Git:
```bash
git clone <repository-url>
cd StockBro/backend
```

If you don't have Git, download the ZIP file and extract it, then navigate to the `backend` folder.

### Step 2: Create a Virtual Environment (Recommended)

A virtual environment keeps your project dependencies separate from other Python projects.

**Windows:**
```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

> 💡 **Tip**: You need to activate the virtual environment every time you open a new terminal window!

### Step 3: Install Dependencies

With your virtual environment activated:

```bash
pip install -r requirements.txt
```

This will install approximately 25 packages. It may take 2-5 minutes depending on your internet speed.

**You should see output like:**
```
Successfully installed fastapi-0.xxx uvicorn-0.xxx ...
```

### Step 4: Set Up Environment Variables

Environment variables store sensitive information like API keys.

1. **Copy the template file:**
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```

2. **Open `.env` in a text editor** (Notepad, VS Code, etc.)

3. **Fill in your credentials:**

```ini
# LLM Providers (AI)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx  # Paste your Groq key here
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxx      # Optional: Google Gemini key

# Stock Market APIs
GROWW_API_KEY=eyJraWQiOiJaTUtjxxxxx    # Your Groww API key
GROWW_API_SECRET=6nypH2DJnKxxxxxXXX     # Your Groww API secret
GROWW_USER_ID=your-email@gmail.com      # Your Groww account email

# News API
GNEWS_API_KEY=0c9b63bxxxxxxxxxxxxxxx    # Optional: GNews API key

# Supabase (Database & Authentication)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx

# Optional: Phidata (for advanced AI features)
PHI_API_KEY=your_phidata_key_optional
```

4. **Save the file**

> ⚠️ **Important**: Never commit your `.env` file to Git! It's already in `.gitignore`.

### Step 5: Set Up Supabase Database

1. **Go to your Supabase project dashboard**
2. **Click on "SQL Editor" in the left sidebar**
3. **Create a new query**
4. **Copy the contents of `app/db/schema.sql`**
5. **Paste and run the SQL**

This creates all necessary tables and security policies.

---

## 🚀 Running the Server

### Start the Development Server

With your virtual environment activated:

```bash
uvicorn main:app --reload
```

**What each part means:**
- `uvicorn` - The ASGI server
- `main:app` - Run the `app` from `main.py`
- `--reload` - Auto-restart on code changes (development only)

**You should see:**
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
🚀 Starting StockBro Backend v1.0.0
📊 Database: uwvvggyfhmwzevjtfebq.supabase.co
🤖 LLM: Groq
INFO:     Application startup complete.
```

### Server is Running! 🎉

Your backend is now running at:
- **API Base**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs (Interactive API documentation)
- **Health Check**: http://localhost:8000/health

> 💡 **Tip**: Keep this terminal window open. The server runs here!

### Stop the Server

Press `CTRL+C` in the terminal to stop the server.

---

## ✅ Testing Your Setup

### Test 1: Health Check

**Using Browser:**
1. Open http://localhost:8000/health
2. You should see:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "database": "connected"
   }
   ```

**Using cURL:**
```bash
curl http://localhost:8000/health
```

**Using PowerShell:**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test 2: Interactive API Documentation

1. Visit http://localhost:8000/api/v1/docs
2. You'll see **Swagger UI** with all available endpoints
3. Try the `/health` endpoint:
   - Click on "GET /health"
   - Click "Try it out"
   - Click "Execute"
   - See the response!

### Test 3: Get Stock Data

Using the API docs (http://localhost:8000/api/v1/docs):

1. Find `GET /api/v1/stocks/{symbol}`
2. Click "Try it out"
3. Enter a stock symbol (e.g., `NSE-RELIANCE`)
4. Click "Execute"
5. View real-time stock data!

---

## 📚 API Documentation

### Available Endpoints

#### Authentication
- `GET /api/v1/auth/me` - Get current user profile

#### Watchlists
- `POST /api/v1/watchlists/` - Create a watchlist
- `GET /api/v1/watchlists/` - Get all watchlists
- `GET /api/v1/watchlists/{id}` - Get specific watchlist
- `PATCH /api/v1/watchlists/{id}` - Update watchlist
- `DELETE /api/v1/watchlists/{id}` - Delete watchlist
- `POST /api/v1/watchlists/{id}/items` - Add stock to watchlist
- `DELETE /api/v1/watchlists/{id}/items/{item_id}` - Remove stock

#### Stocks
- `GET /api/v1/stocks/{symbol}` - Get real-time stock data
  - Supports Indian stocks: `NSE-RELIANCE`, `BSE-SENSEX`, etc.

#### Chat (AI Assistant)
- `POST /api/v1/chat/` - Send message to AI
- `GET /api/v1/chat/conversations` - Get conversation history
- `GET /api/v1/chat/conversations/{id}` - Get specific conversation
- `DELETE /api/v1/chat/conversations/{id}` - Delete conversation

### Authentication

Most endpoints require authentication via Supabase JWT tokens.

**How to get authenticated:**
1. Use Supabase client library in your frontend
2. User signs up/logs in via Supabase Auth
3. Get JWT token from Supabase
4. Include in requests: `Authorization: Bearer <token>`

---

## 📁 Project Structure

```
backend/
├── app/                          # Main application code
│   ├── agents/                   # AI agents
│   │   ├── master_agent.py      # Orchestrator agent
│   │   ├── finance_agent.py     # Stock analysis agent
│   │   ├── news_agent.py        # Financial news agent
│   │   └── shared_model.py      # Shared AI model config
│   ├── api/                      # API layer
│   │   └── v1/                  # API version 1
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── chat.py          # Chat endpoints
│   │       ├── stocks.py        # Stock data endpoints
│   │       ├── watchlist.py     # Watchlist endpoints
│   │       └── router.py        # API router
│   ├── core/                     # Core utilities
│   │   ├── dependencies.py      # Dependency injection
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── supabase_client.py   # Supabase client
│   ├── db/                       # Database
│   │   ├── schema.sql           # Database schema (Supabase)
│   │   └── models/              # (Deprecated - using Supabase)
│   ├── integrations/             # External API integrations
│   │   ├── groww.py             # Groww stock API
│   │   └── finnhub.py           # Finnhub API (optional)
│   ├── schemas/                  # Pydantic models
│   │   ├── auth.py              # Auth schemas
│   │   ├── chat.py              # Chat schemas
│   │   ├── stock.py             # Stock schemas
│   │   └── watchlist.py         # Watchlist schemas
│   ├── services/                 # Business logic
│   │   └── stock_service.py     # Stock data service
│   └── config.py                 # Configuration settings
├── tests/                        # Test suite
│   ├── integration/             # Integration tests
│   └── unit/                    # Unit tests
├── .env                          # Environment variables (create this)
├── .env.example                  # Environment template
├── .gitignore                   # Git ignore file
├── main.py                       # Application entry point
├── README.md                     # This file
├── requirements.txt              # Python dependencies
└── TESTING_GUIDE.md             # Testing documentation
```

---

## 🛠️ Troubleshooting

### Issue: "python: command not found"

**Solution:**
- Windows: Reinstall Python and check "Add Python to PATH"
- macOS/Linux: Use `python3` instead of `python`

### Issue: Port 8000 already in use

**Error message:**
```
ERROR: [Errno 48] Address already in use
```

**Solution (Windows):**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

**Solution (macOS/Linux):**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

### Issue: ModuleNotFoundError

**Error message:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: GROQ_API_KEY not set

**Error message:**
```
ValueError: GROQ_API_KEY environment variable is not set
```

**Solution:**
1. Make sure you created `.env` file
2. Add your Groq API key to `.env`:
   ```ini
   GROQ_API_KEY=gsk_your_actual_key_here
   ```
3. Restart the server

### Issue: Supabase connection error

**Error message:**
```
ValueError: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set
```

**Solution:**
1. Check your `.env` file has all three Supabase variables:
   ```ini
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbGci...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
   ```
2. Make sure you ran the `schema.sql` in Supabase SQL Editor
3. Restart the server

### Issue: "Stock not found" when testing

**Solution:**
- Make sure you're using the correct format: `NSE-RELIANCE` or `BSE-SENSEX`
- Check that your Groww API credentials are correct
- Verify the stock symbol exists on Groww platform

### Issue: Import errors after cleanup

**Solution:**
```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} +  # macOS/Linux
# Or manually delete __pycache__ folders on Windows

# Restart the server
```

---

## 💻 Development Tips

### Using Virtual Environment

Always activate before working:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

To deactivate:
```bash
deactivate
```

### Hot Reload

The server auto-reloads when you save code changes (thanks to `--reload` flag). No need to restart manually!

### Viewing Logs

All logs appear in your terminal. Watch for:
- ✅ `INFO` - Normal operation
- ⚠️ `WARNING` - Potential issues
- ❌ `ERROR` - Something went wrong

### Installing New Packages

```bash
# Install a package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Database Schema Changes

After modifying `schema.sql`:
1. Go to Supabase SQL Editor
2. Run the new/modified SQL
3. No server restart needed!

### Testing API Endpoints

**Method 1: Swagger UI (Easiest)**
- http://localhost:8000/api/v1/docs
- Click, try, execute!

**Method 2: cURL**
```bash
curl -X GET "http://localhost:8000/api/v1/stocks/NSE-RELIANCE"
```

**Method 3: Python requests**
```python
import requests
response = requests.get("http://localhost:8000/health")
print(response.json())
```

**Method 4: Postman**
- Import the OpenAPI schema from `/api/v1/openapi.json`

---

## 🤖 AI Features

StockBro uses a **multi-agent AI system**:

### Agents
- **Master Agent**: Coordinates the team and manages conversations
- **Finance Agent**: Provides stock analysis and market data using Groww API
- **News Agent**: Fetches and analyzes financial news using DuckDuckGo

### How It Works
1. User sends a message via chat endpoint
2. Master Agent receives the message
3. Master Agent delegates to appropriate specialized agent
4. Specialized agent processes and returns data
5. Master Agent synthesizes response
6. Response stored in Supabase conversations table

### Powered By
- **Groq**: Primary LLM provider (llama-3.3-70b-versatile)
- **Google Gemini**: Fallback option
- **Phidata**: Agent framework

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use strong SECRET_KEY** - Generate with:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```
3. **Enable Supabase RLS** - Row Level Security policies are in `schema.sql`
4. **Use HTTPS in production** - Not HTTP
5. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

---

## 📖 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Supabase Documentation**: https://supabase.com/docs
- **Groq Documentation**: https://console.groq.com/docs
- **Phidata Documentation**: https://docs.phidata.com/

---

## 🆘 Getting Help

If you're stuck:

1. **Check the error message** - Often tells you exactly what's wrong
2. **Review this README** - Solution might be in Troubleshooting section
3. **Check API docs** - http://localhost:8000/api/v1/docs
4. **Review logs** - Look at terminal output for clues
5. **Search online** - Copy error message to Google/Stack Overflow

---

## 🎉 Success Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with all API keys
- [ ] Supabase database schema applied
- [ ] Server starts without errors (`uvicorn main:app --reload`)
- [ ] Health check returns "healthy" (http://localhost:8000/health)
- [ ] API documentation loads (http://localhost:8000/api/v1/docs)
- [ ] Can fetch stock data (try `NSE-RELIANCE`)

**If all checked - congratulations! Your backend is ready! 🚀**

---

## 📝 Quick Reference

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

# Run tests
pytest tests/ -v

# Check code style
black app/
flake8 app/

# Deactivate virtual environment
deactivate
```

---

**Built with ❤️ using FastAPI, Supabase, and AI**
