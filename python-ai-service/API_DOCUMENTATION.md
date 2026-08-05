# KIDECO Fuel Ratio AI Service - API Documentation

Microservice AI untuk Forecasting Fuel Ratio, Deteksi Anomali Unit (PyTorch Autoencoder), dan Combined Capacity Determination.

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (atau sesuai konfigurasi server)

---

## 1. Forecasting Engine

### `POST /api/v1/forecast`
**Predict Daily Fuel Ratio**

Predicts daily Total Fuel Ratio (L/BCM) dan mengevaluasi status operasional (NORMAL, WARNING, CRITICAL) menggunakan XGBoost Regressor yang telah di-training dan pipeline fitur TimeSeriesSplit.

#### Request Body
`application/json`

| Field | Type | Default | Description | Example |
| --- | --- | --- | --- | --- |
| `date` **(Required)** | string | - | Tanggal operasional (YYYY-MM-DD) | `2026-08-05` |
| `curah_hujan_mm` | number | 0.0 | Prakiraan curah hujan (mm). Range: 0.0 - 200.0 | `12.5` |
| `temp_max_c` | number | 32.0 | Suhu maksimum (°C). Range: 10.0 - 50.0 | `33.5` |
| `kecepatan_angin_kmh` | number | 12.0 | Kecepatan angin (km/h). Range: 0.0 - 100.0 | `15.0` |
| `haul_distance_m` | number | 3900.0 | Jarak angkut (meter). Range: 500.0 - 15000.0 | `4100.0` |
| `daily_prod_bcm` | number | 40000.0 | Target produksi harian (BCM). Range: 1000.0 - 150000.0 | `42000.0` |
| `rain_lag1` | number | 0.0 | Curah hujan H-1 (mm) | `5.0` |
| `rain_lag2` | number | 0.0 | Curah hujan H-2 (mm) | `0.0` |
| `fr_lag1` | number | 1.018 | Fuel Ratio H-1 (L/BCM) | `1.025` |
| `fr_lag2` | number | 1.018 | Fuel Ratio H-2 (L/BCM) | `1.015` |
| `rolling_avg_fr_7d` | number | 1.018 | Rata-rata Fuel Ratio 7 hari terakhir | `1.02` |

#### Response `200 OK`
Mengembalikan object `ForecastResponse` yang berisi hasil prediksi.

```json
{
  "log_date": "2026-08-05",
  "forecast_fr": 1.05,
  "status": "NORMAL",
  "warning_threshold": 1.08,
  "critical_threshold": 1.12,
  "daily_prod_bcm": 42000.0,
  "haul_distance_m": 4100.0,
  "features_input": {
    "date": "2026-08-05",
    "curah_hujan_mm": 12.5,
    "temp_max_c": 33.5
  }
}
```

---

## 2. Anomaly Detection Engine

### `POST /api/v1/anomaly-detect`
**Detect Unit Fuel Anomalies**

Memindai data konsumsi BBM unit dan mendeteksi lonjakan (anomali) yang tidak biasa menggunakan PyTorch Deep Autoencoder. Model ini dilatih secara eksklusif menggunakan data operasional baseline normal.

#### Request Body
`application/json`

**`records`** (Array of Objects) - **Required**

| Field | Type | Description | Example |
| --- | --- | --- | --- |
| `Date` **(Required)** | string | Tanggal catatan (YYYY-MM-DD) | `2026-08-05` |
| `Unit` **(Required)** | string | Kode/Nama Unit Alat | `HD785-7` |
| `Activity` **(Required)** | string | Kategori Aktivitas (LOADING, HAULING, SUPPORT, DEWATERING) | `HAULING` |
| `FC_Actual` **(Required)** | number | Konsumsi BBM Aktual per Jam (L/hr) | `78.5` |
| `Unit_Fuel_L_Day` **(Required)** | number | Total BBM Harian Unit (L/day) | `1570.0` |
| `Unit_FR` **(Required)** | number | Fuel Ratio individual unit (L/BCM) | `0.285` |
| `Rain_mm` | number (Default: 0.0) | Curah hujan harian (mm) | `5.0` |

#### Response `200 OK`
Mengembalikan daftar record beserta probabilitas/status anomalinya.

---

## 3. Capacity Determination Engine

### `POST /api/v1/calculate-capacity`
**Calculate Combined Capacity Allocation**

Menghitung kapasitas efektif armada secara dinamis, kebutuhan unit yang beroperasi, persentase utilisasi, dan alokasi BBM harian gabungan. Perhitungan mengintegrasikan XGBoost Forecast, PyTorch Autoencoder Spikes, dan Non-linear Rain Derating.

#### Request Body
`application/json`

| Field | Type | Default | Description | Example |
| --- | --- | --- | --- | --- |
| `date` **(Required)** | string | - | Tanggal operasional (YYYY-MM-DD) | `2026-08-05` |
| `forecast_prod_bcm` | number | 40000.0 | Hasil forecast produksi BCM harian | `40000.0` |
| `curah_hujan_mm` | number | 0.0 | Prakiraan curah hujan (mm) | `12.5` |
| `equipment_list` | array of objects | null | Daftar armada (Opsional, jika kosong mengambil dari DB) | - |
| `nn_spike_count_by_unit` | object | null | Map bobot anomali spike unit hasil Autoencoder | `{"HD785-7MUD": 2}` |

**Detail Objek `equipment_list`:**

| Field | Type | Description | Example |
| --- | --- | --- | --- |
| `unit_name` **(Required)** | string | Nama/Tipe Alat Heavy Equipment | `HD785-7` |
| `qty` **(Required)** | integer | Jumlah populasi unit | `205` |
| `activity` **(Required)** | string | Aktivitas (LOADING, HAULING, SUPPORT, DEWATERING) | `HAULING` |
| `fc_lhr` **(Required)** | number | Konsumsi BBM standar (L/hr) | `75.0` |
| `prod_bcmhr` | number (Default: 0.0)| Kapasitas produksi per jam (BCM/hr) | `109.56` |

#### Response `200 OK`
Mengembalikan hasil kalkulasi alokasi kapasitas untuk masing-masing unit/aktivitas.

---

## 4. System & Health Checks

### `GET /health`
**Health Check**

Memeriksa kesehatan service dan status koneksi ke Database.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "environment": "development",
  "database": {
    "status": "connected",
    "type": "postgres"
  }
}
```

### `GET /ready`
**Readiness Check**

Memastikan model ML sudah pre-loaded di RAM dan siap menerima trafik inferensi (< 2.0s latency).

#### Response `200 OK`
```json
{
  "status": "ready",
  "warmup_details": {
    "xgboost": "warmed_up",
    "pytorch": "warmed_up",
    "latency_ms": 150
  }
}
```

### `GET /`
**Root Endpoint**

Memberikan informasi umum terkait service.

#### Response `200 OK`
```json
{
  "app": "KIDECO Fuel Ratio AI Service",
  "version": "1.0.0",
  "status": "online",
  "docs": "/docs"
}
```

---

*Catatan:*
- Referensi OpenAPI interaktif tersedia dengan mengakses `GET /docs` (Swagger UI) atau `GET /redoc` (ReDoc) setelah menjalankan service.
