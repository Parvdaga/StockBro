# Quick Start Guide - StockBro Backend

## ✅ Your Backend is Running!

If you can see this, your backend is already set up and running on **http://localhost:8000**

## 🧪 Test the Backend

### Option 1: Run Test Script (Recommended)
```powershell
.\test_backend.ps1
```

### Option 2: Manual Testing

**Health Check:**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Open API Docs:**
```powershell
start http://localhost:8000/api/v1/docs
```

## 🚀 Running the Backend

### If Backend is NOT Running

**Start the server:**
```powershell
python -m uvicorn main:app --reload
```

**You should see:**
```
🚀 Starting StockBro Backend v1.0.0
📊 Database: sqlite+aiosqlite:///./stockbro.db
🤖 LLM: Groq
INFO: Uvicorn running on http://127.0.0.1:8000
```

### If Backend IS Already Running

**Check running processes:**
```powershell
Get-Process python | Where-Object {$_.Path -like "*StockBro*backend*"}
```

**Stop all backend processes:**
```powershell
Get-Process python | Where-Object {$_.Path -like "*StockBro*backend*"} | Stop-Process -Force
```

**Then restart:**
```powershell
python -m uvicorn main:app --reload
```

## 📝 Test the API

### 1. Create Test User

```powershell
$body = @{
    email = "test@example.com"
    password = "password123"
    full_name = "Test User"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/v1/auth/signup `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -UseBasicParsing
```

### 2. Login

```powershell
$loginBody = @{
    username = "test@example.com"
    password = "password123"
} | ConvertTo-Json

$login = Invoke-WebRequest -Uri http://localhost:8000/api/v1/auth/login `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "username=test@example.com&password=password123" `
    -UseBasicParsing

$token = ($login.Content | ConvertFrom-Json).access_token
Write-Host "Token: $token"
```

### 3. Test Chat (with token)

```powershell
$chatBody = @{
    message = "What is the stock market?"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/v1/chat/ `
    -Method POST `
    -Headers @{Authorization = "Bearer $token"} `
    -ContentType "application/json" `
    -Body $chatBody `
    -UseBasicParsing
```

## 🌐 Interactive Testing (Easiest!)

Open the Swagger UI in your browser:
```
http://localhost:8000/api/v1/docs
```

This provides a visual interface to test all endpoints without writing code!

## 🔍 Common Issues

### "uvicorn: command not found"
**Fix:** Use `python -m uvicorn` instead of just `uvicorn`

### "Port 8000 already in use"
**Fix:** Kill existing processes:
```powershell
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /PID YOUR_PID_HERE /F
```

### Backend not responding
**Check if it's running:**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

If you get an error, the backend is not running. Start it with:
```powershell
python -m uvicorn main:app --reload
```

## 📚 More Information

- Full README: [`README.md`](file:///README.md)
- Detailed Setup: [`SETUP.md`](file:///SETUP.md)
