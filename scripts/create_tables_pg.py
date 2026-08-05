import os
import psycopg2

def create_schema():
    host = os.getenv("DB_HOST", "aws-0-ap-southeast-1.pooler.supabase.com")
    port = int(os.getenv("DB_PORT", "6543"))
    database = os.getenv("DB_DATABASE", "postgres")
    user = os.getenv("DB_USERNAME", "postgres.nxgurgphgoelraasauqt")
    password = os.getenv("DB_PASSWORD", "SiG8AHzB5E4BxtV2")

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=user,
        password=password,
        sslmode="require"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    schema_statements = [
        """
        CREATE TABLE IF NOT EXISTS equipment_catalogs (
            id SERIAL PRIMARY KEY,
            unit_name VARCHAR(100) NOT NULL UNIQUE,
            qty INTEGER NOT NULL DEFAULT 1,
            activity VARCHAR(50) NOT NULL,
            fc_lhr DOUBLE PRECISION NOT NULL
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_eq_catalog_name ON equipment_catalogs(unit_name);",
        "CREATE INDEX IF NOT EXISTS idx_eq_catalog_activity ON equipment_catalogs(activity);",

        """
        CREATE TABLE IF NOT EXISTS loading_units_baseline (
            id SERIAL PRIMARY KEY,
            unit_code VARCHAR(100) NOT NULL UNIQUE,
            activity VARCHAR(50) NOT NULL DEFAULT 'Loading',
            fc_lhr DOUBLE PRECISION NOT NULL,
            prod_bcmhr DOUBLE PRECISION NOT NULL
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS hauling_units_baseline (
            id SERIAL PRIMARY KEY,
            unit_code VARCHAR(100) NOT NULL UNIQUE,
            activity VARCHAR(50) NOT NULL DEFAULT 'Hauling',
            fc_lhr DOUBLE PRECISION NOT NULL,
            prod_bcmhr DOUBLE PRECISION NOT NULL
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS supporting_units_baseline (
            id SERIAL PRIMARY KEY,
            unit_code VARCHAR(100) NOT NULL UNIQUE,
            activity VARCHAR(50) NOT NULL DEFAULT 'Supporting',
            pa DOUBLE PRECISION,
            ua DOUBLE PRECISION,
            fc_lhr DOUBLE PRECISION NOT NULL
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS dewatering_units_baseline (
            id SERIAL PRIMARY KEY,
            unit_code VARCHAR(100) NOT NULL UNIQUE,
            activity VARCHAR(50) NOT NULL DEFAULT 'Dewatering',
            pa DOUBLE PRECISION,
            ua DOUBLE PRECISION,
            fc_lhr DOUBLE PRECISION NOT NULL
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS weather_daily_logs (
            id SERIAL PRIMARY KEY,
            log_date DATE NOT NULL UNIQUE,
            curah_hujan_mm DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            temp_max_c DOUBLE PRECISION NOT NULL DEFAULT 32.0,
            kecepatan_angin_kmh DOUBLE PRECISION NOT NULL DEFAULT 12.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_weather_date ON weather_daily_logs(log_date);",

        """
        CREATE TABLE IF NOT EXISTS daily_forecast_logs (
            id SERIAL PRIMARY KEY,
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
        """,
        "CREATE INDEX IF NOT EXISTS idx_forecast_date ON daily_forecast_logs(log_date);",

        """
        CREATE TABLE IF NOT EXISTS unit_anomaly_spikes (
            id SERIAL PRIMARY KEY,
            log_date DATE NOT NULL,
            unit_code VARCHAR(100) NOT NULL,
            activity VARCHAR(50) NOT NULL,
            equipment_id INTEGER REFERENCES equipment_catalogs(id) ON DELETE SET NULL,
            fc_actual DOUBLE PRECISION NOT NULL,
            unit_fuel_day DOUBLE PRECISION NOT NULL,
            unit_fr DOUBLE PRECISION NOT NULL,
            nn_anomaly_spike INTEGER NOT NULL DEFAULT 0,
            reconstruction_error DOUBLE PRECISION DEFAULT 0.0
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_unit_anomaly_date ON unit_anomaly_spikes(log_date);",
        "CREATE INDEX IF NOT EXISTS idx_unit_anomaly_unit ON unit_anomaly_spikes(unit_code);",

        """
        CREATE TABLE IF NOT EXISTS capacity_allocations (
            id SERIAL PRIMARY KEY,
            log_date DATE NOT NULL UNIQUE,
            installed_prod_bcmhr DOUBLE PRECISION NOT NULL,
            effective_prod_bcmday DOUBLE PRECISION NOT NULL,
            utilization_pct DOUBLE PRECISION NOT NULL,
            operating_units INTEGER NOT NULL,
            combined_fuel_lday DOUBLE PRECISION NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_capacity_date ON capacity_allocations(log_date);",

        """
        CREATE TABLE IF NOT EXISTS capacity_unit_allocations (
            id SERIAL PRIMARY KEY,
            capacity_allocation_id INTEGER NOT NULL REFERENCES capacity_allocations(id) ON DELETE CASCADE,
            log_date DATE NOT NULL,
            unit_name VARCHAR(100) NOT NULL,
            activity VARCHAR(50) NOT NULL,
            total_qty INTEGER NOT NULL,
            operating_units INTEGER NOT NULL,
            prod_bcm_hr_unit DOUBLE PRECISION NOT NULL,
            prod_bcm_hr_total DOUBLE PRECISION NOT NULL,
            fuel_l_hr_unit DOUBLE PRECISION NOT NULL,
            fuel_l_day_total DOUBLE PRECISION NOT NULL
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS fuel_ratio_logs (
            id SERIAL PRIMARY KEY,
            equipment_id VARCHAR(50) NOT NULL,
            operating_hours NUMERIC(8,2) NOT NULL,
            fuel_consumed_liters NUMERIC(8,2) NOT NULL,
            load_tonnage NUMERIC(8,2) NOT NULL,
            calculated_fuel_ratio NUMERIC(8,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]

    for stmt in schema_statements:
        try:
            cursor.execute(stmt)
            print("Successfully executed DDL statement.")
        except Exception as e:
            print(f"Error executing DDL: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_schema()
