import csv
from pathlib import Path

BRONZE_FILE = Path("lake/bronze/metadata/adsbdb/airports/airports_raw.csv")
SILVER_DIR = Path("lake/silver/dim_airport")
OUT_FILE = SILVER_DIR / "dim_airport.csv"


def main():
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    with BRONZE_FILE.open("r", encoding="utf-8") as f, OUT_FILE.open("w", newline="", encoding="utf-8") as out:
        reader = csv.DictReader(f)

        writer = csv.DictWriter(
            out,
            fieldnames=[
                "airport_icao",
                "airport_iata",
                "airport_name",
                "country",
                "latitude_deg",
                "longitude_deg",
                "elevation_ft",
            ],
        )
        writer.writeheader()

        kept = 0
        for r in reader:
            icao = (r.get("ident") or "").strip()
            lat = (r.get("latitude_deg") or "").strip()
            lon = (r.get("longitude_deg") or "").strip()

            # must have ICAO + coordinates
            if not icao or not lat or not lon:
                continue

            writer.writerow({
                "airport_icao": icao,
                "airport_iata": (r.get("iata_code") or "").strip() or None,
                "airport_name": (r.get("name") or "").strip() or None,
                "country": (r.get("iso_country") or "").strip() or None,
                "latitude_deg": lat,
                "longitude_deg": lon,
                "elevation_ft": (r.get("elevation_ft") or "").strip() or None,
            })
            kept += 1

    print(f"dim_airport written: {kept} rows → {OUT_FILE}")


if __name__ == "__main__":
    main()
