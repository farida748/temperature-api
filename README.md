# 🌡️ Temperature API

A REST API for storing and querying city temperature readings, with a live map dashboard.

Built with **FastAPI**, **SQLAlchemy 2.0** and **Pydantic**, tested with **pytest**, containerized with **Docker**, and checked on every push with **GitHub Actions**.

![Tests](https://github.com/farida748/temperature-api/actions/workflows/tests.yml/badge.svg)

## Features

- **REST endpoints** for cities, readings and aggregate statistics
- **Time-range filtering and pagination** on readings
- **Input validation** with Pydantic (coordinates, realistic temperature and humidity ranges)
- **API key authentication** on write endpoints (`X-API-Key` header); reads stay public
- **Map dashboard** built with Leaflet and Chart.js: every city colored by its latest temperature, click for a 48-hour chart and min/avg/max
- **Single-query aggregations** (latest reading per city without N+1 queries) and a composite index on `(city_id, recorded_at)`
- **CORS** configured so a separate frontend (e.g. Angular on `localhost:4200`) can call the API
- **16 automated tests** running against an isolated in-memory database
- **Docker image** running as a non-root user
- **CI pipeline** that runs the tests and builds the image

## API

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | – | Health check |
| GET | `/cities` | – | List all cities |
| GET | `/cities/{id}` | – | One city |
| POST | `/cities` | 🔑 | Add a city |
| GET | `/cities/{id}/readings?start=&end=&limit=&offset=` | – | Readings, newest first |
| GET | `/cities/{id}/stats?start=&end=` | – | Min, max, average temperature |
| POST | `/readings` | 🔑 | Record a reading |
| GET | `/map/latest` | – | Latest reading per city, with coordinates |

Interactive documentation is generated automatically at **`/docs`** (Swagger UI).

### Example

```bash
# Read
curl "http://localhost:8000/cities/1/stats?start=2026-11-01T00:00:00"

# Write (needs the API key)
curl -X POST http://localhost:8000/readings \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"city_id": 1, "temperature_c": 31.4, "humidity": 40, "recorded_at": "2026-11-05T14:00:00"}'
```

## Run it

### With Python

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000 for the map and http://localhost:8000/docs for the API.

### With Docker

```bash
docker build -t temperature-api .
docker run -p 8000:8000 -e API_KEY=my-secret temperature-api
```

### Tests

```bash
pytest -v
```

## Project structure

```
app/
├── main.py          # App setup, CORS, startup, routes
├── config.py        # Settings from environment variables
├── database.py      # Engine, session and get_db dependency
├── models.py        # SQLAlchemy tables
├── schemas.py       # Pydantic request/response models
├── crud.py          # Database queries
├── security.py      # API key dependency
├── seed.py          # Sample data
├── routers/
│   ├── cities.py
│   └── readings.py
└── static/
    └── index.html   # Map dashboard
tests/
├── conftest.py      # Test client with an in-memory database
└── test_api.py
```

## Configuration

Copy `.env.example` to `.env` and change what you need:

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./temperature.db` | Any SQLAlchemy URL, e.g. PostgreSQL |
| `API_KEY` | `dev-secret-key` | Key required for write endpoints |
| `SEED_ON_STARTUP` | `true` | Fill an empty database with sample data |

## Note on the data

The sample readings are **synthetic**: a daily temperature curve around each city's typical value with small random noise. They exist to demonstrate the API and dashboard, not to describe real weather.

## Possible next steps

- Ingest real data from a public weather API on a schedule
- Move to PostgreSQL with Alembic migrations
- Rewrite the dashboard as an Angular app with Angular Material

---

Built by [Farida Saad](https://www.linkedin.com/in/farida-saad-17b5162b1)
