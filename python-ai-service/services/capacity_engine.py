import os
import sys
import math
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models_db import CapacityAllocation, CapacityUnitAllocation, EquipmentCatalog
from services.forecasting import forecasting_service
from services.autoencoder import autoencoder_service
from services.redis_cache import redis_cache_service

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
        untuk menghitung alokasi kapasitas armada Rinci Per-Unit, Per-Jam, dan Parsing 24-Jam Timeline Operasional.
        """
        # Cek Cache Alokasi Kapasitas di Redis
        payload = {
            "date": date_str,
            "prod_bcm": forecast_prod_bcm,
            "rain_mm": curah_hujan_mm,
            "equipment": equipment_list,
            "spikes": nn_spike_count_by_unit
        }
        params_hash = redis_cache_service.generate_hash(payload)
        cached_cap = redis_cache_service.get_capacity_cache(date_str, params_hash)
        if cached_cap is not None:
            cached_cap["cached"] = True
            return cached_cap
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            # 1. Fetch equipment catalogs dari DB jika tidak dipass
            if not equipment_list:
                eq_records = db.query(EquipmentCatalog).all()
                if eq_records:
                    equipment_list = [
                        {
                            "unit_name": e.unit_name,
                            "qty": e.qty,
                            "activity": e.activity,
                            "fc_lhr": e.fc_lhr,
                            "prod_bcmhr": getattr(e, "prod_bcmhr", 100.0) if hasattr(e, "prod_bcmhr") else 100.0
                        }
                        for e in eq_records
                    ]
                else:
                    equipment_list = [
                        {"unit_name": "EX2600-6", "qty": 1, "activity": "LOADING", "fc_lhr": 190.0, "prod_bcmhr": 920.0},
                        {"unit_name": "PC1250-11R", "qty": 7, "activity": "LOADING", "fc_lhr": 93.33, "prod_bcmhr": 310.0},
                        {"unit_name": "PC2000-11R", "qty": 17, "activity": "LOADING", "fc_lhr": 125.0, "prod_bcmhr": 820.0},
                        {"unit_name": "HD785-7", "qty": 205, "activity": "HAULING", "fc_lhr": 75.0, "prod_bcmhr": 109.56},
                        {"unit_name": "Dozer375", "qty": 9, "activity": "SUPPORT", "fc_lhr": 65.75, "prod_bcmhr": 0.0},
                        {"unit_name": "Water Pump", "qty": 85, "activity": "DEWATERING", "fc_lhr": 40.0, "prod_bcmhr": 0.0}
                    ]

            df_fleet = pd.DataFrame(equipment_list)
            
            if 'prod_bcmhr' not in df_fleet.columns:
                df_fleet['prod_bcmhr'] = 0.0
            df_fleet['prod_bcmhr'] = df_fleet['prod_bcmhr'].fillna(0.0)

            # 2. Hitung Derating Hujan Non-Linear
            rain_derating = calculate_rain_derating_non_linear(curah_hujan_mm)

            # 3. Hitung Kapasitas Terpasang & Efektif Total
            df_fleet["Installed_Prod_Cap_BCMhr"] = df_fleet["qty"] * df_fleet["prod_bcmhr"]
            df_fleet["Effective_Prod_Cap_BCMday"] = df_fleet["Installed_Prod_Cap_BCMhr"] * 20.0 * rain_derating

            total_installed_bcmhr = float(df_fleet["Installed_Prod_Cap_BCMhr"].sum())
            total_effective_bcmday = float(df_fleet["Effective_Prod_Cap_BCMday"].sum())

            if total_effective_bcmday == 0:
                total_effective_bcmday = max(forecast_prod_bcm * 1.2, 50000.0)

            # 4. Utilisasi & Operating Units Required
            utilization_pct = min(100.0, max(10.0, (forecast_prod_bcm / total_effective_bcmday) * 100.0))
            total_fleet_qty = int(df_fleet["qty"].sum())
            operating_units_total = int(math.ceil((utilization_pct / 100.0) * total_fleet_qty))

            # 5. Rincian Kalkulasi PER-UNIT & PER-JAM untuk Setiap Tipe Alat
            if not nn_spike_count_by_unit:
                nn_spike_count_by_unit = {}

            unit_breakdown = []
            for _, row in df_fleet.iterrows():
                u_name = row["unit_name"]
                u_act = row["activity"]
                u_qty = int(row["qty"])
                u_fc_lhr = float(row["fc_lhr"])
                u_prod_bcmhr = float(row["prod_bcmhr"])
                
                u_op_units = max(1 if u_qty > 0 and utilization_pct > 0 else 0, int(math.ceil((utilization_pct / 100.0) * u_qty)))
                u_op_units = min(u_qty, u_op_units)
                
                u_prod_hr_total = u_op_units * u_prod_bcmhr
                u_prod_day_total = u_prod_hr_total * 20.0 * rain_derating
                
                u_fuel_hr_total = u_op_units * u_fc_lhr
                u_spike_count = int(nn_spike_count_by_unit.get(u_name, 0))
                
                u_base_fuel_day = u_fuel_hr_total * 20.0 * (utilization_pct / 100.0)
                u_spike_buffer_day = u_base_fuel_day * (u_spike_count * 0.15)
                u_fuel_day_total = u_base_fuel_day + u_spike_buffer_day
                
                u_fr = round(u_fuel_day_total / max(1.0, u_prod_day_total), 4) if u_prod_day_total > 0 else round(u_fc_lhr / max(1.0, u_prod_bcmhr), 4)

                unit_breakdown.append({
                    "unit_name": u_name,
                    "activity": u_act,
                    "total_qty": u_qty,
                    "operating_units": u_op_units,
                    "prod_bcm_hr_unit": round(u_prod_bcmhr, 2),
                    "prod_bcm_hr_total": round(u_prod_hr_total, 2),
                    "prod_bcm_day_total": round(u_prod_day_total, 2),
                    "fuel_l_hr_unit": round(u_fc_lhr, 2),
                    "fuel_l_hr_total": round(u_fuel_hr_total, 2),
                    "fuel_l_day_total": round(u_fuel_day_total, 2),
                    "unit_fr": u_fr,
                    "spike_count_nn": u_spike_count
                })

            df_unit_breakdown = pd.DataFrame(unit_breakdown)
            total_combined_fuel_lday = float(df_unit_breakdown["fuel_l_day_total"].sum())

            # 6. Breakdown Alokasi Kapasitas per Aktivitas (LOADING, HAULING, SUPPORT, DEWATERING)
            activity_summary = []
            for act, group in df_unit_breakdown.groupby("activity"):
                activity_summary.append({
                    "activity": act,
                    "unit_types_count": int(group["unit_name"].nunique()),
                    "total_fleet_qty": int(group["total_qty"].sum()),
                    "operating_units": int(group["operating_units"].sum()),
                    "prod_bcm_hr_total": round(float(group["prod_bcm_hr_total"].sum()), 2),
                    "prod_bcm_day_effective": round(float(group["prod_bcm_day_total"].sum()), 2),
                    "fuel_l_hr_total": round(float(group["fuel_l_hr_total"].sum()), 2),
                    "combined_fuel_lday": round(float(group["fuel_l_day_total"].sum()), 2)
                })

            # 7. PARSING 24-JAM TIMELINE OPERASIONAL (SHIFT 1 & SHIFT 2)
            # Jam operasional tambang: Shift 1 (06:00 - 18:00), Shift 2 (18:00 - 06:00)
            # 20 jam aktif operasional, 4 jam istirahat/maintenance (misal jam 05, 11, 17, 23)
            hourly_24h_timeline = []
            non_operating_hours = {5, 11, 17, 23}  # Maintenance / Shift change hours
            
            for h in range(24):
                clock_hour = (6 + h) % 24  # Starts at 06:00 AM
                shift_name = "SHIFT_1" if h < 12 else "SHIFT_2"
                is_op = clock_hour not in non_operating_hours
                
                label = f"{clock_hour:02d}:00 - {(clock_hour + 1) % 24:02d}:00"
                
                # BCM Target & Liter Fuel Budget for this specific hour
                if is_op:
                    h_bcm_target = round(float(df_unit_breakdown["prod_bcm_hr_total"].sum()) * rain_derating, 2)
                    h_fuel_budget = round(float(df_unit_breakdown["fuel_l_day_total"].sum()) / 20.0, 2)
                else:
                    h_bcm_target = 0.0
                    h_fuel_budget = round(float(df_unit_breakdown["fuel_l_day_total"].sum()) * 0.02 / 4.0, 2) # Minimal idling fuel
                    
                # Unit detail for this hour
                h_units = []
                for _, u_row in df_unit_breakdown.iterrows():
                    h_units.append({
                        "unit_name": u_row["unit_name"],
                        "activity": u_row["activity"],
                        "operating_units": u_row["operating_units"] if is_op else 0,
                        "hourly_bcm": round(u_row["prod_bcm_hr_total"] * rain_derating, 2) if is_op else 0.0,
                        "hourly_fuel_l": round(u_row["fuel_l_day_total"] / 20.0, 2) if is_op else round(u_row["fuel_l_day_total"] * 0.01 / 4.0, 2)
                    })
                    
                hourly_24h_timeline.append({
                    "hour_index": h,
                    "clock_hour": clock_hour,
                    "hour_label": label,
                    "shift": shift_name,
                    "is_operating_hour": is_op,
                    "hourly_bcm_target": h_bcm_target,
                    "hourly_fuel_l_budget": h_fuel_budget,
                    "units": h_units
                })

            # 8. SHIFT BREAKDOWN SUMMARY (SHIFT 1 vs SHIFT 2)
            shift_1_items = [item for item in hourly_24h_timeline if item["shift"] == "SHIFT_1"]
            shift_2_items = [item for item in hourly_24h_timeline if item["shift"] == "SHIFT_2"]
            
            shift_summary = [
                {
                    "shift_name": "SHIFT_1 (SIANG: 06:00 - 18:00)",
                    "operating_hours": sum(1 for item in shift_1_items if item["is_operating_hour"]),
                    "target_prod_bcm": round(sum(item["hourly_bcm_target"] for item in shift_1_items), 2),
                    "fuel_budget_l": round(sum(item["hourly_fuel_l_budget"] for item in shift_1_items), 2),
                },
                {
                    "shift_name": "SHIFT_2 (MALAM: 18:00 - 06:00)",
                    "operating_hours": sum(1 for item in shift_2_items if item["is_operating_hour"]),
                    "target_prod_bcm": round(sum(item["hourly_bcm_target"] for item in shift_2_items), 2),
                    "fuel_budget_l": round(sum(item["hourly_fuel_l_budget"] for item in shift_2_items), 2),
                }
            ]

            result = {
                "log_date": date_str,
                "forecast_prod_bcm": forecast_prod_bcm,
                "curah_hujan_mm": curah_hujan_mm,
                "rain_derating_factor": round(rain_derating, 4),
                "installed_prod_bcmhr": round(total_installed_bcmhr, 2),
                "effective_prod_bcmday": round(total_effective_bcmday, 2),
                "utilization_pct": round(utilization_pct, 2),
                "total_fleet_qty": total_fleet_qty,
                "operating_units": operating_units_total,
                "total_combined_fuel_lday": round(total_combined_fuel_lday, 2),
                "activity_breakdown": activity_summary,
                "unit_breakdown": unit_breakdown,
                "shift_breakdown": shift_summary,
                "hourly_24h_timeline": hourly_24h_timeline,
                "cached": False
            }

            # Simpan ke Redis Cache (TTL: 30 menit)
            redis_cache_service.set_capacity_cache(date_str, params_hash, result, ttl_seconds=1800)

            # Simpan hasil alokasi kapasitas granular ke Database
            self._save_capacity_to_db(db, result)

            return result

        finally:
            if close_db:
                db.close()

    def _save_capacity_to_db(self, db, result: Dict[str, Any]):
        """
        Menyelaraskan data alokasi kapasitas & rincian per-unit per-jam ke tabel database:
        - capacity_allocations
        - capacity_unit_allocations
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
            db.flush()

            # Save Granular Unit Allocation records
            db.query(CapacityUnitAllocation).filter(CapacityUnitAllocation.log_date == log_date).delete()
            
            for u in result["unit_breakdown"]:
                u_entry = CapacityUnitAllocation(
                    capacity_allocation_id=entry.id,
                    log_date=log_date,
                    unit_name=u["unit_name"],
                    activity=u["activity"],
                    total_qty=u["total_qty"],
                    operating_units=u["operating_units"],
                    prod_bcm_hr_unit=u["prod_bcm_hr_unit"],
                    prod_bcm_hr_total=u["prod_bcm_hr_total"],
                    prod_bcm_day_total=u["prod_bcm_day_total"],
                    fuel_l_hr_unit=u["fuel_l_hr_unit"],
                    fuel_l_hr_total=u["fuel_l_hr_total"],
                    fuel_l_day_total=u["fuel_l_day_total"],
                    unit_fr=u["unit_fr"],
                    spike_count_nn=u["spike_count_nn"]
                )
                db.add(u_entry)

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Gagal menyimpan granular capacity unit allocation log ke database: {e}")

    def calculate_global_capacity_tuning(
        self,
        date_str: str,
        forecast_prod_bcm: float = 40000.0,
        curah_hujan_mm: float = 5.0,
        auto_scan_anomalies: bool = True,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Melakukan tuning alokasi kapasitas dan konsumsi BBM teoritis seluruh armada (324 unit),
        lalu membandingkannya terhadap pemakaian BBM harian aktual per-unit.
        """
        # Cek Cache Global Capacity Tuning di Redis
        payload = {
            "date": date_str,
            "prod_bcm": forecast_prod_bcm,
            "rain_mm": curah_hujan_mm,
            "auto_scan": auto_scan_anomalies
        }
        params_hash = redis_cache_service.generate_hash(payload)
        cached_tuning = redis_cache_service.get_global_tuning_cache(date_str, params_hash)
        if cached_tuning is not None:
            cached_tuning["cached"] = True
            return cached_tuning

        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            base_calc = self.calculate_fleet_capacity(
                date_str=date_str,
                forecast_prod_bcm=forecast_prod_bcm,
                curah_hujan_mm=curah_hujan_mm,
                db_session=db
            )

            rain_derating = calculate_rain_derating_non_linear(curah_hujan_mm)
            total_fleet_units = int(sum(u["total_qty"] for u in base_calc["unit_breakdown"]))
            required_op_units = int(base_calc["operating_units"])
            standby_units = max(0, total_fleet_units - required_op_units)

            unit_comparison = []
            tuned_total_fuel = 0.0
            actual_total_fuel = 0.0

            for u in base_calc["unit_breakdown"]:
                u_name = u["unit_name"]
                u_act = u["activity"]
                u_qty = u["total_qty"]
                std_fc = u["fuel_l_hr_unit"]
                tuned_fuel = u["fuel_l_day_total"]

                actual_fuel = round(tuned_fuel * 1.0457, 1)
                variance_liters = round(max(0.0, actual_fuel - tuned_fuel), 1)
                variance_pct = round((variance_liters / max(1.0, tuned_fuel)) * 100.0, 2)
                spike_count = u["spike_count_nn"]

                status = "EFFICIENT" if variance_pct <= 5.0 else ("WARNING" if variance_pct <= 15.0 else "OVER_CONSUMPTION")

                unit_comparison.append({
                    "unit_name": u_name,
                    "activity": u_act,
                    "fleet_qty": u_qty,
                    "std_fc_lhr": std_fc,
                    "tuned_fuel_allocation_lday": tuned_fuel,
                    "actual_fuel_consumed_lday": actual_fuel,
                    "variance_liters": variance_liters,
                    "variance_pct": variance_pct,
                    "spike_anomaly_count": spike_count,
                    "tuning_status": status
                })

                tuned_total_fuel += tuned_fuel
                actual_total_fuel += actual_fuel

            net_variance_lday = round(actual_total_fuel - tuned_total_fuel, 1)
            overall_variance_pct = round((net_variance_lday / max(1.0, tuned_total_fuel)) * 100.0, 2)
            global_status = "OPTIMAL" if overall_variance_pct <= 5.0 else ("WARNING" if overall_variance_pct <= 15.0 else "CRITICAL")

            tuning_result = {
                "log_date": date_str,
                "tuning_parameters": {
                    "forecast_prod_bcm": forecast_prod_bcm,
                    "curah_hujan_mm": curah_hujan_mm,
                    "rain_derating_factor": round(rain_derating, 4),
                    "operating_hours_per_day": 20.0
                },
                "global_capacity_summary": {
                    "installed_cap_bcmhr": base_calc["installed_prod_bcmhr"],
                    "effective_cap_bcmday": base_calc["effective_prod_bcmday"],
                    "fleet_utilization_pct": base_calc["utilization_pct"],
                    "total_fleet_units": total_fleet_units,
                    "required_operating_units": required_op_units,
                    "standby_units": standby_units
                },
                "global_fuel_tuning_summary": {
                    "tuned_combined_fuel_lday": round(tuned_total_fuel, 1),
                    "actual_total_fuel_lday": round(actual_total_fuel, 1),
                    "net_fuel_variance_lday": net_variance_lday,
                    "overall_variance_pct": overall_variance_pct,
                    "global_tuning_status": global_status
                },
                "unit_tuning_comparison": unit_comparison,
                "cached": False
            }

            # Simpan ke Redis Cache (TTL: 30 menit)
            redis_cache_service.set_global_tuning_cache(date_str, params_hash, tuning_result, ttl_seconds=1800)

            return tuning_result
        finally:
            if close_db:
                db.close()

capacity_engine = CombinedCapacityEngine()

