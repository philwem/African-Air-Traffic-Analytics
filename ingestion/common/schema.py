# ingestion/common/schema.py
from pydantic import BaseModel, Field


class PositionSchema(BaseModel):
    """
    Canonical schema for a raw ADS-B position record.
    """
    icao24: str = Field(..., description="Unique aircraft identifier")
    callsign: str | None = Field(None, description="Aircraft callsign")
    origin_country: str = Field(...,
                                description="Country of aircraft registration")
    time_position: int | None = Field(
        None, description="Unix timestamp of position")
    last_contact: int = Field(...,
                              description="Unix timestamp of last contact")
    longitude: float | None = Field(None, description="Longitude in degrees")
    latitude: float | None = Field(None, description="Latitude in degrees")
    baro_altitude: float | None = Field(
        None, description="Barometric altitude in meters")
    on_ground: bool = Field(..., description="True if aircraft is on ground")
    velocity: float | None = Field(None, description="Velocity in m/s")
    true_track: float | None = Field(
        None, description="True track / heading in degrees")
    vertical_rate: float | None = Field(
        None, description="Vertical speed in m/s")
    sensors: list[int] | None = Field(
        None, description="Optional sensor IDs that reported this")
