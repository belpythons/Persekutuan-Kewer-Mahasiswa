"""
Self-check for XGBoost feature contributions (pred_contribs) returned by /api/v1/forecast.

Locks in that the contribution values are real SHAP-style additive explanations — they must
sum to the predicted forecast_fr — rather than a static/fabricated breakdown.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from pipelines.feature_engineering import FEATURE_COLUMNS

client = TestClient(app)


def test_forecast_feature_contributions_sum_to_prediction():
    response = client.post("/api/v1/forecast", json={
        "date": "2026-08-05",
        "curah_hujan_mm": 12.5,
        "temp_max_c": 33.0,
        "kecepatan_angin_kmh": 15.0,
        "haul_distance_m": 4100.0,
        "daily_prod_bcm": 42000.0,
    })
    assert response.status_code == 200
    data = response.json()

    contributions = data["feature_contributions"]
    assert contributions is not None

    # Every model feature must be present, plus the base_value (SHAP bias term).
    for col in FEATURE_COLUMNS:
        assert col in contributions
    assert "base_value" in contributions

    # Additive property: sum of all contributions (including base_value) reconstructs the
    # unrounded prediction to within XGBoost's float32 precision.
    total = sum(contributions.values())
    assert abs(total - data["forecast_fr"]) < 0.01


if __name__ == "__main__":
    test_forecast_feature_contributions_sum_to_prediction()
    print("OK: feature-contributions self-check passed")
