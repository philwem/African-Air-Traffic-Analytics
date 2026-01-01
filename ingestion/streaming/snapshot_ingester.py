"""
Hourly snapshot ingestion for ADS-B positions
"""

import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from ingestion.config import config
import logging

logger = logging.getLogger("snapshot-ingester")


class SnapshotIngester:
    def capture_snapshot(self, positions: list[dict]):
        now = datetime.utcnow()
        df = pd.DataFrame(positions)

        df["snapshot_timestamp"] = now.isoformat()
        df["ingestion_type"] = "snapshot"

        output_dir = (
            Path(config.storage.raw_positions_path)
            / f"{now.year}"
            / f"{now.month:02d}"
            / f"{now.day:02d}"
            / f"{now.hour:02d}"
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"snapshot_{now:%Y%m%d_%H%M%S}.parquet"
        df.to_parquet(output_file, index=False)

        logger.info(f"Snapshot saved → {output_file}")

    def run_hourly(self):
        while True:
            try:
                logger.info("Waiting for external stream input...")
                time.sleep(3600)
            except KeyboardInterrupt:
                break
