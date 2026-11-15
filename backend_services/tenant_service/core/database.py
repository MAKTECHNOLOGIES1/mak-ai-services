"""
Asynchronous Database Connection Pool for Tenant Service
Compatible with Supabase PostgreSQL and cloud poolers (Supavisor / PgBouncer)
"""

from core.config import settings

try:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()
    db_url = settings.get_database_url()

    engine_kwargs = {
        "echo": settings.DEBUG and settings.ENVIRONMENT == "development",
        "pool_pre_ping": True,
        "connect_args": {
            "statement_cache_size": 0
        }
    }

    if settings.ENVIRONMENT != "development":
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 1800
        })

    engine = create_async_engine(db_url, **engine_kwargs)

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
except Exception:
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    AsyncSession = None  # type: ignore
    engine = None
    AsyncSessionLocal = None  # type: ignore

async def get_db():
    """FastAPI Dependency for database session"""
    if AsyncSessionLocal is None:
        yield None
        return
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
