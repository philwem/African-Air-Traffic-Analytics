import json
from datetime import datetime, timezone
from pathlib import Path


BRONZE_RAW_DIR = Path("lake/bronze/adsb/opensky")
BRONZE_CANONICAL_DIR = Path("lake/bronze/adsb/opensky_canonical")


def to_iso_utc(epoch_seconds: int | float | None) -> str | None:
    if epoch_seconds is None:
        return None
    return (
        datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def main():
    BRONZE_CANONICAL_DIR.mkdir(parents=True, exist_ok=True)

    raw_files = sorted(BRONZE_RAW_DIR.glob("opensky_states_*.json"))

    for raw_file in raw_files:
        payload = json.loads(raw_file.read_text(encoding="utf-8"))
        states = payload.get("states") or []

        if not states:
            continue

        out_file = BRONZE_CANONICAL_DIR / raw_file.name.replace(
            "opensky_states_", "opensky_canonical_"
        ).replace(".json", ".jsonl")

        with out_file.open("w", encoding="utf-8") as f:
            for s in states:
                record = {
                    "source": "opensky",
                    "aircraft_icao": s[0],
                    "callsign": s[1].strip() if s[1] else None,
                    "event_timestamp_utc": to_iso_utc(s[3] or s[4]),
                    "longitude_deg": s[5],
                    "latitude_deg": s[6],
                    "baro_altitude_m": s[7],
                    "on_ground": s[8],
                    "ground_speed_mps": s[9],
                    "track_deg": s[10],
                    "vertical_rate_mps": s[11],
                    "altitude_m": s[13],
                    "squawk": s[14],
                    "receiver_timestamp_utc": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                }

                f.write(json.dumps(record) + "\n")

        print(f"Converted {raw_file.name} → {out_file.name}")


if __name__ == "__main__":
    main()
