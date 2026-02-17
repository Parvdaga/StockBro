# StockBro AI 🚀

**StockBro** is an AI-powered stock analysis assistant for the **Indian Stock Market**. It combines real-time data, news, and advanced LLMs to provide actionable insights.

## 🏗️ Architecture

The project is divided into two main components:

1.  **Backend** (`/backend`): A robust FastAPI engine that powers the AI agents, data fetching, and API.
2.  **Frontend** (`/streamlit_app`): A clean, interactive Streamlit interface for users.

## 🛠️ Tech Stack

- **AI**: Groq (Llama 3), Phidata (Agents).
- **Backend**: FastAPI, Supabase (PostgreSQL + Auth).
- **Frontend**: Streamlit, Plotly.
- **Data**: Groww (Market Data), NewsData.io (News).

## ⚡ Quick Start

To get the full application running, you need to start both the backend and the frontend.

### 1. Setup Backend
Follow the [Backend Documentation](backend/README.md) to set up the environment and start the server.

```bash
# Quick command (from backend/ directory)
uvicorn app.main:app --reload
```

### 2. Setup Frontend
Follow the [Frontend Documentation](streamlit_app/README.md) to install dependencies and launch the UI.

```bash
# Quick command (from root directory)
python -m streamlit run streamlit_app/main.py
```

## 📖 Documentation

- [Backend Guide](backend/README.md): Setup, Configuration, API details.
- [Frontend Guide](streamlit_app/README.md): Installation, Features, Usage.

## ⚠️ Disclaimer

StockBro AI outputs are **not financial advice**. Always consult professionals and conduct your own research before making investment decisions.
