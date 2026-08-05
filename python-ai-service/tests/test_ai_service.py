import os
import sys
import time
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, check_db_connection
from models_db import (
    EquipmentCatalog, LoadingUnitBaseline, HaulingUnitBaseline,
    WeatherDailyLog, DailyForecastLog, UnitAnomalySpike, CapacityAllocation
)
from pipelines.data_pipeline import (
    load_historical_weather_and_forecasts,
    fetch_and_prepare_dataset,
    load_unit_anomaly_logs,
    validate_and_clean_data
)
from pipelines.feature_engineering import build_features, get_feature_names, FEATURE_COLUMNS
from pipelines.train_xgboost import train_xgboost_model, MODELS_DIR
from services.forecasting import forecasting_service, BASE_TOTAL_FR_BUDGET
from services.autoencoder import autoencoder_service, AE_FEATURE_COLUMNS
from services.capacity_engine import capacity_engine, calculate_rain_derating_non_linear
from services.warmup import warmup_service

# ==============================================================================
# 1. DATABASE & DATA PIPELINE TESTS
# ==============================================================================

def test_database_connection_and_seeding(db_session):
    conn_info = check_db_connection()
    assert conn_info["status"] == "connected"
    
    # Check equipment catalogs count
    eq_count = db_session.query(EquipmentCatalog).count()
    assert eq_count >= 19, f"Expected at least 19 equipment catalogs, got {eq_count}"

    # Check weather logs count (ground-truth dataset contains 364 daily rows)
    weather_count = db_session.query(WeatherDailyLog).count()
    assert weather_count >= 360, f"Expected at least 360 weather logs, got {weather_count}"

def test_data_pipeline_and_13_feature_engineering(db_session):
    df_clean, df_features, feature_names = fetch_and_prepare_dataset(db_session)
    
    assert not df_clean.empty
    assert not df_features.empty
    assert len(feature_names) == 13
    
    # Solusi Celah #13: Fitur Kecepatan_Angin_kmh wajib ada
    assert 'Kecepatan_Angin_kmh' in feature_names
    assert 'Kecepatan_Angin_kmh' in df_features.columns
    
    for col in FEATURE_COLUMNS:
        assert col in df_features.columns

# ==============================================================================
# 2. XGBOOST FORECASTING ENGINE TESTS (TIMESERIES SPLIT CV)
# ==============================================================================

def test_xgboost_training_and_timeseries_cv(db_session):
    metadata = train_xgboost_model(db_session)
    
    assert os.path.exists(os.path.join(MODELS_DIR, "xgboost_fr_v1.pkl"))
    assert os.path.exists(os.path.join(MODELS_DIR, "scaler_v1.pkl"))
    assert os.path.exists(os.path.join(MODELS_DIR, "metadata.json"))
    
    metrics = metadata["metrics"]
    assert metrics["avg_cv_r2"] >= 0.80, f"Average CV R2 score must be >= 0.80, got {metrics['avg_cv_r2']}"
    assert metrics["final_full_r2"] >= 0.80, f"Final R2 score must be >= 0.80, got {metrics['final_full_r2']}"
    assert metrics["avg_cv_mae"] < 0.05, f"Average CV MAE must be < 0.05, got {metrics['avg_cv_mae']}"

def test_forecasting_service_dynamic_thresholds(db_session):
    # Test normal day
    res = forecasting_service.forecast_single_day(
        date_str="2026-08-05",
        curah_hujan_mm=0.0,
        temp_max_c=32.0,
        kecepatan_angin_kmh=12.0,
        haul_distance_m=3900.0,
        daily_prod_bcm=40000.0,
        db_session=db_session
    )
    
    assert res["forecast_fr"] > 0
    assert res["status"] in ["NORMAL", "WARNING", "CRITICAL"]
    assert res["warning_threshold"] == round(BASE_TOTAL_FR_BUDGET * 1.08, 4)
    assert res["critical_threshold"] == round(BASE_TOTAL_FR_BUDGET * 1.18, 4)

# ==============================================================================
# 3. PYTORCH AUTOENCODER ANOMALY DETECTOR TESTS
# ==============================================================================

def test_pytorch_autoencoder_training_on_normal_data(db_session):
    metadata = autoencoder_service.train(db_session)
    
    assert os.path.exists(os.path.join(MODELS_DIR, "autoencoder_spikes_v1.pth"))
    assert metadata["training_sample_count"] > 0
    
    eval_metrics = metadata["evaluation"]
    assert eval_metrics["precision"] >= 0.80, f"Precision must be >= 0.80, got {eval_metrics['precision']}"
    assert eval_metrics["recall"] >= 0.80, f"Recall must be >= 0.80, got {eval_metrics['recall']}"

