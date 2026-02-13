@echo off
cd /d "%~dp0"
:: Activate virtual environment if it exists in backend/venv
if exist "backend\venv\Scripts\activate.bat" (
    call backend\venv\Scripts\activate
) else (
    echo Virtual environment not found in backend/venv. Using system Python...
)

echo Starting StockBro Streamlit App...
python -m streamlit run streamlit_app/main.py
pause
