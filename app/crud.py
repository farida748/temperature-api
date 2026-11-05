"""Database queries, kept separate from the HTTP layer (like a repository in .NET)."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas


# ---------- Cities ----------
def list_cities(db: Session) -> list[models.City]:
    return list(db.scalars(select(models.City).order_by(models.City.name)))


def get_city(db: Session, city_id: int) -> models.City | None:
    return db.get(models.City, city_id)


def get_city_by_name(db: Session, name: str) -> models.City | None:
    return db.scalar(select(models.City).where(func.lower(models.City.name) == name.lower()))


def create_city(db: Session, data: schemas.CityCreate) -> models.City:
    city = models.City(**data.model_dump())
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


# ---------- Readings ----------
def list_readings(
    db: Session,
    city_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[models.Reading]:
    query = select(models.Reading).where(models.Reading.city_id == city_id)
    if start:
        query = query.where(models.Reading.recorded_at >= start)
    if end:
        query = query.where(models.Reading.recorded_at <= end)
    query = query.order_by(models.Reading.recorded_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query))


def create_reading(db: Session, data: schemas.ReadingCreate) -> models.Reading:
    reading = models.Reading(**data.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


def city_stats(
    db: Session, city: models.City, start: datetime | None, end: datetime | None
) -> schemas.CityStats:
    query = select(
        func.count(models.Reading.id),
        func.min(models.Reading.temperature_c),
        func.max(models.Reading.temperature_c),
        func.avg(models.Reading.temperature_c),
    ).where(models.Reading.city_id == city.id)
    if start:
        query = query.where(models.Reading.recorded_at >= start)
    if end:
        query = query.where(models.Reading.recorded_at <= end)

    count, min_c, max_c, avg_c = db.execute(query).one()
    return schemas.CityStats(
        city_id=city.id,
        city_name=city.name,
        count=count,
        min_c=min_c,
        max_c=max_c,
        avg_c=round(avg_c, 2) if avg_c is not None else None,
        start=start,
        end=end,
    )


def latest_per_city(db: Session) -> list[schemas.LatestReading]:
    """Most recent reading for every city, in a single query (no N+1)."""
    latest = (
        select(
            models.Reading.city_id,
            func.max(models.Reading.recorded_at).label("max_time"),
        )
        .group_by(models.Reading.city_id)
        .subquery()
    )
    query = (
        select(models.City, models.Reading)
        .join(models.Reading, models.Reading.city_id == models.City.id)
        .join(
            latest,
            (latest.c.city_id == models.Reading.city_id)
            & (latest.c.max_time == models.Reading.recorded_at),
        )
        .order_by(models.City.name)
    )
    return [
        schemas.LatestReading(
            city_id=city.id,
            city_name=city.name,
            country=city.country,
            latitude=city.latitude,
            longitude=city.longitude,
            temperature_c=reading.temperature_c,
            humidity=reading.humidity,
            recorded_at=reading.recorded_at,
        )
        for city, reading in db.execute(query)
    ]
