import os
import sys
import json
# Adjust import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import SessionLocal
from pipelines.train_xgboost import train_xgboost_model, MODELS_DIR
from services.forecasting import forecasting_service, BASE_TOTAL_FR_BUDGET
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_xgboost_model_training_and_serialization():
    db = SessionLocal()
    try:
        metadata = train_xgboost_model(db)
        
        # Verify model output files exist
        assert os.path.exists(os.path.join(MODELS_DIR, "xgboost_fr_v1.pkl")), "Model pkl file must exist"
        assert os.path.exists(os.path.join(MODELS_DIR, "scaler_v1.pkl")), "Scaler pkl file must exist"
        assert os.path.exists(os.path.join(MODELS_DIR, "metadata.json")), "Metadata json file must exist"
        
        # Check metrics performance
        metrics = metadata["metrics"]
        print(f"\nTraining Results: Final Full R2 = {metrics['final_full_r2']:.4f}, MAE = {metrics['final_full_mae']:.4f}")
        assert metrics["final_full_r2"] >= 0.80, f"R2 score should be >= 0.80, got {metrics['final_full_r2']}"
        assert metrics["final_full_mae"] <= 0.08, f"MAE should be <= 0.08, got {metrics['final_full_mae']}"
    finally:
        db.close()

def test_forecasting_service_inference_and_thresholds():
    db = SessionLocal()
    try:
        # Test Normal Condition (No rain, normal haul distance)
        res_normal = forecasting_service.forecast_single_day(
            date_str="2026-08-05",
            curah_hujan_mm=0.0,
            temp_max_c=32.0,
            kecepatan_angin_kmh=12.0,
            haul_distance_m=3900.0,
            daily_prod_bcm=40000.0,
            db_session=db
        )
        assert res_normal["forecast_fr"] > 0, "Forecast FR must be positive"
        assert res_normal["status"] in ["NORMAL", "WARNING", "CRITICAL"]
        assert res_normal["warning_threshold"] == round(BASE_TOTAL_FR_BUDGET * 1.08, 4)
        assert res_normal["critical_threshold"] == round(BASE_TOTAL_FR_BUDGET * 1.18, 4)
        
        # Test High Rain & Long Haul Distance (Expect WARNING or CRITICAL)
        res_heavy = forecasting_service.forecast_single_day(
            date_str="2026-08-06",
            curah_hujan_mm=45.0,
            temp_max_c=30.0,
            kecepatan_angin_kmh=25.0,
            haul_distance_m=5500.0,
            daily_prod_bcm=30000.0,
            rain_lag1=20.0,
            fr_lag1=1.25,
            db_session=db
        )
        assert res_heavy["forecast_fr"] > res_normal["forecast_fr"], "Heavy rain & long haul distance should increase FR"
    finally:
        db.close()

def test_fastapi_forecast_endpoint():
    payload = {
        "date": "2026-08-05",
        "curah_hujan_mm": 10.0,
        "temp_max_c": 33.0,
        "kecepatan_angin_kmh": 14.0,
        "haul_distance_m": 4000.0,
        "daily_prod_bcm": 40000.0,
        "rain_lag1": 2.0,
        "rain_lag2": 0.0,
        "fr_lag1": 1.02,
        "fr_lag2": 1.01,
        "rolling_avg_fr_7d": 1.018
    }
    
    response = client.post("/api/v1/forecast", json=payload)
    assert response.status_code == 200, f"Endpoint /api/v1/forecast returned status {response.status_code}"
    
    data = response.json()
    assert "forecast_fr" in data
    assert "status" in data
    assert "warning_threshold" in data
    assert "critical_threshold" in data
    assert data["status"] in ["NORMAL", "WARNING", "CRITICAL"]

if __name__ == "__main__":
    test_xgboost_model_training_and_serialization()
    test_forecasting_service_inference_and_thresholds()
    test_fastapi_forecast_endpoint()
    print(" [OK] SELURUH PYTEST TASK 3 PASSED 100%!")
