import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


CONFIG_FILE = Path("ingestion/metadata/adsbdb_config.json")
OUT_DIR = Path("lake/bronze/metadata/adsbdb/airlines")


def utc_now_filename() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S_%fZ")


def main():
    cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    base_url = cfg["base_url"].rstrip("/")
    headers = {}
    if cfg.get("api_key"):
        headers["Authorization"] = f"Bearer {cfg['api_key']}"

    # NOTE: endpoint may vary by provider
    url = f"{base_url}/v0/operators"
    ts = utc_now_filename()

    try:
        r = requests.get(url, headers=headers, timeout=cfg["timeout_seconds"])
        r.raise_for_status()
        payload = r.json()

        out_file = OUT_DIR / f"adsbdb_operators_{ts}.json"
        out_file.write_text(json.dumps(payload), encoding="utf-8")
        print(f"Wrote airline metadata → {out_file}")

    except Exception as e:
        print(f"ERROR fetching airline metadata: {e}")


if __name__ == "__main__":
    main()
