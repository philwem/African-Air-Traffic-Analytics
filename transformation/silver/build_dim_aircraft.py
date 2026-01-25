import json
from pathlib import Path

BRONZE_DIR = Path("lake/bronze/metadata/adsbdb/aircraft")
SILVER_DIR = Path("lake/silver/dim_aircraft")
OUT_FILE = SILVER_DIR / "dim_aircraft.jsonl"


def main():
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    latest_by_icao = {}
    scanned = 0
    extracted = 0

    for file in BRONZE_DIR.glob("*.json"):
        scanned += 1
        payload = json.loads(file.read_text(encoding="utf-8"))

        aircraft = payload.get("response", {}).get("aircraft", {})
        if not aircraft:
            continue

        # ADSBDB uses mode_s as the ICAO24 hex
        icao = aircraft.get("mode_s")
        if not icao:
            continue

        icao = str(icao).lower().strip()

        rec = {
            "aircraft_icao": icao,
            "registration": aircraft.get("registration"),
            "manufacturer": aircraft.get("manufacturer"),
            "model": aircraft.get("type"),                 # e.g., "EMB-190 AR"
            "type_code": aircraft.get("icao_type"),        # e.g., "E190"

            # Operator details
            # e.g., "Airlink"
            "operator_name": aircraft.get("registered_owner"),
            # e.g., "LNK"
            "operator_icao": aircraft.get("registered_owner_operator_flag_code"),

            # Country
            "country_of_registration": aircraft.get("registered_owner_country_name"),
            "country_iso": aircraft.get("registered_owner_country_iso_name"),

            "source": "adsbdb"
        }

        latest_by_icao[icao] = rec
        extracted += 1

    with OUT_FILE.open("w", encoding="utf-8") as out:
        for rec in latest_by_icao.values():
            out.write(json.dumps(rec) + "\n")

    print(f"Scanned files: {scanned}")
    print(f"Extracted aircraft records: {extracted}")
    print(f"dim_aircraft written: {len(latest_by_icao)} rows → {OUT_FILE}")


if __name__ == "__main__":
    main()
            