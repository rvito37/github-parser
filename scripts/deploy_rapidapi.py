#!/usr/bin/env python3
"""
Deploy GitHub Profile Parser API to RapidAPI Hub.

Usage:
    python scripts/deploy_rapidapi.py \
        --rapidapi-key YOUR_KEY \
        --owner-id YOUR_OWNER_ID \
        --base-url http://YOUR_VPS_IP:8000

To find your credentials in RapidAPI Studio:
    - x-rapidapi-key: Go to https://rapidapi.com/developer/dashboard → Security → API Keys
    - owner-id: Go to Hub Listing → Endpoints → OpenAPI → API Details → "Owner ID"
    - API version ID: Hub Listing → Endpoints → pick version → OpenAPI → "API Version ID"
"""

import argparse
import json
import sys
import time
from pathlib import Path
from urllib import request as urllib_request
from urllib.error import HTTPError


RAPIDAPI_GRAPHQL_URL = "https://graphql-platform.p.rapidapi.com/"
RAPIDAPI_GRAPHQL_HOST = "graphql-platform.p.rapidapi.com"

# REST PAPI endpoints
CREATE_API_URL = "https://platformv.p.rapidapi.com/v1/apis/rapidapi-file/admin"
UPDATE_API_URL = "https://platformapi1.p.rapidapi.com/v1/apis/rapidapi-file/admin/{api_id}/versions/{version_id}"
PAPI_HOST = "platformapi1.rapidapi-x.rapidapi.com"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OPENAPI_PATH = PROJECT_ROOT / "openapi.json"


def load_openapi_spec(base_url: str) -> dict:
    """Load and patch openapi.json with the VPS base URL."""
    with open(OPENAPI_PATH) as f:
        spec = json.load(f)

    # Add server URL pointing to the VPS
    spec["servers"] = [{"url": base_url, "description": "Production VPS"}]
    return spec


def create_multipart_body(fields: dict, files: dict):
    """Build a multipart/form-data body without external dependencies."""
    boundary = "----RapidAPIDeployBoundary"
    body = b""

    for key, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode()
        body += f"{value}\r\n".encode()

    for key, (filename, content, content_type) in files.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode()
        body += f"Content-Type: {content_type}\r\n\r\n".encode()
        if isinstance(content, str):
            content = content.encode()
        body += content + b"\r\n"

    body += f"--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def graphql_query(api_key: str, query: str, variables: dict | None = None) -> dict:
    """Execute a GraphQL query against the RapidAPI Platform API."""
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib_request.Request(
        RAPIDAPI_GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": RAPIDAPI_GRAPHQL_HOST,
        },
        method="POST",
    )
    try:
        with urllib_request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"GraphQL error {e.code}: {error_body}", file=sys.stderr)
        raise


def get_api_info(api_key: str, api_id: str) -> dict | None:
    """Get API info including version ID via GraphQL PAPI."""
    query = """
    query getApi($apiId: ID!) {
        api(id: $apiId) {
            id
            name
            ownerId
            currentVersion {
                id
                name
            }
            versions {
                id
                name
            }
        }
    }
    """
    result = graphql_query(api_key, query, {"apiId": api_id})
    if result.get("data", {}).get("api"):
        return result["data"]["api"]
    return None


def upload_spec_create(api_key: str, owner_id: str, spec: dict) -> dict:
    """Create a new API by uploading the OpenAPI spec via REST PAPI."""
    spec_json = json.dumps(spec, indent=2)
    body, content_type = create_multipart_body(
        fields={"ownerId": owner_id},
        files={"file": ("openapi.json", spec_json, "application/json")},
    )
    req = urllib_request.Request(
        CREATE_API_URL,
        data=body,
        headers={
            "Content-Type": content_type,
            "x-rapidapi-host": PAPI_HOST,
            "x-rapidapi-key": api_key,
        },
        method="POST",
    )
    with urllib_request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def upload_spec_update(api_key: str, owner_id: str, api_id: str, version_id: str, spec: dict) -> dict:
    """Update an existing API by uploading the OpenAPI spec via REST PAPI."""
    spec_json = json.dumps(spec, indent=2)
    url = UPDATE_API_URL.format(api_id=api_id, version_id=version_id)
    body, content_type = create_multipart_body(
        fields={"ownerId": owner_id},
        files={"file": ("openapi.json", spec_json, "application/json")},
    )
    req = urllib_request.Request(
        url,
        data=body,
        headers={
            "Content-Type": content_type,
            "x-rapidapi-host": PAPI_HOST,
            "x-rapidapi-key": api_key,
        },
        method="PUT",
    )
    with urllib_request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def update_api_description(api_key: str, api_version_id: str, description: str) -> dict:
    """Update the API description via GraphQL PAPI."""
    mutation = """
    mutation updateApiVersion($apiVersionId: ID!, $updateData: ApiVersionUpdateInput!) {
        updateApiVersion(apiVersionId: $apiVersionId, updateData: $updateData) {
            id
            description
        }
    }
    """
    return graphql_query(
        api_key,
        mutation,
        {
            "apiVersionId": api_version_id,
            "updateData": {"description": description},
        },
    )


