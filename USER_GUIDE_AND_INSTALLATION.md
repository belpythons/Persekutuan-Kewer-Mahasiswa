# 📘 KIDECO Fuel Ratio AI — Comprehensive Installation & User Guide
### *Buku Panduan Instalasi, Setup Lingkungan, Arsitektur, dan Operasional Pengguna*

---

## 📑 Daftar Bab (Table of Contents)
- [Bab 1: Pengenalan Sistem & Arsitektur Solusi](#bab-1-pengenalan-sistem--arsitektur-solusi)
- [Bab 2: Prasyarat Perangkat Keras & Perangkat Lunak](#bab-2-prasyarat-perangkat-keras--perangkat-lunak)
- [Bab 3: Panduan Instalasi Langkah-demi-Langkah (Step-by-Step Installation)](#bab-3-panduan-instalasi-langkah-demi-langkah-step-by-step-installation)
  - [3.1 Menyiapkan Repository](#31-menyiapkan-repository)
  - [3.2 Menyiapkan Python AI Microservice (FastAPI & ML Engine)](#32-menyiapkan-python-ai-microservice-fastapi--ml-engine)
  - [3.3 Menyiapkan Laravel 11 & Vue 3 Frontend Portal](#33-menyiapkan-laravel-11--vue-3-frontend-portal)
- [Bab 4: Konfigurasi Database & Environment (.env)](#bab-4-konfigurasi-database--environment-env)
- [Bab 5: Panduan Pengguna (User Guide per Modul)](#bab-5-panduan-pengguna-user-guide-per-modul)
  - [5.1 Modul 1: Executive Dashboard (`/dashboard`)](#51-modul-1-executive-dashboard-dashboard)
  - [5.2 Modul 2: AI Forecasting & Real-Time Simulator (`/forecasting-ai`)](#52-modul-2-ai-forecasting--real-time-simulator-forecasting-ai)
  - [5.3 Modul 3: Mining Fuel AI Assistant (Chatbot Gemini)](#53-modul-3-mining-fuel-ai-assistant-chatbot-gemini)
  - [5.4 Modul 4: Combined Capacity Determination (`/global-capacity`)](#54-modul-4-combined-capacity-determination-global-capacity)
  - [5.5 Modul 5: Production & Equipment Fleet Catalog (`/production-capacity`)](#55-modul-5-production--equipment-fleet-catalog-production-capacity)
- [Bab 6: Pengujian API & Validasi Sistem (Verification & Testing)](#bab-6-pengujian-api--validasi-sistem-verification--testing)
- [Bab 7: FAQ & Panduan Penyelesaian Masalah (Troubleshooting)](#bab-7-faq--panduan-penyelesaian-masalah-troubleshooting)

---

## Bab 1: Pengenalan Sistem & Arsitektur Solusi

Sistem **KIDECO Fuel Ratio AI** dibangun untuk menjawab tantangan operasional bahan bakar di industri pertambangan batubara skala besar, khususnya:
1. **Volatilitas Konsumsi Bahan Bakar:** Dampak signifikan cuaca hujan terhadap hambatan gelinding (*rolling resistance*), kondisi jalan tambang licin (*slippery haul road*), dan penurunan efisiensi armada.
2. **Deteksi Dini Pemborosan Unit:** Mengidentifikasi unit alat berat spesifik yang mengalami lonjakan konsumsi (*fuel spikes*) abnormal akibat kerusakan mekanis, kebiasaan operator, atau *under-performance*.
3. **Optimasi Alokasi Armada Gabungan:** Menentukan jumlah unit yang beroperasi secara presisi (*Loading, Hauling, Support, Dewatering*) agar target produksi tercapai tanpa terjadi pemborosan solar harian.

### Diagram Alur Data & Komponen
```
[Pengguna / Mine Planner]
          |
          v
[Frontend Vue 3 + Vuetify 3 (Port 8000 / Vite)]
          |
          v (AJAX / REST)
[Laravel 11 Gateway & Controllers]
          |
          v (Internal HTTP Proxy)
[FastAPI AI Microservice (Port 8002)]
   ├── XGBoost Regressor (TimeSeriesSplit Cross-Validation)
   ├── PyTorch Deep Autoencoder (Neural Reconstruction Loss)
   ├── Non-Linear Rain Derating Engine
   └── Google Gemini 1.5 Flash Chatbot
          |
          v (SQLAlchemy ORM Connection Pool)
[PostgreSQL / Supabase Database Cloud]
```

---

## Bab 2: Prasyarat Perangkat Keras & Perangkat Lunak

### Spesifikasi Minimum Hardware
- **CPU:** Dual Core 2.0 GHz (Disarankan Quad Core / Apple Silicon M-series)
- **RAM:** Minimum 8 GB RAM (Disarankan 16 GB untuk training Autoencoder & XGBoost)
- **Disk:** Minimum 2 GB ruang penyimpanan bebas

### Kebutuhan Software
1. **PHP:** Versi `>= 8.2`
2. **Composer:** Versi `>= 2.5`
3. **Node.js:** Versi `>= 18.0.0` (Rekomendasi: Node 20 LTS)
4. **Python:** Versi `>= 3.10` atau `3.11`
5. **Git:** Versi terbaru

---

## Bab 3: Panduan Instalasi Langkah-demi-Langkah (Step-by-Step Installation)

### 3.1 Menyiapkan Repository
Buka terminal Anda dan clone repositori ini:
```bash
git clone https://github.com/belpythons/Persekutuan-Kewer-Mahasiswa
cd Persekutuan-Kewer-Mahasiswa
```

---

### 3.2 Menyiapkan Python AI Microservice (FastAPI & ML Engine)

1. **Masuk ke folder AI Microservice:**
   ```bash
   cd python-ai-service
   ```

2. **Buat dan aktifkan Virtual Environment:**
   - Di macOS / Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Di Windows (PowerShell / Command Prompt):
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install Dependensi Python:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Konfigurasi `.env`:**
   Buat file `.env` di dalam folder `python-ai-service/`:
   ```env
   APP_NAME="KIDECO Fuel Ratio AI Service"
   APP_ENV=development
   DEBUG=True

   # Supabase Cloud Database (Default Cloud Pool)
   SUPABASE_URL=https://nxgurgphgoelraasauqt.supabase.co
   SUPABASE_KEY=sb_publishable_iRCaHzS3-hjk9id4GjIRKg_oMx-UrrP
   SUPABASE_PROJECT_ID=nxgurgphgoelraasauqt

   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=
   POSTGRES_HOST=db.nxgurgphgoelraasauqt.supabase.co
   POSTGRES_PORT=5432
   POSTGRES_DB=postgres

   # Google Gemini API Key
   GEMINI_API_KEY=
   GEMINI_MODEL=gemini-1.5-flash
   ```

5. **Inisialisasi Data & Model:**
   - Untuk mempopulasikan database dengan katalog unit dan data baseline:
     ```bash
     python seed_database.py
     ```
   - Untuk melatih model XGBoost:
     ```bash
     python pipelines/train_xgboost.py
     ```

6. **Menjalankan AI Microservice:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8002 --reload
   ```
   *Uji ketersediaan di browser:* `http://localhost:8002/docs`

---

### 3.3 Menyiapkan Laravel 11 & Vue 3 Frontend Portal

Buka jendela terminal baru dan navigasikan ke direktori `laravel`:

1. **Masuk ke folder Laravel:**
   ```bash
   cd laravel
   ```

2. **Install PHP Dependencies:**
   ```bash
   composer install
   ```

3. **Install Node & Vue Dependencies:**
   ```bash
   npm install
   ```

4. **Konfigurasi `.env` Laravel:**
   Salin contoh file konfigurasi:
   ```bash
   cp .env.example .env
   ```
   Pastikan variabel berikut ada di `laravel/.env`:
   ```env
   APP_NAME="KIDECO Fuel Ratio Portal"
   APP_ENV=local
   APP_KEY=
   APP_DEBUG=true
   APP_URL=http://127.0.0.1:8000

   # Koneksi ke Python AI Microservice
   AI_SERVICE_URL=http://localhost:8002/api/v1
   AI_SERVICE_TIMEOUT=15

   # Mirror Gemini API Key (Opsional)
   GEMINI_API_KEY=
   ```

5. **Generate Kunci Aplikasi & Build Icons:**
   ```bash
   php artisan key:generate
   npm run build:icons
   ```

6. **Jalankan Aplikasi:**
   Jalankan development server:
   ```bash
   npm run dev
   ```
   *(Secara otomatis menjalankan Vite dan menghubungkan ke server Laravel)*

   Buka peramban (browser) di: **`http://127.0.0.1:8000/dashboard`**

---

## Bab 4: Konfigurasi Database & Environment (.env)

### Kunci Konfigurasi Penting
| File | Kunci | Penjelasan |
| --- | --- | --- |
| `python-ai-service/.env` | `GEMINI_API_KEY` | Kunci API Google Gemini untuk fungsionalitas Chatbot AI cerdas |
| `python-ai-service/.env` | `POSTGRES_HOST` | Host database PostgreSQL / Supabase |
| `laravel/.env` | `AI_SERVICE_URL` | Endpoint komunikasi dari Laravel ke Python AI Microservice (`http://localhost:8002/api/v1`) |
| `laravel/.env` | `APP_URL` | Base URL portal web (`http://127.0.0.1:8000`) |

---

## Bab 5: Panduan Pengguna (User Guide per Modul)

### 5.1 Modul 1: Executive Dashboard (`/dashboard`)
Halaman ini adalah pusat monitoring harian bagi *Management* dan *Mine Operation Supervisor*:
1. **Dynamic Threshold Alert:**
   - Membandingkan Fuel Ratio hari ini terhadap ambang batas dinamis.
   - Status **NORMAL** (Hijau): Operasional efisien.
   - Status **WARNING** (Kuning): Peringatan dini potensi pemborosan akibat kondisi rute/hujan.
   - Status **CRITICAL** (Merah): Terjadi anomali signifikan yang memerlukan investigasi lapangan segera.
2. **PyTorch Spike Summary:**
   - Menghitung jumlah anomali aktif yang terdeteksi dalam 24 jam terakhir.
3. **Activity Fuel Allocation Donut Chart:**
   - Memvisualisasikan persentase alokasi solar untuk *Hauling*, *Loading*, *Support*, dan *Dewatering*.
4. **Top Anomalous Leaderboard:**
   - Menampilkan tabel unit paling boros lengkap dengan ID unit, nilai *Actual FC*, *Normal FC*, serta deviasi persentasenya (`+16.2%`, `+85.5%`, dll.).

---

### 5.2 Modul 2: AI Forecasting & Real-Time Simulator (`/forecasting-ai`)
Modul perencanaan masa depan dan simulasi skenario:
1. **7-Day Fuel Ratio Projection:**
   - Melihat grafik estimasi rasio bahan bakar 7 hari ke depan dibandingkan target volume galian BCM.
2. **Reactive Scenario Simulator (Tanpa Tombol Manual):**
   - Geser slider **Curah Hujan (mm)** untuk melihat efek hujan terhadap Fuel Ratio.
   - Geser slider **Jarak Angkut (m)** untuk melihat pengaruh jarak *disposal*.
   - Geser slider **Target Produksi (BCM)** untuk menyesuaikan skala produksi.
   - Hasil kalkulasi dan status risiko terupdate secara instan dan otomatis (*debounced*).

---

### 5.3 Modul 3: Mining Fuel AI Assistant (Chatbot Gemini)
Terletak pada kartu chatbot di halaman Forecasting AI:
- **Tanya Jawab Percakapan:** Ketik pertanyaan dalam bahasa Indonesia atau Inggris.
- **Contoh Pertanyaan:**
  - *"Halo, siapa kamu dan apa fungsimu?"*
  - *"Unit apa saja yang terdeteksi mengalami anomali solar hari ini?"*
  - *"Bagaimana rekomendasi penyesuaian armada jika besok diprediksi hujan lebat 30 mm?"*
  - *"Berapa konsumsi rata-rata unit HD785-7?"*

---

### 5.4 Modul 4: Combined Capacity Determination (`/global-capacity`)
Modul perencanaan armada dan kalkulasi derating cuaca:
1. **Baseline vs AI Derated Allocation:**
   - Menampilkan tabel perbandingan unit nominal vs unit efektif yang dibutuhkan.
2. **Metrik Aktivitas Operasional:**
   - Kebutuhan unit aktif per kategori (*Loading, Hauling, Support, Dewatering*).
   - Utilisasi armada rata-rata.
   - Total konsumsi solar per jam dan estimasi kebutuhan solar harian (Liter/hari).

---

### 5.5 Modul 5: Production & Equipment Fleet Catalog (`/production-capacity`)
Pustaka spesifikasi unit:
- Memuat spesifikasi teknis standar konsumsi bahan bakar (*L/hr*), kapasitas angkut/gali (*BCM/hr*), dan status operasional armada PT Kideco Jaya Agung.

---

## Bab 6: Pengujian API & Validasi Sistem (Verification & Testing)

Anda dapat menguji microservice secara langsung menggunakan perintah cURL:

### 1. Test Prediksi Fuel Ratio (XGBoost)
```bash
curl -X POST http://localhost:8002/api/v1/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-08-05",
    "curah_hujan_mm": 15.0,
    "temp_max_c": 32.5,
    "haul_distance_m": 4200.0,
    "daily_prod_bcm": 45000.0
  }'
```

### 2. Test Kalkulasi Kapasitas Armada
```bash
curl -X POST http://localhost:8002/api/v1/calculate-capacity \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-08-05",
    "forecast_prod_bcm": 42000.0,
    "curah_hujan_mm": 10.0
  }'
```

### 3. Test AI Chatbot
```bash
curl -X POST http://localhost:8002/api/v1/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Unit mana saja yang boros hari ini?"
  }'
```

---

## Bab 7: FAQ & Panduan Penyelesaian Masalah (Troubleshooting)

| Gejala Masalah | Kemungkinan Penyebab | Langkah Solusi |
| --- | --- | --- |
| **`uvicorn: command not found`** | Virtual environment Python belum aktif | Jalankan `source venv/bin/activate` (macOS/Linux) atau `venv\Scripts\activate` (Windows). |
| **Chatbot merespon dengan fallback data** | `GEMINI_API_KEY` belum terisi di `.env` | Masukkan API key Gemini di `python-ai-service/.env`, lalu restart uvicorn. |
| **Koneksi Database Timeout / Refused** | Host PostgreSQL diblokir firewall atau koneksi internet terputus | Periksa koneksi internet ke Supabase Cloud dan pastikan port `5432` terbuka. |
| **Vite Hot-Reload Error** | Port `5173` sedang digunakan proses lain | Hentikan proses yang berjalan atau restart terminal. |
| **Ikon tidak muncul di Dashboard** | File build iconify belum dibuat | Jalankan `npm run build:icons` di dalam folder `laravel`. |

---

*Dokumen ini disusun untuk memudahkan seluruh tim dalam instalasi, pemeliharaan, dan pengoperasian sistem KIDECO Fuel Ratio AI.*
