import os
import re
import psycopg2

def run_migration():
    host = os.getenv("DB_HOST", "aws-0-ap-southeast-1.pooler.supabase.com")
    port = int(os.getenv("DB_PORT", "6543"))
    database = os.getenv("DB_DATABASE", "postgres")
    user = os.getenv("DB_USERNAME", "postgres.nxgurgphgoelraasauqt")
    password = os.getenv("DB_PASSWORD", "SiG8AHzB5E4BxtV2")

    print(f"Connecting to Supabase PostgreSQL at {host}:{port}/{database}...")
    
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

    sql_file_path = os.path.join(os.path.dirname(__file__), "..", "database_schema_and_seed.sql")
    print(f"Reading SQL dump file: {sql_file_path}")

    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Adapt SQLite/MySQL syntax to PostgreSQL syntax
    pg_sql = re.sub(r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', sql_content, flags=re.IGNORECASE)
    pg_sql = pg_sql.replace("`", "")

    # Split into individual statements
    raw_statements = [s.strip() for s in pg_sql.split(";") if s.strip() and not s.strip().startswith("--")]
    print(f"Total SQL statements to execute: {len(raw_statements)}")

    batch_size = 100
    executed_count = 0
    error_count = 0

    for i in range(0, len(raw_statements), batch_size):
        chunk = raw_statements[i:i + batch_size]
        batch_sql = ";\n".join(chunk) + ";"
        try:
            cursor.execute(batch_sql)
            executed_count += len(chunk)
            print(f"Executed batch {i // batch_size + 1}/{(len(raw_statements) + batch_size - 1) // batch_size} ({executed_count}/{len(raw_statements)} statements)")
        except Exception:
            # Fallback to single statement execution for chunk on error
            for stmt in chunk:
                try:
                    cursor.execute(stmt)
                    executed_count += 1
                except Exception as ex:
                    error_count += 1
                    if error_count <= 5:
                        print(f"Warning on stmt: {ex}")

    print("\n--- Supabase Database Migration & Seeding Completed ---")
    print(f"Successfully executed statements: {executed_count}")
    print(f"Warnings/Skipped: {error_count}")

    # Verify table row counts
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

    print("\n--- Supabase Table Row Counts ---")
    for tbl in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
            count = cursor.fetchone()[0]
            print(f"Table '{tbl}': {count} rows")
        except Exception as e:
            print(f"Table '{tbl}': Error ({e})")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_migration()
