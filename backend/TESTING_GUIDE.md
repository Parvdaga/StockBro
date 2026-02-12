# StockBro Backend - Simple Testing Guide

Follow these steps in order to test the StockBro backend.

## ✅ Prerequisites

1. **Backend Running**:
   Open a terminal and run:
   ```powershell
   python -m uvicorn main:app --reload
   ```
   Keep this terminal open!

2. **Open Swagger UI**:
   Go to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🚀 Step 1: Create a Test User

You need a user account to get an access token. We've made a script for this.

1. Open a **new** terminal (keep the backend running in the first one).
2. Run:
   ```powershell
   python scripts/create_test_user.py
   ```
3. Enter an email (e.g., `test@example.com`) and a password (min 6 chars).
4. **Note:** If it says "Check your email", you might need to disable email confirmation in your Supabase project settings for testing, or check your inbox.

---

## 🔑 Step 2: Get Your Access Token

You need an "access token" to tell the backend who you are.

1. In the same terminal, run:
   ```powershell
   python scripts/get_access_token.py
   ```
2. Enter the email and password you just created.
3. **COPY the long token** starting with `ey...` that is printed on the screen.

---

## 🔓 Step 3: Authorize Swagger UI

1. Go back to your browser: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Click the **Authorize** button (green lock icon) at the top right.
3. In the `Value` box, type `Bearer ` followed by your token.
   - Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5c...`
4. Click **Authorize**, then **Close**.

🎉 **You are now logged in!**

---

## 🧪 Step 4: Test Endpoints

Now you can test any feature.

### 💬 Test Chat (Talk to `StockBro`)

1. Scroll to **Chat**.
2. Click **POST /api/v1/chat/** -> **Try it out**.
3. Edit the Request body:
   ```json
   {
     "message": "What is the price of Apple stock?",
     "conversation_id": null
   }
   ```
4. Click **Execute**.
5. See the AI response below!

### 📈 Test Stock Data

1. Scroll to **Stocks**.
2. Click **GET /api/v1/stocks/search** -> **Try it out**.
3. Enter a query like `Tesla` or `NVDA`.
4. Click **Execute**.

### ⭐ Test Watchlist

1. Scroll to **Watchlist**.
2. Click **POST /api/v1/watchlist/** -> **Try it out**.
3. Add a stock:
   ```json
   {
     "symbol": "TSLA",
     "name": "Tesla Inc."
   }
   ```
4. Click **Execute**.
5. Then verify by clicking **GET /api/v1/watchlist/** -> **Try it out** -> **Execute**.

---

## ❓ Common Issues

- **401 Unauthorized**: You forgot Step 3, or your token expired. Run `get_access_token.py` again.
- **Email Not Confirmed**: Run `python scripts/confirm_user.py` to auto-confirm your email.
- **Connection Refused**: Your backend is not running. Check Step 1.
