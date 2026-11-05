from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import cities, readings
from app.seed import seed

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup: create tables and add demo data.
    Base.metadata.create_all(engine)
    if settings.seed_on_startup:
        with SessionLocal() as db:
            seed(db)
    yield


app = FastAPI(
    title="Temperature API",
    description="Store and query city temperature readings, with a live map dashboard.",
    version="1.0.0",
    lifespan=lifespan,
)

# Lets a separate frontend (e.g. an Angular app on localhost:4200) call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cities.router)
app.include_router(readings.router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def dashboard():
    """Serves the map dashboard."""
    return FileResponse(STATIC_DIR / "index.html")
