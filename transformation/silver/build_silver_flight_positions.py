import json
from pathlib import Path

BRONZE_CANONICAL_DIR = Path("lake/bronze/adsb/opensky_canonical")
SILVER_DIR = Path("lake/silver/flight_positions")
LOG_DIR = Path("lake/silver/logs")

# Africa bounding box (MVP)
AFRICA_LAT_MIN = -35.0
AFRICA_LAT_MAX = 38.0
AFRICA_LON_MIN = -20.0
AFRICA_LON_MAX = 55.0


def in_africa(lat: float, lon: float) -> bool:
    return (
        AFRICA_LAT_MIN <= lat <= AFRICA_LAT_MAX
        and AFRICA_LON_MIN <= lon <= AFRICA_LON_MAX
    )


def main():
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    out_file = SILVER_DIR / "silver_flight_positions.jsonl"
    rejected_file = LOG_DIR / "rejected_positions.log"

    written = 0
    rejected = 0
    scanned = 0

    with out_file.open("w", encoding="utf-8") as out, rejected_file.open("w", encoding="utf-8") as rej:
        for file in BRONZE_CANONICAL_DIR.glob("*.jsonl"):
            with file.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue

                    scanned += 1
                    rec = json.loads(line)

                    # Required fields for Silver
                    lat = rec.get("latitude_deg")
                    lon = rec.get("longitude_deg")
                    ts = rec.get("event_timestamp_utc")
                    icao = rec.get("aircraft_icao")

                    # 1) Clean: reject missing required fields
                    if lat is None or lon is None or ts is None or icao is None:
                        rejected += 1
                        rej.write(
                            f"missing_required_fields file={file.name} rec={rec}\n")
                        continue

                    # 2) Clean: enforce numeric lat/lon
                    try:
                        lat_f = float(lat)
                        lon_f = float(lon)
                    except Exception:
                        rejected += 1
                        rej.write(
                            f"invalid_lat_lon file={file.name} lat={lat} lon={lon} icao={icao}\n")
                        continue

                    # 3) Filter: Africa-only (records outside are dropped, not rejected)
                    if not in_africa(lat_f, lon_f):
                        continue

                    # 4) Normalize
                    rec["latitude_deg"] = lat_f
                    rec["longitude_deg"] = lon_f
                    rec["aircraft_icao"] = str(icao).lower()

                    # 5) Airline fallback: derive operator code guess from callsign
                    cs = rec.get("callsign")
                    if cs and isinstance(cs, str):
                        cs_clean = cs.strip().upper()
                        rec["operator_icao_guess"] = cs_clean[:3] if len(
                            cs_clean) >= 3 else None
                    else:
                        rec["operator_icao_guess"] = None

                    out.write(json.dumps(rec) + "\n")
                    written += 1

    print(
        f"Silver build complete: scanned={scanned} written={written} rejected={rejected}")
    print(f"Output: {out_file}")
    print(f"Reject log: {rejected_file}")


if __name__ == "__main__":
    main()
