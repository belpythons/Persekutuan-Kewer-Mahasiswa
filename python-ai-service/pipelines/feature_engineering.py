import pandas as pd
import numpy as np
from typing import List, Tuple
from operational_constants import DEFAULT_WIND_KMH, DEFAULT_TEMP_MAX_C, DEFAULT_RAIN_MM

# Daftar 13 Fitur Wajib Sesuai Implementation Plan (Celah #13 resolved)
FEATURE_COLUMNS: List[str] = [
    'Curah_Hujan_mm',
    'Temp_Max_C',
    'Kecepatan_Angin_kmh',  # Wajib dimasukkan
    'Haul_Distance_m',
    'Daily_Prod_BCM',
    'DayOfWeek',
    'Month',
    'IsWeekend',
    'Rain_Lag1',
    'Rain_Lag2',
    'FR_Lag1',
    'FR_Lag2',
    'RollingAvg_FR_7d'
]

def build_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Mengekstrak dan mentransformasi 13+ fitur ML dari data mentah harian.
    
    Parameters:
    - df: DataFrame berisi kolom 'Date', 'Curah_Hujan_mm', 'Temp_Max_C', 
          'Kecepatan_Angin_kmh', 'Haul_Distance_m', 'Daily_Prod_BCM', 'Actual_FR_L_BCM'
          
    Returns:
    - Tuple (df_transformed, FEATURE_COLUMNS)
    """
    df_transformed = df.copy()
    
    # Pastikan kolom Date bertipe datetime
    if not pd.api.types.is_datetime64_any_dtype(df_transformed['Date']):
        df_transformed['Date'] = pd.to_datetime(df_transformed['Date'])
        
    # Urutkan berdasarkan tanggal
    df_transformed = df_transformed.sort_values('Date').reset_index(drop=True)
    
    # Fitur Kalender & Temporal
    df_transformed['DayOfWeek'] = df_transformed['Date'].dt.dayofweek
    df_transformed['Month'] = df_transformed['Date'].dt.month
    df_transformed['IsWeekend'] = df_transformed['DayOfWeek'].isin([5, 6]).astype(int)
    
    # Fitur Lag Hujan
    df_transformed['Rain_Lag1'] = df_transformed['Curah_Hujan_mm'].shift(1).fillna(0.0)
    df_transformed['Rain_Lag2'] = df_transformed['Curah_Hujan_mm'].shift(2).fillna(0.0)
    
    # Fitur Lag Fuel Ratio (jika Actual_FR_L_BCM ada)
    if 'Actual_FR_L_BCM' in df_transformed.columns:
        df_transformed['FR_Lag1'] = df_transformed['Actual_FR_L_BCM'].shift(1).bfill()
        df_transformed['FR_Lag2'] = df_transformed['Actual_FR_L_BCM'].shift(2).bfill()
        df_transformed['RollingAvg_FR_7d'] = (
            df_transformed['Actual_FR_L_BCM']
            .shift(1)
            .rolling(window=7, min_periods=1)
            .mean()
            .bfill()
        )
    else:
        # Fallback jika prediksi real-time (tanpa Actual FR hari H)
        df_transformed['FR_Lag1'] = 0.0
        df_transformed['FR_Lag2'] = 0.0
        df_transformed['RollingAvg_FR_7d'] = 0.0

    # Pastikan nilai default jika ada missing value
    df_transformed['Kecepatan_Angin_kmh'] = df_transformed['Kecepatan_Angin_kmh'].fillna(DEFAULT_WIND_KMH)
    df_transformed['Temp_Max_C'] = df_transformed['Temp_Max_C'].fillna(DEFAULT_TEMP_MAX_C)
    df_transformed['Curah_Hujan_mm'] = df_transformed['Curah_Hujan_mm'].fillna(DEFAULT_RAIN_MM)
    
    return df_transformed, FEATURE_COLUMNS

def get_feature_names() -> List[str]:
    """
    Mengembalikan daftar 13 nama fitur
    """
    return FEATURE_COLUMNS.copy()
