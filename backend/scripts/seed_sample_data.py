"""
Seeds a running Rolodex API with the 5 sample LinkedIn profiles, using the
real ingestion pipeline (OpenAI extraction + embeddings), so you see genuine
generated entries rather than the static fixtures in sample_data/generated_entries/.

Usage:
    python3 scripts/seed_sample_data.py
    python3 scripts/seed_sample_data.py --api-url https://your-backend.up.railway.app/api/v1

Requires the backend to be running and reachable, and OPENAI_API_KEY to be
set on the backend (this script only makes HTTP requests — it doesn't call
OpenAI directly).
"""
import argparse
import sys
import time
from pathlib import Path

import httpx

PROFILES_DIR = Path(__file__).parent.parent / "sample_data" / "linkedin_profiles"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/api/v1",
        help="Base URL of the running API (default: %(default)s)",
    )
    args = parser.parse_args()

    profile_files = sorted(PROFILES_DIR.glob("*.txt"))
    if not profile_files:
        print(f"No sample profiles found in {PROFILES_DIR}", file=sys.stderr)
        sys.exit(1)

    with httpx.Client(timeout=60.0) as client:
        for path in profile_files:
            raw_text = path.read_text(encoding="utf-8")
            print(f"Ingesting {path.name} ...", end=" ", flush=True)
            try:
                response = client.post(
                    f"{args.api_url}/contacts/ingest/force",
                    json={"source_type": "text", "raw_text": raw_text},
                )
                response.raise_for_status()
                data = response.json()
                name = (data.get("contact") or {}).get("full_name", "unknown")
                print(f"OK -> {name}")
            except httpx.HTTPStatusError as exc:
                print(f"FAILED ({exc.response.status_code}): {exc.response.text}")
            except httpx.RequestError as exc:
                print(f"FAILED (connection error): {exc}")
                sys.exit(1)
            time.sleep(0.5)  # gentle on rate limits

    print("\nDone. Open the frontend and check the dashboard / all contacts page.")


if __name__ == "__main__":
    main()
