import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import time

# Load environment variables
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
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .stock-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Positive/Negative Colors */
    .positive { color: #00ff7f; }
    .negative { color: #ff4b4b; }
    
    /* Chat Message Styles */
    .stChatMessage {
        background-color: #262730;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
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

# --- Helper Functions ---
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

# --- Sidebar & Navigation ---
with st.sidebar:
    st.title("📈 StockBro")
    
    if not st.session_state.authenticated:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign In", type="primary"):
            if login_user(email, password):
                st.rerun()
        
        st.info("Don't have an account? Use the test credentials provided in the backend documentation.")
    
    else:
        st.success(f"Welcome, {st.session_state.user.email}")
        
        page = st.radio("Navigation", ["Chat", "Market", "Watchlist"])
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

# --- Main Content ---
if not st.session_state.authenticated:
    st.markdown("""
    # Welcome to StockBro 🚀
    
    ### Your AI-Powered Stock Analysis Assistant
    
    Login to start chatting with our intelligent agent about the Indian stock market, get real-time data, and manage your portfolio.
    """)
    
    # Display trending stocks as a teaser (no auth required for this simplified view if backend allowed, but backend requires auth)
    # So just show a hero image or text
    st.image("https://images.unsplash.com/photo-1611974765215-60d978396071?q=80&w=2070&auto=format&fit=crop", width="stretch")

else:
    # --- Chat Interface ---
    if page == "Chat":
        st.title("💬 Chat with StockBro")
        
        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Display structured data if available (stocks)
                if msg.get("stocks"):
                    cols = st.columns(len(msg["stocks"]))
                    for idx, stock in enumerate(msg["stocks"]):
                        with cols[idx]:
                            color = "positive" if (stock.get('change_percent') or 0) >= 0 else "negative"
                            st.markdown(f"""
                            <div class="stock-card">
                                <h4>{stock['symbol']}</h4>
                                <h2>₹{stock['current_price']}</h2>
                                <p class="{color}">{stock.get('change_percent', 0)}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Display news
                if msg.get("news"):
                    with st.expander("Related News"):
                        for item in msg["news"]:
                            st.write(f"**[{item['title']}]({item['url']})**")
                            st.caption(f"{item.get('source')} • {item.get('published_at', '')}")

        # Chat input
        if prompt := st.chat_input("Ask about a stock (e.g., 'How is Tata Motors doing?'):"):
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Call Backend API
            with st.chat_message("assistant"):
                with st.spinner("Analyzing market data..."):
                    try:
                        payload = {"message": prompt}
                        if st.session_state.conversation_id:
                            payload["conversation_id"] = st.session_state.conversation_id
                            
                        response = requests.post(
                            f"{BACKEND_URL}/chat/",
                            json=payload,
                            headers=get_headers()
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            answer = data["answer"]
                            stocks = data.get("stocks")
                            news = data.get("news")
                            
                            st.session_state.conversation_id = data["conversation_id"]
                            
                            st.markdown(answer)
                            
                            # Show Stocks
                            if stocks:
                                cols = st.columns(len(stocks))
                                for idx, stock in enumerate(stocks):
                                    with cols[idx]:
                                        color = "positive" if (stock.get('change_percent') or 0) >= 0 else "negative"
                                        st.markdown(f"""
                                        <div class="stock-card">
                                            <h4>{stock['symbol']}</h4>
                                            <h2>₹{stock['current_price']}</h2>
                                            <p class="{color}">{stock.get('change_percent', 0)}%</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            # Show News
                            if news:
                                with st.expander("Related News"):
                                    for item in news:
                                        st.write(f"**[{item['title']}]({item['url']})**")
                                        st.caption(f"{item.get('source')} • {item.get('published_at', '')}")
                            
                            # Save to history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "stocks": stocks,
                                "news": news
                            })
                            
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")

    # --- Market Interface ---
    elif page == "Market":
        st.title("📈 Market Dashboard")
        
        # Search Bar
        search_query = st.text_input("Search Stock (e.g., RELIANCE, TCS)", "")
        if search_query:
            try:
                res = requests.get(f"{BACKEND_URL}/stocks/{search_query.upper()}", headers=get_headers())
                if res.status_code == 200:
                    stock = res.json()
                    
                    # Display Stock Details
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        color = "positive" if (stock.get('change_percent') or 0) >= 0 else "negative"
                        st.markdown(f"""
                        <div class="stock-card">
                            <h1>{stock['symbol']}</h1>
                            <h3>{stock['name']}</h3>
                            <h1>₹{stock['current_price']}</h1>
                            <h3 class="{color}">{stock.get('change_percent', 0)}%</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("Add to Watchlist"):
                            # Helper to add to default watchlist (simplified)
                            st.toast("Feature coming soon! Use Watchlist tab.")
                            
                    with col2:
                        st.subheader("Fundamentals")
                        f_cols = st.columns(3)
                        f_cols[0].metric("Market Cap", f"₹{stock.get('market_cap', 'N/A')}")
                        f_cols[1].metric("P/E Ratio", stock.get('pe_ratio', 'N/A'))
                        f_cols[2].metric("Dividend Yield", f"{stock.get('dividend_yield', 'N/A')}%")
                        
                        f_cols2 = st.columns(3)
                        f_cols2[0].metric("52W High", f"₹{stock.get('week_52_high', 'N/A')}")
                        f_cols2[1].metric("52W Low", f"₹{stock.get('week_52_low', 'N/A')}")
                        
                else:
                    st.error("Stock not found. Try typical NSE symbols like RELIANCE, INF, TCS.")
            except Exception as e:
                st.error(f"Error fetching stock: {e}")
        
        st.markdown("---")
        st.subheader("🔥 Trending Stocks")
        
        try:
            res = requests.get(f"{BACKEND_URL}/stocks/trending", headers=get_headers())
            if res.status_code == 200:
                trending = res.json()
                
                # Grid Layout
                cols = st.columns(3)
                for idx, stock in enumerate(trending):
                    with cols[idx % 3]:
                        color = "positive" if (stock.get('change_percent') or 0) >= 0 else "negative"
                        st.markdown(f"""
                        <div class="stock-card">
                            <h4>{stock['symbol']}</h4>
                            <p>{stock['name']}</p>
                            <h3>₹{stock['current_price']}</h3>
                            <p class="{color}">{stock.get('change_percent', 0)}%</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Could not fetch trending stocks.")
        except Exception as e:
            st.error(f"Connection error: {e}")

    # --- Watchlist Interface ---
    elif page == "Watchlist":
        st.title("📋 My Watchlists")
        
        # Create New Watchlist
        with st.expander("Create New Watchlist"):
            new_wl_name = st.text_input("Watchlist Name")
            if st.button("Create"):
                res = requests.post(
                    f"{BACKEND_URL}/watchlists/",
                    json={"name": new_wl_name, "description": "Created from Streamlit"},
                    headers=get_headers()
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
                    
                    # Add Item Form
                    with st.form(key=f"add_item_{wl['id']}"):
                        col1, col2 = st.columns([3, 1])
                        symbol = col1.text_input("Add Symbol (e.g. TCS)", key=f"sym_{wl['id']}")
                        if col2.form_submit_button("Add"):
                            add_res = requests.post(
                                f"{BACKEND_URL}/watchlists/{wl['id']}/items",
                                json={"symbol": symbol.upper(), "notes": ""},
                                headers=get_headers()
                            )
                            if add_res.status_code == 201:
                                st.success(f"Added {symbol}")
                                st.rerun()
                            else:
                                st.error("Failed to add stock.")

                    # List Items
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
