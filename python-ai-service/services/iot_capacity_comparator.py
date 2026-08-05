import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models_db import IoTTelemetryLog, WeatherDailyLog, EquipmentCatalog
from services.capacity_engine import calculate_rain_derating_non_linear
from operational_constants import (
    OPERATING_HOURS_PER_DAY, WARNING_THRESHOLD_PCT, CRITICAL_THRESHOLD_PCT
)

logger = logging.getLogger(__name__)

class IoTCapacityComparatorEngine:
    """
    Engine Audit Komparasi Anomali:
    Data Telemetri Mesin IoT (Flowmeter Solar, HM Jam Kerja, Payload VIMS)
    vs Kapasitas Teoritis Efektif Fleet yang Diselaraskan Cuaca Non-Linear (BMKG).
    """

    def evaluate_iot_capacity_anomalies(self, date_str: str, db_session = None) -> Dict[str, Any]:
        """
        Melakukan evaluasi komparasi data telemetri IoT mesin per unit terhadap batas toleransi kapasitas efisiensi cuaca.
        """
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            log_date = pd.to_datetime(date_str).date()

            # 1. Lookup Data Cuaca BMKG / Daily Log
            w_entry = db.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == log_date).first()
            rain_mm = float(w_entry.curah_hujan_mm) if w_entry else 0.0
            rain_derating = calculate_rain_derating_non_linear(rain_mm)

            # 2. Fetch Data Telemetri IoT Mesin Harian
            iot_records = db.query(IoTTelemetryLog).filter(IoTTelemetryLog.log_date == log_date).all()
            if not iot_records:
                # Auto-seed jika database belum terisi
                from seed_database import seed_database
                logger.info("Data IoT Telemetry di database kosong. Menjalankan auto-seeding...")
                seed_database()
                iot_records = db.query(IoTTelemetryLog).filter(IoTTelemetryLog.log_date == log_date).all()

            # 3. Lookup Equipment Catalog Specs
            catalogs = {e.unit_name: e for e in db.query(EquipmentCatalog).all()}

            audit_unit_results = []
            total_iot_fuel_consumed = 0.0
            total_weather_allowed_fuel = 0.0
            total_anomalies_count = 0

            for rec in iot_records:
                u_code = rec.unit_code
                act = rec.activity
                hm_hours = float(rec.hm_operating_hours or 0.0)
                iot_fuel = float(rec.fuel_consumed_iot_l or 0.0)
                iot_payload = float(rec.actual_payload_bcm or 0.0)

                cat_spec = catalogs.get(u_code)
                std_fc_lhr = float(cat_spec.fc_lhr) if cat_spec else 75.0
                std_prod_bcmhr = float(cat_spec.prod_bcmhr) if cat_spec else 109.56

                actual_fc_iot_lhr = iot_fuel / max(0.1, hm_hours)
                
                # Base Theoretical Fuel & Weather Adjusted Max Allowed Fuel
                base_theoretical_fuel = hm_hours * std_fc_lhr
                weather_adjusted_allowed_fuel = base_theoretical_fuel * rain_derating

                fuel_variance_l = iot_fuel - weather_adjusted_allowed_fuel
                variance_pct = (fuel_variance_l / weather_adjusted_allowed_fuel * 100.0) if weather_adjusted_allowed_fuel > 0 else 0.0

                total_iot_fuel_consumed += iot_fuel
                total_weather_allowed_fuel += weather_adjusted_allowed_fuel

                # Anomaly Status Logic
                is_iot_anomaly = False
                is_weather_slippage = False

                if variance_pct > (FR_CRITICAL_THRESHOLD_PCT * 100.0): # > 18% over
                    anomaly_status = "CRITICAL_IOT_FUEL_SPIKE"
                    is_iot_anomaly = True
                    total_anomalies_count += 1
                elif variance_pct > (FR_WARNING_THRESHOLD_PCT * 100.0): # > 8% over
                    anomaly_status = "WARNING_OVER_CONSUMPTION"
                elif variance_pct < -20.0:
                    anomaly_status = "UNDER_UTILIZED"
                else:
                    anomaly_status = "NORMAL_EFFICIENT"

                # Check Weather Slippage Anomaly (Jam kerja HM tinggi tetapi payload BCM drop saat hujan)
                if rain_derating < 0.85 and hm_hours >= 12.0 and iot_payload < (hm_hours * std_prod_bcmhr * 0.5):
                    is_weather_slippage = True
                    anomaly_status = "WEATHER_SLIPPAGE_ANOMALY"

                audit_unit_results.append({
                    "unit_code": u_code,
                    "activity": act,
                    "hm_operating_hours": round(hm_hours, 2),
                    "fuel_consumed_iot_l": round(iot_fuel, 2),
                    "actual_fc_iot_lhr": round(actual_fc_iot_lhr, 2),
                    "actual_payload_bcm": round(iot_payload, 2),
                    "std_fc_lhr": std_fc_lhr,
                    "weather_derating_factor": round(rain_derating, 4),
                    "weather_allowed_fuel_l": round(weather_adjusted_allowed_fuel, 2),
                    "variance_liters": round(fuel_variance_l, 2),
                    "variance_pct": round(variance_pct, 2),
                    "is_iot_anomaly": is_iot_anomaly,
                    "is_weather_slippage": is_weather_slippage,
                    "anomaly_status": anomaly_status
                })

            overall_net_variance_l = total_iot_fuel_consumed - total_weather_allowed_fuel
            overall_variance_pct = (overall_net_variance_l / total_weather_allowed_fuel * 100.0) if total_weather_allowed_fuel > 0 else 0.0

            return {
                "log_date": date_str,
                "weather_context": {
                    "curah_hujan_mm": rain_mm,
                    "rain_derating_factor": round(rain_derating, 4)
                },
                "fleet_iot_audit_summary": {
                    "total_units_audited": len(audit_unit_results),
                    "total_anomalies_detected": total_anomalies_count,
                    "total_iot_fuel_consumed_l": round(total_iot_fuel_consumed, 2),
                    "total_weather_allowed_fuel_l": round(total_weather_allowed_fuel, 2),
                    "net_variance_liters": round(overall_net_variance_l, 2),
                    "overall_variance_pct": round(overall_variance_pct, 2),
                    "fleet_audit_status": "NORMAL" if overall_variance_pct <= 5.0 else "OVER_CONSUMPTION_ALERT"
                },
                "unit_audit_details": audit_unit_results
            }

        finally:
            if close_db:
                db.close()

iot_capacity_comparator = IoTCapacityComparatorEngine()
