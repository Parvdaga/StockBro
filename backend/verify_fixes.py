
import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    print("Importing app.api.v1.chat...")
    from app.api.v1 import chat
    print("Success importing chat")
    
    print("Importing app.api.v1.watchlist...")
    from app.api.v1 import watchlist
    print("Success importing watchlist")
    
    print("Importing app.schemas.chat...")
    from app.schemas import chat as chat_schema
    print("Success importing chat_schema")

    print("All imports successful. Syntax checks passed.")
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
