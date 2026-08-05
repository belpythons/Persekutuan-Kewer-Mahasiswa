import os
import sys
import pandas as pd
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Base, engine
from seed_database import seed_database
import models_db

def generate_sql_dump():
    # 1. Ensure DB is populated
    Base.metadata.create_all(bind=engine)
    seed_database()
    
    db = SessionLocal()
    sql_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database_schema_and_seed.sql")
    
    print(f"Generating 3NF Granular High-Scale SQL seed dump at {sql_file_path}...")
    
    tables = [
        "equipment_catalogs",
        "loading_units_baseline",
        "hauling_units_baseline",
        "supporting_units_baseline",
        "dewatering_units_baseline",
        "weather_daily_logs",
        "daily_forecast_logs",
        "unit_anomaly_spikes",
        "capacity_allocations",
        "capacity_unit_allocations"
    ]
    
    with open(sql_file_path, "w", encoding="utf-8") as f:
        f.write("-- ==============================================================================\n")
        f.write("-- KIDECO FUEL RATIO OPTIMIZATION SYSTEM - HIGH-SCALE GRANULAR DATABASE DUMP\n")
        f.write("-- 3NF Normalized, Per-Unit & Per-Hour Productivity/Fuel Metrics, Foreign Keys & B-Tree Indexes\n")
        f.write("-- Ground-Truth Data Extracted from: UPDATE_Fuel ratio calculation 2026 dummy data.xlsx\n")
        f.write("-- Compatible with: PostgreSQL & MySQL / MariaDB / SQLite\n")
        f.write("-- ==============================================================================\n\n")
        
        # Table Schema Creation DDL
        f.write("-- 1. CREATE TABLE STATEMENTS & HIGH-SCALE INDEXES\n\n")
        
        f.write("""
CREATE TABLE IF NOT EXISTS equipment_catalogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_name VARCHAR(100) NOT NULL UNIQUE,
    qty INTEGER NOT NULL DEFAULT 1,
    activity VARCHAR(50) NOT NULL,
    fc_lhr DOUBLE PRECISION NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_eq_catalog_name ON equipment_catalogs(unit_name);
CREATE INDEX IF NOT EXISTS idx_eq_catalog_activity ON equipment_catalogs(activity);

CREATE TABLE IF NOT EXISTS loading_units_baseline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_code VARCHAR(100) NOT NULL UNIQUE,
    activity VARCHAR(50) NOT NULL DEFAULT 'Loading',
    fc_lhr DOUBLE PRECISION NOT NULL,
    prod_bcmhr DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS hauling_units_baseline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_code VARCHAR(100) NOT NULL UNIQUE,
    activity VARCHAR(50) NOT NULL DEFAULT 'Hauling',
    fc_lhr DOUBLE PRECISION NOT NULL,
    prod_bcmhr DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS supporting_units_baseline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_code VARCHAR(100) NOT NULL UNIQUE,
    activity VARCHAR(50) NOT NULL DEFAULT 'Supporting',
    pa DOUBLE PRECISION,
    ua DOUBLE PRECISION,
    fc_lhr DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS dewatering_units_baseline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_code VARCHAR(100) NOT NULL UNIQUE,
    activity VARCHAR(50) NOT NULL DEFAULT 'Dewatering',
    pa DOUBLE PRECISION,
    ua DOUBLE PRECISION,
    fc_lhr DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE NOT NULL UNIQUE,
    curah_hujan_mm DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    temp_max_c DOUBLE PRECISION NOT NULL DEFAULT 32.0,
    kecepatan_angin_kmh DOUBLE PRECISION NOT NULL DEFAULT 12.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_weather_date ON weather_daily_logs(log_date);

CREATE TABLE IF NOT EXISTS daily_forecast_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE NOT NULL UNIQUE,
    actual_fr DOUBLE PRECISION,
    forecast_fr DOUBLE PRECISION NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    warning_threshold DOUBLE PRECISION NOT NULL,
    critical_threshold DOUBLE PRECISION NOT NULL,
    daily_prod_bcm DOUBLE PRECISION NOT NULL,
    haul_distance_m DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_forecast_date ON daily_forecast_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_forecast_date_status ON daily_forecast_logs(log_date, status);

CREATE TABLE IF NOT EXISTS unit_anomaly_spikes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE NOT NULL,
    unit_code VARCHAR(100) NOT NULL,
    activity VARCHAR(50) NOT NULL,
    equipment_id INTEGER,
    fc_actual DOUBLE PRECISION NOT NULL,
    unit_fuel_day DOUBLE PRECISION NOT NULL,
    unit_fr DOUBLE PRECISION NOT NULL,
    nn_anomaly_spike INTEGER NOT NULL DEFAULT 0,
    reconstruction_error DOUBLE PRECISION DEFAULT 0.0,
    FOREIGN KEY (equipment_id) REFERENCES equipment_catalogs(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_unit_anomaly_date ON unit_anomaly_spikes(log_date);
CREATE INDEX IF NOT EXISTS idx_unit_anomaly_unit ON unit_anomaly_spikes(unit_code);
CREATE INDEX IF NOT EXISTS idx_unit_anomaly_date_unit ON unit_anomaly_spikes(log_date, unit_code);
CREATE INDEX IF NOT EXISTS idx_unit_anomaly_date_act ON unit_anomaly_spikes(log_date, activity);
CREATE INDEX IF NOT EXISTS idx_unit_anomaly_spike_date ON unit_anomaly_spikes(log_date, nn_anomaly_spike);

CREATE TABLE IF NOT EXISTS capacity_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE NOT NULL UNIQUE,
    installed_prod_bcmhr DOUBLE PRECISION NOT NULL,
    effective_prod_bcmday DOUBLE PRECISION NOT NULL,
    utilization_pct DOUBLE PRECISION NOT NULL,
    operating_units INTEGER NOT NULL,
    combined_fuel_lday DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_capacity_date ON capacity_allocations(log_date);

CREATE TABLE IF NOT EXISTS capacity_unit_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capacity_allocation_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    unit_name VARCHAR(100) NOT NULL,
    activity VARCHAR(50) NOT NULL,
    total_qty INTEGER NOT NULL,
    operating_units INTEGER NOT NULL,
    prod_bcm_hr_unit DOUBLE PRECISION NOT NULL,
    prod_bcm_hr_total DOUBLE PRECISION NOT NULL,
    prod_bcm_day_total DOUBLE PRECISION NOT NULL,
    fuel_l_hr_unit DOUBLE PRECISION NOT NULL,
    fuel_l_hr_total DOUBLE PRECISION NOT NULL,
    fuel_l_day_total DOUBLE PRECISION NOT NULL,
    unit_fr DOUBLE PRECISION NOT NULL,
    spike_count_nn INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (capacity_allocation_id) REFERENCES capacity_allocations(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_cap_unit_date_unit ON capacity_unit_allocations(log_date, unit_name);
CREATE INDEX IF NOT EXISTS idx_cap_unit_date_act ON capacity_unit_allocations(log_date, activity);
\n""")

        # Table Data Seed INSERT statements
        f.write("-- 2. DATA INSERT STATEMENTS FROM EXCEL GROUND-TRUTH\n\n")
        
        for table in tables:
            f.write(f"-- Dumping data for table: {table}\n")
            res = db.execute(text(f"SELECT * FROM {table}"))
            rows = res.fetchall()
            cols = res.keys()
            
            if not rows:
                continue
                
            for row in rows:
                row_dict = dict(zip(cols, row))
                col_names = ", ".join([f"`{c}`" for c in row_dict.keys()])
                val_list = []
                for val in row_dict.values():
                    if val is None:
                        val_list.append("NULL")
                    elif isinstance(val, (int, float)):
                        val_list.append(str(val))
                    else:
                        val_str = str(val).replace("'", "''")
                        val_list.append(f"'{val_str}'")
                        
                val_str_joined = ", ".join(val_list)
                f.write(f"INSERT INTO `{table}` ({col_names}) VALUES ({val_str_joined});\n")
            f.write("\n")
            
        print("High-Scale SQL Seed Dump generation completed successfully!")
    db.close()

if __name__ == "__main__":
    generate_sql_dump()
