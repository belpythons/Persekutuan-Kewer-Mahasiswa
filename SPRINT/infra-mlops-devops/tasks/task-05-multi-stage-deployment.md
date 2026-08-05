# [TASK-05] Production Multi-Stage Containerization & Hardening

## 1. Metadata
- **Sprint**: Infra-MLOps-DevOps - Sprint 16
- **Kategori**: Infrastructure / DevOps
- **Status**: Ready for Implementation
- **Estimasi Effort**: 8 Story Points (~16 Jam)

## 2. Deskripsi Task
Menyusun file pembentuk kontainer produksi berbasis *Multi-Stage Build* (`Dockerfile.laravel` & `Dockerfile.ai`) untuk meminimalkan ukuran *image*, menghilangkan dependensi *build-time* yang tidak diperlukan pada runtime produksi, serta mengamankan eksekusi kontainer. Image hasil build tahap akhir HANYA berisi artefak terkompilasi dan dijalankan oleh pengguna non-root (`www-data` atau `appuser`), sehingga secara drastis mengurangi *attack surface* di lingkungan produksi.

## 3. Objective & Key Results (OKR)
- Objective: Menghasilkan image kontainer produksi yang efisien, berukuran kecil, dan aman (*hardened*).
- Key Results:
  - [ ] Ukuran final image `laravel-portal:prod` di bawah 250 MB.
  - [ ] Ukuran final image `python-ai:prod` di bawah 1.2 GB (termasuk PyTorch & XGBoost runtime).
  - [ ] Eksekusi proses di dalam kontainer berjalan di bawah ID pengguna non-root.

## 4. Technical Deliverables & Specifications
- **Target Files**:
  - `laravel-web-portal/Dockerfile`
  - `python-ai-service/Dockerfile`
- **Multi-Stage Dockerfile Laravel (`laravel-web-portal/Dockerfile`)**:
  ```dockerfile
  # Stage 1: Build Dependencies & Compile Assets
  FROM composer:2.6 AS vendor
  WORKDIR /app
  COPY composer.json composer.lock ./
  RUN composer install --no-dev --no-scripts --prefer-dist --optimize-autoloader

  # Stage 2: Production Runtime Image
  FROM php:8.2-fpm-alpine
  WORKDIR /var/www/html

  RUN apk add --no-linux-headers --no-cache postgresql-dev libpng-dev zip \
      && docker-php-ext-install pdo pdo_pgsql gd opcache

  COPY --chown=www-data:www-data . /var/www/html
  COPY --chown=www-data:www-data --from=vendor /app/vendor /var/www/html/vendor

  USER www-data
  EXPOSE 9000
  CMD ["php-fpm"]
  ```
- **Multi-Stage Dockerfile Python AI (`python-ai-service/Dockerfile`)**:
  ```dockerfile
  # Stage 1: Builder Stage
  FROM python:3.11-slim AS builder
  WORKDIR /app
  RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ libpq-dev
  COPY requirements.txt .
  RUN pip install --user --no-cache-dir -r requirements.txt

  # Stage 2: Final Production Runtime Image
  FROM python:3.11-slim
  WORKDIR /app
  RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
      && rm -rf /var/lib/apt/lists/* \
      && useradd -m appuser

  COPY --from=builder /root/.local /home/appuser/.local
  COPY --chown=appuser:appuser . /app

  ENV PATH=/home/appuser/.local/bin:$PATH
  USER appuser
  EXPOSE 8000
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

## 5. Acceptance Criteria (Definition of Done)
- [ ] Image kontainer berhasil dibangun (*build*) tanpa error menggunakan `docker build`.
- [ ] Kontainer berjalan di lingkungan produksi dengan status `USER non-root`.
- [ ] Aplikasi Laravel dan Python AI Engine lulus uji fungsionalitas inferensi pada image produksi.
