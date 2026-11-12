"""
Check users table in Supabase
"""
import asyncio
import asyncpg

USER = "postgres.enkssiilvwiemxvsqaoy"
PASSWORD = "Anil_21kb1a3029"
HOST = "aws-0-ap-south-1.pooler.supabase.com"
PORT = 6543
DB = "postgres"

async def check_users():
    conn = await asyncpg.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DB,
        ssl="require"
    )
    users = await conn.fetch("""
        SELECT user_id, tenant_id, email, password_hash, role_id, is_active, created_at 
        FROM identity_service.users 
        ORDER BY created_at DESC;
    """)
    print("\n--- Users currently in identity_service.users ---")
    for u in users:
        print(f"user_id: '{u['user_id']}' | email: '{u['email']}' | role: '{u['role_id']}' | active: {u['is_active']} | hash_len: {len(u['password_hash'])} | hash_prefix: {u['password_hash'][:10]}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_users())

