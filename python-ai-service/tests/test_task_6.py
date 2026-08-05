import os
import sys
import time
# Adjust import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.warmup import warmup_service
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_warmup_service_execution():
    details = warmup_service.perform_warmup()
    assert details["status"] == "ready"
    assert details["xgboost_warmed_up"] is True
    assert details["pytorch_autoencoder_warmed_up"] is True
    assert details["warmup_duration_ms"] > 0
    print(f"\nWarmup completed in {details['warmup_duration_ms']:.2f} ms")

def test_readiness_probe_endpoint():
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "warmup_details" in data

def test_api_latency_benchmarks_under_2_seconds():
    # Benchmark 1: Forecast Endpoint
    start_fc = time.time()
    res_fc = client.post("/api/v1/forecast", json={
        "date": "2026-08-05",
        "curah_hujan_mm": 5.0,
        "temp_max_c": 32.0,
        "kecepatan_angin_kmh": 12.0,
        "haul_distance_m": 3900.0,
        "daily_prod_bcm": 40000.0
    })
    latency_fc_ms = (time.time() - start_fc) * 1000.0
    assert res_fc.status_code == 200
    assert latency_fc_ms < 2000.0, f"Forecast API latency should be < 2000ms, got {latency_fc_ms:.2f}ms"
    
    # Benchmark 2: Anomaly Detection Endpoint
    start_ad = time.time()
    res_ad = client.post("/api/v1/anomaly-detect", json={
        "records": [
            {
                "Date": "2026-08-05",
                "Unit": "HD785-7",
                "Activity": "HAULING",
                "FC_Actual": 75.0,
                "Unit_Fuel_L_Day": 1500.0,
                "Unit_FR": 0.26,
                "Rain_mm": 5.0
            }
        ]
    })
    latency_ad_ms = (time.time() - start_ad) * 1000.0
    assert res_ad.status_code == 200
    assert latency_ad_ms < 2000.0, f"Anomaly Detect API latency should be < 2000ms, got {latency_ad_ms:.2f}ms"
    
    # Benchmark 3: Capacity Determination Endpoint
    start_cap = time.time()
    res_cap = client.post("/api/v1/calculate-capacity", json={
        "date": "2026-08-05",
        "forecast_prod_bcm": 40000.0,
        "curah_hujan_mm": 5.0
    })
    latency_cap_ms = (time.time() - start_cap) * 1000.0
    assert res_cap.status_code == 200
    assert latency_cap_ms < 2000.0, f"Capacity API latency should be < 2000ms, got {latency_cap_ms:.2f}ms"
    
    print(f"Latency Benchmarks: Forecast = {latency_fc_ms:.2f}ms | Anomaly = {latency_ad_ms:.2f}ms | Capacity = {latency_cap_ms:.2f}ms")

if __name__ == "__main__":
    test_warmup_service_execution()
    test_readiness_probe_endpoint()
    test_api_latency_benchmarks_under_2_seconds()
    print(" [OK] SELURUH PYTEST TASK 6 PASSED 100%!")
