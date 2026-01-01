"""
Phase 2 — Daily Batch Ingestion of Aircraft Metadata from ADSBDB

Source of ICAOs: OpenSky raw state vectors (Bronze)
"""

import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta, UTC

import pandas as pd

from ingestion.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("adsbdb-metadata-ingestion")


class ADSBDBMetadataIngester:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(config.adsbdb.headers)
        self.processed_icao: Set[str] = set()

    # -----------------------------
    # STEP 1: Extract ICAOs
    # -----------------------------
    def extract_unique_aircraft_from_raw(
        self, start_date: datetime, end_date: datetime
    ) -> Set[str]:
        """
        Read OpenSky Bronze JSON files and extract unique ICAO24 identifiers.
        """
        aircraft: Set[str] = set()
        raw_path = Path(config.storage.raw_positions_path)

        for file in raw_path.rglob("*.json"):
            with file.open("r", encoding="utf-8") as f:
                payload = json.load(f)

            ingestion_ts = datetime.fromisoformat(
                payload["ingestion_timestamp"]
            )

            if not (start_date <= ingestion_ts < end_date):
                continue

            for state in payload.get("states", []):
                if isinstance(state, list) and len(state) > 0:
                    icao = state[0]
                    if isinstance(icao, str) and icao.strip():
                        aircraft.add(icao)

        logger.info("Extracted %d unique aircraft ICAOs", len(aircraft))
        return aircraft

    # -----------------------------
    # STEP 2: Fetch metadata
    # -----------------------------
    def fetch_aircraft_metadata(self, icao_hex: str) -> Optional[Dict]:
        try:
            url = f"{config.adsbdb.base_url}/aircraft/{icao_hex}"
            response = self.session.get(url, timeout=config.adsbdb.timeout)
            response.raise_for_status()

            data = response.json()
            data["icao24"] = icao_hex
            data["metadata_fetched_at"] = datetime.now(UTC).isoformat()
            data["source"] = "adsbdb"

            time.sleep(config.adsbdb.rate_limit_delay)
            return data

        except requests.RequestException as e:
            logger.warning("Metadata fetch failed for %s: %s", icao_hex, e)
            return None

    # -----------------------------
    # STEP 3: Persist metadata
    # -----------------------------
    def save_metadata(self, records: List[Dict]) -> None:
        if not records:
            logger.info("No metadata records to save")
            return

        df = pd.DataFrame(records)
        now = datetime.now(UTC)

        output_dir = (
            Path(config.storage.bronze_metadata_path)
            / f"{now.year}"
            / f"{now.month:02d}"
            / f"{now.day:02d}"
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"metadata_{now:%Y%m%d_%H%M%S}.parquet"
        df.to_parquet(output_file, index=False)

        logger.info("Saved %d metadata records → %s", len(df), output_file)

    # -----------------------------
    # STEP 4: Orchestrate batch
    # -----------------------------
    def run_daily_batch(self) -> None:
        end = datetime.now(UTC)
        start = end - timedelta(hours=24)


        aircraft = self.extract_unique_aircraft_from_raw(start, end)
        records: List[Dict] = []

        for icao in aircraft:
            if icao in self.processed_icao:
                continue

            metadata = self.fetch_aircraft_metadata(icao)
            if metadata:
                records.append(metadata)
                self.processed_icao.add(icao)

        self.save_metadata(records)

        logger.info("Metadata batch completed cleanly")


if __name__ == "__main__":
    ADSBDBMetadataIngester().run_daily_batch()
