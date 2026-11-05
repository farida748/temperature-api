from datetime import datetime, timedelta


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


# ---------- Cities ----------
def test_list_cities_returns_seeded_data(client):
    res = client.get("/cities")
    assert res.status_code == 200
    names = [c["name"] for c in res.json()]
    assert "Cairo" in names
    assert names == sorted(names)


def test_get_city_not_found(client):
    res = client.get("/cities/9999")
    assert res.status_code == 404


def test_create_city_requires_api_key(client):
    body = {"name": "Luxor", "country": "Egypt", "latitude": 25.69, "longitude": 32.64}
    assert client.post("/cities", json=body).status_code == 401
    assert client.post("/cities", json=body, headers={"X-API-Key": "wrong"}).status_code == 401


def test_create_city(client, auth):
    body = {"name": "Luxor", "country": "Egypt", "latitude": 25.69, "longitude": 32.64}
    res = client.post("/cities", json=body, headers=auth)
    assert res.status_code == 201
    assert res.json()["id"] > 0


def test_create_duplicate_city_conflicts(client, auth):
    body = {"name": "cairo", "country": "Egypt", "latitude": 30, "longitude": 31}
    assert client.post("/cities", json=body, headers=auth).status_code == 409


def test_create_city_validates_coordinates(client, auth):
    body = {"name": "Nowhere", "country": "X", "latitude": 200, "longitude": 31}
    assert client.post("/cities", json=body, headers=auth).status_code == 422


# ---------- Readings ----------
def test_readings_are_newest_first_and_paginated(client):
    res = client.get("/cities/1/readings", params={"limit": 5})
    data = res.json()
    assert res.status_code == 200
    assert len(data) == 5
    times = [r["recorded_at"] for r in data]
    assert times == sorted(times, reverse=True)


def test_readings_time_range_filter(client):
    end = datetime.now()
    start = end - timedelta(hours=6)
    res = client.get(
        "/cities/1/readings", params={"start": start.isoformat(), "end": end.isoformat()}
    )
    assert res.status_code == 200
    for r in res.json():
        assert start <= datetime.fromisoformat(r["recorded_at"]) <= end


def test_readings_rejects_inverted_range(client):
    res = client.get(
        "/cities/1/readings", params={"start": "2026-01-02T00:00", "end": "2026-01-01T00:00"}
    )
    assert res.status_code == 400


def test_create_reading(client, auth):
    body = {"city_id": 1, "temperature_c": 41.5, "humidity": 12, "recorded_at": "2030-07-01T14:00:00"}
    res = client.post("/readings", json=body, headers=auth)
    assert res.status_code == 201

    # It should now be the latest reading for that city on the map.
    latest = {c["city_id"]: c for c in client.get("/map/latest").json()}
    assert latest[1]["temperature_c"] == 41.5


def test_create_reading_unknown_city(client, auth):
    body = {"city_id": 9999, "temperature_c": 20, "recorded_at": "2030-01-01T00:00:00"}
    assert client.post("/readings", json=body, headers=auth).status_code == 404


def test_create_reading_rejects_impossible_temperature(client, auth):
    body = {"city_id": 1, "temperature_c": 500, "recorded_at": "2030-01-01T00:00:00"}
    assert client.post("/readings", json=body, headers=auth).status_code == 422


# ---------- Aggregates ----------
def test_stats(client):
    stats = client.get("/cities/1/stats").json()
    assert stats["count"] == 48  # 2 days x 24 hours from the test seed
    assert stats["min_c"] <= stats["avg_c"] <= stats["max_c"]


def test_map_latest_has_one_row_per_city(client):
    cities = client.get("/cities").json()
    latest = client.get("/map/latest").json()
    assert len(latest) == len(cities)
    assert all({"latitude", "longitude", "temperature_c"} <= row.keys() for row in latest)


def test_dashboard_is_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "Temperature Dashboard" in res.text
