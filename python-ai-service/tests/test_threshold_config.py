"""
Self-check for GET/PUT /api/v1/threshold-config and its effect on forecasting_service.

Locks in: (1) defaults match the constants forecasting.py used to hardcode, so this change
is behavior-preserving until someone edits the config; (2) an edit actually changes what
/api/v1/forecast returns; (3) the config is restored so it doesn't leak into other tests.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

FORECAST_PAYLOAD = {
    "date": "2026-08-05",
    "curah_hujan_mm": 0.0,
    "temp_max_c": 32.0,
    "kecepatan_angin_kmh": 12.0,
    "haul_distance_m": 3900.0,
    "daily_prod_bcm": 40000.0,
}


def test_threshold_config_defaults_match_legacy_constants():
    response = client.get("/api/v1/threshold-config")
    assert response.status_code == 200
    data = response.json()
    assert data["budget_baseline"] == 1.018
    assert data["warning_pct"] == 8.0
    assert data["critical_pct"] == 18.0


def test_updating_threshold_config_changes_live_forecast_thresholds():
    original = client.get("/api/v1/threshold-config").json()
    try:
        put_resp = client.put("/api/v1/threshold-config", json={"warning_pct": 20.0})
        assert put_resp.status_code == 200
        assert put_resp.json()["warning_pct"] == 20.0

        forecast = client.post("/api/v1/forecast", json=FORECAST_PAYLOAD).json()
        expected_warning = round(original["budget_baseline"] * 1.20, 4)
        assert forecast["warning_threshold"] == expected_warning
    finally:
        # Restore so other tests (and manual runs after this one) see the original config.
        client.put("/api/v1/threshold-config", json={
            "budget_baseline": original["budget_baseline"],
            "warning_pct": original["warning_pct"],
            "critical_pct": original["critical_pct"],
        })


if __name__ == "__main__":
    test_threshold_config_defaults_match_legacy_constants()
    test_updating_threshold_config_changes_live_forecast_thresholds()
    print("OK: threshold-config self-checks passed")
