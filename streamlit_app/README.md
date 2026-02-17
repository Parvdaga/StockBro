# StockBro Frontend 📈

The frontend of StockBro is built with [Streamlit](https://streamlit.io/), providing an interactive / clean interface to chat with the AI, view stock data, and manage watchlists.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- The **Backend** must be running (see `../backend/README.md`).

### 2. Installation

Navigate to the project root (if not already there) and install dependencies:

```bash
pip install -r streamlit_app/requirements.txt
```

### 3. Configuration

The frontend automatically loads environment variables from `backend/.env`. Ensure you have set up the `.env` file in the `backend/` directory.

Key variables used:
- `SUPABASE_URL`: To connect to the database (for auth/watchlists).
- `SUPABASE_ANON_KEY`: Supabase anonymous key.

### 4. Run the App

From the **project root** directory:

```bash
python -m streamlit run streamlit_app/main.py
```

The app will open in your browser at `http://localhost:8501`.

## 🌟 Features

### 💬 Chat Interface
- Ask questions about Indian stocks (e.g., "Analyze RELIANCE").
- Get AI-generated answers, real-time prices, charts, and relevant news.

### 📈 Market Dashboard
- **Search**: Look up any NSE/BSE stock.
- **Charts**: Interactive candlestick charts (Plotly).
- **Fundamentals**: 52-week high/low, volume, etc.
- **News**: Latest articles for the searched stock.
- **Trending**: See what's hot in the market.

### 📋 Watchlists
- Create multiple watchlists.
- Add/Remove stocks.
- View your save stocks at a glance.

## 📁 Structure

- `main.py`: The entry point and main application logic.
- `requirements.txt`: Python dependencies for the frontend.
