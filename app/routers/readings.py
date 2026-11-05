from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import require_api_key

router = APIRouter(tags=["Readings"])

DB = Annotated[Session, Depends(get_db)]


@router.post(
    "/readings",
    response_model=schemas.ReadingOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_reading(data: schemas.ReadingCreate, db: DB):
    """Record a new temperature reading. Requires the `X-API-Key` header."""
    if crud.get_city(db, data.city_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"City {data.city_id} not found")
    return crud.create_reading(db, data)


@router.get("/map/latest", response_model=list[schemas.LatestReading])
def latest_for_map(db: DB):
    """The latest reading for every city, with coordinates. Used by the map dashboard."""
    return crud.latest_per_city(db)
