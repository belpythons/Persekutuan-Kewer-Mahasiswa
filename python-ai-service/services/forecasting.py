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
from services.redis_cache import redis_cache_service

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "xgboost_fr_v1.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler_v1.pkl")

# Baseline Fuel Ratio Budget (L/BCM)
BASE_TOTAL_FR_BUDGET = 1.018

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
        curah_hujan_mm: Optional[float] = None,
        temp_max_c: Optional[float] = None,
        kecepatan_angin_kmh: Optional[float] = None,
        haul_distance_m: Optional[float] = None,
        daily_prod_bcm: Optional[float] = None,
        rain_lag1: Optional[float] = None,
        rain_lag2: Optional[float] = None,
        fr_lag1: Optional[float] = None,
        fr_lag2: Optional[float] = None,
        rolling_avg_fr_7d: Optional[float] = None,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Memprediksi Fuel Ratio harian berdasarkan 13 variabel input operasional.
        Jika variabel cuaca / operasional tidak dikirim (None), sistem otomatis mengambil data dari database Supabase / Redis Feature Store.
        """
        # 1. Cek Caching Hasil Inferensi di Redis
        input_payload = {
            "date_str": date_str,
            "curah_hujan_mm": curah_hujan_mm,
            "temp_max_c": temp_max_c,
            "kecepatan_angin_kmh": kecepatan_angin_kmh,
            "haul_distance_m": haul_distance_m,
            "daily_prod_bcm": daily_prod_bcm,
            "rain_lag1": rain_lag1,
            "rain_lag2": rain_lag2,
            "fr_lag1": fr_lag1,
            "fr_lag2": fr_lag2,
            "rolling_avg_fr_7d": rolling_avg_fr_7d
        }
        params_hash = redis_cache_service.generate_hash(input_payload)
        cached_forecast = redis_cache_service.get_forecast_cache(date_str, params_hash)
        if cached_forecast is not None:
            cached_forecast["cached"] = True
            return cached_forecast

        if self.model is None or self.scaler is None:
            from pipelines.train_xgboost import train_xgboost_model
            train_xgboost_model(db_session)
            self._load_model()
            
        dt = pd.to_datetime(date_str)
        cur_date = dt.date()

        # 2. Cek Redis Feature Store untuk Autoregressive Lags
        cached_lags = redis_cache_service.get_lag_features_cache(date_str)
        if cached_lags:
            if rain_lag1 is None: rain_lag1 = cached_lags.get("rain_lag1")
            if rain_lag2 is None: rain_lag2 = cached_lags.get("rain_lag2")
            if fr_lag1 is None: fr_lag1 = cached_lags.get("fr_lag1")
            if fr_lag2 is None: fr_lag2 = cached_lags.get("fr_lag2")
            if rolling_avg_fr_7d is None: rolling_avg_fr_7d = cached_lags.get("rolling_avg_fr_7d")

        # Auto-query database jika variabel atau lags masih None
        if db_session is not None:
            w_record = db_session.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == cur_date).first()
            if w_record:
                if curah_hujan_mm is None: curah_hujan_mm = float(w_record.curah_hujan_mm)
                if temp_max_c is None: temp_max_c = float(w_record.temp_max_c)
                if kecepatan_angin_kmh is None: kecepatan_angin_kmh = float(w_record.kecepatan_angin_kmh)
                
            f_record = db_session.query(DailyForecastLog).filter(DailyForecastLog.log_date == cur_date).first()
            if f_record:
                if haul_distance_m is None: haul_distance_m = float(f_record.haul_distance_m)
                if daily_prod_bcm is None: daily_prod_bcm = float(f_record.daily_prod_bcm)

            # Auto-calculate Lags dari database jika masih None
            if rain_lag1 is None:
                w1 = db_session.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == cur_date - datetime.timedelta(days=1)).first()
                rain_lag1 = float(w1.curah_hujan_mm) if w1 else 0.0
            if rain_lag2 is None:
                w2 = db_session.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == cur_date - datetime.timedelta(days=2)).first()
                rain_lag2 = float(w2.curah_hujan_mm) if w2 else 0.0

            if fr_lag1 is None:
                f1 = db_session.query(DailyForecastLog).filter(DailyForecastLog.log_date == cur_date - datetime.timedelta(days=1)).first()
                fr_lag1 = float(f1.forecast_fr if f1 else BASE_TOTAL_FR_BUDGET)
            if fr_lag2 is None:
                f2 = db_session.query(DailyForecastLog).filter(DailyForecastLog.log_date == cur_date - datetime.timedelta(days=2)).first()
                fr_lag2 = float(f2.forecast_fr if f2 else BASE_TOTAL_FR_BUDGET)

            if rolling_avg_fr_7d is None:
                f_7d = db_session.query(DailyForecastLog.forecast_fr)\
                    .filter(DailyForecastLog.log_date < cur_date)\
                    .order_by(DailyForecastLog.log_date.desc()).limit(7).all()
                if f_7d:
                    rolling_avg_fr_7d = float(np.mean([r[0] for r in f_7d if r[0] is not None]))
                else:
                    rolling_avg_fr_7d = BASE_TOTAL_FR_BUDGET

            # Simpan Lags yang dihitung ke Redis Feature Store untuk request berikutnya
            redis_cache_service.set_lag_features_cache(date_str, {
                "rain_lag1": rain_lag1,
                "rain_lag2": rain_lag2,
                "fr_lag1": fr_lag1,
                "fr_lag2": fr_lag2,
                "rolling_avg_fr_7d": rolling_avg_fr_7d
            }, ttl_seconds=86400)

        # Fallback default values jika tetap None (misal tanggal belum ada di DB)
        if curah_hujan_mm is None: curah_hujan_mm = 0.0
        if temp_max_c is None: temp_max_c = 32.0
        if kecepatan_angin_kmh is None: kecepatan_angin_kmh = 12.0
        if haul_distance_m is None: haul_distance_m = 3900.0
        if daily_prod_bcm is None: daily_prod_bcm = 40000.0
        if rain_lag1 is None: rain_lag1 = 0.0
        if rain_lag2 is None: rain_lag2 = 0.0
        if fr_lag1 is None: fr_lag1 = BASE_TOTAL_FR_BUDGET
        if fr_lag2 is None: fr_lag2 = BASE_TOTAL_FR_BUDGET
        if rolling_avg_fr_7d is None: rolling_avg_fr_7d = BASE_TOTAL_FR_BUDGET

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
        warning_threshold = BASE_TOTAL_FR_BUDGET * 1.08  # 1.0994
        critical_threshold = BASE_TOTAL_FR_BUDGET * 1.18 # 1.2012
        
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
            "features_input": feature_dict,
            "cached": False
        }
        
        # Simpan ke Redis Cache (TTL: 1 jam)
        redis_cache_service.set_forecast_cache(date_str, params_hash, result, ttl_seconds=3600)

        # Update / Insert log forecast di database
        if db_session is not None:
            self._save_forecast_to_db(db_session, result)
            
        return result

    def forecast_7days_horizon(
        self,
        start_date_str: str,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Melakukan prediksi Fuel Ratio beruntun selama 7 HARI berturut-turut (Horizon 7-Day Forecasting)
        dimulai dari start_date_str dengan memperbarui autoregressive lag variables secara ilmiah.
        """
        # Cek Cache 7-Day Horizon di Redis
        cached_7d = redis_cache_service.get_forecast_7days_cache(start_date_str)
        if cached_7d is not None:
            cached_7d["cached"] = True
            return cached_7d

        start_dt = pd.to_datetime(start_date_str)
        daily_results = []
        
        running_fr_lags = []
        running_rain_lags = []
        
        # Pull initial history for lags from DB
        if db_session is not None:
            cur_d = start_dt.date()
            f_prev = db_session.query(DailyForecastLog.forecast_fr)\
                .filter(DailyForecastLog.log_date < cur_d)\
                .order_by(DailyForecastLog.log_date.desc()).limit(7).all()
            if f_prev:
                running_fr_lags = [r[0] for r in f_prev if r[0] is not None]
            w_prev = db_session.query(WeatherDailyLog.curah_hujan_mm)\
                .filter(WeatherDailyLog.log_date < cur_d)\
                .order_by(WeatherDailyLog.log_date.desc()).limit(2).all()
            if w_prev:
                running_rain_lags = [w[0] for w in w_prev if w[0] is not None]
                
        if not running_fr_lags:
            running_fr_lags = [BASE_TOTAL_FR_BUDGET] * 7
        if not running_rain_lags:
            running_rain_lags = [0.0, 0.0]

        for step in range(7):
            cur_date_dt = start_dt + datetime.timedelta(days=step)
            cur_date_str = cur_date_dt.strftime("%Y-%m-%d")
            
            rain_l1 = running_rain_lags[0] if len(running_rain_lags) > 0 else 0.0
            rain_l2 = running_rain_lags[1] if len(running_rain_lags) > 1 else 0.0
            fr_l1 = running_fr_lags[0] if len(running_fr_lags) > 0 else BASE_TOTAL_FR_BUDGET
            fr_l2 = running_fr_lags[1] if len(running_fr_lags) > 1 else BASE_TOTAL_FR_BUDGET
            r_avg7d = float(np.mean(running_fr_lags[:7])) if running_fr_lags else BASE_TOTAL_FR_BUDGET
            
            single_res = self.forecast_single_day(
                date_str=cur_date_str,
                rain_lag1=rain_l1,
                rain_lag2=rain_l2,
                fr_lag1=fr_l1,
                fr_lag2=fr_l2,
                rolling_avg_fr_7d=r_avg7d,
                db_session=db_session
            )
            
            daily_results.append(single_res)
            
            # Update running lag lists with current step predictions
            pred_fr = single_res["forecast_fr"]
            rain_val = single_res["features_input"]["Curah_Hujan_mm"]
            
            running_fr_lags.insert(0, pred_fr)
            running_rain_lags.insert(0, rain_val)

        # Summary Metrics
        all_fr = [d["forecast_fr"] for d in daily_results]
        warning_count = sum(1 for d in daily_results if d["status"] == "WARNING")
        critical_count = sum(1 for d in daily_results if d["status"] == "CRITICAL")
        
        horizon_result = {
            "start_date": start_date_str,
            "end_date": (start_dt + datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
            "forecast_horizon_days": 7,
            "summary": {
                "avg_forecast_fr": round(float(np.mean(all_fr)), 4),
                "max_forecast_fr": round(float(np.max(all_fr)), 4),
                "min_forecast_fr": round(float(np.min(all_fr)), 4),
                "warning_alert_days": warning_count,
                "critical_alert_days": critical_count
            },
            "daily_forecasts": daily_results,
            "cached": False
        }

        # Simpan ke Redis Cache 7-Days Horizon (TTL: 1 jam)
        redis_cache_service.set_forecast_7days_cache(start_date_str, horizon_result, ttl_seconds=3600)

        return horizon_result

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
                from sqlalchemy import text
                try:
                    db.execute(text("SELECT setval('daily_forecast_logs_id_seq', (SELECT COALESCE(MAX(id), 1) FROM daily_forecast_logs));"))
                except Exception:
                    pass
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
