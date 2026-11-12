"""
Fix Seed Passwords in Supabase Database
"""
import asyncio
import asyncpg
import bcrypt

USER = "postgres.enkssiilvwiemxvsqaoy"
PASSWORD = "Anil_21kb1a3029"
HOST = "aws-0-ap-south-1.pooler.supabase.com"
PORT = 6543
DB = "postgres"

async def fix_passwords():
    # Generate proper bcrypt hash for Password123!
    valid_hash = bcrypt.hashpw(b"Password123!", bcrypt.gensalt(rounds=12)).decode("utf-8")
    print(f"Generated valid BCrypt hash: {valid_hash}")
    
    conn = await asyncpg.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DB,
        ssl="require"
    )
    
    # Update ADM-SRIT-001, FAC-SRIT-001, 22731A0501
    await conn.execute("""
        UPDATE identity_service.users
        SET password_hash = $1
        WHERE user_id IN ('ADM-SRIT-001', 'FAC-SRIT-001', '22731A0501');
    """, valid_hash)
    
    print("SUCCESS: Updated seed accounts ('ADM-SRIT-001', 'FAC-SRIT-001', '22731A0501') with valid Password123! hash.")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_passwords())

