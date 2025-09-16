# StockBro AI

StockBro AI is an agentic AI-driven multi-agent system inspired by **Finsage AI**. It supports retail investors, analysts, and financial enthusiasts by combining real-time market data, news sentiment, and scenario simulations, all powered by advanced LLMs and coordinated agents.

---

## 🔍 Overview

StockBro AI provides:

- **Real-time stock market insights & analytics**, including metrics like P/E, EPS, etc.  
- **Multi-agent architecture** using Phidata (or another orchestrator), where different agents specialize in different tasks (e.g. data fetching, sentiment analysis, model simulation).  
- **Built-in LLM agents** using Llama 3.1 (8B Instant) for intelligent reasoning, summarization, interpretation.  
- **Live news fetching & sentiment / thematic analysis** via APIs (Finnhub, NewsAPI, etc.).  
- **What-if / scenario simulation tools**: users can explore how changes in key financial variables might play out.  
- **Extensible framework**: easy to add new agents, integrate new APIs, or branch out into frontend/dashboard/model components.

---

## 🛠 Tech Stack

| Component | Tools / Frameworks |
|-----------|---------------------|
| Language | Python |
| LLM | Llama 3.1 (8B Instant) — via GroqCloud API (or fallback) |
| API Sources | Finnhub, NewsAPI, OpenAI, possibly others |
| Agent Orchestration | Phidata (or similar multi-agent runtime) |
| Data Processing & Visualization | Pandas, Matplotlib / Plotly, etc. |
| Frontend / Dashboard (optional but planned) | React / Next.js or similar |

---

## ⚙️ Environment Setup

Before running the project, set up your environment variables in a `.env` file in the root directory:

```bash
GROQ_API_KEY=your_groqcloud_key
FINNHUB_API_KEY=your_finnhub_key
NEWS_API_KEY=your_newsapi_key
OPENAI_API_KEY=your_openai_key  # optional / fallback
````

---

## 🚀 Installation & Running

```bash
git clone https://github.com/your-username/StockBroAI.git
cd StockBroAI
python -m venv venv
source venv/bin/activate        # or appropriate virtualenv command
pip install -r requirements.txt
```

To run:

```bash
# Start the agent system/orchestrator
phidata app run    # or whatever command you use to launch

# (If frontend exists)
cd frontend
npm install
npm run dev
```

---
## 📚 Related Research & Recent Papers (2025)

| Title                                                             | Authors          | Summary                                                                                                                                                                                                                                                   | Link                                                                                                               |
| ----------------------------------------------------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| AI-Driven Financial Advisory: The Rise of Robo-Advisors           | A. Kashyap       | Explores how AI-driven robo-advisors transform personal finance, providing automated planning and investing. Covers accessibility, efficiency, issues (privacy, bias, regulation), and future directions. Highlights democratization and industry impact. | [Read](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5268858)                                                |
| An AI analyst made 30 years of stock picks - Stanford Report      | E. deHaan et al. | A large-scale longitudinal experiment: AI analyst outperformed 93% of mutual fund managers over 30 years using scalable automation and diverse variables. Raises implications for future asset management.                                                | [Read](https://news.stanford.edu/stories/2025/06/ai-stock-analyst-analysis-performance-human-mutual-fund-managers) |
| Leveraging AI Multi-Agent Systems in Financial Analysis           | R. Bhattacharya  | Reviews AI multi-agent systems in financial analytics: scalable agent-based workflows, collaboration across finance tasks, risk modeling, and explainability challenges.                                                                                  | [Read](https://cacm.acm.org/blogcacm/leveraging-ai-multi-agent-systems-in-financial-analysis)                      |
| Large Language Models in Equity Markets: Applications and Risks   | Anonymous        | A review of 84 studies (2022–2025) on LLMs in equity analysis. Finds strengths in sentiment mining, summarization, and anomaly detection, while highlighting risks in overfitting and ethical use.                                                        | [Read](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5297432)                                                |
| Architectures and Challenges of AI Multi-Agent Systems in Finance | S. Joshi         | Examines multi-agent architectures (LangChain, Phidata, AutoGen) in finance. Discusses latency, orchestration, transparency, and regulatory challenges. Suggests modular solutions.                                                                       | [Read](https://journalcjast.com/index.php/CJAST/article/view/6142)                                                 |

---

## 🎯 Potential Roadmap

Here are possible future directions:

1. **Frontend & Dashboard**: Interactive UI for watchlists, charts, alerts.
2. **Model Extensions**: More advanced simulation agents (e.g. macroeconomic variables, risk models).
3. **Explainability / Transparency**: Logging, summarization of agent reasoning.
4. **Regulatory / Ethical Features**: Fairness, bias detection, handling sensitive/inaccurate news.
5. **Productionization**: Dockerization, CI/CD, scaling, monitoring.

---

## ⚠️ Disclaimer

The outputs of StockBro AI are **not financial advice**. Always do your own research, consult professionals before making investment decisions. Models and agents may have errors or outdated information.

---
