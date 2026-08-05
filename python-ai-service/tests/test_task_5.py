import os
import sys
import json
# Adjust import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import SessionLocal
from services.capacity_engine import capacity_engine, calculate_rain_derating_non_linear
from models_db import CapacityAllocation
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_non_linear_rain_derating_calculator():
    # Rain <= 5mm: Derating = 1.0
    assert calculate_rain_derating_non_linear(0.0) == 1.0
    assert calculate_rain_derating_non_linear(5.0) == 1.0
    
    # Rain 5 - 20mm: Moderat non-linear transition
    d15 = calculate_rain_derating_non_linear(15.0)
    assert 0.75 < d15 < 1.0
    
    # Rain 20 - 50mm: Significant derating
    d35 = calculate_rain_derating_non_linear(35.0)
    assert 0.65 <= d35 < 0.85
    
    # Rain > 50mm: Minimum 0.60
    assert calculate_rain_derating_non_linear(60.0) == 0.60
    print(f"\nDerating non-linear tests: 0mm -> {calculate_rain_derating_non_linear(0):.2f}, 15mm -> {d15:.2f}, 35mm -> {d35:.2f}, 60mm -> 0.60")

def test_capacity_engine_calculation_and_db_save():
    db = SessionLocal()
    try:
        res = capacity_engine.calculate_fleet_capacity(
            date_str="2026-08-05",
            forecast_prod_bcm=40000.0,
            curah_hujan_mm=12.5,
            nn_spike_count_by_unit={"HD785-7MUD": 2},
            db_session=db
        )
        
        assert res["forecast_prod_bcm"] == 40000.0
        assert res["rain_derating_factor"] < 1.0
        assert res["effective_prod_bcmday"] > 0
        assert 0 < res["utilization_pct"] <= 100.0
        assert res["operating_units"] > 0
        assert res["total_combined_fuel_lday"] > 0
        assert len(res["activity_breakdown"]) > 0
        
        # Verify saved to database
        db_entry = db.query(CapacityAllocation).filter(CapacityAllocation.log_date == pd.to_datetime("2026-08-05").date()).first()
        assert db_entry is not None, "Capacity allocation record should be saved in DB"
        assert db_entry.combined_fuel_lday == res["total_combined_fuel_lday"]
    finally:
        db.close()

def test_fastapi_calculate_capacity_endpoint():
    payload = {
        "date": "2026-08-05",
        "forecast_prod_bcm": 40000.0,
        "curah_hujan_mm": 10.0,
        "nn_spike_count_by_unit": {"HD785-7MUD": 1}
    }
    
    response = client.post("/api/v1/calculate-capacity", json=payload)
    assert response.status_code == 200, f"Endpoint /api/v1/calculate-capacity returned status {response.status_code}"
    
    data = response.json()
    assert "installed_prod_bcmhr" in data
    assert "effective_prod_bcmday" in data
    assert "utilization_pct" in data
    assert "operating_units" in data
    assert "total_combined_fuel_lday" in data
    assert "activity_breakdown" in data

if __name__ == "__main__":
    import pandas as pd
    test_non_linear_rain_derating_calculator()
    test_capacity_engine_calculation_and_db_save()
    test_fastapi_calculate_capacity_endpoint()
    print(" [OK] SELURUH PYTEST TASK 5 PASSED 100%!")
