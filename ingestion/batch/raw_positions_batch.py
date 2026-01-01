"""
Phase 1 — Raw ADS-B Position Batch Ingestion (Bronze)

Source: OpenSky Network
Purpose: Fetch and persist unaltered aircraft state vectors
"""

import json
import logging
from datetime import datetime, UTC
from pathlib import Path
import requests

from ingestion.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("raw-positions-batch")


OPENSKY_URL = "https://opensky-network.org/api/states/all"


def fetch_raw_states() -> list[list]:
    """
    Fetch raw ADS-B state vectors from OpenSky.
    Returns a list of state arrays.
    """
    response = requests.get(OPENSKY_URL, timeout=30)
    response.raise_for_status()

    payload = response.json()

    if "states" not in payload or payload["states"] is None:
        raise ValueError("OpenSky response does not contain state vectors")

    return payload["states"]


def save_raw_states(states: list[list]) -> None:
    """
    Persist raw state vectors exactly as received (Bronze).
    """
    ingestion_time = datetime.now(UTC)
    date_path = Path(
        config.storage.raw_positions_path,
        f"{ingestion_time.year}",
        f"{ingestion_time.month:02d}",
        f"{ingestion_time.day:02d}",
    )
    date_path.mkdir(parents=True, exist_ok=True)

    output_file = date_path / f"states_{ingestion_time:%Y%m%d_%H%M%S}.json"

    record = {
        "ingestion_timestamp": ingestion_time.isoformat(),
        "source": "opensky",
        "states": states,
    }

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False)

    logger.info(
        "Saved %d raw state vectors → %s",
        len(states),
        output_file,
    )


def run() -> None:
    logger.info("Starting raw ADS-B batch ingestion (OpenSky)")
    states = fetch_raw_states()
    save_raw_states(states)
    logger.info("Raw batch ingestion completed successfully")


if __name__ == "__main__":
    run()
