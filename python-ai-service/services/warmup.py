import time
import logging
from typing import Dict, Any
from services.forecasting import forecasting_service
from services.autoencoder import autoencoder_service
from database import check_db_connection

logger = logging.getLogger(__name__)

class WarmupService:
    def __init__(self):
        self.is_warmed_up = False
        self.warmup_time_ms = 0.0
        self.warmup_details = {}

    def perform_warmup(self) -> Dict[str, Any]:
        """
        Melakukan pre-loading model ML (XGBoost & PyTorch Autoencoder) ke RAM saat server booting,
        dan mengeksekusi dummy inference awal untuk mengeliminasi first-hit latency.
        """
        logger.info("=== STARTING MODEL WARM-UP & INFRASTRUCTURE PRE-LOADING ===")
        start_time = time.time()
        
        # 1. Warm-up XGBoost Forecasting Service
        forecast_start = time.time()
        if forecasting_service.model is None:
            from pipelines.train_xgboost import train_xgboost_model
            train_xgboost_model()
            forecasting_service._load_model()
            
        # Execute dummy forecast inference to warm-up CPU caches & JIT
        dummy_forecast = forecasting_service.forecast_single_day(
            date_str="2026-08-05",
            curah_hujan_mm=5.0,
            temp_max_c=32.0,
            kecepatan_angin_kmh=12.0,
            haul_distance_m=3900.0,
            daily_prod_bcm=40000.0
        )
        forecast_duration_ms = (time.time() - forecast_start) * 1000.0

        # 2. Warm-up PyTorch Autoencoder Anomaly Service
        ae_start = time.time()
        if autoencoder_service.model is None:
            autoencoder_service.train()
            autoencoder_service._load_model()
            
        # Execute dummy autoencoder scan
        dummy_scan = autoencoder_service.detect_anomalies_for_records([
            {
                "Date": "2026-08-05",
                "Unit": "HD785-7",
                "Activity": "HAULING",
                "FC_Actual": 75.0,
                "Unit_Fuel_L_Day": 1500.0,
                "Unit_FR": 0.26,
                "Rain_mm": 5.0
            }
        ])
        ae_duration_ms = (time.time() - ae_start) * 1000.0

        # 3. Check Database Connection Pool
        db_status = check_db_connection()

        total_duration_ms = (time.time() - start_time) * 1000.0
        self.is_warmed_up = True
        self.warmup_time_ms = round(total_duration_ms, 2)
        
        self.warmup_details = {
            "status": "ready" if self.is_warmed_up else "warming",
            "warmup_duration_ms": self.warmup_time_ms,
            "xgboost_warmed_up": forecasting_service.model is not None,
            "xgboost_warmup_ms": round(forecast_duration_ms, 2),
            "pytorch_autoencoder_warmed_up": autoencoder_service.model is not None,
            "pytorch_warmup_ms": round(ae_duration_ms, 2),
            "database_status": db_status.get("status", "unknown")
        }

        logger.info(f"=== MODEL WARM-UP COMPLETED IN {self.warmup_time_ms:.2f} ms ===")
        return self.warmup_details

warmup_service = WarmupService()
