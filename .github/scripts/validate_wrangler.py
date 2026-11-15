#!/usr/bin/env python3
import glob
import json
import os
import re
import sys

def strip_jsonc(text: str) -> str:
    # Strip UTF-8 BOM
    if text.startswith("\ufeff"):
        text = text[1:]
    # Strip single-line comments
    text = re.sub(r"//.*", "", text)
    # Strip multi-line comments
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pattern = os.path.join(root_dir, "**", "wrangler.jsonc")
    files = glob.glob(pattern, recursive=True)
    # Exclude node_modules
    files = [f for f in files if "node_modules" not in f]

    print(f"Inspecting {len(files)} wrangler configurations...")
    errors = 0

    for f in sorted(files):
        rel_path = os.path.relpath(f, root_dir)
        try:
            with open(f, "r", encoding="utf-8") as fp:
                raw = fp.read()
            cleaned = strip_jsonc(raw)
            data = json.loads(cleaned)
            if "name" not in data:
                raise ValueError("Missing 'name' field")
            print(f"✅ {rel_path} -> valid (name: {data['name']})")
        except Exception as e:
            print(f"❌ {rel_path} -> error: {e}", file=sys.stderr)
            errors += 1

    if errors > 0:
        print(f"\nFound {errors} invalid configuration(s).", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nAll {len(files)} configurations validated successfully!")

if __name__ == "__main__":
    main()

