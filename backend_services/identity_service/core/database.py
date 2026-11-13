"""
Asynchronous Database Connection Pool
Compatible with Supabase PostgreSQL and cloud poolers (PgBouncer/Supavisor)
"""

from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Base Declarative Model
Base = declarative_base()

# Configure Async Engine with pre-ping to handle cloud timeouts (Supabase)
db_url = settings.get_database_url()

engine_kwargs = {
    "echo": settings.DEBUG and settings.ENVIRONMENT == "development",
    "pool_pre_ping": True, # Automatically reconnect dropped connections
    "connect_args": {
        "statement_cache_size": 0 # Required for Supabase pooler (Supavisor/PgBouncer)
    }
}

# Add pool size constraints for production/cloud
if settings.ENVIRONMENT != "development":
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800 # 30 min recycle
    })

engine = create_async_engine(db_url, **engine_kwargs)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    """FastAPI Dependency for database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

