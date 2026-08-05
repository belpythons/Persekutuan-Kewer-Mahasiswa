import os
import sys
import datetime
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models_db import DailyForecastLog, WeatherDailyLog
from pipelines.feature_engineering import build_features, FEATURE_COLUMNS
from operational_constants import (
    BASE_TOTAL_FR_BUDGET,
    WARNING_THRESHOLD_PCT,
    CRITICAL_THRESHOLD_PCT
)

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "xgboost_fr_v1.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler_v1.pkl")

class ForecastingService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self._load_model()
        
    def _load_model(self):
        """
        Loads serialized XGBoost model and scaler into memory
        """
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            logger.info("XGBoost Model dan Scaler berhasil di-load ke memory.")
        else:
            logger.warning(f"File model {MODEL_PATH} belum ada. Silakan jalankan training pipeline terlebih dahulu.")

    def forecast_single_day(
        self,
        date_str: str,
        curah_hujan_mm: float,
        temp_max_c: float,
        kecepatan_angin_kmh: float,
        haul_distance_m: float,
        daily_prod_bcm: float,
        rain_lag1: float = 0.0,
        rain_lag2: float = 0.0,
        fr_lag1: float = BASE_TOTAL_FR_BUDGET,
        fr_lag2: float = BASE_TOTAL_FR_BUDGET,
        rolling_avg_fr_7d: float = BASE_TOTAL_FR_BUDGET,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Memprediksi Fuel Ratio harian berdasarkan 13 variabel input operasional dan mengevaluasi Dynamic Thresholds.
        """
        if self.model is None or self.scaler is None:
            # Auto load atau train jika belum siap
            from pipelines.train_xgboost import train_xgboost_model
            train_xgboost_model(db_session)
            self._load_model()
            
        dt = pd.to_datetime(date_str)
        day_of_week = dt.dayofweek
        month = dt.month
        is_weekend = 1 if day_of_week in [5, 6] else 0
        
        feature_dict = {
            'Curah_Hujan_mm': float(curah_hujan_mm),
            'Temp_Max_C': float(temp_max_c),
            'Kecepatan_Angin_kmh': float(kecepatan_angin_kmh),
            'Haul_Distance_m': float(haul_distance_m),
            'Daily_Prod_BCM': float(daily_prod_bcm),
            'DayOfWeek': day_of_week,
            'Month': month,
            'IsWeekend': is_weekend,
            'Rain_Lag1': float(rain_lag1),
            'Rain_Lag2': float(rain_lag2),
            'FR_Lag1': float(fr_lag1),
            'FR_Lag2': float(fr_lag2),
            'RollingAvg_FR_7d': float(rolling_avg_fr_7d)
        }
        
        # Susun dalam DataFrame dengan urutan 13 kolom yang tepat
        df_input = pd.DataFrame([feature_dict])[FEATURE_COLUMNS]
        X_scaled = self.scaler.transform(df_input.values)
        
        # Prediksi XGBoost
        forecast_fr = float(self.model.predict(X_scaled)[0])
        
        # Hitung Dynamic Thresholds (Baseline +8% dan +18%)
        warning_threshold = BASE_TOTAL_FR_BUDGET * (1.0 + WARNING_THRESHOLD_PCT)
        critical_threshold = BASE_TOTAL_FR_BUDGET * (1.0 + CRITICAL_THRESHOLD_PCT)
        
        status = "NORMAL"
        if forecast_fr >= critical_threshold:
            status = "CRITICAL"
        elif forecast_fr >= warning_threshold:
            status = "WARNING"
            
        result = {
            "log_date": date_str,
            "forecast_fr": round(forecast_fr, 4),
            "status": status,
            "warning_threshold": round(warning_threshold, 4),
            "critical_threshold": round(critical_threshold, 4),
            "daily_prod_bcm": daily_prod_bcm,
            "haul_distance_m": haul_distance_m,
            "features_input": feature_dict
        }
        
        # Update / Insert log forecast di database
        if db_session is not None:
            self._save_forecast_to_db(db_session, result)
            
        return result

    def _save_forecast_to_db(self, db, result: Dict[str, Any]):
        """
        Menyimpan atau memperbarui data log prediksi di database PostgreSQL / SQLite
        """
        try:
            log_date = pd.to_datetime(result["log_date"]).date()
            log_entry = db.query(DailyForecastLog).filter(DailyForecastLog.log_date == log_date).first()
            
            if log_entry:
                log_entry.forecast_fr = result["forecast_fr"]
                log_entry.status = result["status"]
                log_entry.warning_threshold = result["warning_threshold"]
                log_entry.critical_threshold = result["critical_threshold"]
                log_entry.daily_prod_bcm = result["daily_prod_bcm"]
                log_entry.haul_distance_m = result["haul_distance_m"]
            else:
                log_entry = DailyForecastLog(
                    log_date=log_date,
                    forecast_fr=result["forecast_fr"],
                    status=result["status"],
                    warning_threshold=result["warning_threshold"],
                    critical_threshold=result["critical_threshold"],
                    daily_prod_bcm=result["daily_prod_bcm"],
                    haul_distance_m=result["haul_distance_m"]
                )
                db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Gagal menyelaraskan forecast log ke database: {e}")

forecasting_service = ForecastingService()
