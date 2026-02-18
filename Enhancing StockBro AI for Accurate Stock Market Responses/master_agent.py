"""
Master Agent — orchestrates finance and news agents for StockBro
Now with intent-based routing and educational tools for consistency.
"""
from phi.agent import Agent
from app.agents.shared_model import get_model
from app.agents.finance_agent import get_stock_price, search_stock
from app.agents.news_agent import get_stock_news, get_market_headlines
from app.agents.query_router import router, ParsedQuery
from app.core.knowledge_base import get_knowledge


# ──────────────────────────────────────────────
# Domain-specific educational tools
# ──────────────────────────────────────────────

def get_sector_stocks(sector: str) -> str:
    """Get a list of notable stocks in a given sector (e.g., 'Banking', 'Defense')."""
    sectors = get_knowledge("sectors")
    if sector.capitalize() in sectors:
        stocks = sectors[sector.capitalize()]
        return f"📊 **Top {sector.capitalize()} Stocks**: {', '.join(stocks)}"
    return f"I don't have a curated list for the '{sector}' sector yet."

def explain_term(term: str) -> str:
    """Explain a stock market term (e.g., 'IPO', 'LTP')."""
    explanation = get_knowledge("terms", term.upper())
    if "No information found" in explanation:
        explanation = get_knowledge("terms", term)
    return f"📚 **{term}**: {explanation}"

def explain_options_basics() -> str:
    """Explain F&O basics for Indian markets — educational content only."""
    return """
📚 **Options & Futures (F&O) Basics — Indian Markets**

**What are Options?**
- **Call Option**: Right to BUY a stock at a fixed price (strike) before expiry
- **Put Option**: Right to SELL a stock at a fixed price before expiry
- In India: F&O traded on NIFTY, BANKNIFTY, and 100+ stocks on NSE

**Key Concepts:**
- **Strike Price**: The agreed price for buying/selling
- **Premium**: Cost you pay to buy the option
- **Expiry**: Last Thursday of the month for Indian F&O
- **Lot Size**: Minimum quantity (e.g., NIFTY = 50 units)

**Beginner Strategies:**
1. **Covered Call**: Own stock + sell call (income generation)
2. **Protective Put**: Own stock + buy put (insurance)
3. **Bull Call Spread**: Buy lower strike call + sell higher strike call (defined risk)

⚠️ **Risk Warning:**
- Options can expire worthless → 100% loss of premium
- F&O requires separate trading account approval
- Leverage amplifies both gains AND losses
- NOT suitable for beginners without paper trading first

**Free Learning Resources:**
- NSE Options Guide: nseindia.com/education
- Zerodha Varsity: zerodha.com/varsity
- Always practice with paper trading before risking real money

_Note: StockBro does not provide live option chains or specific F&O recommendations._
"""


def create_intraday_plan_template(symbol: str) -> str:
    """
    Generate an intraday trading plan template with risk management.

    Args:
        symbol (str): Stock symbol (e.g., 'RELIANCE', 'TCS')

    Returns:
        str: Formatted intraday plan template with risk management rules.
    """
    return f"""
📊 **Intraday Trading Plan Template for {symbol}**

**Pre-Market Preparation:**
1. ✅ Check previous day's close and after-hours movement
2. ✅ Review overnight global markets (US, Asia)
3. ✅ Identify key support/resistance levels
4. ✅ Check for scheduled news/earnings today

**Entry Strategy:**
- **Timeframe**: 5-min or 15-min charts
- **Indicators**: Use 2-3 max (e.g., EMA 20/50, RSI, VWAP)
- **Entry Signal**: Wait for confirmation (breakout + volume)
- **Position Size**: Risk only 1-2% of capital per trade

**Risk Management (CRITICAL):**
- **Stop Loss**: Set BEFORE entry (e.g., below support or 1-2%)
- **Target**: Aim for 1.5:1 or 2:1 reward-to-risk ratio
- **Max Trades**: Limit to 2-3 per day (avoid overtrading)
- **Cut-off Time**: Exit all positions by 3:15 PM to avoid closing volatility

**Exit Rules:**
- Hit target → Exit 50%, trail rest with stop loss
- Hit stop loss → Accept loss, NO revenge trading
- No clear signal → Stay in cash (cash is also a position)

⚠️ **Intraday Trading Risks:**
- 90%+ of retail intraday traders lose money
- High brokerage/taxes eat into small profits
- Emotional decisions destroy capital
- Requires full-time screen monitoring

**Recommended Before Starting:**
1. Paper trade for 3 months minimum
2. Build a trading journal (track every trade)
3. Study market microstructure
4. Have 6 months of risk capital (money you can afford to lose)

_StockBro provides templates only — actual execution is your responsibility._
"""


