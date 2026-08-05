import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Tuple, Optional, Dict, Any
import logging

from models_db import WeatherDailyLog, DailyForecastLog, UnitAnomalySpike, EquipmentCatalog
from pipelines.feature_engineering import build_features, FEATURE_COLUMNS
from operational_constants import (
    DEFAULT_HAUL_DISTANCE_M,
    DEFAULT_DAILY_PROD_BCM,
    DEFAULT_TEMP_MAX_C,
    DEFAULT_WIND_KMH,
    DEFAULT_RAIN_MM
)

logger = logging.getLogger(__name__)

def load_historical_weather_and_forecasts(db_session: Session) -> pd.DataFrame:
    """
    Penarikan data historis gabungan antara weather logs dan forecast logs dari database.
    """
    query = text(f"""
        SELECT 
            w.log_date AS "Date",
            w.curah_hujan_mm AS "Curah_Hujan_mm",
            w.temp_max_c AS "Temp_Max_C",
            w.kecepatan_angin_kmh AS "Kecepatan_Angin_kmh",
            COALESCE(f.haul_distance_m, {DEFAULT_HAUL_DISTANCE_M}) AS "Haul_Distance_m",
            COALESCE(f.daily_prod_bcm, {DEFAULT_DAILY_PROD_BCM}) AS "Daily_Prod_BCM",
            f.actual_fr AS "Actual_FR_L_BCM"
        FROM weather_daily_logs w
        LEFT JOIN daily_forecast_logs f ON w.log_date = f.log_date
        ORDER BY w.log_date ASC
    """)
    
    result = db_session.execute(query)
    rows = result.fetchall()
    
    if not rows:
        logger.warning("Data historis di database kosong. Mengembalikan DataFrame kosong.")
        return pd.DataFrame(columns=['Date', 'Curah_Hujan_mm', 'Temp_Max_C', 'Kecepatan_Angin_kmh', 'Haul_Distance_m', 'Daily_Prod_BCM', 'Actual_FR_L_BCM'])
        
    df = pd.DataFrame(rows, columns=result.keys())
    return df

def fetch_and_prepare_dataset(db_session: Session) -> Tuple[pd.DataFrame, pd.DataFrame, list]:
    """
    Mengambil data dari DB, menjalankan Data Quality Check, dan membentuk 13 Fitur ML.
    """
    df_raw = load_historical_weather_and_forecasts(db_session)
    
    if df_raw.empty:
        return df_raw, pd.DataFrame(columns=FEATURE_COLUMNS), FEATURE_COLUMNS
        
    # Data Quality Check
    df_clean = validate_and_clean_data(df_raw)
    
    # Feature Engineering
    df_features, feature_names = build_features(df_clean)
    
    return df_clean, df_features, feature_names

def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pemeriksaan Kualitas Data (Data Quality Check):
    - Handling missing values
    - Outlier checking & clipping pada batas wajar operasional
    """
    df_clean = df.copy()
    
    # Fill NA defaults
    df_clean['Curah_Hujan_mm'] = df_clean['Curah_Hujan_mm'].fillna(DEFAULT_RAIN_MM).clip(lower=0.0, upper=200.0)
    df_clean['Temp_Max_C'] = df_clean['Temp_Max_C'].fillna(DEFAULT_TEMP_MAX_C).clip(lower=15.0, upper=50.0)
    df_clean['Kecepatan_Angin_kmh'] = df_clean['Kecepatan_Angin_kmh'].fillna(DEFAULT_WIND_KMH).clip(lower=0.0, upper=100.0)
    df_clean['Haul_Distance_m'] = df_clean['Haul_Distance_m'].fillna(DEFAULT_HAUL_DISTANCE_M).clip(lower=500.0, upper=15000.0)
    df_clean['Daily_Prod_BCM'] = df_clean['Daily_Prod_BCM'].fillna(DEFAULT_DAILY_PROD_BCM).clip(lower=1000.0, upper=150000.0)
    
    if 'Actual_FR_L_BCM' in df_clean.columns:
        # Interpolasi missing Actual FR
        df_clean['Actual_FR_L_BCM'] = df_clean['Actual_FR_L_BCM'].ffill().bfill()
        df_clean['Actual_FR_L_BCM'] = df_clean['Actual_FR_L_BCM'].clip(lower=0.1, upper=5.0)
        
    return df_clean

def load_unit_anomaly_logs(db_session: Session) -> pd.DataFrame:
    """
    Penarikan data konsumsi BBM dan spike anomali unit dari database,
    termasuk hitungan rasio pemborosan relatif (FC_Ratio, Unit_FR_Ratio, Unit_Fuel_Ratio).
    """
    query = text("""
        SELECT 
            u.log_date AS "Date",
            u.unit_code AS "Unit",
            u.activity AS "Activity",
            u.fc_actual AS "FC_Actual",
            COALESCE(c.fc_lhr, u.fc_actual) AS "FC_Base",
            (u.fc_actual / NULLIF(COALESCE(c.fc_lhr, u.fc_actual), 0)) AS "FC_Ratio",
            u.unit_fuel_day AS "Unit_Fuel_L_Day",
            u.unit_fr AS "Unit_FR",
            u.nn_anomaly_spike AS "NN_Anomaly_Spike",
            COALESCE(w.curah_hujan_mm, 0.0) AS "Rain_mm"
        FROM unit_anomaly_spikes u
        LEFT JOIN weather_daily_logs w ON u.log_date = w.log_date
        LEFT JOIN equipment_catalogs c ON u.unit_code = c.unit_name
        ORDER BY u.log_date ASC, u.unit_code ASC
    """)
    result = db_session.execute(query)
    rows = result.fetchall()
    
    if not rows:
        return pd.DataFrame(columns=['Date', 'Unit', 'Activity', 'FC_Actual', 'FC_Base', 'FC_Ratio', 'Unit_Fuel_L_Day', 'Unit_FR', 'NN_Anomaly_Spike', 'Rain_mm', 'Unit_FR_Ratio', 'Unit_Fuel_Ratio'])
        
    df = pd.DataFrame(rows, columns=result.keys())
    df['FC_Ratio'] = df['FC_Ratio'].fillna(1.0)
    
    # Hitung rata-rata baseline per unit untuk normalisasi rasio murni per unit
    unit_bases = df.groupby('Unit').agg(
        mean_fr=('Unit_FR', 'mean'),
        mean_fuel=('Unit_Fuel_L_Day', 'mean')
    ).reset_index()
    
    df = df.merge(unit_bases, on='Unit', how='left')
    df['Unit_FR_Ratio'] = (df['Unit_FR'] / df['mean_fr'].replace(0, 1.0)).fillna(1.0)
    df['Unit_Fuel_Ratio'] = (df['Unit_Fuel_L_Day'] / df['mean_fuel'].replace(0, 1.0)).fillna(1.0)
    
    return df
