# StockBro AI

StockBro AI is an AI-driven multi-agent system designed to empower retail investors, analysts, and financial enthusiasts with real-time stock market insights, news sentiment analysis, and advanced scenario-based simulations.

It combines Next.js frontend with ChatGPT-style chat, intelligent Python-based finance agents, and powerful LLMs to deliver an interactive and explainable financial analysis platform.

## 🔍 Overview

StockBro AI provides:

- Real-time stock market insights & analytics (e.g., price, volume, P/E, EPS, revenue)
- Multi-agent architecture powered by Python + Phidata (or LangChain), where specialized agents handle finance, news, and simulations
- Built-in LLM agents (Llama 3.1 via GroqCloud or Gemini fallback) for intelligent reasoning, summarization, and narrative generation
- Live financial news fetching & sentiment analysis using APIs such as Finnhub and NewsAPI
- What-if simulations: explore how changes in financial variables affect outcomes with tables, charts, and narratives
- Extensible, modular design: easily plug in new agents, APIs, features, or dashboards

## 🛠 Tech Stack

| Layer | Technology/Tools |
|-------|------------------|
| Frontend & API | Next.js (serverless API routes, auth, UI) |
| Agent Core | Python, Phidata, LangChain |
| LLMs | Llama 3.1 (GroqCloud), Gemini APIs |
| Data/Processing | Pandas, NumPy, Plotly/Matplotlib, Scikit-learn |
| Database/Auth | Supabase (PostgreSQL + auth) |
| Hosting (Frontend) | Vercel |
| Hosting (Agents) | Railway (Python microservices) |
| CI/CD | GitHub Actions |

## ⚙️ Environment Setup

Create a `.env` file to configure environment variables before running:

```bash
# Backend Agents
FINNHUB_API_KEY=your_finnhub_key
NEWS_API_KEY=your_newsapi_key
GROQ_API_KEY=your_groqcloud_key
OPENAI_API_KEY=your_openai_key  # optional fallback

# Frontend (Next.js)
NEXT_PUBLIC_API_URL=https://api.stockbro.ai
NEXT_PUBLIC_SUPABASE_URL=https://xyzcompany.supabase.co
NEXT_PUBLIC_SUPABASE_KEY=your_supabase_key
```

## 🚀 Installation & Running

Clone repo and set up virtual environment:

```bash
git clone https://github.com/your-username/StockBroAI.git
cd StockBroAI

# Setup Backend (Agents)
python -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` for Windows
pip install -r agents/requirements.txt

# Run Orchestrator / Agents
python agents/orchestrator.py
```

Run frontend in dev mode:

```bash
cd frontend
npm install
npm run dev
```

- Backend runs on Railway (microservices)
- Frontend/API hosted on Vercel

## 📊 Core Features

### ChatGPT-style Homepage
- Ask questions like "What's the latest on AAPL?"
- Real-time AI-powered responses with charts, news, and metrics
- Suggested queries & scrollable history

### Dashboard
- Market snapshot & portfolio view
- Watchlist integration with Supabase
- News digest & interactive analytics charts

### Ticker Detail Page
- Real-time charts & fundamentals
- Analyst recommendations & sentiment analysis
- What-if simulation panel

### Watchlist
- Track favorite stocks with quick add/remove
- Snapshots of stock performance

### What-If Simulation
- Input custom scenarios (e.g., revenue growth changes)
- Outputs sensitivity tables + narrative insights

### Authentication
- User accounts (signup/login)
- Persistent sessions via Supabase

## 📚 Related Research & Papers

| Title | Authors | Summary | Link |
|-------|---------|---------|------|
| AI-Driven Financial Advisory: The Rise of Robo-Advisors | A. Kashyap | Examines the transformational impact of AI-powered robo-advisors on financial services, focusing on automation, efficiency, potential biases, regulatory issues, broader accessibility, and their effects on the finance industry. | [Read](https://example.com/ai-driven-financial-advisory) |
| An AI Analyst Made 30 Years of Stock Picks – Stanford Report | E. deHaan et al. | Presents a 30-year longitudinal study where an AI analyst outperformed 93% of mutual fund managers, highlighting the scalability and game-changing implications for asset management. | [Read](https://example.com/stanford-ai-analyst-stock-picks) |
| Leveraging AI Multi-Agent Systems in Financial Analysis | R. Bhattacharya | Discusses the integration of multi-agent AI systems in financial analytics, highlighting collaborative workflows, advanced risk modeling, and the ongoing challenges of explainability in finance. | [Read](https://example.com/ai-multi-agent-financial-analysis) |
| Large Language Models in Equity Markets: Applications and Risks | Anonymous | Synthesizes findings from 84 research papers regarding LLMs in equity finance, emphasizing their power in sentiment mining and detecting market anomalies, while also addressing risks like overfitting and ethical considerations. | [Read](https://example.com/llms-equity-markets-applications-risks) |
| Architectures and Challenges of AI Multi-Agent Systems in Finance | S. Joshi | Reviews advanced frameworks such as LangChain and Phidata for finance, focusing on multi-agent orchestration, latency issues, transparency, and regulatory hurdles unique to the sector. | [Read](https://example.com/ai-multi-agent-architectures-finance) |

## ⚠️ Disclaimer

StockBro AI outputs are not financial advice. Always consult professionals and conduct your own research before making investment decisions. Models and agents may produce errors, outdated responses, or biased interpretations.