def generate_ipo_overview_template(company_name: str = "Upcoming IPO") -> str:
    """
    Generate an IPO analysis due diligence template.

    Args:
        company_name (str): Name of the company or "Upcoming IPO"

    Returns:
        str: Formatted IPO analysis checklist template.
    """
    return f"""
📋 **IPO Analysis Template: {company_name}**

**Due Diligence Checklist:**

**1. Company Fundamentals:**
- [ ] Industry position and competitive moat
- [ ] Revenue growth trend (3-5 years)
- [ ] Profitability: EBITDA margin, net margin
- [ ] Debt-to-equity ratio
- [ ] Use of IPO proceeds (check red flag: debt repayment)

**2. Valuation Metrics:**
- [ ] P/E ratio vs industry peers
- [ ] Price-to-sales ratio
- [ ] Market cap post-IPO
- [ ] Valuation justified by growth?

**3. Promoter & Management:**
- [ ] Promoter track record
- [ ] Dilution: How much are promoters selling?
- [ ] Related-party transactions (red flag if high)

**4. Grey Market Premium (GMP):**
- Unofficial indicator, NOT reliable for decision
- High GMP often leads to listing day profit booking

**5. Subscription Data:**
- QIB (institutional) subscription most important
- Retail oversubscription doesn't guarantee returns

⚠️ **IPO Investment Risks:**
- Listing gains NOT guaranteed (many IPOs list below issue price)
- Lock-in period for promoters (check DRHP)
- Hype-driven IPOs often correct 30-50% in 6-12 months
- New companies have limited track record

**Research Sources (Free):**
- SEBI DRHP: sebi.gov.in
- NSE IPO watch: nseindia.com
- Moneycontrol IPO section
- Company investor presentation

_Always read the Draft Red Herring Prospectus (DRHP) before applying._
"""


# ──────────────────────────────────────────────
# Enhanced tools list
# ──────────────────────────────────────────────
enhanced_tools = [
    get_stock_price,
    search_stock,
    get_stock_news,
    get_market_headlines,
    explain_options_basics,
    create_intraday_plan_template,
    generate_ipo_overview_template,
    get_sector_stocks,
    explain_term,
]


# ──────────────────────────────────────────────
# Master Agent
# ──────────────────────────────────────────────
master_agent = Agent(
    name="StockBro",
    role="Indian Stock Market Financial Advisor",
    model=get_model(),
    tools=enhanced_tools,
    add_history_to_messages=True,
    num_history_responses=5,
    instructions=[
        "You are 'StockBro', an expert AI financial advisor specializing in the **Indian stock market** (NSE/BSE).",
        "",
        "**ROUTING LOGIC** (follow strictly):",
        "1. Parse user query to understand intent (price, news, chart, F&O, IPO, etc.)",
        "2. For PRICE queries → ALWAYS call 'get_stock_price' first",
        "3. For NEWS queries → call 'get_stock_news' with symbol or topic",
        "4. For SEARCH queries (no symbol given) → call 'search_stock' first, THEN get price",
        "5. For OPTIONS questions → call 'explain_options_basics' (we don't provide live F&O data)",
        "6. For INTRADAY → call 'create_intraday_plan_template' with the stock symbol",
        "7. For IPO → call 'generate_ipo_overview_template' with company name",
        "8. For SECTOR queries (e.g., 'defense stocks') → call 'get_sector_stocks' first",
        "9. For EDUCATIONAL queries (e.g., 'what is LTP') → call 'explain_term'",
        "10. For general stock questions → use BOTH 'get_stock_price' AND 'get_stock_news'",
        "",
        "**RESPONSE FORMAT** (non-negotiable):",
        "1. **Summary**: 2-3 sentence overview with key takeaway",
        "2. **Data Section**: Price table (Markdown) OR news bullets OR template",
        "3. **Insights**: 3-5 actionable bullet points",
        "4. **Timestamp**: Include 'as of [time]' for live data",
        "5. **Disclaimer**: End with 'This is not financial advice. DYOR.'",
        "",
        "**DATA FRESHNESS**:",
        "- Stock prices are cached for 30 seconds — mention the timestamp from tool output",
        "- News is cached for 10 minutes",
        "- All prices are in Indian Rupees (₹)",
        "",
        "**IMPORTANT RULES**:",
        "- Common symbols: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN, ITC, BHARTIARTL",
        "- **CRITICAL**: The stock tool returns RAW DATA. You MUST format it beautifully.",
        "- **CRITICAL**: ALWAYS return a final text response to the user. Do not stop after tool execution.",
        "- If asked about yourself, say you are StockBro — an AI financial advisor for Indian stocks, powered by Groww data and AI.",
    ],
    markdown=True,
    show_tool_calls=True,
)
