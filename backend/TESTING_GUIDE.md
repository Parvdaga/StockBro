# StockBro Backend - Complete Testing Guide

This guide walks you through testing all backend functions using the Swagger UI.

## 🌐 Access the API Documentation

Open in your browser:
```
http://127.0.0.1:8000/docs
```

You'll see an interactive interface with all available endpoints organized by category.

---

## 📝 Testing Flow

Follow this sequence to test all major functions:

### 1️⃣ **Authentication** (Create User & Login)

#### A. Create Test User

1. In Swagger UI, find **`POST /api/v1/auth/signup`**
2. Click **"Try it out"**
3. Enter this JSON in the Request body:
   ```json
   {
     "email": "test@example.com",
     "password": "password123",
     "full_name": "Test User"
   }
   ```
4. Click **"Execute"**
5. ✅ **Expected Response:** `200 OK` with user data

#### B. Login

1. Find **`POST /api/v1/auth/login`**
2. Click **"Try it out"**
3. Enter credentials (use `application/x-www-form-urlencoded`):
   - **username:** `test@example.com`
   - **password:** `password123`
4. Click **"Execute"**
5. ✅ **Expected Response:** `200 OK` with:
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "bearer"
   }
   ```
6. **📋 COPY THE ACCESS TOKEN** - You'll need it for authenticated endpoints!

#### C. Authorize in Swagger UI

1. Click the **🔓 Authorize** button at the top right
2. Enter: `Bearer YOUR_ACCESS_TOKEN_HERE`
3. Click **"Authorize"**
4. Click **"Close"**

Now you're authenticated and can test all protected endpoints! 🔐

---

### 2️⃣ **Chat with AI Agent**

#### Test Chat Endpoint

1. Find **`POST /api/v1/chat/`**
2. Click **"Try it out"**
3. Enter this JSON:
   ```json
   {
     "message": "What is the stock market?",
     "conversation_id": null
   }
   ```
4. Click **"Execute"**
5. ✅ **Expected Response:** 
   - AI-generated answer about the stock market
   - New `conversation_id` for this chat session

#### Continue Conversation

1. Use the same endpoint
2. This time, include the `conversation_id` from the previous response:
   ```json
   {
     "message": "Tell me about Tesla stock",
     "conversation_id": "UUID-FROM-PREVIOUS-RESPONSE"
   }
   ```
3. ✅ The AI will continue the conversation with context

#### Get Conversation History

1. Find **`GET /api/v1/chat/conversations`**
2. Click **"Try it out"** → **"Execute"**
3. ✅ **Expected Response:** List of all your conversations

---

### 3️⃣ **Stock Data**

#### Search for Stocks

1. Find **`GET /api/v1/stocks/search`**
2. Click **"Try it out"**
3. Enter a query (e.g., `Tesla` or `AAPL`)
4. Click **"Execute"**
5. ✅ **Expected Response:** List of matching stocks

#### Get Stock Details

1. Find **`GET /api/v1/stocks/{symbol}`**
2. Click **"Try it out"**
3. Enter a stock symbol (e.g., `AAPL` or `TSLA`)
4. Click **"Execute"**
5. ✅ **Expected Response:** Detailed stock information including:
   - Current price
   - Company info
   - Market data
   - Historical trends

---

### 4️⃣ **Watchlist**

#### View Watchlist

1. Find **`GET /api/v1/watchlist/`**
2. Click **"Try it out"** → **"Execute"**
3. ✅ **Expected Response:** Your current watchlist (empty initially)

#### Add Stock to Watchlist

1. Find **`POST /api/v1/watchlist/`**
2. Click **"Try it out"**
3. Enter JSON:
   ```json
   {
     "symbol": "AAPL",
     "name": "Apple Inc."
   }
   ```
4. Click **"Execute"**
5. ✅ **Expected Response:** Watchlist item created

#### Remove Stock from Watchlist

1. Find **`DELETE /api/v1/watchlist/{symbol}`**
2. Click **"Try it out"**
3. Enter symbol: `AAPL`
4. Click **"Execute"**
5. ✅ **Expected Response:** `204 No Content` (successfully deleted)

---

## 🧪 Alternative: Testing with PowerShell

If you prefer command-line testing, here's the complete flow:

### 1. Create User
```powershell
$signupBody = @{
    email = "test2@example.com"
    password = "password123"
    full_name = "Test User 2"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/v1/auth/signup `
    -Method POST `
    -ContentType "application/json" `
    -Body $signupBody `
    -UseBasicParsing
```

### 2. Login & Get Token
```powershell
$loginResponse = Invoke-WebRequest -Uri http://localhost:8000/api/v1/auth/login `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "username=test2@example.com&password=password123" `
    -UseBasicParsing

$token = ($loginResponse.Content | ConvertFrom-Json).access_token
Write-Host "Token: $token"
```

### 3. Test Chat with Token
```powershell
$chatBody = @{
    message = "What are some good stocks to invest in?"
    conversation_id = $null
} | ConvertTo-Json

$chatResponse = Invoke-WebRequest -Uri http://localhost:8000/api/v1/chat/ `
    -Method POST `
    -Headers @{Authorization = "Bearer $token"} `
    -ContentType "application/json" `
    -Body $chatBody `
    -UseBasicParsing

$chatResponse.Content | ConvertFrom-Json
```

### 4. Add to Watchlist
```powershell
$watchlistBody = @{
    symbol = "TSLA"
    name = "Tesla Inc."
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/v1/watchlist/ `
    -Method POST `
    -Headers @{Authorization = "Bearer $token"} `
    -ContentType "application/json" `
    -Body $watchlistBody `
    -UseBasicParsing
```

### 5. Get Watchlist
```powershell
$watchlist = Invoke-WebRequest -Uri http://localhost:8000/api/v1/watchlist/ `
    -Method GET `
    -Headers @{Authorization = "Bearer $token"} `
    -UseBasicParsing

$watchlist.Content | ConvertFrom-Json
```

---

## 📊 All Available Endpoints

### Authentication
- ✅ `POST /api/v1/auth/signup` - Create account
- ✅ `POST /api/v1/auth/login` - Login

### Chat (requires auth 🔐)
- ✅ `POST /api/v1/chat/` - Send message to AI
- ✅ `GET /api/v1/chat/conversations` - List all conversations
- ✅ `GET /api/v1/chat/conversations/{id}` - Get specific conversation
- ✅ `DELETE /api/v1/chat/conversations/{id}` - Delete conversation

### Stocks (requires auth 🔐)
- ✅ `GET /api/v1/stocks/search?q=query` - Search stocks
- ✅ `GET /api/v1/stocks/{symbol}` - Get stock details
- ✅ `GET /api/v1/stocks/{symbol}/quote` - Get real-time quote
- ✅ `GET /api/v1/stocks/{symbol}/news` - Get stock news

### Watchlist (requires auth 🔐)
- ✅ `GET /api/v1/watchlist/` - Get user's watchlist
- ✅ `POST /api/v1/watchlist/` - Add to watchlist
- ✅ `DELETE /api/v1/watchlist/{symbol}` - Remove from watchlist

### System
- ✅ `GET /health` - Health check
- ✅ `GET /` - API info

---

## 🎯 Testing Checklist

Use this checklist to verify all functions work:

- [ ] Create test user account
- [ ] Login successfully and receive token
- [ ] Authorize in Swagger UI
- [ ] Send chat message and receive AI response
- [ ] Continue conversation with context
- [ ] View conversation history
- [ ] Search for stocks
- [ ] Get detailed stock information
- [ ] Add stocks to watchlist
- [ ] View watchlist
- [ ] Remove stocks from watchlist
- [ ] Delete conversation

---

## 🐛 Troubleshooting

### "401 Unauthorized" Error
**Solution:** You need to authenticate first
1. Login to get your access token
2. Click the 🔓 Authorize button in Swagger UI
3. Enter: `Bearer YOUR_TOKEN`

### "422 Unprocessable Entity"
**Solution:** Check your request body format
- Ensure JSON is valid
- All required fields are included
- Field types match the schema

### No Response from Chat
**Solution:** Check your Groq API key
- Verify `GROQ_API_KEY` is set in `.env`
- Check terminal for error messages

### Stock Data Not Available
**Solution:** Some stocks may not be in the database
- Try common symbols: `AAPL`, `GOOGL`, `MSFT`, `TSLA`
- The Groww API may have limited coverage

---

## 💡 Tips

1. **Use Swagger UI** - It's the easiest way to test
2. **Save your token** - Copy it after login for reuse
3. **Test incrementally** - Start with auth, then move to other features
4. **Check the terminal** - Backend logs show detailed error messages
5. **Try different stocks** - Some APIs may have limited data

---

## 📚 Next Steps

After testing:
1. Connect your frontend to these endpoints
2. Implement error handling for failed requests
3. Add loading states for async operations
4. Store the auth token securely in your frontend
