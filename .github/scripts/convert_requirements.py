#!/usr/bin/env python3
import json
import os
import re
import sys

# Non-portable C/Rust packages or local-only dev servers incompatible with Pyodide WebAssembly
EXCLUDED_DEPS = {
    "watchfiles",
    "uvicorn",
    "bcrypt",
    "greenlet",
    "asyncpg",
    "httpx",
    "sqlalchemy",
    "email-validator",
    "workers-py",
    "workers-runtime-sdk",
}

def clean_dep_name(dep_str: str) -> str:
    m = re.match(r"^([a-zA-Z0-9_-]+)", dep_str)
    return m.group(1).lower() if m else ""

def convert(service_dir: str = "."):
    pyproject_file = os.path.join(service_dir, "pyproject.toml")
    req_file = os.path.join(service_dir, "requirements.txt")

    # If pyproject.toml already exists, keep it as single source of truth
    if os.path.isfile(pyproject_file):
        if os.path.isfile(req_file):
            try:
                os.remove(req_file)
            except OSError:
                pass
        print(f"ℹ️ Found existing {pyproject_file}, keeping it intact.")
        return

    if not os.path.isfile(req_file):
        return

    service_name = os.path.basename(os.path.abspath(service_dir)).replace("_", "-")

    with open(req_file, "r", encoding="utf-8") as f:
        deps = []
        for line in f:
            clean = line.strip()
            if not clean or clean.startswith("#") or clean.startswith("-"):
                continue
            pkg_name = clean_dep_name(clean)
            if pkg_name in EXCLUDED_DEPS:
                print(f"Skipping non-worker dependency: {clean}")
                continue
            if "passlib[bcrypt]" in clean:
                clean = clean.replace("passlib[bcrypt]", "passlib")
            if "sqlalchemy[asyncio]" in clean:
                clean = clean.replace("sqlalchemy[asyncio]", "sqlalchemy")
            if "python-jose[cryptography]" in clean:
                clean = clean.replace("python-jose[cryptography]", "python-jose")
            deps.append(clean)

    pyproject_content = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mak-{service_name}"
version = "1.0.0"
description = "Cloudflare Worker for {service_name}"
readme = "README.md"
requires-python = ">=3.12"
dependencies = {json.dumps(deps, indent=4)}

[dependency-groups]
dev = [
    "workers-py",
    "workers-runtime-sdk"
]

[tool.setuptools]
packages = ["core", "models", "routes", "schemas", "services"]
py-modules = ["main"]
"""

    with open(pyproject_file, "w", encoding="utf-8") as f:
        f.write(pyproject_content)

    try:
        os.remove(req_file)
    except OSError:
        pass

    print(f"✅ Generated Cloudflare Worker pyproject.toml for 'mak-{service_name}'")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    convert(target)
