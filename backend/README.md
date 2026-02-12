# StockBro Backend

> 🚀 **AI-Powered Stock Analysis Platform**

Welcome to the StockBro backend! this is the engine behind the StockBro app, handling stock data, news, and AI chat.

---

## ⚡ Quick Start (For Beginners)

We've made it super easy to get started.

1.  **Install Python**: Ensure you have [Python 3.10+](https://www.python.org/downloads/) installed.
    *   *Important:* Check "Add Python to PATH" during installation.

2.  **Environment Setup**:
    *   Copy the file `.env.example` and rename it to `.env`.
    *   Open `.env` in Notepad and add your API keys (Groq, Supabase, Groww).

3.  **Run the App**:
    *   Double-click `run.bat`.
    *   This will automatically set up the environment and start the server!

The server will start at: `http://localhost:8000`
API Documentation: `http://localhost:8000/api/v1/docs`

---

## 🛠️ Detailed Setup (Manual)

If you prefer using the terminal or are on Mac/Linux, follow these steps.

### 1. Prerequisites
- Python 3.10 or higher
- Git (optional)

### 2. Installation

Open your terminal in the `backend` folder:

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1.  Duplicate `.env.example` and name it `.env`.
2.  Fill in the required fields:

```ini
GROQ_API_KEY=gsk_...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
GROWW_API_KEY=...
```

### 4. Running the Server

With your virtual environment activated:

```bash
uvicorn main:app --reload
```

---

## 🧪 Testing & Usage

### Interactive API Docs (Swagger UI)
The easiest way to test is via the web interface:
1.  Go to `http://localhost:8000/api/v1/docs`.
2.  **Authorize**: Click the lock icon 🔓.
    *   You'll need an access token.
    *   Run `python scripts/create_test_user.py` to make a user.
    *   Run `python scripts/get_access_token.py` to get a token.
    *   Enter `Bearer <your_token>` in the box.
3.  **Try Endpoints**: Click "Try it out" on any endpoint (e.g., `/api/v1/chat/`).

### Common Commands

| Task | Command |
| :--- | :--- |
| **Start Server** | `uvicorn main:app --reload` |
| **Create User** | `python scripts/create_test_user.py` |
| **Get Token** | `python scripts/get_access_token.py` |
| **Run Tests** | `pytest` |

---

## 📂 Project Structure

*   `app/`: Main application code.
    *   `api/`: API route handlers.
    *   `agents/`: AI logic (Finance Agent, News Agent).
    *   `integrations/`: External APIs (Groww, GNews).
*   `scripts/`: Helper scripts for testing and setup.
*   `tests/`: Automated tests.

---

## 🆘 Troubleshooting

*   **"Python not found"**: Reinstall Python and add to PATH.
*   **"ModuleNotFoundError"**: Run `pip install -r requirements.txt` again (make sure venv is active!).
*   **"Port already in use"**: Another instance is running. Close it or use a different port.
