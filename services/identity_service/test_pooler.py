"""
Supabase Pooler Auto-Detector & Diagnostics
Tests IPv4 Pooler endpoints for project 'enkssiilvwiemxvsqaoy'
"""
import asyncio
import asyncpg

PROJECT_REF = "enkssiilvwiemxvsqaoy"
POOLER_USER = f"postgres.{PROJECT_REF}"
PASSWORD = "Anil_21kb1a3029"
DB = "postgres"

REGIONS = [
    ("ap-south-1", "Mumbai, India"),
    ("ap-southeast-1", "Singapore"),
    ("us-east-1", "North Virginia, US"),
    ("eu-central-1", "Frankfurt, Europe"),
    ("us-west-1", "North California, US")
]

async def check_region(region, name):
    host = f"aws-0-{region}.pooler.supabase.com"
    print(f"Testing {name} ({host}:6543)...", end=" ", flush=True)
    try:
        conn = await asyncio.wait_for(
            asyncpg.connect(
                user=POOLER_USER,
                password=PASSWORD,
                host=host,
                port=6543,
                database=DB,
                ssl="require"
            ),
            timeout=5.0
        )
        print("CONNECTED!")
        version = await conn.fetchval("SELECT version();")
        print(f"  -> PostgreSQL Version: {version.split()[0]} {version.split()[1]}")
        
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'identity_service';
        """)
        print(f"  -> Verified tables in identity_service: {[t['table_name'] for t in tables]}")
        await conn.close()
        return host
    except asyncio.TimeoutError:
        print("Timeout.")
        return None
    except asyncpg.exceptions.InvalidPasswordError:
        print("CONNECTED, but password authentication failed!")
        return host
    except Exception as e:
        print(f"Error: {e}")
        return None

async def main():
    print("=" * 60)
    print("Detecting your Supabase Pooler Region (IPv4 Connection)...")
    print("=" * 60)
    
    for region, name in REGIONS:
        found_host = await check_region(region, name)
        if found_host:
            print("\n" + "=" * 60)
            print(f"SUCCESS! Your project host is: {found_host}")
            print("=" * 60)
            return found_host
            
    print("\nNo auto-detected region matched. Please check your Supabase Dashboard -> Connect -> Transaction pooler.")

if __name__ == "__main__":
    asyncio.run(main())

