# [TASK-02] Dedicated Read-Only PostgreSQL Role (`chatbot_reader`)

## 1. Metadata
- **Sprint**: Infra-MLOps-DevOps - Sprint 11
- **Kategori**: Security / Database Infrastructure
- **Status**: Ready for Implementation
- **Estimasi Effort**: 5 Story Points (~10 Jam)

## 2. Deskripsi Task
Mengimplementasikan peran (*role*) basis data terpisah berbasis akses baca murni (`SELECT`-only) bernama `chatbot_reader` pada PostgreSQL database. Tugas ini dirancang khusus untuk memitigasi celah keamanan **SQL Injection (Solusi Celah #2)** pada modul AI Chatbot Retrieval. Dengan membatasi privilege role ini hanya pada hak pembacaan tabel aman dan secara tegas mencabut izin modifikasi (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`), potensi kerusakan akibat peretasan kueri raw SQL atau manipulasi input user pada Chatbot dapat dibatasi penuh (*Least Privilege Principle*).

## 3. Objective & Key Results (OKR)
- Objective: Menjamin modul AI Chatbot Retrieval berjalan pada kredensial basis data terspesialisasi berbasis izin baca murni.
- Key Results:
  - [ ] Role `chatbot_reader` berhasil dibuat dengan password yang ter-enkripsi.
  - [ ] Hak akses `SELECT` hanya diberikan pada tabel yang diizinkan (`equipment_catalogs`, `daily_forecast_logs`, `unit_anomaly_spikes`, `capacity_allocations`, `weather_daily_logs`).
  - [ ] Hak operasi modifikasi skema/data (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`) secara tegas dicabut (`REVOKE`).

## 4. Technical Deliverables & Specifications
- **Target Files**:
  - `infra-mlops-devops/scripts/init-chatbot-read-only.sql`
  - `laravel-web-portal/config/database.php`
- **Script DDL SQL (`init-chatbot-read-only.sql`)**:
  ```sql
  -- 1. Buat user/role khusus chatbot read-only jika belum ada
  DO $$
  BEGIN
      IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'chatbot_reader') THEN
          CREATE USER chatbot_reader WITH PASSWORD 'chatbot_read_only_secret_2026';
      END IF;
  END $$;

  -- 2. Hak koneksi dan penggunaan schema public
  GRANT CONNECT ON DATABASE kideco_fuel_ratio TO chatbot_reader;
  GRANT USAGE ON SCHEMA public TO chatbot_reader;

  -- 3. Berikan izin SELECT HANYA pada tabel operasional aman
  GRANT SELECT ON TABLE equipment_catalogs TO chatbot_reader;
  GRANT SELECT ON TABLE daily_forecast_logs TO chatbot_reader;
  GRANT SELECT ON TABLE unit_anomaly_spikes TO chatbot_reader;
  GRANT SELECT ON TABLE capacity_allocations TO chatbot_reader;
  GRANT SELECT ON TABLE weather_daily_logs TO chatbot_reader;

  -- 4. Cabut secara tegas seluruh hak modifikasi data & DDL
  REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM chatbot_reader;
  ```
- **Langkah Implementasi Teknis**:
  1. Buat file script SQL `init-chatbot-read-only.sql` pada folder scripts infrastruktur.
  2. Eksekusi script SQL ke database PostgreSQL (dapat diotomatisasi pada docker entrypoint `/docker-entrypoint-initdb.d/`).
  3. Konfigurasi koneksi sekunder `DB_CONNECTION_CHATBOT` pada Laravel `.env` dan `config/database.php` menggunakan kredensial `chatbot_reader`.

## 5. Acceptance Criteria (Definition of Done)
- [ ] User `chatbot_reader` berhasil terdaftar pada PostgreSQL `pg_roles`.
- [ ] Pengujian kueri `SELECT` menggunakan user `chatbot_reader` pada tabel terdaftar berjalan sukses.
- [ ] Pengujian eksekusi `UPDATE` / `DELETE` / `DROP` menggunakan user `chatbot_reader` ditolak oleh PostgreSQL dengan error `permission denied for table`.
