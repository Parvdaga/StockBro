import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import time

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_env_path = os.path.join(current_dir, "..", "backend", ".env")
load_dotenv(backend_env_path)

# --- Configuration ---
BACKEND_URL = "http://localhost:8000/api/v1"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

st.set_page_config(
    page_title="StockBro - AI Stock Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Card Style */
    .stock-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 16px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stock-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }
    .stock-card h4 {
        color: #e0e0e0;
        margin-bottom: 4px;
    }
    .stock-card h2 {
        color: #ffffff;
        margin-bottom: 4px;
    }
    
    /* News Card */
    .news-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
        padding: 16px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 12px;
        transition: transform 0.15s;
    }
    .news-card:hover {
        transform: translateY(-2px);
    }
    .news-card h4 a {
        color: #64b5f6;
        text-decoration: none;
    }
    .news-card h4 a:hover {
        color: #90caf9;
        text-decoration: underline;
    }
    .news-card small {
        color: #9e9e9e;
    }
    .news-card p {
        color: #bdbdbd;
        font-size: 0.9em;
    }
    
    /* Positive/Negative Colors */
    .positive { color: #00e676; font-weight: 600; }
    .negative { color: #ff5252; font-weight: 600; }
    
    /* Chat Message Styles */
    .stChatMessage {
        background-color: #262730;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Chart container */
    .chart-header {
        color: #90caf9;
        font-size: 0.95em;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Reusable UI Components
# ──────────────────────────────────────────────
def render_chart(chart_config: dict, headers: dict):
    """Fetch chart data from backend and render Plotly candlestick chart."""
    try:
        data_url = chart_config.get("data_url", "")
        symbol = chart_config.get("symbol", "STOCK")
        chart_type = chart_config.get("chart_type", "candlestick")

        url = f"http://localhost:8000{data_url}" if data_url.startswith("/") else data_url
        res = requests.get(url, headers=headers, timeout=15)

        if res.status_code == 200:
            chart_data = res.json()
            data_points = chart_data.get("data", [])
            if not data_points:
                st.caption(f"No chart data available for {symbol}")
                return

            df = pd.DataFrame(data_points)
            # Convert timestamp to datetime
            if df["timestamp"].max() > 1e12:
                df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
            else:
                df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

            if chart_type == "candlestick":
                fig = go.Figure(data=[go.Candlestick(
                    x=df["datetime"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    increasing_line_color="#00e676",
                    decreasing_line_color="#ff5252",
                )])
            else:
                fig = go.Figure(data=[go.Scatter(
                    x=df["datetime"],
                    y=df["close"],
                    mode="lines",
                    line=dict(color="#64b5f6", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(100,181,246,0.1)",
                )])

            fig.update_layout(
                title=f"📊 {symbol} Price Chart",
                template="plotly_dark",
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_rangeslider_visible=False,
                margin=dict(l=40, r=20, t=50, b=30),
                font=dict(color="#e0e0e0"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption(f"Could not load chart for {symbol}")
    except Exception as e:
        st.caption(f"Chart unavailable: {e}")


def render_stock_card(stock: dict):
    """Render a single stock data card."""
    color = "positive" if (stock.get('change_percent') or 0) >= 0 else "negative"
    change_val = stock.get('change_percent', 0) or 0
    change_sign = "+" if change_val >= 0 else ""
    st.markdown(f"""
    <div class="stock-card">
        <h4>{stock.get('name', stock['symbol'])}</h4>
        <h2>₹{stock['current_price']:,.2f}</h2>
        <p class="{color}">{change_sign}{change_val:.2f}%</p>
        <small style="color:#9e9e9e">Vol: {stock.get('volume', 'N/A'):,}</small>
    </div>
    """, unsafe_allow_html=True)


def render_news_panel(news_items: list):
    """Render news articles as styled cards."""
    for item in news_items:
        description = item.get("description", "")
        if description and len(description) > 120:
            description = description[:120] + "..."
        st.markdown(f"""
        <div class="news-card">
            <h4><a href="{item.get('url', '#')}" target="_blank">{item.get('title', 'No Title')}</a></h4>
            <p>{description}</p>
            <small>📌 {item.get('source', 'Unknown')} &bull; 📅 {str(item.get('published_at', ''))[:16]}</small>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Session State
# ──────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# ──────────────────────────────────────────────
# Auth Helpers
# ──────────────────────────────────────────────
def login_user(email, password):
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            st.error("Supabase credentials not found in .env")
            return False
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            st.session_state.authenticated = True
            st.session_state.token = res.session.access_token
            st.session_state.user = res.user
            return True
        return False
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False


def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# ──────────────────────────────────────────────
# Sidebar & Navigation
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("📈 StockBro")

    if not st.session_state.authenticated:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign In", type="primary"):
            if login_user(email, password):
                st.rerun()
        st.info("Don't have an account? Use the test credentials in backend docs.")
    else:
        st.success(f"Welcome, {st.session_state.user.email}")
        page = st.radio("Navigation", ["Chat", "Market", "Watchlist"])
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()


# ──────────────────────────────────────────────
# Main Content
# ──────────────────────────────────────────────
if not st.session_state.authenticated:
    st.markdown("""
    # Welcome to StockBro 🚀
    
    ### Your AI-Powered Stock Analysis Assistant
    
    Login to start chatting with our intelligent agent about the Indian stock market,
    get real-time data, and manage your portfolio.
    """)
    st.image("https://images.unsplash.com/photo-1611974765215-60d978396071?q=80&w=2070&auto=format&fit=crop", width="stretch")

else:
    # ─── Chat Interface ───────────────────────
    if page == "Chat":
        st.title("💬 Chat with StockBro")

        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                # Render stock cards
                if msg.get("stocks"):
                    cols = st.columns(min(len(msg["stocks"]), 4))
                    for idx, stock in enumerate(msg["stocks"]):
                        with cols[idx % len(cols)]:
                            render_stock_card(stock)

                # Render charts
                if msg.get("charts"):
                    for chart in msg["charts"]:
                        render_chart(chart, get_headers())

                # Render news
                if msg.get("news"):
                    with st.expander("📰 Related News", expanded=False):
                        render_news_panel(msg["news"])

        # Chat input
        if prompt := st.chat_input("Ask about a stock (e.g., 'How is Reliance doing?'):"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing market data..."):
                    try:
                        payload = {"message": prompt}
                        if st.session_state.conversation_id:
                            payload["conversation_id"] = st.session_state.conversation_id

                        response = requests.post(
                            f"{BACKEND_URL}/chat/",
                            json=payload,
                            headers=get_headers(),
                            timeout=60,
                        )

                        if response.status_code == 200:
                            data = response.json()
                            answer = data["answer"]
                            stocks = data.get("stocks")
                            news = data.get("news")
                            charts = data.get("charts")

                            st.session_state.conversation_id = data["conversation_id"]

                            # Render answer
                            st.markdown(answer)

                            # Render stock cards
                            if stocks:
                                cols = st.columns(min(len(stocks), 4))
                                for idx, stock in enumerate(stocks):
                                    with cols[idx % len(cols)]:
                                        render_stock_card(stock)

                            # Render charts
                            if charts:
                                for chart in charts:
                                    render_chart(chart, get_headers())

                            # Render news
                            if news:
                                with st.expander("📰 Related News", expanded=True):
                                    render_news_panel(news)

                            # Save to history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "stocks": stocks,
                                "news": news,
                                "charts": charts,
                            })
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")

    # ─── Market Interface ─────────────────────
    elif page == "Market":
        st.title("📈 Market Dashboard")

        # Search Bar
        search_query = st.text_input("Search Stock (e.g., RELIANCE, TCS)", "")
        if search_query:
            try:
                res = requests.get(
                    f"{BACKEND_URL}/stocks/{search_query.upper()}",
                    headers=get_headers(),
                    timeout=15,
                )
                if res.status_code == 200:
                    stock = res.json()

                    col1, col2 = st.columns([1, 2])
                    with col1:
                        render_stock_card(stock)

                        st.markdown("**Fundamentals**")
                        f_cols = st.columns(2)
                        f_cols[0].metric("52W High", f"₹{stock.get('week_52_high', 'N/A')}")
                        f_cols[1].metric("52W Low", f"₹{stock.get('week_52_low', 'N/A')}")

                    with col2:
                        # Render chart for this stock
                        render_chart(
                            {
                                "symbol": search_query.upper(),
                                "chart_type": "candlestick",
                                "data_url": f"/api/v1/charts/{search_query.upper()}/history?duration=3M",
                            },
                            get_headers(),
                        )

                    # News for this stock
                    st.markdown("---")
                    st.subheader(f"📰 Latest News: {search_query.upper()}")
                    try:
                        news_res = requests.get(
                            f"{BACKEND_URL}/news/search?q={search_query}+stock+India",
                            headers=get_headers(),
                            timeout=15,
                        )
                        if news_res.status_code == 200:
                            news_data = news_res.json().get("results", [])
                            if news_data:
                                render_news_panel(news_data)
                            else:
                                st.caption("No news found.")
                    except Exception:
                        st.caption("Could not load news.")
                else:
                    st.error("Stock not found. Try typical NSE symbols like RELIANCE, TCS, INFY.")
            except Exception as e:
                st.error(f"Error fetching stock: {e}")

        st.markdown("---")
        st.subheader("🔥 Trending Stocks")

        try:
            res = requests.get(f"{BACKEND_URL}/stocks/trending", headers=get_headers(), timeout=30)
            if res.status_code == 200:
                trending = res.json()
                cols = st.columns(3)
                for idx, stock in enumerate(trending):
                    with cols[idx % 3]:
                        render_stock_card(stock)
            else:
                st.warning("Could not fetch trending stocks.")
        except Exception as e:
            st.error(f"Connection error: {e}")

    # ─── Watchlist Interface ──────────────────
    elif page == "Watchlist":
        st.title("📋 My Watchlists")

        # Create New Watchlist
        with st.expander("Create New Watchlist"):
            new_wl_name = st.text_input("Watchlist Name")
            if st.button("Create"):
                res = requests.post(
                    f"{BACKEND_URL}/watchlists/",
                    json={"name": new_wl_name, "description": "Created from Streamlit"},
                    headers=get_headers(),
                )
                if res.status_code == 201:
                    st.success("Watchlist created!")
                    st.rerun()
                else:
                    st.error("Failed to create watchlist.")

        # List Watchlists
        try:
            res = requests.get(f"{BACKEND_URL}/watchlists/", headers=get_headers())
            if res.status_code == 200:
                watchlists = res.json()

                for wl in watchlists:
                    st.subheader(f"📌 {wl['name']}")

                    with st.form(key=f"add_item_{wl['id']}"):
                        col1, col2 = st.columns([3, 1])
                        symbol = col1.text_input("Add Symbol (e.g. TCS)", key=f"sym_{wl['id']}")
                        if col2.form_submit_button("Add"):
                            add_res = requests.post(
                                f"{BACKEND_URL}/watchlists/{wl['id']}/items",
                                json={"symbol": symbol.upper(), "notes": ""},
                                headers=get_headers(),
                            )
                            if add_res.status_code == 201:
                                st.success(f"Added {symbol}")
                                st.rerun()
                            else:
                                st.error("Failed to add stock.")

                    if wl.get("watchlist_items"):
                        item_cols = st.columns(4)
                        for idx, item in enumerate(wl["watchlist_items"]):
                            with item_cols[idx % 4]:
                                st.info(item["symbol"])
                    else:
                        st.caption("No stocks in this watchlist yet.")

                    st.markdown("---")
            else:
                st.warning("Could not fetch watchlists.")
        except Exception as e:
            st.error(f"Error: {e}")
