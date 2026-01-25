import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


def utc_now_for_filename() -> str:
    # Windows-safe timestamp (no ":" characters)
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S_%fZ")


def main():
    config_path = Path("ingestion/adsb/opensky_config.json")
    cfg = json.loads(config_path.read_text(encoding="utf-8"))

    out_dir = Path(cfg["output_path"])
    out_dir.mkdir(parents=True, exist_ok=True)

    while True:
        ts = utc_now_for_filename()
        try:
            r = requests.get(cfg["endpoint"], timeout=cfg["timeout_seconds"])
            r.raise_for_status()
            payload = r.json()

            out_file = out_dir / f"opensky_states_{ts}.json"
            out_file.write_text(json.dumps(payload), encoding="utf-8")

            print(f"[{ts}] wrote {out_file}")

        except Exception as e:
            print(f"[{ts}] ERROR: {e}")

        time.sleep(cfg["poll_interval_seconds"])


if __name__ == "__main__":
    main()
