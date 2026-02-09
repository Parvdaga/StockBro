"""
Initialize database tables
Run this before first use: python init_db.py
"""
import asyncio
from app.db import Base, engine
from app.db.models import (
    User, Stock, PriceHistory,
    Watchlist, WatchlistItem,
    Conversation, Message,
    Portfolio, Holding, Transaction
)


async def init_db():
    """Create all database tables"""
    async with engine.begin() as conn:
        # Drop all tables (optional - use carefully!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")
    print("\nCreated tables:")
    print("  - users")
    print("  - stocks")
    print("  - price_history")
    print("  - watchlist")
    print("  - watchlistitem")
    print("  - conversation")
    print("  - message")
    print("  - portfolio")
    print("  - holding")
    print("  - transaction")


if __name__ == "__main__":
    print("🔨 Initializing database...")
    asyncio.run(init_db())
