from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import require_api_key

router = APIRouter(prefix="/cities", tags=["Cities"])

DB = Annotated[Session, Depends(get_db)]


def get_city_or_404(city_id: int, db: DB):
    city = crud.get_city(db, city_id)
    if city is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"City {city_id} not found")
    return city


@router.get("", response_model=list[schemas.CityOut])
def list_cities(db: DB):
    """List all cities that have a temperature station."""
    return crud.list_cities(db)


@router.get("/{city_id}", response_model=schemas.CityOut)
def get_city(city=Depends(get_city_or_404)):
    return city


@router.post(
    "",
    response_model=schemas.CityOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_city(data: schemas.CityCreate, db: DB):
    """Add a city. Requires the `X-API-Key` header."""
    if crud.get_city_by_name(db, data.name):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="City already exists")
    return crud.create_city(db, data)


@router.get("/{city_id}/readings", response_model=list[schemas.ReadingOut])
def list_city_readings(
    db: DB,
    city=Depends(get_city_or_404),
    start: datetime | None = Query(None, description="From this time (ISO 8601)"),
    end: datetime | None = Query(None, description="Up to this time (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Readings for one city, newest first, with optional time range and pagination."""
    if start and end and start > end:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="start must be before end")
    return crud.list_readings(db, city.id, start, end, limit, offset)


@router.get("/{city_id}/stats", response_model=schemas.CityStats)
def city_stats(
    db: DB,
    city=Depends(get_city_or_404),
    start: datetime | None = None,
    end: datetime | None = None,
):
    """Min, max and average temperature for a city over a time range."""
    if start and end and start > end:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="start must be before end")
    return crud.city_stats(db, city, start, end)
