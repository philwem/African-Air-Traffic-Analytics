# ingestion/common/geo_filter.py
"""
Geo-filtering utilities for African Air Traffic Analytics Platform
"""

from ingestion.config import DATA_DIR
from dataclasses import dataclass


@dataclass
class GeoBoundingBox:
    """West Africa bounding box"""
    min_latitude: float = 4.0      # Southern boundary
    max_latitude: float = 20.0     # Northern boundary
    min_longitude: float = -17.0   # Western boundary
    max_longitude: float = 15.0    # Eastern boundary

    def contains(self, lat: float, lon: float) -> bool:
        """Check if coordinates fall within the bounding box"""
        if lat is None or lon is None:
            return False
        return (
            self.min_latitude <= lat <= self.max_latitude and
            self.min_longitude <= lon <= self.max_longitude
        )


# Singleton instance for reuse
west_africa_bbox = GeoBoundingBox()


def filter_positions(positions: list[dict]) -> list[dict]:
    """
    Filter a list of position records to West Africa only.
    """
    return [
        pos for pos in positions
        if west_africa_bbox.contains(pos.get("latitude"), pos.get("longitude"))
    ]
