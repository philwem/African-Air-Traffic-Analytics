import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


ICAO_LIST_FILE = Path("docs/samples/unique_aircraft_icao.txt")
CONFIG_FILE = Path("ingestion/metadata/adsbdb_config.json")


def utc_now_filename() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S_%fZ")


def main():
    cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

    out_dir = Path(cfg["output_path"])
    out_dir.mkdir(parents=True, exist_ok=True)

    icao_list = ICAO_LIST_FILE.read_text(encoding="utf-8").splitlines()
    icao_list = [x.strip().lower() for x in icao_list if x.strip()]

    max_requests = int(cfg.get("max_requests", 200))
    icao_list = icao_list[:max_requests]

    session = requests.Session()

    headers = {}
    if cfg.get("api_key"):
        headers["Authorization"] = f"Bearer {cfg['api_key']}"

    base_url = cfg["base_url"].rstrip("/")
    path_tpl = cfg["aircraft_lookup_path"]

    ok = 0
    fail = 0

    for icao in icao_list:
        url = f"{base_url}{path_tpl.format(icao24=icao)}"
        ts = utc_now_filename()

        try:
            r = session.get(url, headers=headers,
                            timeout=cfg["timeout_seconds"])
            r.raise_for_status()
            payload = r.json()

            out_file = out_dir / f"adsbdb_aircraft_{icao}_{ts}.json"
            out_file.write_text(json.dumps(payload), encoding="utf-8")
            ok += 1

        except Exception as e:
            fail += 1
            # Write failures to a log file for debugging
            log_file = out_dir / "adsbdb_aircraft_failures.log"
            with log_file.open("a", encoding="utf-8") as lf:
                lf.write(f"{ts} icao={icao} url={url} error={e}\n")

        time.sleep(0.2)  # polite delay

    print(
        f"Finished ADSBDB aircraft fetch: ok={ok} fail={fail} output={out_dir}")


if __name__ == "__main__":
    main()
