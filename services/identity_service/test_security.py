"""
Test Password Hashing & Verification
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from core.security import hash_password, verify_password

test_passwords = [
    "Password123!",
    "StudentPass@2026",
    "Admin@123",
    "SamplePass#999"
]

print("\n--- Testing Password Hashing & Verification ---")
for p in test_passwords:
    h = hash_password(p)
    matches = verify_password(p, h)
    wrong_matches = verify_password(p + "_wrong", h)
    print(f"Password: '{p}' | Hash prefix: {h[:15]} | Valid match: {matches} | Wrong match: {wrong_matches}")
    if not matches:
        print(f"ERROR: Verification failed for {p}!")

