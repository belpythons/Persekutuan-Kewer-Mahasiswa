import os
import sys
import pandas as pd
import numpy as np
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from models_db import (
    EquipmentCatalog, LoadingUnitBaseline, HaulingUnitBaseline,
    SupportingUnitBaseline, DewateringUnitBaseline, WeatherDailyLog,
    DailyForecastLog, UnitAnomalySpike
)

EXCEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "konsep", "UPDATE_Fuel ratio calculation 2026 dummy data.xlsx")

def seed_database():
    """
    Seeding database dengan data ground-truth dari Excel file:
    'UPDATE_Fuel ratio calculation 2026 dummy data.xlsx'
    3NF Normalized dengan Foreign Keys & High-Scale Composite Indexes.
    """
    print("\n=== MEMBUAT TABEL DATABASE ===")
    Base.metadata.create_all(bind=engine)
    print(" [OK] Seluruh tabel database berhasil dibuat.")
    
    db = SessionLocal()
    try:
        print("\n=== START DATABASE SEEDING FROM EXCEL GROUND-TRUTH ===")
        
        # 1. Equipment Catalog Seeding
        eq_map = {}
        if db.query(EquipmentCatalog).count() == 0:
            equipment_data = [
                {"unit_name": "EX2600-6", "qty": 1, "activity": "LOADING", "fc_lhr": 190.0},
                {"unit_name": "PC1250-11R", "qty": 7, "activity": "LOADING", "fc_lhr": 93.33},
                {"unit_name": "PC2000-11R", "qty": 17, "activity": "LOADING", "fc_lhr": 125.0},
                {"unit_name": "HD785-7", "qty": 172, "activity": "HAULING", "fc_lhr": 75.0},
                {"unit_name": "HD785-7MUD", "qty": 33, "activity": "HAULING", "fc_lhr": 75.0},
                {"unit_name": "Dozer375", "qty": 9, "activity": "SUPPORT", "fc_lhr": 65.75},
                {"unit_name": "Water Pump", "qty": 85, "activity": "DEWATERING", "fc_lhr": 40.0},
            ]
            for item in equipment_data:
                eq = EquipmentCatalog(**item)
                db.add(eq)
            db.commit()
            print(" [OK] Equipment Catalogs berhasil di-seed.")

        # Re-query equipment catalog map for Foreign Key IDs
        for eq in db.query(EquipmentCatalog).all():
            eq_map[eq.unit_name] = eq.id

        # 2. Loading Baseline Seeding
        if db.query(LoadingUnitBaseline).count() == 0:
            loading_data = [
                {"unit_code": "EX2600-6", "activity": "Loading", "fc_lhr": 190.0, "prod_bcmhr": 920.0},
                {"unit_code": "PC1250-11R", "activity": "Loading", "fc_lhr": 93.33, "prod_bcmhr": 310.0},
                {"unit_code": "PC2000-11R", "activity": "Loading", "fc_lhr": 125.0, "prod_bcmhr": 820.0},
            ]
            for item in loading_data:
                db.add(LoadingUnitBaseline(**item))
            db.commit()
            print(" [OK] Loading Baselines berhasil di-seed.")

        # 3. Hauling Baseline Seeding
        if db.query(HaulingUnitBaseline).count() == 0:
            hauling_data = [
                {"unit_code": "HD785-7", "activity": "Hauling", "fc_lhr": 75.0, "prod_bcmhr": 109.56},
                {"unit_code": "HD785-7MUD", "activity": "Hauling", "fc_lhr": 75.0, "prod_bcmhr": 109.56},
            ]
            for item in hauling_data:
                db.add(HaulingUnitBaseline(**item))
            db.commit()
            print(" [OK] Hauling Baselines berhasil di-seed.")

        # 4. Supporting Baseline Seeding
        if db.query(SupportingUnitBaseline).count() == 0:
            db.add(SupportingUnitBaseline(unit_code="Dozer375", activity="Supporting", pa=90.0, ua=85.0, fc_lhr=65.75))
            db.commit()
            print(" [OK] Supporting Baselines berhasil di-seed.")

        # 5. Dewatering Baseline Seeding
        if db.query(DewateringUnitBaseline).count() == 0:
            db.add(DewateringUnitBaseline(unit_code="Water Pump", activity="Dewatering", pa=95.0, ua=90.0, fc_lhr=40.0))
            db.commit()
            print(" [OK] Dewatering Baselines berhasil di-seed.")

        # 6. Time-Series Weather, Forecast & Anomaly Spikes (365 days)
        if db.query(WeatherDailyLog).count() == 0:
            start_date = datetime.date(2025, 1, 1)
            np.random.seed(42)
            
            BASE_TARGET_PROD = 40000.0
            BASE_FR = 1.018  # Baseline Total FR
            
            units_sample = [
                ("EX2600-6", "LOADING", 190.0),
                ("PC1250-11R", "LOADING", 93.33),
                ("PC2000-11R", "LOADING", 125.0),
                ("HD785-7", "HAULING", 75.0),
                ("HD785-7MUD", "HAULING", 75.0),
                ("Dozer375", "SUPPORT", 65.75),
                ("Water Pump", "DEWATERING", 40.0)
            ]
            
            for i in range(365):
                cur_date = start_date + datetime.timedelta(days=i)
                rain = max(0.0, float(np.random.exponential(scale=6.0) if np.random.rand() < 0.35 else 0.0))
                temp = float(30.0 + np.random.normal(0, 1.5))
                wind = float(12.0 + np.random.normal(0, 2.5))
                
                haul_dist = float(3900.0 + (rain * 8.0) + np.random.normal(0, 50))
                prod_bcm = float(BASE_TARGET_PROD * max(0.6, 1.0 - (rain * 0.005)))
                actual_fr = float(BASE_FR * (1.0 + (rain * 0.006) + ((haul_dist - 3900.0)/3900.0)*0.2))
                
                status = "NORMAL"
                if actual_fr >= BASE_FR * 1.18:
                    status = "CRITICAL"
                elif actual_fr >= BASE_FR * 1.08:
                    status = "WARNING"
                    
                w_log = WeatherDailyLog(
                    log_date=cur_date,
                    curah_hujan_mm=rain,
                    temp_max_c=temp,
                    kecepatan_angin_kmh=wind
                )
                db.add(w_log)
                
                f_log = DailyForecastLog(
                    log_date=cur_date,
                    actual_fr=actual_fr,
                    forecast_fr=actual_fr * (1 + np.random.normal(0, 0.015)),
                    status=status,
                    warning_threshold=BASE_FR * 1.08,
                    critical_threshold=BASE_FR * 1.18,
                    daily_prod_bcm=prod_bcm,
                    haul_distance_m=haul_dist
                )
                db.add(f_log)
                
                # Unit Anomaly Spikes
                for unit, act, fc_base in units_sample:
                    is_spike = 1 if np.random.rand() < 0.035 else 0
                    fc_act = fc_base * (1.6 if is_spike else (1.0 + np.random.normal(0, 0.03)))
                    fuel_day = fc_act * 20.0
                    unit_fr = fuel_day / (prod_bcm / len(units_sample))
                    
                    sp_log = UnitAnomalySpike(
                        log_date=cur_date,
                        unit_code=unit,
                        activity=act,
                        equipment_id=eq_map.get(unit),
                        fc_actual=fc_act,
                        unit_fuel_day=fuel_day,
                        unit_fr=unit_fr,
                        nn_anomaly_spike=is_spike,
                        reconstruction_error=0.08 if is_spike else 0.005
                    )
                    db.add(sp_log)
                    
            db.commit()
            print(" [OK] 365 Hari Time-Series Historical Logs berhasil di-seed.")
            
        print("\n=== SEEDING COMPLETED SUCCESSFULLY ===")
    except Exception as e:
        db.rollback()
        print(f" ERROR saat Seeding Database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
