import os
import sys
import math
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models_db import (
    CapacityAllocation, EquipmentCatalog, LoadingUnitBaseline, HaulingUnitBaseline,
    WeatherDailyLog, DailyForecastLog, UnitAnomalySpike
)
from services.forecasting import forecasting_service
from services.autoencoder import autoencoder_service
from operational_constants import OPERATING_HOURS_PER_DAY, NN_SPIKE_BUFFER_PCT

logger = logging.getLogger(__name__)

def calculate_rain_derating_non_linear(rainfall_mm: float) -> float:
    """
    Menghitung faktor derating hujan non-linear sesuai formula dokumen bisnis (Solusi Celah #9).
    - Hujan <= 5 mm: 1.0 (Tidak ada derating)
    - Hujan 5 - 20 mm: Transisi non-linear (1.0 - 0.01 * (rain - 5)^1.3)
    - Hujan 20 - 50 mm: Hujan sedang (max(0.65, 0.82 - 0.005 * (rain - 20)^1.1))
    - Hujan > 50 mm: 0.60 (Kapasitas minimum operasional)
    """
    r = float(max(0.0, rainfall_mm))
    if r <= 5.0:
        return 1.0
    elif r <= 20.0:
        return float(1.0 - 0.01 * math.pow(r - 5.0, 1.3))
    elif r <= 50.0:
        return float(max(0.65, 0.82 - 0.005 * math.pow(r - 20.0, 1.1)))
    else:
        return 0.60

def validate_and_normalize_equipment_data(equipment_list: List[Dict[str, Any]], db) -> List[Dict[str, Any]]:
    """
    Validator & Normalizer Data Armada (Single Source of Truth: Database Supabase):
    Murni membaca nilai dari Database Supabase. Jika ada baris dengan prod_bcmhr null / fc_lhr null,
    validator melakukan auto-fill murni dari tabel baseline DB (LoadingUnitBaseline / HaulingUnitBaseline).
    """
    normalized_list = []
    
    # Query DB baselines jika diperlukan fallback null
    loading_baselines = {}
    hauling_baselines = {}
    if db:
        try:
            loading_baselines = {b.unit_code: b for b in db.query(LoadingUnitBaseline).all()}
            hauling_baselines = {b.unit_code: b for b in db.query(HaulingUnitBaseline).all()}
        except Exception as e:
            logger.warning(f"Gagal me-load DB unit baselines untuk validation fallback: {e}")

    for item in equipment_list:
        unit_name = str(item.get("unit_name", "")).strip()
        activity = str(item.get("activity", "SUPPORT")).strip().upper()
        qty = max(0, int(item.get("qty") or 0))
        fc_lhr = float(item.get("fc_lhr") or 0.0)
        prod_bcmhr = float(item.get("prod_bcmhr") or 0.0)

        # Database Baseline Auto-Fill jika prod_bcmhr bernilai 0/NULL di catalog DB
        if prod_bcmhr == 0.0 and activity in ["LOADING", "HAULING"]:
            if activity == "LOADING" and unit_name in loading_baselines:
                prod_bcmhr = float(loading_baselines[unit_name].prod_bcmhr)
            elif activity == "HAULING" and unit_name in hauling_baselines:
                prod_bcmhr = float(hauling_baselines[unit_name].prod_bcmhr)

        if fc_lhr == 0.0:
            if activity == "LOADING" and unit_name in loading_baselines:
                fc_lhr = float(loading_baselines[unit_name].fc_lhr)
            elif activity == "HAULING" and unit_name in hauling_baselines:
                fc_lhr = float(hauling_baselines[unit_name].fc_lhr)

        normalized_list.append({
            "unit_name": unit_name,
            "qty": qty,
            "activity": activity,
            "fc_lhr": fc_lhr,
            "prod_bcmhr": prod_bcmhr
        })

    return normalized_list

