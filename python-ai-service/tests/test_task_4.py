import os
import sys
import json
# Adjust import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
from database import SessionLocal
from services.autoencoder import autoencoder_service, AE_MODEL_PATH, AE_METADATA_PATH
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_autoencoder_training_and_serialization():
    db = SessionLocal()
    try:
        metadata = autoencoder_service.train(db)
        
        # Verify model files exist
        assert os.path.exists(AE_MODEL_PATH), "PyTorch pth file must exist"
        assert os.path.exists(AE_METADATA_PATH), "Autoencoder metadata json file must exist"
        
        # Verify training sample count is positive
        assert metadata["training_sample_count"] > 0
        assert metadata["global_threshold"] > 0.0
        
        # Verify evaluation metrics
        eval_metrics = metadata["evaluation"]
        print(f"\nAutoencoder Results: Precision = {eval_metrics['precision']:.4f}, Recall = {eval_metrics['recall']:.4f}")
        assert eval_metrics["precision"] >= 0.80, f"Precision should be >= 0.80, got {eval_metrics['precision']}"
        assert eval_metrics["recall"] >= 0.80, f"Recall should be >= 0.80, got {eval_metrics['recall']}"
    finally:
        db.close()

def test_autoencoder_anomaly_detection_logic():
    db = SessionLocal()
    try:
        test_records = [
            # Record Normal
            {
                "Date": "2026-08-05",
                "Unit": "HD785-7",
                "Activity": "HAULING",
                "FC_Actual": 75.0,
                "Unit_Fuel_L_Day": 1500.0,
                "Unit_FR": 0.26,
                "Rain_mm": 0.0
            },
            # Record Spike (Fuel consumption 2x normal)
            {
                "Date": "2026-08-05",
                "Unit": "HD785-7MUD",
                "Activity": "HAULING",
                "FC_Actual": 165.0,  # Lonjakan BBM 2.2x normal!
                "Unit_Fuel_L_Day": 3300.0,
                "Unit_FR": 0.58,
                "Rain_mm": 0.0
            }
        ]
        
        res = autoencoder_service.detect_anomalies_for_records(test_records, db_session=db)
        
        assert res["total_records_scanned"] == 2
        assert len(res["spike_report_per_unit"]) > 0
        assert len(res["detail_report_per_activity"]) > 0
        
        # HD785-7MUD (spike) must be detected as an anomaly
        spikes = res["spikes"]
        spike_units = [s["unit"] for s in spikes]
        assert "HD785-7MUD" in spike_units, "HD785-7MUD dengan lonjakan BBM 2.2x harus terdeteksi sebagai spike"
    finally:
        db.close()

def test_fastapi_anomaly_detect_endpoint():
    payload = {
        "records": [
            {
                "Date": "2026-08-05",
                "Unit": "EX2600-6",
                "Activity": "LOADING",
                "FC_Actual": 190.0,
                "Unit_Fuel_L_Day": 3800.0,
                "Unit_FR": 0.155,
                "Rain_mm": 0.0
            },
            {
                "Date": "2026-08-05",
                "Unit": "EX2600-SPIKE",
                "Activity": "LOADING",
                "FC_Actual": 390.0,  # Spike lonjakan 2x!
                "Unit_Fuel_L_Day": 7800.0,
                "Unit_FR": 0.320,
                "Rain_mm": 0.0
            }
        ]
    }
    
    response = client.post("/api/v1/anomaly-detect", json=payload)
    assert response.status_code == 200, f"Endpoint /api/v1/anomaly-detect returned {response.status_code}"
    
    data = response.json()
    assert "total_records_scanned" in data
    assert "total_spikes_detected" in data
    assert "spike_report_per_unit" in data
    assert data["total_records_scanned"] == 2
    assert data["total_spikes_detected"] >= 1

if __name__ == "__main__":
    test_autoencoder_training_and_serialization()
    test_autoencoder_anomaly_detection_logic()
    test_fastapi_anomaly_detect_endpoint()
    print(" [OK] SELURUH PYTEST TASK 4 PASSED 100%!")
