# [TASK-04] Automated GitHub Actions CI/CD Testing Pipeline

## 1. Metadata
- **Sprint**: Infra-MLOps-DevOps - Sprint 14
- **Kategori**: DevOps
- **Status**: Ready for Implementation
- **Estimasi Effort**: 8 Story Points (~16 Jam)

## 2. Deskripsi Task
Membangun dan mengonfigurasi alur kerja otomatisasi *Continuous Integration* (CI) menggunakan GitHub Actions Workflow (`.github/workflows/ci.yml`). Pipeline ini dipicu secara otomatis pada setiap aksi *Push* atau *Pull Request* ke branch `main` dan `develop`. Pipeline mengeksekusi dua job paralel: pengujian PHPUnit test suite pada modul Laravel Web Portal dan pengujian PyTest test suite pada Python AI Service. Pipeline memastikan tidak ada regresi kode, kesalahan sintaks, atau kegagalan inferensi model AI yang lolos ke branch utama.

## 3. Objective & Key Results (OKR)
- Objective: Menjamin kualitas dan stabilitas seluruh kode repositori melalui pengujian otomatis sebelum penggabungan (*merge*).
- Key Results:
  - [ ] GitHub Actions Workflow terpicu secara otomatis pada push/PR ke branch `main` dan `develop`.
  - [ ] Job `test-laravel` mengeksekusi PHPUnit dan melaporkan 0 error.
  - [ ] Job `test-python-ai` menginstal `requirements.txt` dan mengeksekusi PyTest dengan 100% test pass.

## 4. Technical Deliverables & Specifications
- **Target Files**:
  - `.github/workflows/ci.yml`
- **Konfigurasi Workflow GitHub Actions (`ci.yml`)**:
  ```yaml
  name: CI/CD Automated Testing Pipeline

  on:
    push:
      branches: [ main, develop ]
    pull_request:
      branches: [ main, develop ]

  jobs:
    test-laravel-portal:
      runs-on: ubuntu-latest
      services:
        postgres:
          image: postgres:16-alpine
          env:
            POSTGRES_DB: kideco_fuel_ratio_test
            POSTGRES_USER: postgres
            POSTGRES_PASSWORD: secret_password
          ports:
            - 5432:5432
          options: >-
            --health-cmd pg_isready
            --health-interval 10s
            --health-timeout 5s
            --health-retries 5

      steps:
        - uses: actions/checkout@v3
        - name: Setup PHP Environment
          uses: shivammathur/setup-php@v2
          with:
            php-version: '8.2'
            extensions: mbstring, pdo_pgsql, bcmath, ctype, json, openssl
        - name: Install Composer Dependencies
          run: |
            cd laravel-web-portal
            composer install --prefer-dist --no-progress
        - name: Run PHPUnit Tests
          env:
            DB_CONNECTION: pgsql
            DB_HOST: 127.0.0.1
            DB_PORT: 5432
            DB_DATABASE: kideco_fuel_ratio_test
            DB_USERNAME: postgres
            DB_PASSWORD: secret_password
          run: |
            cd laravel-web-portal
            php artisan test --parallel

    test-python-ai-service:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Setup Python Environment
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'
        - name: Install Python AI Dependencies
          run: |
            cd python-ai-service
            python -m pip install --upgrade pip
            pip install -r requirements.txt
        - name: Run PyTest Suite
          run: |
            cd python-ai-service
            pytest --tb=short
  ```

## 5. Acceptance Criteria (Definition of Done)
- [ ] Pipeline CI/CD terdaftar dan terlihat hijau pada tab *Actions* di GitHub repository.
- [ ] Pull Request yang memiliki pengujian gagal ditahan (*blocked*) dari proses *Merge*.
- [ ] Waktu total eksekusi pipeline CI/CD di bawah 5 menit.
