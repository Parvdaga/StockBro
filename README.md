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
| AI-Driven Financial Advisory: The Rise of Robo-Advisors | A. Kashyap | Explores how AI robo-advisors transform finance through automation. Covers efficiency, bias, regulation, accessibility, and industry impact. | [Read](link) |
| An AI analyst made 30 years of stock picks - Stanford Report | E. deHaan et al. | Longitudinal study: AI outperformed 93% of mutual fund managers over 30 years. Demonstrates scalability and implications for asset management. | [Read](link) |
| Leveraging AI Multi-Agent Systems in Financial Analysis | R. Bhattacharya | Reviews multi-agent workflows in financial analytics, scalable collaboration, risk modeling, and explainability challenges. | [Read](link) |
| Large Language Models in Equity Markets: Applications and Risks | Anonymous | Meta-study of 84 papers on LLMs in finance. Finds strong sentiment mining and anomaly detection capabilities, but highlights risks in overfitting and ethics. | [Read](link) |
| Architectures and Challenges of AI Multi-Agent Systems in Finance | S. Joshi | Reviews frameworks like LangChain, Phidata in finance. Focuses on orchestration, latency, transparency, and regulatory complexities. | [Read](link) |


## ⚠️ Disclaimer

StockBro AI outputs are not financial advice. Always consult professionals and conduct your own research before making investment decisions. Models and agents may produce errors, outdated responses, or biased interpretations.
