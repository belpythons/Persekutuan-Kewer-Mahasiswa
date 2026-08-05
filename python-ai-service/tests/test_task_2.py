import os
import sys
# Path adjustment for module import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import SessionLocal
from pipelines.data_pipeline import fetch_and_prepare_dataset, load_historical_weather_and_forecasts, load_unit_anomaly_logs
from pipelines.feature_engineering import FEATURE_COLUMNS, build_features

def test_database_has_seeded_data():
    db = SessionLocal()
    try:
        df_raw = load_historical_weather_and_forecasts(db)
        assert not df_raw.empty, "Database historis tidak boleh kosong setelah seeding"
        assert len(df_raw) >= 365, f"Expected at least 365 days of weather/forecast logs, got {len(df_raw)}"
    finally:
        db.close()

def test_feature_engineering_13_columns():
    db = SessionLocal()
    try:
        df_clean, df_features, feature_names = fetch_and_prepare_dataset(db)
        assert not df_features.empty, "DataFrame fitur tidak boleh kosong"
        assert len(feature_names) == 13, f"Expected 13 features, got {len(feature_names)}"
        
        # Verify mandatory feature Kecepatan_Angin_kmh (Solusi Celah #13)
        assert 'Kecepatan_Angin_kmh' in feature_names, "Fitur Kecepatan_Angin_kmh wajib ada di feature columns"
        assert 'Kecepatan_Angin_kmh' in df_features.columns, "Kolom Kecepatan_Angin_kmh harus ada di DataFrame output"
        
        # Check all 13 features exist in df_features
        for col in FEATURE_COLUMNS:
            assert col in df_features.columns, f"Missing feature column: {col}"
    finally:
        db.close()

def test_unit_anomaly_logs_fetch():
    db = SessionLocal()
    try:
        df_unit_logs = load_unit_anomaly_logs(db)
        assert not df_unit_logs.empty, "Data log unit anomaly tidak boleh kosong"
        assert 'Unit' in df_unit_logs.columns
        assert 'Activity' in df_unit_logs.columns
        assert 'NN_Anomaly_Spike' in df_unit_logs.columns
    finally:
        db.close()

if __name__ == "__main__":
    test_database_has_seeded_data()
    test_feature_engineering_13_columns()
    test_unit_anomaly_logs_fetch()
    print(" [OK] SELURUH PYTEST TASK 2 PASSED 100%!")
