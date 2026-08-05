# [TASK-01] Docker Compose Local Multi-Container Environment

## 1. Metadata
- **Sprint**: Infra-MLOps-DevOps - Sprint 1
- **Kategori**: Infrastructure
- **Status**: Ready for Implementation
- **Estimasi Effort**: 8 Story Points (~16 Jam)

## 2. Deskripsi Task
Menyusun dan mengonfigurasi Orkestrasi Container berbasis Docker Compose untuk lingkungan pengembangan lokal. Arsitektur mencakup service PostgreSQL 16 Alpine, Redis 7, Laravel Web Portal (PHP 8.2), dan Python AI Microservice (FastAPI + XGBoost + PyTorch Autoencoder). Pengkonfigurasian ini menjamin paritas lingkungan lokal dengan server staging/produksi serta memfasilitasi interkoneksi antar layanan tanpa hambatan jaringan lokal.

## 3. Objective & Key Results (OKR)
- Objective: Menyediakan infrastruktur lokal ter-kontainerisasi yang konsisten dan siap pakai untuk seluruh tim pengembang.
- Key Results:
  - [ ] Kontainer PostgreSQL 16, Redis 7, Laravel Web Portal, dan Python AI Service dapat di-spin up dengan 1 perintah (`docker-compose up -d`).
  - [ ] Volume persistensi data PostgreSQL (`pgdata`) terisolasi dengan aman dari siklus pembuangan kontainer.
  - [ ] Jaringan internal Docker (`kideco_network`) terkonfigurasi untuk mengizinkan komunikasi HTTP antar servis secara aman.

## 4. Technical Deliverables & Specifications
- **Target Files**:
  - `infra-mlops-devops/docker-compose.yml`
  - `.env.example`
- **Konfigurasi Environment Variables (`.env.example`)**:
  ```env
  APP_ENV=local
  POSTGRES_DB=kideco_fuel_ratio
  POSTGRES_USER=kideco_user
  POSTGRES_PASSWORD=kideco_secret
  POSTGRES_HOST=postgres
  POSTGRES_PORT=5432
  REDIS_HOST=redis
  REDIS_PORT=6379
  PYTHON_AI_SERVICE_URL=http://python-ai:8000
  ```
- **Langkah Implementasi Teknis**:
  1. Buat file `docker-compose.yml` pada root repository atau folder infrastruktur.
  2. Definisikan service `postgres` menggunakan image `postgres:16-alpine` beserta mounting volume persistensi ke `/var/lib/postgresql/data`.
  3. Definisikan service `redis` menggunakan image `redis:7-alpine` untuk kebutuhan caching & queue Laravel.
  4. Build service `laravel-portal` menunjuk ke folder `laravel-web-portal/` dengan expose port `8000`.
  5. Build service `python-ai` menunjuk ke folder `python-ai-service/` dengan expose port `8001:8000`.
  6. Uji konektivitas antar container menggunakan `docker exec` dan `curl`.

## 5. Acceptance Criteria (Definition of Done)
- [ ] Seluruh container (`postgres`, `redis`, `laravel-portal`, `python-ai`) berstatus `Up (healthy)`.
- [ ] Aplikasi Laravel Web Portal dapat melakukan koneksi ke database PostgreSQL dan Redis via nama service container.
- [ ] Microservice Python AI dapat merespons request GET `/health` dan POST `/api/v1/forecast` secara lokal.
