"""
Database package initialization
Exports Base, engine, and session factory
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Base class for models
Base = declarative_base()

# Create Async Engine
engine = create_async_engine(
    settings.DB_URL,
    echo=settings.DEBUG,
    future=True
)

# Create Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

__all__ = ["Base", "engine", "AsyncSessionLocal"]
