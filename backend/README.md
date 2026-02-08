# StockBro Backend

This directory contains the FastAPI backend for the StockBro application.

## Prerequisites

- Python 3.10+
- [Groq API Key](https://console.groq.com/)
- [OpenAI API Key](https://platform.openai.com/)
- [Google Gemini API Key](https://aistudio.google.com/)
- [Phidata API Key](https://docs.phidata.com/)

## Setup

1.  **Navigate to the backend directory:**

    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    -   **Windows:**
        ```powershell
        .\venv\Scripts\Activate
        ```
    -   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Environment Configuration:**

    Create a `.env` file in the `backend` directory based on `.env.example`:

    ```ini
    # LLM Providers
    GROQ_API_KEY=your_groq_api_key
    OPENAI_API_KEY=your_openai_api_key
    GOOGLE_API_KEY=your_google_api_key
    PHI_API_KEY=your_phidata_api_key

    # Database
    DB_URL=sqlite+aiosqlite:///./stockbro.db
    # For Production (Supabase/PostgreSQL):
    # DB_URL=postgresql+asyncpg://user:pass@host:port/dbname
    ```

## Running the Server

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.
API Documentation (Swagger UI) is available at `http://localhost:8000/docs`.

## Project Structure

-   `app/`: Main application logic.
    -   `api/`: API route handlers.
    -   `core/`: Core configuration and security.
    -   `db/`: Database models and session management.
    -   `services/`: Business logic and external service integrations.
-   `main.py`: Application entry point.
-   `llm_config.py`: Configuration for LLM agents (Phidata).