def main():
    parser = argparse.ArgumentParser(description="Deploy to RapidAPI Hub")
    parser.add_argument("--rapidapi-key", required=True, help="Your RapidAPI API key (x-rapidapi-key)")
    parser.add_argument("--owner-id", required=True, help="Your RapidAPI owner/user ID")
    parser.add_argument("--base-url", required=True, help="Your VPS base URL (e.g. http://123.45.67.89:8000)")
    parser.add_argument("--api-id", default=None, help="Existing API ID to update (leave empty to create new)")
    parser.add_argument("--version-id", default=None, help="API version ID to update (auto-detected if --api-id given)")
    args = parser.parse_args()

    print("=" * 60)
    print("  RapidAPI Deployment — GitHub Profile Parser")
    print("=" * 60)

    # 1) Load and patch the spec
    print(f"\n[1/4] Loading OpenAPI spec from {OPENAPI_PATH}")
    spec = load_openapi_spec(args.base_url.rstrip("/"))
    print(f"       Base URL set to: {args.base_url}")
    print(f"       Endpoints: {list(spec['paths'].keys())}")

    # 2) Check if API already exists
    api_id = args.api_id
    version_id = args.version_id

    if api_id and not version_id:
        print(f"\n[2/4] Fetching API info for {api_id}...")
        try:
            info = get_api_info(args.rapidapi_key, api_id)
            if info:
                version_id = info["currentVersion"]["id"]
                print(f"       API: {info['name']}")
                print(f"       Version: {info['currentVersion']['name']} (ID: {version_id})")
            else:
                print("       API not found, will create new one")
                api_id = None
        except Exception as e:
            print(f"       Could not fetch API info: {e}")
            print("       Will attempt to create new API instead")
            api_id = None
    else:
        print("\n[2/4] Skipped API lookup")

    # 3) Upload spec
    print("\n[3/4] Uploading OpenAPI spec to RapidAPI...")
    try:
        if api_id and version_id:
            print(f"       Updating API {api_id} version {version_id}")
            result = upload_spec_update(args.rapidapi_key, args.owner_id, api_id, version_id, spec)
            print(f"       Updated successfully!")
        else:
            print("       Creating new API listing...")
            result = upload_spec_create(args.rapidapi_key, args.owner_id, spec)
            print(f"       Created successfully!")
        print(f"       Response: {json.dumps(result, indent=2)[:500]}")
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"\n  ERROR {e.code}: {error_body}", file=sys.stderr)
        if e.code == 403:
            print("\n  Possible causes:", file=sys.stderr)
            print("  - Invalid x-rapidapi-key", file=sys.stderr)
            print("  - Key doesn't have Platform API access", file=sys.stderr)
            print("  - Wrong owner-id", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n  ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # 4) Done
    print("\n[4/4] Deployment complete!")
    print("\n" + "=" * 60)
    print("  NEXT STEPS:")
    print("=" * 60)
    print(f"""
  1. Go to RapidAPI Studio and verify endpoints are visible:
     https://rapidapi.com/studio

  2. Set up the Proxy Secret on your VPS:
     - In RapidAPI Studio -> Settings -> copy "Proxy Secret"
     - SSH to VPS and edit .env:
       RAPIDAPI_PROXY_SECRET=<paste-secret-here>
     - Restart: docker-compose restart

  3. Test the API on RapidAPI Hub:
     - Go to your API's "Endpoints" tab
     - Try GET /profile/torvalds

  4. Configure pricing (optional):
     - Studio -> Monetize -> Add plans

  5. Publish:
     - Studio -> Publish -> General -> "Make API Public"
""")


if __name__ == "__main__":
    main()
