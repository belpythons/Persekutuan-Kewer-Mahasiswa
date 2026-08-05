import os
import re
import psycopg2

def run_seed():
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
    conn.autocommit = False
    cursor = conn.cursor()

    sql_file_path = os.path.join(os.path.dirname(__file__), "..", "database_schema_and_seed.sql")
    print(f"Reading SQL file: {sql_file_path}")

    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Remove backtick quote characters
    pg_sql = sql_content.replace("`", "")

    # Extract all INSERT statements
    insert_statements = [s.strip() + ";" for s in pg_sql.split(";") if s.strip().startswith("INSERT INTO")]
    print(f"Total INSERT statements to seed: {len(insert_statements)}")

    batch_size = 200
    inserted_count = 0
    error_count = 0

    for i in range(0, len(insert_statements), batch_size):
        batch_chunk = insert_statements[i:i + batch_size]
        batch_sql = "\n".join(batch_chunk)
        try:
            cursor.execute(batch_sql)
            conn.commit()
            inserted_count += len(batch_chunk)
            print(f"Seeded batch {i // batch_size + 1}/{(len(insert_statements) + batch_size - 1) // batch_size} ({inserted_count}/{len(insert_statements)} inserts)")
        except Exception as e:
            conn.rollback()
            # Retry item by item in chunk
            for stmt in batch_chunk:
                try:
                    cursor.execute(stmt)
                    conn.commit()
                    inserted_count += 1
                except Exception as ex:
                    conn.rollback()
                    error_count += 1
                    if error_count <= 5:
                        print(f"Warning inserting item: {ex}")

    print("\n--- Supabase Database Seeding Completed ---")
    print(f"Successfully inserted rows: {inserted_count}")
    print(f"Errors/Skipped: {error_count}")

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

    print("\n--- Supabase Final Table Row Counts ---")
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
    run_seed()
