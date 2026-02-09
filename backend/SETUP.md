# StockBro Backend - Setup Guide

## ✅ Prerequisites (Already Done)
- [x] Python 3.10+ installed
- [x] Virtual environment created
- [x] Dependencies installed (`pip install -r requirements.txt`)

## 🔧 Quick Setup Steps

### 1. Configure Environment Variables

Copy `.env.example` to `.env` if you haven't already:
```bash
cp .env.example .env
```

**Required Variables** (update in `.env`):
```ini
# Minimum required for basic functionality
GROQ_API_KEY=your_actual_groq_key  # Get from https://console.groq.com/keys
SECRET_KEY=your-secret-key-123     # Any random secure string

# Optional: For full stock data functionality
FINNHUB_API_KEY=your_finnhub_key   # Get from https://finnhub.io
```

### 2. Run the Server

```bash
# Make sure you're in the backend directory
cd backend

# Start the server
python -m uvicorn main:app --reload
```

You should see:
```
🚀 Starting StockBro API v1.0
📊 Database: sqlite+aiosqlite:///./stockbro.db
🤖 LLM: Groq
INFO: Uvicorn running on http://127.0.0.1:8000
```

### 3. Test the API

Visit the interactive API docs:
```
http://localhost:8000/api/v1/docs
```

Or test with curl:
```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

## 🎯 Optional Setup

### Database Migration (For Production)
```bash
# Initialize Alembic migrations
alembic init migrations

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Get Free API Keys

1. **Groq API** (Required for AI features)
   - Visit: https://console.groq.com/keys
   - Sign up (free)
   - Create API key
   - Add to `.env`: `GROQ_API_KEY=gsk_...`

2. **Finnhub API** (Optional - for stock data)
   - Visit: https://finnhub.io/register
   - Sign up (free tier available)
   - Get API key
   - Add to `.env`: `FINNHUB_API_KEY=...`

## 🔍 Verify Everything is Working

### 1. Check Server is Running
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"healthy","version":"1.0.0","database":"connected"}`

### 2. Test AI Chat (Requires Groq API Key)
```bash
# First, signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'

# Then login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'

# Use the access_token from login response
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the stock market?"}'
```

## 📁 Important Files

- **`.env`** - Your environment variables (DO NOT commit to git)
- **`main.py`** - Application entry point
- **`app/config.py`** - Configuration settings
- **`stockbro.db`** - SQLite database (auto-created on first run)

## ❓ Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt
```

### Issue: "GROQ_API_KEY not set"
**Solution:** Add your Groq API key to `.env` file
```ini
GROQ_API_KEY=gsk_your_actual_key_here
```

### Issue: "Port 8000 already in use"
**Solution:** Kill existing process or use different port
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Or use different port
uvicorn main:app --reload --port 8001
```

## 🚀 You're All Set!

Your backend is now running on: **http://localhost:8000**

API Documentation: **http://localhost:8000/api/v1/docs**

Happy coding! 🎉
