# ingestion/run_ingestion_pipeline.py
"""
Plug-and-play ingestion pipeline:
1. Phase 1: Raw ADS-B positions batch
2. Phase 2: Metadata batch ingestion
Automatically detects Phase 1 outputs and runs Phase 2.
"""

from pathlib import Path
import glob
import importlib
import sys

# ----------------- Config / Paths -----------------
try:
    from ingestion.config import config, BRONZE_POSITIONS_DIR
except ImportError:
    from config import BRONZE_POSITIONS_DIR

RAW_POSITIONS_DIR = Path(
    getattr(config.storage, "raw_positions_path", BRONZE_POSITIONS_DIR)
)

# ----------------- Phase Imports -----------------


def import_phase_module(module_name: str):
    """Dynamic import with fallback for direct execution"""
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        sys.path.append(str(Path(".").resolve()))
        return importlib.import_module(module_name)


raw_positions_batch = import_phase_module(
    "ingestion.batch.raw_positions_batch")
adsbdb_metadata_ingestion = import_phase_module(
    "ingestion.batch.adsbdb_metadata_ingestion")

# ----------------- Helpers -----------------


def phase1_needs_run() -> bool:
    """Check if Phase 1 raw positions exist in bronze folder."""
    json_files = list(RAW_POSITIONS_DIR.rglob("*.json"))
    parquet_files = list(RAW_POSITIONS_DIR.rglob("*.parquet"))
    return not (json_files or parquet_files)

# ----------------- Main Pipeline -----------------


def run_pipeline():
    print("=== Starting ADS-B ingestion pipeline ===\n")

    # Phase 1: Raw positions batch
    if phase1_needs_run():
        print("Phase 1: Raw batch ingestion (no existing data detected)")
        raw_positions_batch.run()
        print("Phase 1 completed.\n")
    else:
        print(f"Phase 1: Raw positions already exist in {RAW_POSITIONS_DIR}")
        print("Skipping Phase 1.\n")

    # Phase 2: Metadata enrichment batch
    print("Phase 2: Metadata batch ingestion")
    adsbdb_metadata_ingestion.ADSBDBMetadataIngester().run_daily_batch()
    print("Phase 2 completed.\n")

    print("=== Ingestion pipeline finished successfully ===")


# ----------------- Entrypoint -----------------
if __name__ == "__main__":
    run_pipeline()
