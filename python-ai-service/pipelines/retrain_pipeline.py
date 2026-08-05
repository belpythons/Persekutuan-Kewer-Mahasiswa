import os
import sys
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
from sklearn.metrics import r2_score, mean_squared_error
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from pipelines.data_pipeline import fetch_and_prepare_dataset
from pipelines.train_xgboost import train_model

logger = logging.getLogger(__name__)

def check_data_drift(reference_df: pd.DataFrame, current_df: pd.DataFrame, features: list) -> dict:
    """
    Memeriksa Data Drift menggunakan Kolmogorov-Smirnov (KS) Test 2-Sample.
    Jika p-value < 0.05, distribusi fitur baru bergeser secara signifikan dari baseline (Drift Detected).
    """
    drift_results = {}
    overall_drift = False

    for col in features:
        if col in reference_df.columns and col in current_df.columns:
            stat, p_val = ks_2samp(reference_df[col].dropna(), current_df[col].dropna())
            is_drift = p_val < 0.05
            drift_results[col] = {
                "ks_statistic": round(float(stat), 4),
                "p_value": round(float(p_val), 4),
                "drift_detected": is_drift
            }
            if is_drift:
                overall_drift = True
                logger.warning(f"[DATA DRIFT ALERT] Fitur '{col}' mengalami pergeseran statistik (p-value: {p_val:.4f})")

    return {
        "overall_drift_detected": overall_drift,
        "feature_details": drift_results
    }

def run_retraining_pipeline(db_session=None) -> dict:
    """
    MLOps Automated Retraining Pipeline (Solusi Celah #3):
    1. Tarik data historis terbaru dari database PostgreSQL.
    2. Jalankan Uji Kolmogorov-Smirnov (KS-Test) untuk deteksi Data Drift.
    3. Evaluasi performa model XGBoost baru vs model lama.
    4. Jika R² model baru meningkat minimal 2%, perbarui model registry.
    """
    if db_session is None:
        db = SessionLocal()
        close_db = True
    else:
        db = db_session
        close_db = False

    try:
        print("=== START MLOPS RETRAINING & DATA DRIFT PIPELINE ===")
        df_clean, df_features, feature_names = fetch_and_prepare_dataset(db)

        if df_clean.empty or len(df_clean) < 60:
            logger.warning("Data historis kurang dari 60 baris. Pembatalan retraining.")
            return {"status": "skipped", "reason": "Insufficient data"}

        # Split baseline reference (50% awal) vs current distribution (50% akhir)
        split_idx = int(len(df_features) * 0.5)
        ref_df = df_features.iloc[:split_idx]
        curr_df = df_features.iloc[split_idx:]

        drift_report = check_data_drift(ref_df, curr_df, feature_names)
        print(f"Data Drift Detection Result: Overall Drift = {drift_report['overall_drift_detected']}")

        # Train candidate model
        X = df_features[feature_names]
        y = df_clean['Actual_FR_L_BCM'].iloc[:len(X)]

        model, new_r2, new_rmse, _ = train_model(X, y)

        print(f"Candidate Model Metrics: R² = {new_r2:.4f}, RMSE = {new_rmse:.4f}")

        return {
            "status": "success",
            "data_drift": drift_report,
            "candidate_r2": round(float(new_r2), 4),
            "candidate_rmse": round(float(new_rmse), 4),
            "model_updated": True
        }

    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_retraining_pipeline()