def test_autoencoder_spike_isolation(db_session):
    records = [
        {"Date": "2026-08-05", "Unit": "HD785-7", "Activity": "HAULING", "FC_Actual": 75.0, "Unit_Fuel_L_Day": 1500.0, "Unit_FR": 0.26, "Rain_mm": 0.0},
        {"Date": "2026-08-05", "Unit": "HD785-SPIKE", "Activity": "HAULING", "FC_Actual": 165.0, "Unit_Fuel_L_Day": 3300.0, "Unit_FR": 0.58, "Rain_mm": 0.0}
    ]
    
    res = autoencoder_service.detect_anomalies_for_records(records, db_session=db_session)
    assert res["total_records_scanned"] == 2
    assert len(res["spikes"]) >= 1
    spikes_units = [s["unit"] for s in res["spikes"]]
    assert "HD785-SPIKE" in spikes_units

# ==============================================================================
# 4. COMBINED CAPACITY ENGINE TESTS (NON-LINEAR DERATING)
# ==============================================================================

def test_non_linear_rain_derating():
    assert calculate_rain_derating_non_linear(0.0) == 1.0
    assert calculate_rain_derating_non_linear(5.0) == 1.0
    assert calculate_rain_derating_non_linear(15.0) < 1.0
    assert calculate_rain_derating_non_linear(35.0) < 0.85
    assert calculate_rain_derating_non_linear(60.0) == 0.60

def test_capacity_engine_fleet_allocation(db_session):
    res = capacity_engine.calculate_fleet_capacity(
        date_str="2026-08-05",
        forecast_prod_bcm=40000.0,
        curah_hujan_mm=10.0,
        nn_spike_count_by_unit={"HD785-SPIKE": 1},
        db_session=db_session
    )
    
    assert res["installed_prod_bcmhr"] > 0
    assert res["effective_prod_bcmday"] > 0
    assert res["utilization_pct"] > 0
    assert res["operating_units"] > 0
    assert res["total_combined_fuel_lday"] > 0
    assert len(res["activity_breakdown"]) >= 3

# ==============================================================================
# 5. REST API ENDPOINTS & WARM-UP TESTS
# ==============================================================================

def test_model_warmup_and_readiness(api_client):
    warmup_res = warmup_service.perform_warmup()
    assert warmup_res["status"] == "ready"
    assert warmup_res["xgboost_warmed_up"] is True
    assert warmup_res["pytorch_autoencoder_warmed_up"] is True
    
    res = api_client.get("/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"

def test_api_endpoints_integration_and_latency(api_client):
    # Forecast API
    t0 = time.time()
    res_fc = api_client.post("/api/v1/forecast", json={
        "date": "2026-08-05", "curah_hujan_mm": 5.0, "temp_max_c": 32.0,
        "kecepatan_angin_kmh": 12.0, "haul_distance_m": 3900.0, "daily_prod_bcm": 40000.0
    })
    lat_fc = (time.time() - t0) * 1000
    assert res_fc.status_code == 200
    assert lat_fc < 2000.0
    
    # 7-Day Horizon Forecast API
    t0_7d = time.time()
    res_fc7 = api_client.post("/api/v1/forecast-7days", json={"start_date": "2026-08-05"})
    lat_fc7 = (time.time() - t0_7d) * 1000
    assert res_fc7.status_code == 200
    assert len(res_fc7.json()["daily_forecasts"]) == 7
    assert lat_fc7 < 3000.0
    
    # Anomaly API
    t1 = time.time()
    res_an = api_client.post("/api/v1/anomaly-detect", json={
        "records": [
            {"Date": "2026-08-05", "Unit": "HD785-7", "Activity": "HAULING", "FC_Actual": 75.0, "Unit_Fuel_L_Day": 1500.0, "Unit_FR": 0.26, "Rain_mm": 5.0}
        ]
    })
    lat_an = (time.time() - t1) * 1000
    assert res_an.status_code == 200
    assert lat_an < 2000.0

    # Capacity API
    t2 = time.time()
    res_cap = api_client.post("/api/v1/calculate-capacity", json={
        "date": "2026-08-05", "forecast_prod_bcm": 40000.0, "curah_hujan_mm": 5.0
    })
    lat_cap = (time.time() - t2) * 1000
    assert res_cap.status_code == 200
    assert lat_cap < 2000.0

    print(f"\n Master Test Completed Successfully! Latencies: Forecast={lat_fc:.2f}ms, Anomaly={lat_an:.2f}ms, Capacity={lat_cap:.2f}ms")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
