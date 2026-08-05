import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Base, engine
from models_db import (
    EquipmentCatalog, LoadingUnitBaseline, HaulingUnitBaseline,
    SupportingUnitBaseline, DewateringUnitBaseline, WeatherDailyLog,
    DailyForecastLog, UnitAnomalySpike, CapacityAllocation
)

def seed_database():
    """
    Seeding database dengan data ground-truth dari file Excel:
    UPDATE_Fuel ratio calculation 2026 dummy data.xlsx
    """
    db = SessionLocal()
    try:
        print("=== START DATABASE SEEDING FROM EXCEL GROUND-TRUTH ===")
        
        # 1. Seed Equipment Catalog
        if db.query(EquipmentCatalog).count() == 0:
            catalogs = [
                EquipmentCatalog(unit_name="HT 2600", qty=1, activity="LOADING", fc_lhr=190.0),
                EquipmentCatalog(unit_name="EX2600-6", qty=1, activity="LOADING", fc_lhr=190.0),
                EquipmentCatalog(unit_name="PC 1250", qty=7, activity="LOADING", fc_lhr=93.33),
                EquipmentCatalog(unit_name="PC1250-11R", qty=7, activity="LOADING", fc_lhr=93.33),
                EquipmentCatalog(unit_name="PC 1250_Mud", qty=1, activity="LOADING", fc_lhr=97.58),
                EquipmentCatalog(unit_name="PC 2000", qty=16, activity="LOADING", fc_lhr=125.0),
                EquipmentCatalog(unit_name="PC2000-11R", qty=17, activity="LOADING", fc_lhr=125.0),
                EquipmentCatalog(unit_name="PC 2000_Mud", qty=1, activity="LOADING", fc_lhr=125.0),
                EquipmentCatalog(unit_name="PC 3400", qty=1, activity="LOADING", fc_lhr=195.625),
                EquipmentCatalog(unit_name="HD785-7", qty=205, activity="HAULING", fc_lhr=75.0),
                EquipmentCatalog(unit_name="HD785-7MUD", qty=28, activity="HAULING", fc_lhr=75.0),
                EquipmentCatalog(unit_name="HD785-SPIKE", qty=1, activity="HAULING", fc_lhr=75.0),
                EquipmentCatalog(unit_name="EX2600-SPIKE", qty=1, activity="LOADING", fc_lhr=190.0),
                EquipmentCatalog(unit_name="MID DRILLING", qty=1, activity="SUPPORT", fc_lhr=54.17),
                EquipmentCatalog(unit_name="SMALL DRILLING", qty=4, activity="SUPPORT", fc_lhr=28.06),
                EquipmentCatalog(unit_name="Dozer375", qty=9, activity="SUPPORT", fc_lhr=65.75),
                EquipmentCatalog(unit_name="Booster Pump", qty=7, activity="DEWATERING", fc_lhr=50.0),
                EquipmentCatalog(unit_name="Dragflow", qty=4, activity="DEWATERING", fc_lhr=45.0),
                EquipmentCatalog(unit_name="Water Pump", qty=85, activity="DEWATERING", fc_lhr=40.0)
            ]
            db.add_all(catalogs)
            db.commit()
            print(" [OK] Equipment Catalog berhasil di-seed.")

        # Build eq_map for foreign key linking
        eq_records = db.query(EquipmentCatalog).all()
        eq_map = {}
        for eq in eq_records:
            eq_map[eq.unit_name] = eq.id
            clean_name = eq.unit_name.replace(" ", "").replace("-", "").lower()
            eq_map[clean_name] = eq.id

        # 2. Seed Baselines
        if db.query(LoadingUnitBaseline).count() == 0:
            loading = [
                LoadingUnitBaseline(unit_code="EX2600-6", activity="Loading", fc_lhr=190.0, prod_bcmhr=920.0),
                LoadingUnitBaseline(unit_code="PC1250-11R", activity="Loading", fc_lhr=93.33, prod_bcmhr=310.0),
                LoadingUnitBaseline(unit_code="PC2000-11R", activity="Loading", fc_lhr=125.0, prod_bcmhr=820.0)
            ]
            db.add_all(loading)
            
        if db.query(HaulingUnitBaseline).count() == 0:
            hauling = [
                HaulingUnitBaseline(unit_code="HD785-7", activity="Hauling", fc_lhr=75.0, prod_bcmhr=109.56)
            ]
            db.add_all(hauling)

        if db.query(SupportingUnitBaseline).count() == 0:
            supporting = [
                SupportingUnitBaseline(unit_code="MID DRILLING", activity="Supporting", pa=85.0, ua=75.0, fc_lhr=54.17),
                SupportingUnitBaseline(unit_code="SMALL DRILLING", activity="Supporting", pa=85.0, ua=75.0, fc_lhr=28.06),
                SupportingUnitBaseline(unit_code="Dozer375", activity="Supporting", pa=85.0, ua=75.0, fc_lhr=65.75)
            ]
            db.add_all(supporting)

        if db.query(DewateringUnitBaseline).count() == 0:
            dewatering = [
                DewateringUnitBaseline(unit_code="Booster Pump", activity="Dewatering", pa=90.0, ua=80.0, fc_lhr=50.0),
                DewateringUnitBaseline(unit_code="Dragflow", activity="Dewatering", pa=90.0, ua=80.0, fc_lhr=45.0),
                DewateringUnitBaseline(unit_code="Water Pump", activity="Dewatering", pa=90.0, ua=80.0, fc_lhr=40.0)
            ]
            db.add_all(dewatering)

        db.commit()
        print(" [OK] Unit Baselines berhasil di-seed.")

        # 3. Seed Time Series Historical Data (365 Hari)
        if db.query(DailyForecastLog).count() == 0:
            start_date = datetime(2025, 1, 1).date()
            BASE_TARGET_PROD = 40000.0
            BASE_FR = 1.018
            
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
                cur_date = start_date + timedelta(days=i)
                rain = float(max(0.0, np.random.exponential(scale=4.5) if np.random.rand() < 0.3 else 0.0))
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
                
                # Unit Anomaly Spikes with populated Foreign Key
                for unit, act, fc_base in units_sample:
                    is_spike = 1 if np.random.rand() < 0.035 else 0
                    fc_act = fc_base * (1.6 if is_spike else (1.0 + np.random.normal(0, 0.03)))
                    fuel_day = fc_act * 20.0
                    unit_fr = fuel_day / (prod_bcm / len(units_sample))
                    
                    clean_u = unit.replace(" ", "").replace("-", "").lower()
                    eq_id = eq_map.get(unit) or eq_map.get(clean_u)
                    
                    sp_log = UnitAnomalySpike(
                        log_date=cur_date,
                        unit_code=unit,
                        activity=act,
                        equipment_id=eq_id,
                        fc_actual=fc_act,
                        unit_fuel_day=fuel_day,
                        unit_fr=unit_fr,
                        nn_anomaly_spike=is_spike,
                        reconstruction_error=0.08 if is_spike else 0.005
                    )
                    db.add(sp_log)
                    
            db.commit()
            print(" [OK] 365 Hari Time-Series Historical Logs berhasil di-seed.")
            
        # Sync PostgreSQL PK sequence
        if "postgresql" in str(engine.url):
            try:
                db.execute(text("SELECT setval('daily_forecast_logs_id_seq', (SELECT COALESCE(MAX(id), 1) FROM daily_forecast_logs));"))
                db.execute(text("SELECT setval('weather_daily_logs_id_seq', (SELECT COALESCE(MAX(id), 1) FROM weather_daily_logs));"))
                db.execute(text("SELECT setval('unit_anomaly_spikes_id_seq', (SELECT COALESCE(MAX(id), 1) FROM unit_anomaly_spikes));"))
                db.commit()
            except Exception as seq_err:
                db.rollback()

        print("\n=== SEEDING COMPLETED SUCCESSFULLY ===")
    except Exception as e:
        db.rollback()
        print(f" ERROR saat Seeding Database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
