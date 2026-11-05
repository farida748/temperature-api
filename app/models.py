from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    country: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    readings: Mapped[list["Reading"]] = relationship(
        back_populates="city", cascade="all, delete-orphan"
    )


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    temperature_c: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime)

    city: Mapped[City] = relationship(back_populates="readings")

    # Most queries filter by city and time range, so index both together.
    __table_args__ = (Index("ix_readings_city_time", "city_id", "recorded_at"),)
