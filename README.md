# 🚀 KIDECO Fuel Ratio AI & Capacity Optimization System
### *Intelligent Mining Fuel Management, Machine Learning Forecasting, Anomaly Detection & Fleet Capacity Allocation*

---

## 📌 Daftar Isi (Table of Contents)
1. [Tentang Proyek (Overview)](#-tentang-proyek-overview)
2. [Arsitektur Sistem (System Architecture)](#-arsitektur-sistem-system-architecture)
3. [Teknologi & Stack (Tech Stack)](#-teknologi--stack-tech-stack)
4. [Prasyarat Sistem (Prerequisites)](#-prasyarat-sistem-prerequisites)
5. [Panduan Instalasi & Setup Lengkap (Installation & Setup)](#-panduan-instalasi--setup-lengkap-installation--setup)
   - [Langkah 1: Clone Repository](#langkah-1-clone-repository)
   - [Langkah 2: Setup Python AI Microservice](#langkah-2-setup-python-ai-microservice-port-8002)
   - [Langkah 3: Setup Laravel & Vue 3 Frontend](#langkah-3-setup-laravel--vue-3-frontend-port-8000)
6. [Konfigurasi Environment Variables (.env)](#-konfigurasi-environment-variables-env)
7. [Panduan Penggunaan Fitur (User Guide)](#-panduan-penggunaan-fitur-user-guide)
   - [1. Executive Dashboard (`/dashboard`)](#1-executive-dashboard-dashboard)
   - [2. AI Forecasting & Reactive Simulator (`/forecasting-ai`)](#2-ai-forecasting--reactive-simulator-forecasting-ai)
   - [3. Mining Fuel AI Chatbot Assistant](#3-mining-fuel-ai-chatbot-assistant)
   - [4. Global Capacity Tuning (`/global-capacity`)](#4-global-capacity-tuning-global-capacity)
   - [5. Production & Equipment Catalog (`/production-capacity`)](#5-production--equipment-catalog-production-capacity)
8. [Dokumentasi API Endpoints (API Reference)](#-dokumentasi-api-endpoints-api-reference)
9. [Troubleshooting & FAQ](#-troubleshooting--faq)

---

## 📖 Tentang Proyek (Overview)

**KIDECO Fuel Ratio AI System** adalah platform analitik dan optimasi bahan bakar pertambangan terintegrasi berbasis AI. Sistem ini dirancang untuk memprediksi konsumsi bahan bakar (*Fuel Ratio* - L/BCM), mendeteksi anomali konsumsi unit alat berat secara *real-time*, menghitung penyesuaian kapasitas produksi terhadap faktor cuaca ekstrem (hujan), serta menyediakan asisten percakapan cerdas bertenaga **Google Gemini 1.5 Flash**.

### 🌟 Fitur Utama
- **XGBoost Fuel Ratio Forecasting:** Prediksi Fuel Ratio harian dan proyeksi 7 hari ke depan dengan mempertimbangkan curah hujan, jarak angkut (*haul distance*), target produksi (BCM), serta *lag features*. Dilatih dengan *TimeSeriesSplit Cross-Validation*.
- **PyTorch Deep Autoencoder Anomaly Detection:** Deteksi anomali dan lonjakan (*spikes*) konsumsi bahan bakar unit alat berat (*Excavator, Hauler, Dozer, Dewatering Pump*) berdasarkan *reconstruction error* terhadap baseline normal.
- **Combined Capacity & Weather Derating Engine:** Formula kalkulasi kapasitas armada dinamis dengan derating non-linear akibat curah hujan (efisiensi jalan, kondisi *mud/slippery*, utilisasi pompa).
- **Interactive Reactive Scenario Simulator:** Simulator *what-if* real-time berbasis slider reaktif untuk mensimulasikan dampak perubahan curah hujan, jarak angkut, dan target produksi terhadap Fuel Ratio dan status operasional.
- **Mining Fuel AI Chatbot Assistant:** Asisten AI cerdas berbasis Google Gemini 1.5 Flash yang terhubung langsung ke database operasional via SQLAlchemy ORM (*anti-SQL injection*) untuk menjawab pertanyaan seputar performa armada dan anomali BBM.
- **Clean Enterprise Dashboard:** Tampilan UI modern, minimalis, dan responsif berbasis Vue 3, TypeScript, Vuetify 3, dan ApexCharts.

---

## 🏗️ Arsitektur Sistem (System Architecture)

Sistem menggunakan arsitektur **Microservices Decoupled**:

```
+-----------------------------------------------------------------------+
|                    CLIENT BROWSER (VUE 3 + VUETIFY)                  |
|        - Executive Dashboard       - AI Forecasting & Simulator       |
|        - Capacity Tuning           - Mining Fuel AI Chatbot           |
+-----------------------------------+-----------------------------------+
                                    | (HTTP / REST JSON)
                                    v
+-----------------------------------------------------------------------+
|                     LARAVEL 11 FULLSTACK WEB PORTAL                   |
|                   (Port: 8000 | PHP 8.2+ | Vite 5)                    |
|  - Web Routing & Blade Templates      - Eloquent ORM & Authentication  |
|  - FuelRatioAiClient (Proxy)          - API Controllers (/api/v1/*)   |
+-----------------------------------+-----------------------------------+
                                    | (Internal Reverse Proxy / cURL)
                                    v
+-----------------------------------------------------------------------+
|                   PYTHON AI FASTAPI MICROSERVICE                      |
|                   (Port: 8002 | Python 3.10+ | Uvicorn)               |
|  +-----------------------------------------------------------------+  |
|  | ML Inference Engine:                                            |  |
|  |  * XGBoost Fuel Ratio Regressor (TimeSeriesSplit)               |  |
|  |  * PyTorch Deep Autoencoder (Spike & Anomaly Detector)          |  |
|  |  * Non-Linear Rain Derating & Fleet Allocation Calculator       |  |
|  |  * Gemini 1.5 Flash Chatbot with ORM Grounding                  |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------+-----------------------------------+
                                    | (SQLAlchemy / Connection Pool)
                                    v
+-----------------------------------------------------------------------+
|                  POSTGRESQL / SUPABASE CLOUD DATABASE                 |
|  - equipment_catalogs         - daily_forecast_logs                   |
|  - unit_anomaly_spikes        - capacity_allocations                  |
|  - weather_daily_logs         - baseline_activity_tables              |
+-----------------------------------------------------------------------+
```

---

## 💻 Teknologi & Stack (Tech Stack)

| Komponen | Teknologi / Library |
| --- | --- |
| **Frontend UI** | Vue 3 (Composition API), TypeScript, Vuetify 3, ApexCharts, Vite 5 |
| **Backend Web Portal** | Laravel 11.x, PHP 8.2+, Composer, GuzzleHTTP / cURL |
| **AI Microservice** | FastAPI 0.110, Python 3.10 / 3.11, Uvicorn, Pydantic v2 |
| **Machine Learning** | PyTorch 2.2+, XGBoost 2.0+, Scikit-Learn 1.4+, Pandas, NumPy, Optuna |
| **Generative AI** | Google Gemini 1.5 Flash REST API |
| **Database & ORM** | PostgreSQL 15+ (Supabase Cloud), SQLAlchemy 2.0, Eloquent ORM |

---

## ⚙️ Prasyarat Sistem (Prerequisites)

Pastikan lingkungan lokal Anda telah terpasang:
1. **PHP:** Versi `>= 8.2` (dengan ekstensi `pdo`, `pdo_pgsql` / `pdo_sqlite`, `curl`, `mbstring`, `openssl`).
2. **Composer:** Versi `>= 2.5`.
3. **Node.js & npm:** Node.js `>= 18.0.0` (disarankan Node.js 20 LTS) & `npm` / `pnpm`.
4. **Python:** Versi `>= 3.10` atau `3.11` & `pip`.
5. **Git:** Versi terbaru.

---

## 🛠️ Panduan Instalasi & Setup Lengkap (Installation & Setup)

Ikuti langkah-langkah berikut secara berurutan untuk menjalankan seluruh sistem di komputer lokal Anda:

### Langkah 1: Clone Repository
```bash
git clone https://github.com/belpythons/Persekutuan-Kewer-Mahasiswa
cd Persekutuan-Kewer-Mahasiswa
```

---

### Langkah 2: Setup Python AI Microservice (Port: 8002)

Microservice ini menangani seluruh inferensi XGBoost, PyTorch Autoencoder, kalkulasi kapasitas armada, dan AI Chatbot.

1. **Masuk ke direktori microservice:**
   ```bash
   cd python-ai-service
   ```

2. **Buat & aktifkan Virtual Environment:**
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows (Command Prompt / PowerShell):**
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install Dependensi Python:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Konfigurasi Environment (`.env`):**
   Salin atau buat file `.env` di dalam folder `python-ai-service/`:
   ```bash
   cp .env.example .env   # atau buat file .env baru
   ```
   Isi konfigurasi `.env` sebagai berikut:
   ```env
   APP_NAME="KIDECO Fuel Ratio AI Service"
   APP_ENV=development
   DEBUG=True

   # Supabase / PostgreSQL Credentials
   SUPABASE_URL=https://nxgurgphgoelraasauqt.supabase.co
   SUPABASE_KEY=sb_publishable_iRCaHzS3-hjk9id4GjIRKg_oMx-UrrP
   SUPABASE_PROJECT_ID=nxgurgphgoelraasauqt

   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=
   POSTGRES_HOST=db.nxgurgphgoelraasauqt.supabase.co
   POSTGRES_PORT=5432
   POSTGRES_DB=postgres

   # Google Gemini AI API Key (Untuk Chatbot)
   GEMINI_API_KEY=
   GEMINI_MODEL=gemini-1.5-flash
   ```
   > 💡 **Catatan Gemini API Key:** Jika `GEMINI_API_KEY` belum diisi, chatbot akan secara otomatis beralih ke *Smart Fallback Engine* berbasis database tanpa error. Dapatkan API Key gratis di [Google AI Studio](https://aistudio.google.com/app/apikey).

5. **Inisialisasi & Seeding Database (Opsional jika ingin seed ulang):**
   ```bash
   python seed_database.py
   ```

6. **Training Model Machine Learning (Opsional jika ingin re-train):**
   ```bash
   python pipelines/train_xgboost.py
   ```

7. **Jalankan Python AI Microservice:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8002 --reload
   ```
   Service akan aktif di:
   - **Base URL:** `http://localhost:8002`
   - **Interactive API Docs (Swagger UI):** `http://localhost:8002/docs`
   - **ReDoc:** `http://localhost:8002/redoc`
   - **Health Check:** `http://localhost:8002/health`
   - **Readiness Check:** `http://localhost:8002/ready`

---

### Langkah 3: Setup Laravel & Vue 3 Frontend (Port: 8000)

Buka jendela terminal baru, arahkan ke folder `laravel`.

1. **Masuk ke folder Laravel:**
   ```bash
   cd laravel
   ```

2. **Install PHP Dependencies (Composer):**
   ```bash
   composer install
   ```

3. **Install Frontend Dependencies (Node/npm):**
   ```bash
   npm install
   ```

4. **Konfigurasi Environment (`.env`):**
   Salin `.env.example` menjadi `.env`:
   ```bash
   cp .env.example .env
   ```
   Pastikan variabel kunci terkonfigurasi di `laravel/.env`:
   ```env
   APP_NAME="KIDECO Fuel Ratio Portal"
   APP_ENV=local
   APP_KEY=
   APP_DEBUG=true
   APP_URL=http://127.0.0.1:8000

   # AI Microservice Connection
   AI_SERVICE_URL=http://localhost:8002/api/v1
   AI_SERVICE_TIMEOUT=15

   # Gemini API Key (Opsional mirror)
   GEMINI_API_KEY=
   ```

5. **Generate Laravel Application Key:**
   ```bash
   php artisan key:generate
   ```

6. **Jalankan Database Migration & Build Icons:**
   ```bash
   php artisan migrate
   npm run build:icons
   ```

7. **Jalankan Development Server:**
   Anda dapat menjalankan server menggunakan satu perintah praktis:
   ```bash
   npm run dev
   ```
   *Atau jalankan secara terpisah:*
   - **Terminal 1 (Laravel Server):** `php artisan serve --port=8000`
   - **Terminal 2 (Vite Hot-Reload):** `npm run dev` (atau `npm run build` untuk mode produksi)

8. **Buka Aplikasi di Browser:**
   Akses portal utama di: **`http://127.0.0.1:8000/dashboard`**

---

## 🔑 Konfigurasi Environment Variables (.env)

### Tabel Referensi `python-ai-service/.env`
| Variabel | Tipe | Default | Keterangan |
| --- | --- | --- | --- |
| `APP_NAME` | String | `"KIDECO Fuel Ratio AI Service"` | Nama microservice |
| `APP_ENV` | String | `development` | Lingkungan runtime (`development` / `production`) |
| `DEBUG` | Boolean | `True` | Mode debug & hot-reload |
| `POSTGRES_HOST` | String | `db.nxgurgphgoelraasauqt.supabase.co` | Host PostgreSQL Supabase |
| `POSTGRES_PORT` | Integer | `5432` | Port database PostgreSQL |
| `POSTGRES_USER` | String | `postgres` | User database PostgreSQL |
| `POSTGRES_PASSWORD` | String | `""` | Password PostgreSQL Supabase |
| `POSTGRES_DB` | String | `postgres` | Nama database |
| `GEMINI_API_KEY` | String | `""` | API Key Google Gemini 1.5 Flash |
| `GEMINI_MODEL` | String | `gemini-1.5-flash` | Versi model LLM Gemini |

### Tabel Referensi `laravel/.env`
| Variabel | Tipe | Default | Keterangan |
| --- | --- | --- | --- |
| `APP_URL` | String | `http://127.0.0.1:8000` | URL aplikasi Laravel |
| `AI_SERVICE_URL` | String | `http://localhost:8002/api/v1` | URL endpoint Python FastAPI |
| `AI_SERVICE_TIMEOUT` | Integer | `15` | Timeout HTTP request ke AI microservice (detik) |

---

## 🖥️ Panduan Penggunaan Fitur (User Guide)

### 1. Executive Dashboard (`/dashboard`)
Dashboard utama memberikan ringkasan holistik kondisi konsumsi bahan bakar dan kesehatan armada:
- **Dynamic Threshold Alert Widget:** Menampilkan status *NORMAL*, *WARNING*, atau *CRITICAL* secara otomatis berdasarkan ambang batas dinamis yang memperhitungkan faktor cuaca hari ini.
- **PyTorch Spike Summary Widget:** Memantau jumlah anomali aktif dan lonjakan konsumsi bahan bakar ekstrem yang terdeteksi oleh neural network dalam 24 jam terakhir.
- **Activity Fuel Allocation Donut Chart:** Diagram distribusi konsumsi solar harian antar aktivitas (*Hauling*, *Loading*, *Support*, *Dewatering*).
- **Top Anomalous Fleet Leaderboard:** Daftar unit alat berat yang mengalami deviasi konsumsi tertinggi dibandingkan baseline normal (dilengkapi persentase deviasi seperti `+16.2%` dan indikator aktivitas).

---

### 2. AI Forecasting & Reactive Simulator (`/forecasting-ai`)
Halaman analitik prediktif dan simulasi skenario:
- **7-Day Rolling Fuel Ratio Forecast:** Grafik proyeksi Fuel Ratio (L/BCM) selama 7 hari ke depan beserta kurva target produksi (BCM).
- **Interactive Reactive Scenario Simulator:** Geser slider secara *real-time*:
  - *Prakiraan Curah Hujan (0 - 150 mm)*
  - *Jarak Angkut / Haul Distance (1.000 - 10.000 m)*
  - *Target Produksi Harian (10.000 - 100.000 BCM)*
  Sistem secara otomatis menghitung ulang proyeksi Fuel Ratio, status risiko, dan rekomendasi operasional tanpa perlu menekan tombol manual.

---

### 3. Mining Fuel AI Chatbot Assistant
Asisten percakapan cerdas yang terletak di pojok bawah halaman Forecasting AI:
- **Kemampuan:**
  - Menjawab pertanyaan kasual dan greeting secara natural (*"Halo"*, *"Siapa kamu?"*).
  - Menjelaskan rincian unit yang sedang mengalami anomali konsumsi (*"Unit mana yang boros hari ini?"*).
  - Memberikan ringkasan alokasi kapasitas armada dan dampak hujan (*"Berapa unit HD785 yang beroperasi jika hujan 25 mm?"*).
- **Keamanan:** Kueri data dilakukan secara otomatis melalui SQLAlchemy ORM terparameterisasi (*strict anti-SQL injection*).

---

### 4. Global Capacity Tuning (`/global-capacity`)
Halaman perencanaan kapasitas armada gabungan (*Combined Capacity Determination*):
- **Baseline vs AI Derated Allocation:** Perbandingan antara kapasitas nominal alat berat vs kapasitas efektif setelah memperhitungkan faktor hujan dan anomali unit.
- **Detail Alokasi per Aktivitas:**
  - *Loading (Excavator PC1250, PC2000, EX2600)*
  - *Hauling (Dump Truck HD785-7, HD785-7MUD)*
  - *Support (Dozer D375, Drilling Mid/Small)*
  - *Dewatering (Water Pump, Booster Pump, Dragflow)*
- Menampilkan kebutuhan unit aktif (*Req Units*), utilisasi armada (%), konsumsi solar per jam, dan total solar harian (Liter).

---

### 5. Production & Equipment Catalog (`/production-capacity`)
Katalog referensi seluruh armada pertambangan KIDECO:
- Data spesifikasi populasi unit, konsumsi standar (L/hr), kapasitas produksi standar (BCM/hr), dan baseline performa historis.

---

## 📡 Dokumentasi API Endpoints (API Reference)

Seluruh endpoint AI microservice dapat diakses langsung pada port `8002` atau via proxy Laravel pada port `8000`:

| Method | FastAPI Endpoint (`:8002`) | Laravel Proxy Endpoint (`:8000`) | Deskripsi |
| --- | --- | --- | --- |
| `POST` | `/api/v1/forecast` | `/api/v1/forecast` | Prediksi Fuel Ratio harian (XGBoost) |
| `POST` | `/api/v1/forecast-7days` | `/api/v1/forecast-7days` | Proyeksi Fuel Ratio 7 hari ke depan |
| `GET` | `/api/v1/forecast-history` | `/api/v1/forecast-history` | Data historis Fuel Ratio aktual vs prediksi |
| `POST` | `/api/v1/anomaly-detect` | `/api/v1/anomaly-detect` | Deteksi anomali unit (PyTorch Autoencoder) |
| `POST` | `/api/v1/calculate-capacity` | `/api/v1/calculate-capacity` | Kalkulasi alokasi kapasitas gabungan armada |
| `POST` | `/api/v1/global-capacity-tuning` | `/api/v1/global-capacity-tuning` | Tuning kapasitas global berdasarkan cuaca |
| `POST` | `/api/v1/chatbot/query` | `/api/v1/chatbot/query` | Kueri AI Chatbot Assistant (Gemini 1.5 Flash) |
| `GET` | `/health` | `/api/v1/ai-health` | Health check service & koneksi database |
| `GET` | `/ready` | `/api/v1/ai-ready` | Readiness probe status pre-loaded model RAM |

### Contoh Request & Response: Prediksi Fuel Ratio (`POST /api/v1/forecast`)
**Request Body (`application/json`):**
```json
{
  "date": "2026-08-05",
  "curah_hujan_mm": 12.5,
  "temp_max_c": 33.0,
  "haul_distance_m": 4200.0,
  "daily_prod_bcm": 45000.0
}
```

**Response (`200 OK`):**
```json
{
  "log_date": "2026-08-05",
  "forecast_fr": 1.042,
  "status": "NORMAL",
  "warning_threshold": 1.08,
  "critical_threshold": 1.12,
  "daily_prod_bcm": 45000.0,
  "haul_distance_m": 4200.0
}
```

---

## ❓ Troubleshooting & FAQ

### 1. Error: `uvicorn: command not found`
**Penyebab:** Virtual environment Python belum diaktifkan.  
**Solusi:**
```bash
cd python-ai-service
source venv/bin/activate    # macOS / Linux
# atau: venv\Scripts\activate  (Windows)
pip install -r requirements.txt
```

### 2. Chatbot memberikan respon fallback / "Smart Fallback"
**Penyebab:** Variabel `GEMINI_API_KEY` di `python-ai-service/.env` masih kosong.  
**Solusi:** Dapatkan API Key di [Google AI Studio](https://aistudio.google.com/app/apikey) dan masukkan ke file `.env`:
```env
GEMINI_API_KEY=AIzaSyD...
```
Restart server uvicorn setelah mengubah `.env`.

### 3. Halaman Dashboard menampilkan "AI Service Offline"
**Penyebab:** Python AI Microservice di port `8002` belum berjalan atau firewall memblokir koneksi lokal.  
**Solusi:**
1. Pastikan uvicorn berjalan: `python -m uvicorn main:app --port 8002 --reload`.
2. Periksa health check di browser: `http://localhost:8002/health`.
3. Pastikan `AI_SERVICE_URL=http://localhost:8002/api/v1` di `laravel/.env`.

### 4. Iconify / Font Icons tidak muncul di Vue
**Solusi:** Jalankan script build iconify pada folder `laravel`:
```bash
npm run build:icons
```

---

## 👥 Tim Pengembang
Dikembangkan oleh **Tim Persekutuan Kewer Mahasiswa** untuk optimasi efisiensi operasional dan bahan bakar PT Kideco Jaya Agung.
