@echo off
echo Starting StockBro Backend...
echo.

:: Check if venv exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run the setup steps in README.md first.
    pause
    exit /b
)

:: Activate virtual environment
call venv\Scripts\activate

:: Check if dependencies are installed (rudimentary check)
python -c "import fastapi" 2>NUL
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

:: Run the server
echo.
echo 🚀 Starting Server on http://localhost:8000
echo 📝 API Docs available at http://localhost:8000/api/v1/docs
echo.
python -m uvicorn app.main:app --reload

pause
