import json
from pathlib import Path

CANONICAL_DIR = Path("lake/bronze/adsb/opensky_canonical")
OUT_DIR = Path("docs/samples")
OUT_FILE = OUT_DIR / "unique_aircraft_icao.txt"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    icao_set = set()

    for file in CANONICAL_DIR.glob("*.jsonl"):
        with file.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                icao = rec.get("aircraft_icao")
                if icao:
                    icao_set.add(icao.lower())

    icao_list = sorted(icao_set)

    OUT_FILE.write_text("\n".join(icao_list), encoding="utf-8")
    print(f"Saved {len(icao_list)} unique ICAO24 codes → {OUT_FILE}")


if __name__ == "__main__":
    main()
