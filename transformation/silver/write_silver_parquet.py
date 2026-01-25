import json
from pathlib import Path

import pandas as pd

SILVER_FLIGHTS = Path(
    "lake/silver/flight_positions/silver_flight_positions.jsonl")
SILVER_AIRCRAFT = Path("lake/silver/dim_aircraft/dim_aircraft.jsonl")
SILVER_AIRPORT = Path("lake/silver/dim_airport/dim_airport.csv")

OUT_FLIGHTS = Path(
    "lake/silver/flight_positions/silver_flight_positions.parquet")
OUT_AIRCRAFT = Path("lake/silver/dim_aircraft/dim_aircraft.parquet")
OUT_AIRPORT = Path("lake/silver/dim_airport/dim_airport.parquet")


def read_jsonl(path: Path) -> pd.DataFrame:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def main():
    # Flights
    df_f = read_jsonl(SILVER_FLIGHTS)
    df_f.to_parquet(OUT_FLIGHTS, index=False)
    print(f"Wrote: {OUT_FLIGHTS} rows={len(df_f)}")

    # Aircraft
    df_a = read_jsonl(SILVER_AIRCRAFT)
    df_a.to_parquet(OUT_AIRCRAFT, index=False)
    print(f"Wrote: {OUT_AIRCRAFT} rows={len(df_a)}")

    # Airport
    df_p = pd.read_csv(SILVER_AIRPORT)
    df_p.to_parquet(OUT_AIRPORT, index=False)
    print(f"Wrote: {OUT_AIRPORT} rows={len(df_p)}")


if __name__ == "__main__":
    main()
