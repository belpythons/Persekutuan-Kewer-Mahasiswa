import os

# Baseline Fuel Ratio Budget (L/BCM)
BASE_TOTAL_FR_BUDGET = float(os.getenv("BASE_FR_BUDGET", "1.018"))

# Dynamic Threshold Multipliers (+8% Warning, +18% Critical)
WARNING_THRESHOLD_PCT = float(os.getenv("WARNING_THRESHOLD_PCT", "0.08"))
CRITICAL_THRESHOLD_PCT = float(os.getenv("CRITICAL_THRESHOLD_PCT", "0.18"))

# Jam Operasional Efektif per Hari
OPERATING_HOURS_PER_DAY = float(os.getenv("OPERATING_HOURS_DAY", "20.0"))

# Buffer BBM Penyesuaian Anomali Lonjakan Spike (+15% per unit spike)
NN_SPIKE_BUFFER_PCT = float(os.getenv("NN_SPIKE_BUFFER_PCT", "0.15"))

# Nilai Standard Imputation / Imputation Defaults
DEFAULT_HAUL_DISTANCE_M = float(os.getenv("DEFAULT_HAUL_DISTANCE_M", "3900.0"))
DEFAULT_DAILY_PROD_BCM = float(os.getenv("DEFAULT_DAILY_PROD_BCM", "40000.0"))
DEFAULT_TEMP_MAX_C = float(os.getenv("DEFAULT_TEMP_MAX_C", "32.0"))
DEFAULT_WIND_KMH = float(os.getenv("DEFAULT_WIND_KMH", "12.0"))
DEFAULT_RAIN_MM = float(os.getenv("DEFAULT_RAIN_MM", "0.0"))
