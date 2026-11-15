#!/usr/bin/env python3
import json
import os
import sys

def convert(service_dir: str = "."):
    req_file = os.path.join(service_dir, "requirements.txt")
    pyproject_file = os.path.join(service_dir, "pyproject.toml")

    if not os.path.isfile(req_file):
        return

    if os.path.isfile(pyproject_file):
        # pyproject.toml already exists; simply remove requirements.txt to avoid wrangler conflict
        try:
            os.remove(req_file)
        except OSError:
            pass
        return

    service_name = os.path.basename(os.path.abspath(service_dir)).replace("_", "-")

    with open(req_file, "r", encoding="utf-8") as f:
        deps = []
        for line in f:
            clean = line.strip()
            if clean and not clean.startswith("#") and not clean.startswith("-"):
                deps.append(clean)

    pyproject_content = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mak-{service_name}"
version = "1.0.0"
description = "Cloudflare Worker for {service_name}"
readme = "README.md"
requires-python = ">=3.11"
dependencies = {json.dumps(deps, indent=4)}

[tool.setuptools.packages.find]
where = ["."]
include = ["*"]
"""

    with open(pyproject_file, "w", encoding="utf-8") as f:
        f.write(pyproject_content)

    try:
        os.remove(req_file)
    except OSError:
        pass

    print(f"✅ Converted {req_file} to {pyproject_file} for service 'mak-{service_name}'")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    convert(target)

