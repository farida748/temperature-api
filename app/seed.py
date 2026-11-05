"""Fills an empty database with sample cities and 7 days of hourly readings.

The numbers are synthetic: a daily sine curve around each city's typical
temperature, plus small random noise. Good enough to demo the API and the map.
"""

import math
import random
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models

# name, country, lat, lon, typical daily mean °C
SAMPLE_CITIES = [
    ("Cairo", "Egypt", 30.0444, 31.2357, 24),
    ("Alexandria", "Egypt", 31.2001, 29.9187, 22),
    ("Aswan", "Egypt", 24.0889, 32.8998, 29),
    ("Shibin El Kom", "Egypt", 30.5527, 31.0091, 23),
    ("Dubai", "UAE", 25.2048, 55.2708, 30),
    ("Abu Dhabi", "UAE", 24.4539, 54.3773, 30),
    ("Riyadh", "Saudi Arabia", 24.7136, 46.6753, 28),
    ("Amman", "Jordan", 31.9454, 35.9284, 18),
]


def seed(db: Session, days: int = 7, rng_seed: int = 42) -> None:
    if db.scalar(select(models.City).limit(1)) is not None:
        return  # already seeded

    rng = random.Random(rng_seed)
    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    for name, country, lat, lon, mean in SAMPLE_CITIES:
        city = models.City(name=name, country=country, latitude=lat, longitude=lon)
        db.add(city)
        db.flush()  # gives city.id

        for h in range(days * 24):
            t = now - timedelta(hours=h)
            # coolest around 05:00, hottest around 15:00
            daily = 6 * math.sin((t.hour - 9) / 24 * 2 * math.pi)
            temp = round(mean + daily + rng.uniform(-1.5, 1.5), 1)
            humidity = round(max(5, min(95, 55 - daily * 3 + rng.uniform(-8, 8))), 1)
            db.add(
                models.Reading(
                    city_id=city.id, temperature_c=temp, humidity=humidity, recorded_at=t
                )
            )
    db.commit()


if __name__ == "__main__":
    from app.database import Base, SessionLocal, engine

    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        seed(session)
    print("Database seeded.")
