from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- Cities ----------
class CityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Cairo"])
    country: str = Field(min_length=1, max_length=100, examples=["Egypt"])
    latitude: float = Field(ge=-90, le=90, examples=[30.0444])
    longitude: float = Field(ge=-180, le=180, examples=[31.2357])


class CityOut(CityCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Readings ----------
class ReadingCreate(BaseModel):
    city_id: int
    temperature_c: float = Field(ge=-90, le=70, description="Air temperature in °C")
    humidity: float | None = Field(default=None, ge=0, le=100, description="Relative humidity %")
    recorded_at: datetime


class ReadingOut(ReadingCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Aggregates ----------
class CityStats(BaseModel):
    city_id: int
    city_name: str
    count: int
    min_c: float | None
    max_c: float | None
    avg_c: float | None
    start: datetime | None
    end: datetime | None


class LatestReading(BaseModel):
    """One point on the map: a city and its most recent reading."""

    city_id: int
    city_name: str
    country: str
    latitude: float
    longitude: float
    temperature_c: float
    humidity: float | None
    recorded_at: datetime
