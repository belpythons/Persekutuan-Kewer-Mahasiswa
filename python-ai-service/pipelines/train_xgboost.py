import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
import logging

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import xgboost as xgb

# Set path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from pipelines.data_pipeline import fetch_and_prepare_dataset
from pipelines.feature_engineering import FEATURE_COLUMNS

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

def train_xgboost_model(db_session=None) -> Dict[str, Any]:
    """
    Melatih model XGBoost Regressor untuk memprediksi Total Fuel Ratio (L/BCM) harian
    menggunakan TimeSeriesSplit Cross-Validation (5 folds) sesuai aturan AGENTS.md & SKILL.md.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    if db_session is None:
        db = SessionLocal()
        close_db = True
    else:
        db = db_session
        close_db = False
        
    try:
        # 1. Fetch data historis dari Database via Data Pipeline
        df_raw, df_features, feature_names = fetch_and_prepare_dataset(db)
        
        if df_raw.empty or len(df_raw) < 30:
            raise ValueError("Data historis tidak mencukupi untuk training XGBoost (minimal 30 record).")
            
        X = df_features[feature_names].values
        y = df_raw['Actual_FR_L_BCM'].values
        
        # 2. TimeSeriesSplit Cross-Validation (5 Folds - Solusi Celah #6)
        # DILARANG random 80/20 train_test_split pada data time-series!
        n_splits = 5
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        cv_results = []
        best_model = None
        best_scaler = None
        best_r2 = -float('inf')
        
        print(f"=== TRAINING XGBOOST FORECASTING ENGINE ({n_splits}-Fold TimeSeriesSplit CV) ===")
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Scaler per fold (mencegah data leakage)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            # XGBoost Regressor dengan hyperparameter terkalibrasi
            model = xgb.XGBRegressor(
                n_estimators=120,
                learning_rate=0.04,
                max_depth=4,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(
                X_train_scaled, y_train,
                eval_set=[(X_val_scaled, y_val)],
                verbose=False
            )
            
            y_pred_val = model.predict(X_val_scaled)
            
            r2 = r2_score(y_val, y_pred_val)
            mae = mean_absolute_error(y_val, y_pred_val)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
            
            cv_results.append({
                "fold": fold + 1,
                "train_size": len(train_idx),
                "val_size": len(val_idx),
                "r2": float(r2),
                "mae": float(mae),
                "rmse": float(rmse)
            })
            
            print(f"  Fold {fold+1}: R2 = {r2:.4f} | MAE = {mae:.4f} | RMSE = {rmse:.4f}")
            
            if r2 > best_r2:
                best_r2 = r2
                best_model = model
                best_scaler = scaler

        # 3. Fit Final Model pada Seluruh Dataset
        final_scaler = StandardScaler()
        X_scaled_all = final_scaler.fit_transform(X)
        
        final_model = xgb.XGBRegressor(
            n_estimators=120,
            learning_rate=0.04,
            max_depth=4,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            n_jobs=-1
        )
        final_model.fit(X_scaled_all, y)
        
        y_pred_all = final_model.predict(X_scaled_all)
        final_r2 = float(r2_score(y, y_pred_all))
        final_mae = float(mean_absolute_error(y, y_pred_all))
        final_rmse = float(np.sqrt(mean_squared_error(y, y_pred_all)))
        
        avg_cv_r2 = float(np.mean([r['r2'] for r in cv_results]))
        avg_cv_mae = float(np.mean([r['mae'] for r in cv_results]))
        
        # 4. Serialisasi Model & Metadata
        model_path = os.path.join(MODELS_DIR, "xgboost_fr_v1.pkl")
        scaler_path = os.path.join(MODELS_DIR, "scaler_v1.pkl")
        metadata_path = os.path.join(MODELS_DIR, "metadata.json")
        
        joblib.dump(final_model, model_path)
        joblib.dump(final_scaler, scaler_path)
        
        metadata = {
            "model_name": "XGBoost Fuel Ratio Forecasting Engine",
            "version": "1.0.0",
            "features_used": feature_names,
            "feature_count": len(feature_names),
            "cv_strategy": f"TimeSeriesSplit (n_splits={n_splits})",
            "metrics": {
                "avg_cv_r2": avg_cv_r2,
                "avg_cv_mae": avg_cv_mae,
                "final_full_r2": final_r2,
                "final_full_mae": final_mae,
                "final_full_rmse": final_rmse
            },
            "cv_folds_detail": cv_results
        }
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        print(f"\n [OK] Model XGBoost berhasil dilatih dan disimpan.")
        print(f"      Average CV R2: {avg_cv_r2:.4f} | Average CV MAE: {avg_cv_mae:.4f}")
        print(f"      Final Model R2: {final_r2:.4f} | Final Model MAE: {final_mae:.4f}")
        
        return metadata

    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    train_xgboost_model()
