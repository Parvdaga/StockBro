# Quick Start Guide - StockBro Backend

## 🚀 1. Run the Backend

Open a terminal in the `backend` folder and run:

```powershell
python -m uvicorn main:app --reload
```

You should see: `INFO: Uvicorn running on http://127.0.0.1:8000`

## 🧪 2. Test the API

**Do NOT use curl/PowerShell for login/signup**. Authentication is handled by Supabase, not direct API endpoints.

### Step A: Create a User & Get Token
Open a **new** terminal and run:

1. **Create User**:
   ```powershell
   python scripts/create_test_user.py
   ```

2. **Get Token**:
   ```powershell
   python scripts/get_access_token.py
   ```
   *Copy the token printed to the screen.*

### Step B: Interactive Testing (Recommended)

1. Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
2. Click **Authorize**.
3. Enter `Bearer YOUR_TOKEN_HERE`.
4. Test endpoints like `/chat` or `/stocks`.

## 🛠️ Validation Script

If you just want to verify everything is installed correctly:

```powershell
.\test_backend.ps1
```

(Note: This might fail on specific API tests if you don't have a valid token configured in the script, so Manual Testing via Swagger UI is preferred).

---

## 📚 More Info

- Detailed Walkthrough: [`TESTING_GUIDE.md`](file:///TESTING_GUIDE.md)
