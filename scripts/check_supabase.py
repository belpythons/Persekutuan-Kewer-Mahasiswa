import os
import psycopg2

def check_tables():
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
    cursor = conn.cursor()

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
        "capacity_unit_allocations",
        "fuel_ratio_logs"
    ]

    print("--- Supabase Table Row Counts ---")
    for tbl in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
            count = cursor.fetchone()[0]
            print(f"Table '{tbl}': {count} rows")
        except Exception as e:
            conn.rollback()
            print(f"Table '{tbl}': Error ({e})")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_tables()