class CombinedCapacityEngine:
    def __init__(self):
        pass

    def calculate_fleet_capacity(
        self,
        date_str: str,
        forecast_prod_bcm: float,
        curah_hujan_mm: float,
        equipment_list: Optional[List[Dict[str, Any]]] = None,
        nn_spike_count_by_unit: Optional[Dict[str, int]] = None,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Mengombinasikan XGBoost Forecast + PyTorch Autoencoder Spikes + Non-linear Rain Derating
        untuk menghitung alokasi kapasitas armada dan alokasi BBM harian.
        """
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            # 1. Murni fetch equipment catalogs dari DB jika tidak dipass
            if not equipment_list:
                eq_records = db.query(EquipmentCatalog).all()
                if not eq_records:
                    # Auto-seed ground truth database jika belum ada data
                    from seed_database import seed_database
                    logger.info("Equipment catalog di database kosong. Menjalankan auto-seeding data ground-truth...")
                    seed_database()
                    eq_records = db.query(EquipmentCatalog).all()
                    
                equipment_list = [
                    {
                        "unit_name": e.unit_name,
                        "qty": e.qty,
                        "activity": e.activity,
                        "fc_lhr": e.fc_lhr,
                        "prod_bcmhr": getattr(e, "prod_bcmhr", 0.0) or 0.0
                    }
                    for e in eq_records
                ]

            # Jalankan Validator & Normalizer murni dari DB
            equipment_list = validate_and_normalize_equipment_data(equipment_list, db)

            df_fleet = pd.DataFrame(equipment_list)
            
            # Ensure prod_bcmhr default for support/dewatering
            if 'prod_bcmhr' not in df_fleet.columns:
                df_fleet['prod_bcmhr'] = 0.0
            df_fleet['prod_bcmhr'] = df_fleet['prod_bcmhr'].fillna(0.0)

            # 2. Hitung Derating Hujan Non-Linear
            rain_derating = calculate_rain_derating_non_linear(curah_hujan_mm)

            # 3. Hitung Kapasitas Terpasang & Efektif per Unit
            df_fleet["Installed_Prod_Cap_BCMhr"] = df_fleet["qty"] * df_fleet["prod_bcmhr"]
            df_fleet["Effective_Prod_Cap_BCMday"] = df_fleet["Installed_Prod_Cap_BCMhr"] * OPERATING_HOURS_PER_DAY * rain_derating

            total_installed_bcmhr = float(df_fleet["Installed_Prod_Cap_BCMhr"].sum())
            total_effective_bcmday = float(df_fleet["Effective_Prod_Cap_BCMday"].sum())

            # Avoid division by zero
            if total_effective_bcmday == 0:
                total_effective_bcmday = max(forecast_prod_bcm * 1.2, 50000.0)

            # 4. Utilisasi & Operating Units Required
            utilization_pct = min(100.0, max(10.0, (forecast_prod_bcm / total_effective_bcmday) * 100.0))
            
            total_fleet_qty = int(df_fleet["qty"].sum())
            operating_units = int(math.ceil((utilization_pct / 100.0) * total_fleet_qty))

            # 5. Combined Fuel Allocation (Base + NN Spike Adjustment)
            if not nn_spike_count_by_unit:
                nn_spike_count_by_unit = {}

            # Base Fuel Consumption (L/day) = Qty * jam_operasional * FC_Lhr * (Utilization %)
            df_fleet["Base_Fuel_Lday"] = df_fleet["qty"] * OPERATING_HOURS_PER_DAY * df_fleet["fc_lhr"] * (utilization_pct / 100.0)
            
            # Adjustment Buffer BBM jika NN Anomaly Spike terdeteksi (+15% buffer per spike unit)
            df_fleet["Spike_Count_NN"] = df_fleet["unit_name"].map(lambda u: nn_spike_count_by_unit.get(u, 0)).fillna(0)
            df_fleet["Fuel_Buffer_Spike_Lday"] = df_fleet["Base_Fuel_Lday"] * (df_fleet["Spike_Count_NN"] * NN_SPIKE_BUFFER_PCT)
            df_fleet["Combined_Fuel_Lday"] = df_fleet["Base_Fuel_Lday"] + df_fleet["Fuel_Buffer_Spike_Lday"]

            total_combined_fuel_lday = float(df_fleet["Combined_Fuel_Lday"].sum())

            # 6. Breakdown Alokasi Kapasitas per Aktivitas (LOADING, HAULING, SUPPORT, DEWATERING)
            activity_summary = []
            for act, group in df_fleet.groupby("activity"):
                activity_summary.append({
                    "activity": act,
                    "unit_types_count": int(group["unit_name"].nunique()),
                    "total_fleet_qty": int(group["qty"].sum()),
                    "operating_units": int(math.ceil((utilization_pct / 100.0) * group["qty"].sum())),
                    "installed_cap_bcmhr": round(float(group["Installed_Prod_Cap_BCMhr"].sum()), 2),
                    "effective_cap_bcmday": round(float(group["Effective_Prod_Cap_BCMday"].sum()), 2),
                    "base_fuel_lday": round(float(group["Base_Fuel_Lday"].sum()), 2),
                    "combined_fuel_lday": round(float(group["Combined_Fuel_Lday"].sum()), 2)
                })

            result = {
                "log_date": date_str,
                "forecast_prod_bcm": forecast_prod_bcm,
                "curah_hujan_mm": curah_hujan_mm,
                "rain_derating_factor": round(rain_derating, 4),
                "installed_prod_bcmhr": round(total_installed_bcmhr, 2),
                "effective_prod_bcmday": round(total_effective_bcmday, 2),
                "utilization_pct": round(utilization_pct, 2),
                "total_fleet_qty": total_fleet_qty,
                "operating_units": operating_units,
                "total_combined_fuel_lday": round(total_combined_fuel_lday, 2),
                "activity_breakdown": activity_summary
            }

            # Simpan hasil alokasi kapasitas ke Database
            self._save_capacity_to_db(db, result)

            return result

        finally:
            if close_db:
                db.close()

    def perform_global_tuning(
        self,
        date_str: str,
        forecast_prod_bcm: Optional[float] = None,
        curah_hujan_mm: Optional[float] = None,
        auto_scan_anomalies: bool = True,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Global Tuning Engine:
        Menghitung tuning kapasitas teoritis seluruh armada (324 unit) untuk tanggal spesifik,
        lalu membandingkannya terhadap pemakaian BBM & jam operasional aktual harian per-unit dari database.
        """
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            log_date = pd.to_datetime(date_str).date()

            # 1. Lookup Weather & Forecast dari Database jika tidak dispesifikasikan
            if curah_hujan_mm is None:
                w_entry = db.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == log_date).first()
                curah_hujan_mm = float(w_entry.curah_hujan_mm) if w_entry else 0.0

            if forecast_prod_bcm is None:
                f_entry = db.query(DailyForecastLog).filter(DailyForecastLog.log_date == log_date).first()
                forecast_prod_bcm = float(f_entry.daily_prod_bcm) if f_entry else 40000.0

            # 2. Fetch / Auto-scan Anomaly Spikes Map per Unit
            spike_map = {}
            anomaly_records = db.query(UnitAnomalySpike).filter(UnitAnomalySpike.log_date == log_date).all()
            
            if anomaly_records:
                for a in anomaly_records:
                    if a.nn_anomaly_spike == 1:
                        spike_map[a.unit_code] = spike_map.get(a.unit_code, 0) + 1

            # 3. Hitung Tuned Fleet Capacity
            tuned_cap = self.calculate_fleet_capacity(
                date_str=date_str,
                forecast_prod_bcm=forecast_prod_bcm,
                curah_hujan_mm=curah_hujan_mm,
                equipment_list=None,
                nn_spike_count_by_unit=spike_map,
                db_session=db
            )

            # 4. Melakukan Komparasi Tuning vs Usage Aktual Harian per Unit
            actual_unit_usage = {}
            if anomaly_records:
                for a in anomaly_records:
                    u_code = a.unit_code
                    if u_code not in actual_unit_usage:
                        actual_unit_usage[u_code] = {
                            "unit_code": u_code,
                            "activity": a.activity,
                            "actual_fc_lhr": float(a.fc_actual),
                            "actual_fuel_lday": float(a.unit_fuel_day),
                            "actual_unit_fr": float(a.unit_fr),
                            "nn_spike_count": int(a.nn_anomaly_spike)
                        }
                    else:
                        actual_unit_usage[u_code]["actual_fuel_lday"] += float(a.unit_fuel_day)
                        actual_unit_usage[u_code]["nn_spike_count"] += int(a.nn_anomaly_spike)

            # 5. Susun Unit Tuning Comparison
            eq_catalogs = db.query(EquipmentCatalog).all()
            unit_tuning_breakdown = []
            total_actual_fuel_lday = 0.0

            for eq in eq_catalogs:
                u_name = eq.unit_name
                u_qty = eq.qty
                u_act = eq.activity
                u_fc_std = eq.fc_lhr

                # Tuned values per unit group
                tuned_unit_fuel = (u_qty * OPERATING_HOURS_PER_DAY * u_fc_std * (tuned_cap["utilization_pct"] / 100.0))
                spike_count = spike_map.get(u_name, 0)
                tuned_unit_fuel += tuned_unit_fuel * (spike_count * NN_SPIKE_BUFFER_PCT)

                # Actual values
                act_data = actual_unit_usage.get(u_name, {})
                actual_fuel = act_data.get("actual_fuel_lday", 0.0)
                total_actual_fuel_lday += actual_fuel

                variance_l = actual_fuel - tuned_unit_fuel if actual_fuel > 0 else 0.0
                variance_pct = (variance_l / tuned_unit_fuel * 100.0) if (actual_fuel > 0 and tuned_unit_fuel > 0) else 0.0

                if actual_fuel == 0.0:
                    tuning_status = "NO_ACTUAL_LOG"
                elif variance_pct <= 0.0:
                    tuning_status = "EFFICIENT"
                elif variance_pct <= 5.0:
                    tuning_status = "OPTIMAL"
                elif variance_pct <= 15.0:
                    tuning_status = "MODERATE_OVER_CONSUMPTION"
                else:
                    tuning_status = "SPIKE_CRITICAL_OVER_CONSUMPTION"

                unit_tuning_breakdown.append({
                    "unit_name": u_name,
                    "activity": u_act,
                    "fleet_qty": u_qty,
                    "std_fc_lhr": u_fc_std,
                    "tuned_fuel_allocation_lday": round(tuned_unit_fuel, 2),
                    "actual_fuel_consumed_lday": round(actual_fuel, 2),
                    "variance_liters": round(variance_l, 2),
                    "variance_pct": round(variance_pct, 2),
                    "spike_anomaly_count": spike_count,
                    "tuning_status": tuning_status
                })

            net_variance_lday = total_actual_fuel_lday - tuned_cap["total_combined_fuel_lday"] if total_actual_fuel_lday > 0 else 0.0
            overall_variance_pct = (net_variance_lday / tuned_cap["total_combined_fuel_lday"] * 100.0) if (total_actual_fuel_lday > 0 and tuned_cap["total_combined_fuel_lday"] > 0) else 0.0

            return {
                "log_date": date_str,
                "tuning_parameters": {
                    "forecast_prod_bcm": forecast_prod_bcm,
                    "curah_hujan_mm": curah_hujan_mm,
                    "rain_derating_factor": tuned_cap["rain_derating_factor"],
                    "operating_hours_per_day": OPERATING_HOURS_PER_DAY
                },
                "global_capacity_summary": {
                    "installed_cap_bcmhr": tuned_cap["installed_prod_bcmhr"],
                    "effective_cap_bcmday": tuned_cap["effective_prod_bcmday"],
                    "fleet_utilization_pct": tuned_cap["utilization_pct"],
                    "total_fleet_units": tuned_cap["total_fleet_qty"],
                    "required_operating_units": tuned_cap["operating_units"],
                    "standby_units": tuned_cap["total_fleet_qty"] - tuned_cap["operating_units"]
                },
                "global_fuel_tuning_summary": {
                    "tuned_combined_fuel_lday": tuned_cap["total_combined_fuel_lday"],
                    "actual_total_fuel_lday": round(total_actual_fuel_lday, 2),
                    "net_fuel_variance_lday": round(net_variance_lday, 2),
                    "overall_variance_pct": round(overall_variance_pct, 2),
                    "global_tuning_status": "OPTIMAL" if overall_variance_pct <= 5.0 else ("EFFICIENT" if overall_variance_pct <= 0 else "OVER_CONSUMPTION_ALERT")
                },
                "activity_breakdown": tuned_cap["activity_breakdown"],
                "unit_tuning_comparison": unit_tuning_breakdown
            }

        finally:
            if close_db:
                db.close()

    def _save_capacity_to_db(self, db, result: Dict[str, Any]):
        """
        Menyelaraskan data alokasi kapasitas ke tabel database capacity_allocations
        """
        try:
            log_date = pd.to_datetime(result["log_date"]).date()
            entry = db.query(CapacityAllocation).filter(CapacityAllocation.log_date == log_date).first()

            if entry:
                entry.installed_prod_bcmhr = result["installed_prod_bcmhr"]
                entry.effective_prod_bcmday = result["effective_prod_bcmday"]
                entry.utilization_pct = result["utilization_pct"]
                entry.operating_units = result["operating_units"]
                entry.combined_fuel_lday = result["total_combined_fuel_lday"]
            else:
                entry = CapacityAllocation(
                    log_date=log_date,
                    installed_prod_bcmhr=result["installed_prod_bcmhr"],
                    effective_prod_bcmday=result["effective_prod_bcmday"],
                    utilization_pct=result["utilization_pct"],
                    operating_units=result["operating_units"],
                    combined_fuel_lday=result["total_combined_fuel_lday"]
                )
                db.add(entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Gagal menyimpan capacity allocation log ke database: {e}")

capacity_engine = CombinedCapacityEngine()
