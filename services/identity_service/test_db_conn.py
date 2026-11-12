"""
Test SQLAlchemy Async Engine with Supabase Pooler
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

PROJECT_REF = "enkssiilvwiemxvsqaoy"
USER = f"postgres.{PROJECT_REF}"
PASSWORD = "Anil_21kb1a3029"
HOST = "aws-0-ap-south-1.pooler.supabase.com"
DB = "postgres"

async def test_session_mode():
    print("\n--- Testing Session Mode (Port 5432) ---")
    url = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:5432/{DB}?ssl=require"
    try:
        engine = create_async_engine(url, pool_pre_ping=True)
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT version();"))
            print(f"SUCCESS: Session Mode (5432) works! {res.scalar()[:20]}")
            
            # Check schema
            res_tables = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='identity_service'"))
            tables = [row[0] for row in res_tables.fetchall()]
            print(f"Tables in identity_service: {tables}")
        await engine.dispose()
        return 5432
    except Exception as e:
        print(f"Port 5432 failed: {e}")
        return None

async def test_transaction_mode():
    print("\n--- Testing Transaction Mode (Port 6543) ---")
    url = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:6543/{DB}?ssl=require"
    try:
        # asyncpg with transaction pooler requires statement_cache_size=0
        engine = create_async_engine(
            url, 
            pool_pre_ping=True,
            connect_args={"statement_cache_size": 0}
        )
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT version();"))
            print(f"SUCCESS: Transaction Mode (6543) works! {res.scalar()[:20]}")
        await engine.dispose()
        return 6543
    except Exception as e:
        print(f"Port 6543 failed: {e}")
        return None

async def main():
    s = await test_session_mode()
    t = await test_transaction_mode()
    print("\n" + "=" * 50)
    if s:
        print(f"RECOMMENDED PORT: 5432 (Session Mode - Full SQLAlchemy Compatibility)")
    elif t:
        print(f"RECOMMENDED PORT: 6543 (Transaction Mode)")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
