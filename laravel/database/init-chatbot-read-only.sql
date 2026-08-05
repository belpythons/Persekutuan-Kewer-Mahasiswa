-- ==============================================================================
-- KIDECO FUEL RATIO OPTIMIZATION SYSTEM - READ-ONLY CHATBOT DATABASE ROLE
-- Solusi Celah Keamanan #2: Mencegah SQL Injection via Least Privilege Principle
-- ==============================================================================

-- 1. Buat role khusus chatbot_reader jika belum ada
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'chatbot_reader') THEN
        CREATE USER chatbot_reader WITH PASSWORD 'chatbot_read_only_secret_2026';
    END IF;
END $$;

-- 2. Hak koneksi ke database dan penggunaan schema public
GRANT CONNECT ON DATABASE kideco_fuel_ratio TO chatbot_reader;
GRANT USAGE ON SCHEMA public TO chatbot_reader;

-- 3. Berikan izin SELECT HANYA pada tabel-tabel operasional aman
GRANT SELECT ON TABLE equipment_catalogs TO chatbot_reader;
GRANT SELECT ON TABLE daily_forecast_logs TO chatbot_reader;
GRANT SELECT ON TABLE unit_anomaly_spikes TO chatbot_reader;
GRANT SELECT ON TABLE capacity_allocations TO chatbot_reader;
GRANT SELECT ON TABLE weather_daily_logs TO chatbot_reader;

-- 4. TEGAS: Cabut seluruh hak modifikasi data & DDL
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM chatbot_reader;
