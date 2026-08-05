# Dokumentasi Penyelesaian Task 1 — Environment & Database Connection Setup

Dokumen ini mencatat penyelesaian teknis untuk **Task 1 (Sprint 1-3)** pada folder `python-ai-service/`.

---

## 📌 Ringkasan Pekerjaan Task 1

Task 1 berfokus pada penyiapan struktur dasar microservice AI, dependensi Python 3.11, konfigurasi environment variabel, SQLAlchemy database engine terhubung ke PostgreSQL, serta scaffold FastAPI aplikasi beserta endpoint health check dan readiness probe.

---

## 📂 Struktur File yang Dibuat

```
python-ai-service/
├── config.py                 # Pengelolaan environment variables (Pydantic Settings)
├── database.py               # Connection pool SQLAlchemy, Session maker, & DB Health check
├── main.py                   # Scaffold FastAPI App, CORS Middleware, /health & /ready endpoints
├── requirements.txt          # Dependensi Python 3.11
└── TASK_1_DOCUMENTATION.md   # Dokumentasi teknis penyelesaian Task 1
```

---

## 🛠️ Detail Rincian Komponen Task 1

### 1. File `requirements.txt`
Mendefinisikan seluruh paket dependensi yang dibutuhkan oleh microservice AI:
- **Web Framework:** `fastapi==0.110.0`, `uvicorn==0.28.0`, `pydantic==2.6.4`, `pydantic-settings==2.2.1`
- **Machine Learning & Deep Learning:** `xgboost==2.0.3`, `torch==2.2.1`, `scikit-learn==1.4.1`, `pandas==2.2.1`, `numpy==1.26.4`, `optuna==3.5.0`
- **Database:** `sqlalchemy==2.0.28`, `psycopg2-binary==2.9.9`
- **Testing & Environment:** `pytest==8.0.2`, `python-dotenv==1.0.1`

### 2. File `config.py`
Mengelola konfigurasi variabel lingkungan menggunakan `pydantic_settings.BaseSettings`:
- Mengatur variabel `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, dan `POSTGRES_DB`.
- Membentuk properti dinamis `DATABASE_URL`: `postgresql://{user}:{password}@{host}:{port}/{db}`.

### 3. File `database.py`
Mengelola infrastruktur koneksi database relasional:
- **Connection Pool Engine:** Dibuat menggunakan SQLAlchemy `create_engine` dengan `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True` (mencegah koneksi mati), dan `pool_recycle=3600`.
- **Session Dependency:** Fungsi `get_db()` menyediakan Session SQLAlchemy per HTTP request.
- **Database Health Check:** Fungsi `check_db_connection()` mengeksekusi `SELECT 1` untuk memverifikasi keaktifan PostgreSQL.

### 4. File `main.py`
Membangun scaffold aplikasi FastAPI:
- CORS Middleware diaktifkan untuk akses aman dari frontend.
- Endpoint `GET /`: Mengembalikan info status aplikasi dan lokasi OpenAPI Swagger (`/docs`).
- Endpoint `GET /health`: Mengembalikan status kesehatan service dan koneksi PostgreSQL (`healthy`/`unhealthy`).
- Endpoint `GET /ready`: Readiness probe untuk Kubernetes/Docker orchestration.

---

## 🧪 Verifikasi & Pengujian Task 1

Verifikasi telah dilakukan dengan menguji import seluruh modul dan pengaktifan konfigurasi:

```bash
python -c "import config, database, main; print('Config APP_NAME:', config.settings.APP_NAME); print('Database URL:', config.settings.DATABASE_URL); print('Main App Title:', main.app.title)"
```

**Hasil Verifikasi:**
- `Config APP_NAME`: KIDECO Fuel Ratio AI Service
- `Database URL`: postgresql://kideco_user:kideco_secret@localhost:5432/kideco_fuel_ratio
- `Main App Title`: KIDECO Fuel Ratio AI Service

---

## 🚀 Langkah Selanjutnya (Task 2)

Setelah Task 1 selesai, langkah selanjutnya adalah mengeksekusi **Task 2 (Sprint 4)**:
- Implementasi `pipelines/data_pipeline.py` untuk penarikan data aktual dari PostgreSQL.
- Implementasi `pipelines/feature_engineering.py` mengekstraksi 13+ fitur lengkap termasuk `Kecepatan_Angin_kmh`.
