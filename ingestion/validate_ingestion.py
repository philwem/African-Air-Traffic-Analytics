"""
Phase 3 — Bronze Ingestion Validation & Observability
"""

import json
import logging
from pathlib import Path
from typing import Set

import pandas as pd

from ingestion.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion-validation")


def validate_raw_positions() -> Set[str]:
    """
    Validate Bronze raw position ingestion.
    Returns set of unique ICAO24 identifiers.
    """
    raw_path = Path(config.storage.raw_positions_path)

    files = list(raw_path.rglob("*.json"))
    total_states = 0
    aircraft: Set[str] = set()

    for file in files:
        with file.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        states = payload.get("states", [])
        total_states += len(states)

        for state in states:
            if isinstance(state, list) and len(state) > 0:
                icao = state[0]
                if isinstance(icao, str) and icao.strip():
                    aircraft.add(icao)

    logger.info("RAW POSITIONS")
    logger.info("Files processed        : %d", len(files))
    logger.info("Total state vectors    : %d", total_states)
    logger.info("Unique aircraft (ICAO) : %d", len(aircraft))

    return aircraft


def validate_metadata() -> Set[str]:
    """
    Validate Bronze metadata ingestion.
    Returns set of ICAO24 identifiers with metadata.
    """
    meta_path = Path(config.storage.bronze_metadata_path)
    files = list(meta_path.rglob("*.parquet"))

    if not files:
        logger.warning("No metadata files found")
        return set()

    df = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)

    icao_col = "icao24" if "icao24" in df.columns else "icao"
    aircraft = set(df[icao_col].dropna().astype(str).unique())

    logger.info("METADATA")
    logger.info("Files processed        : %d", len(files))
    logger.info("Metadata records       : %d", len(df))
    logger.info("Unique aircraft (ICAO) : %d", len(aircraft))

    return aircraft


def validate_coverage(raw_aircraft: Set[str], meta_aircraft: Set[str]) -> None:
    """
    Validate enrichment coverage.
    """
    if not raw_aircraft:
        logger.warning("No raw aircraft found — skipping coverage check")
        return

    covered = raw_aircraft & meta_aircraft
    missing = raw_aircraft - meta_aircraft

    coverage_pct = (len(covered) / len(raw_aircraft)) * 100

    logger.info("ENRICHMENT COVERAGE")
    logger.info("Aircraft observed      : %d", len(raw_aircraft))
    logger.info("Aircraft enriched      : %d", len(covered))
    logger.info("Coverage %%             : %.2f", coverage_pct)

    if missing:
        sample = list(missing)[:10]
        logger.info("Sample missing ICAOs   : %s", ", ".join(sample))


def run() -> None:
    logger.info("Starting ingestion validation")

    raw_aircraft = validate_raw_positions()
    meta_aircraft = validate_metadata()
    validate_coverage(raw_aircraft, meta_aircraft)

    logger.info("Ingestion validation completed")


if __name__ == "__main__":
    run()
