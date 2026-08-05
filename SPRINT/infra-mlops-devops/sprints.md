# Infra & MLOps DevOps — Dekomposisi Sprint 1 hingga Sprint 18

Dokumen ini berisi panduan implementasi teknis mendetail per sprint untuk sub-proyek **`infra-mlops-devops/`** (Docker, PostgreSQL, Redis, CI/CD, Security, Grafana & MLOps) berdasarkan acuan `implementation_plan.md` dan `prd.md`.

---

## 📅 Matriks Ringkasan Sprint `infra-mlops-devops/`

| Sprint | Judul / Fokus Utama | Output / Deliverable | Target Celah |
|:-------|:-------------------|:---------------------|:-------------|
| **Sprint 1** | Docker Compose & Local Stack | `docker-compose.yml` (Postgres, Redis, PHP, Python) | Local Environment |
| **Sprint 11**| Read-Only Chatbot Role | User PostgreSQL `chatbot_reader` (SELECT-only) | #2 (SQL Injection) |
| **Sprint 13**| Security & CORS/SSL Setup | Nginx SSL Config, CORS, CSP Headers | Security Hardening |
| **Sprint 14**| Automated CI/CD Pipeline | GitHub Actions Workflow (`ci.yml`) | Automated Testing |
| **Sprint 16**| Production Multi-Stage Deployment | Production Server Setup & Docker Multi-stage | Prod Infrastructure |
| **Sprint 17**| MLOps Monitoring & Alerting | Prometheus + Grafana Stack & Data Drift Alert | #3 (Retraining MLOps) |

---

## 🛠️ Detil Instruksi Pengerjaan Per Sprint

### 📌 Sprint 1: Docker Compose Environment
**Folder Target:** `infra-mlops-devops/`
- **Langkah Pengerjaan:**
  1. Buat file `docker-compose.yml`:
     ```yaml
     version: '3.8'
     services:
       postgres:
         image: postgres:16-alpine
         environment:
           POSTGRES_DB: kideco_fuel_ratio
           POSTGRES_USER: kideco_user
           POSTGRES_PASSWORD: kideco_secret
         ports:
           - "5432:5432"
         volumes:
           - pgdata:/var/lib/postgresql/data

       redis:
         image: redis:7-alpine
         ports:
           - "6379:6379"

       laravel-app:
         build:
           context: ../laravel-web-portal
         ports:
           - "8000:8000"
         depends_on:
           - postgres
           - redis

       python-ai:
         build:
           context: ../python-ai-service
         ports:
           - "8001:8000"
         depends_on:
           - postgres

     volumes:
       pgdata:
     ```

---

### 📌 Sprint 11: Dedicated Read-Only Chatbot Role (Solusi Celah #2)
- **Langkah Pengerjaan:**
  1. Buat SQL Seeder Script `init-chatbot-read-only.sql`:
     ```sql
     -- Buat role khusus chatbot read-only
     CREATE USER chatbot_reader WITH PASSWORD 'read_only_secret';
     GRANT CONNECT ON DATABASE kideco_fuel_ratio TO chatbot_reader;
     GRANT USAGE ON SCHEMA public TO chatbot_reader;
     
     -- Hanya izinkan SELECT pada tabel-tabel aman
     GRANT SELECT ON equipment_catalogs, daily_forecast_logs, unit_anomaly_spikes, capacity_allocations, weather_daily_logs TO chatbot_reader;
     
     -- TEGAS: Revoke privileges modifikasi
     REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM chatbot_reader;
     ```

---

### 📌 Sprint 14: GitHub Actions CI/CD Pipeline
- **Langkah Pengerjaan:**
  1. Buat Workflow File `.github/workflows/ci.yml`:
     ```yaml
     name: CI/CD Pipeline

     on:
       push:
         branches: [ main, develop ]
       pull_request:
         branches: [ main ]

     jobs:
       test-laravel:
         runs-on: ubuntu-latest
         steps:
           - uses: actions/checkout@v3
           - name: Setup PHP
             uses: shivammathur/setup-php@v2
             with:
               php-version: '8.2'
           - name: Run PHPUnit Tests
             run: |
               cd laravel-web-portal
               composer install
               php artisan test

       test-python-ai:
         runs-on: ubuntu-latest
         steps:
           - uses: actions/checkout@v3
           - name: Setup Python
             uses: actions/setup-python@v4
             with:
               python-version: '3.11'
           - name: Run PyTest
             run: |
               cd python-ai-service
               pip install -r requirements.txt
               pytest
     ```

---

### 📌 Sprint 17: MLOps Prometheus & Grafana Monitoring (Solusi Celah #3)
- **Langkah Pengerjaan:**
  1. Buat `docker-compose.monitoring.yml` memasang Prometheus + Grafana.
  2. Dapatkan metric latensi inferensi FastAPI dan R² model harian.
  3. Konfigurasi Alertmanager Grafana jika data drift terdeteksi atau R² model turun di bawah 0.70.
