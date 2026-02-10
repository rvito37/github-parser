#!/usr/bin/env python3
"""Regenerate openapi.json from the FastAPI app.

Usage:
    python scripts/generate_openapi.py
    python scripts/generate_openapi.py --base-url http://123.45.67.89:8000
"""

import argparse
import json
from pathlib import Path

from app.main import app

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_ROOT / "openapi.json"


def main():
    parser = argparse.ArgumentParser(description="Generate openapi.json")
    parser.add_argument("--base-url", default=None, help="Add a server base URL to the spec")
    args = parser.parse_args()

    spec = app.openapi()

    if args.base_url:
        spec["servers"] = [{"url": args.base_url.rstrip("/"), "description": "Production VPS"}]

    with open(OUTPUT, "w") as f:
        json.dump(spec, f, indent=2)
        f.write("\n")

    print(f"Generated {OUTPUT}")
    print(f"Endpoints: {list(spec['paths'].keys())}")
    if args.base_url:
        print(f"Server: {args.base_url}")


if __name__ == "__main__":
    main()
