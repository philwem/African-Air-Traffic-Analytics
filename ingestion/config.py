"""
Configuration management for African Air Traffic Analysis Platform
Handles environment variables and application settings
"""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# ---------- PHASE 1 / MINIMAL CONFIG ----------
# These are required by raw_positions_batch.py
ADSB_API_URL = os.getenv(
    "ADSB_API_URL", "https://api.adsbdb.com/v0/aircraft/A18D58?callsign=SWA5516")
DATA_DIR = Path("./data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

BRONZE_POSITIONS_DIR = DATA_DIR / "bronze" / "positions"
BRONZE_POSITIONS_DIR.mkdir(parents=True, exist_ok=True)

# ---------- FULL DATALASS CONFIG ----------


@dataclass
class GeoBoundingBox:
    """West Africa bounding box coordinates"""
    min_latitude: float = 4.0
    max_latitude: float = 20.0
    min_longitude: float = -17.0
    max_longitude: float = 15.0

    def contains(self, lat: float, lon: float) -> bool:
        if lat is None or lon is None:
            return False
        return (
            self.min_latitude <= lat <= self.max_latitude
            and self.min_longitude <= lon <= self.max_longitude
        )


@dataclass
class ADSBDBConfig:
    base_url: str = "https://api.adsbdb.com/v0"
    timeout: int = 30
    rate_limit_delay: float = 0.5

    @property
    def headers(self) -> dict:
        return {"Accept": "application/json"}


@dataclass
class KafkaConfig:
    bootstrap_servers: str = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    filtered_topic: str = "adsb.bronze.positions"
    metadata_topic: str = "adsb.bronze.metadata"


@dataclass
class StorageConfig:
    raw_positions_path: str = str(BRONZE_POSITIONS_DIR)
    bronze_metadata_path: str = "./data/bronze/metadata"

    def __post_init__(self):
        os.makedirs(self.raw_positions_path, exist_ok=True)
        os.makedirs(self.bronze_metadata_path, exist_ok=True)


@dataclass
class FeatureFlags:
    enable_kafka: bool = False
    enable_streaming: bool = False


class Config:
    def __init__(self):
        self.geo_bbox = GeoBoundingBox()
        self.adsbdb = ADSBDBConfig()
        self.kafka = KafkaConfig()
        self.storage = StorageConfig()
        self.features = FeatureFlags()


config = Config()
