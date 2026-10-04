"""
Self-check for POST /api/v1/weather/sync-bmkg and GET /api/v1/model-metrics.

sync-bmkg used to fabricate weather data with random.uniform() and persist it into
weather_daily_logs labeled as a live BMKG/Open-Meteo sync. This test locks in that it
now calls Open-Meteo for real and only ever writes the values the API actually returned
(mocked here so the test doesn't depend on network access or real-world weather).
"""
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models_db import WeatherDailyLog

client = TestClient(app)


def _fake_open_meteo_response(rain=7.5, temp=31.2, wind=11.4):
    fake = MagicMock()
    fake.raise_for_status = lambda: None
    fake.json.return_value = {
        "daily": {
            "time": ["2026-09-01"],
            "precipitation_sum": [rain],
            "temperature_2m_max": [temp],
            "wind_speed_10m_max": [wind],
        }
    }
    return fake


def test_sync_bmkg_writes_exactly_the_api_response_no_randomness():
    with patch("requests.get", return_value=_fake_open_meteo_response(rain=7.5, temp=31.2, wind=11.4)) as mocked_get:
        response = client.post("/api/v1/weather/sync-bmkg")

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "OPEN_METEO_FORECAST_API"
    assert data["data"] == [{
        "date": "2026-09-01",
        "curah_hujan_mm": 7.5,
        "temp_max_c": 31.2,
        "kecepatan_angin_kmh": 11.4,
        "source": "OPEN_METEO_FORECAST_API",
    }]
    mocked_get.assert_called_once()

    # Persisted row matches the mocked API response exactly — no random.uniform() substitute.
    db = SessionLocal()
    try:
        import datetime
        row = db.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == datetime.date(2026, 9, 1)).first()
        assert row is not None
        assert row.curah_hujan_mm == 7.5
        assert row.temp_max_c == 31.2
        assert row.kecepatan_angin_kmh == 11.4
    finally:
        db.close()


def test_sync_bmkg_upstream_failure_returns_502_not_fabricated_data():
    with patch("requests.get", side_effect=ConnectionError("network down")):
        response = client.post("/api/v1/weather/sync-bmkg")

    assert response.status_code == 502


def test_model_metrics_endpoint_returns_real_training_metadata():
    response = client.get("/api/v1/model-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data["xgboost"]
    assert "final_full_r2" in data["xgboost"]["metrics"]


if __name__ == "__main__":
    test_sync_bmkg_writes_exactly_the_api_response_no_randomness()
    test_sync_bmkg_upstream_failure_returns_502_not_fabricated_data()
    test_model_metrics_endpoint_returns_real_training_metadata()
    print("OK: weather sync + model metrics self-checks passed")
