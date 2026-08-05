# 📖 Dokumentasi Integrasi Microservice AI untuk Laravel Web Portal

Dokumen ini berisi panduan API lengkap untuk pengembang Laravel agar dapat mengonsumsi REST API dari `python-ai-service` secara efisien, aman, dan selaras 100% dengan skema database terbaru (**3NF Normalized & Granular Per-Unit/Per-Hour Capacity Allocations**).

---

## 🌐 Konfigurasi Dasar & Base URL

### Base URL Microservice:
- **Pengembangan Lokal (Local Development):** `http://localhost:8000`
- **Docker Compose Network:** `http://python-ai-service:8000`
- **Production Staging:** `http://ai-engine.kideco.co.id:8000`

### Headers HTTP Wajib:
```http
Content-Type: application/json
Accept: application/json
```

---

## ⚙️ 1. Setup Konfigurasi Laravel (`.env` & `config/services.php`)

Tambahkan variabel berikut pada file `.env` Laravel:

```env
AI_SERVICE_BASE_URL=http://localhost:8000
AI_SERVICE_TIMEOUT_SECONDS=5
AI_SERVICE_RETRY_TIMES=3
```

Daftarkan pada `config/services.php`:

```php
'ai_service' => [
    'base_url' => env('AI_SERVICE_BASE_URL', 'http://localhost:8000'),
    'timeout'  => env('AI_SERVICE_TIMEOUT_SECONDS', 5),
    'retry'    => env('AI_SERVICE_RETRY_TIMES', 3),
],
```

---

## 📡 2. Daftar REST API Endpoints & Respon Payload Terbaru

### 2.1. Health Check & Readiness Probes

#### A. Health Check (`GET /health`)
Memeriksa kesehatan microservice dan koneksi database.

- **Request:** `GET /health`
- **Response `200 OK`:**
```json
{
  "status": "healthy",
  "environment": "development",
  "database": {
    "status": "connected",
    "dialects": "sqlite"
  }
}
```

#### B. Readiness Probe (`GET /ready`)
Memastikan model ML (XGBoost & PyTorch Autoencoder) sudah pre-loaded di RAM dan siap melayani permintaan inferensi (< 2.0s).

- **Request:** `GET /ready`
- **Response `200 OK`:**
```json
{
  "status": "ready",
  "warmup_details": {
    "status": "ready",
    "warmup_duration_ms": 62.84,
    "xgboost_warmed_up": true,
    "xgboost_warmup_ms": 55.2,
    "pytorch_autoencoder_warmed_up": true,
    "pytorch_warmup_ms": 41.23,
    "database_status": "connected"
  }
}
```

---

### 2.2. Fuel Ratio Forecasting Endpoint (`POST /api/v1/forecast`)

Prediksi Fuel Ratio harian (L/BCM) menggunakan **XGBoost Regressor Model** dengan penyesuaian faktor cuaca dan jarak angkut. Automatically syncs to table `daily_forecast_logs`.

- **Endpoint:** `POST /api/v1/forecast`
- **Request Payload Example:**
```json
{
  "date": "2026-08-05",
  "curah_hujan_mm": 12.5,
  "temp_max_c": 32.0,
  "kecepatan_angin_kmh": 14.2,
  "haul_distance_m": 4200.0,
  "daily_prod_bcm": 45000.0
}
```

- **Response Payload `200 OK` Example:**
```json
{
  "log_date": "2026-08-05",
  "forecast_fr": 1.0234,
  "status": "NORMAL",
  "budget_baseline": 1.018,
  "warning_threshold": 1.0994,
  "critical_threshold": 1.2012,
  "features_used": {
    "Curah_Hujan_mm": 12.5,
    "Temp_Max_C": 32.0,
    "Kecepatan_Angin_kmh": 14.2,
    "Haul_Distance_m": 4200.0,
    "Daily_Prod_BCM": 45000.0,
    "Rain_Lag1": 0.0,
    "FR_Lag1": 1.018
  }
}
```

---

### 2.3. Unit Anomaly Detection Endpoint (`POST /api/v1/anomaly-detect`)

Memindai log konsumsi BBM harian per unit alat berat menggunakan **PyTorch Deep Autoencoder Neural Network** untuk mendeteksi *lonjakan tak wajar (spike anomalies)*. Automatically syncs to table `unit_anomaly_spikes`.

- **Endpoint:** `POST /api/v1/anomaly-detect`
- **Request Payload Example:**
```json
{
  "records": [
    {
      "Date": "2026-08-05",
      "Unit": "HD785-7",
      "Activity": "HAULING",
      "FC_Actual": 75.0,
      "Unit_Fuel_L_Day": 1500.0,
      "Unit_FR": 0.26,
      "Rain_mm": 5.0
    },
    {
      "Date": "2026-08-05",
      "Unit": "HD785-SPIKE",
      "Activity": "HAULING",
      "FC_Actual": 165.0,
      "Unit_Fuel_L_Day": 3300.0,
      "Unit_FR": 0.58,
      "Rain_mm": 5.0
    }
  ]
}
```

- **Response Payload `200 OK` Example:**
```json
{
  "total_records_scanned": 2,
  "total_spikes_detected": 1,
  "spikes": [
    {
      "date": "2026-08-05",
      "unit": "HD785-SPIKE",
      "activity": "HAULING",
      "fc_actual": 165.0,
      "unit_fuel_l_day": 3300.0,
      "unit_fr": 0.58,
      "rain_mm": 5.0,
      "reconstruction_error": 2.451203,
      "threshold_used": 1.872077,
      "is_spike": 1
    }
  ],
  "spike_report_per_unit": [
    {
      "unit": "HD785-SPIKE",
      "activity": "HAULING",
      "total_spikes": 1,
      "avg_fc_normal": 0.0,
      "avg_fc_spike": 165.0,
      "max_fr_recorded": 0.58
    }
  ],
  "detail_report_per_activity": [
    {
      "activity": "HAULING",
      "total_unit_types": 2,
      "total_spike_events": 1,
      "avg_unit_fr": 0.42,
      "total_fuel_cons_l": 4800.0
    }
  ]
}
```

---

### 2.4. Combined Capacity Determination Endpoint (`POST /api/v1/calculate-capacity`)

Kalkulasi penentuan alokasi kapasitas armada efektif, utilisasi %, unit operasional, dan alokasi Solar harian **Secara Rinci Per-Unit & Per-Jam** untuk setiap aktivitas (`LOADING`, `HAULING`, `SUPPORT`, `DEWATERING`). Automatically syncs to tables `capacity_allocations` & `capacity_unit_allocations`.

- **Endpoint:** `POST /api/v1/calculate-capacity`
- **Request Payload Example:**
```json
{
  "date": "2026-08-05",
  "forecast_prod_bcm": 40000.0,
  "curah_hujan_mm": 12.5,
  "equipment_list": null,
  "nn_spike_count_by_unit": {
    "HD785-7MUD": 1
  }
}
```

- **Response Payload `200 OK` Example (Dilengkapi Breakdown Per-Unit & Per-Jam):**
```json
{
  "log_date": "2026-08-05",
  "forecast_prod_bcm": 40000.0,
  "curah_hujan_mm": 12.5,
  "rain_derating_factor": 0.8251,
  "installed_prod_bcmhr": 24200.0,
  "effective_prod_bcmday": 399348.4,
  "utilization_pct": 10.02,
  "total_fleet_qty": 326,
  "operating_units": 33,
  "total_combined_fuel_lday": 58240.5,
  "activity_breakdown": [
    {
      "activity": "LOADING",
      "unit_types_count": 3,
      "total_fleet_qty": 25,
      "operating_units": 3,
      "prod_bcm_hr_total": 2050.0,
      "prod_bcm_day_effective": 33829.1,
      "fuel_l_hr_total": 408.33,
      "combined_fuel_lday": 7242.0
    },
    {
      "activity": "HAULING",
      "unit_types_count": 2,
      "total_fleet_qty": 205,
      "operating_units": 21,
      "prod_bcm_hr_total": 2300.76,
      "prod_bcm_day_effective": 37967.14,
      "fuel_l_hr_total": 1575.0,
      "combined_fuel_lday": 35397.0
    }
  ],
  "unit_breakdown": [
    {
      "unit_name": "EX2600-6",
      "activity": "LOADING",
      "total_qty": 1,
      "operating_units": 1,
      "prod_bcm_hr_unit": 920.0,
      "prod_bcm_hr_total": 920.0,
      "prod_bcm_day_total": 15181.84,
      "fuel_l_hr_unit": 190.0,
      "fuel_l_hr_total": 190.0,
      "fuel_l_day_total": 380.76,
      "unit_fr": 0.0251,
      "spike_count_nn": 0
    },
    {
      "unit_name": "PC2000-11R",
      "activity": "LOADING",
      "total_qty": 17,
      "operating_units": 2,
      "prod_bcm_hr_unit": 820.0,
      "prod_bcm_hr_total": 1640.0,
      "prod_bcm_day_total": 27063.28,
      "fuel_l_hr_unit": 125.0,
      "fuel_l_hr_total": 250.0,
      "fuel_l_day_total": 501.0,
      "unit_fr": 0.0185,
      "spike_count_nn": 0
    },
    {
      "unit_name": "HD785-7",
      "activity": "HAULING",
      "total_qty": 172,
      "operating_units": 18,
      "prod_bcm_hr_unit": 109.56,
      "prod_bcm_hr_total": 1972.08,
      "prod_bcm_day_total": 32543.26,
      "fuel_l_hr_unit": 75.0,
      "fuel_l_hr_total": 1350.0,
      "fuel_l_day_total": 2705.4,
      "unit_fr": 0.0831,
      "spike_count_nn": 0
    }
  ]
}
```

---

## 💻 3. Contoh Implementasi Client Service Class di Laravel (PHP)

Buat file Service Class `app/Services/FuelRatioAiClient.php` di Laravel:

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Exception;

class FuelRatioAiClient
{
    protected string $baseUrl;
    protected int $timeout;
    protected int $retry;

    public function __construct()
    {
        $this->baseUrl = config('services.ai_service.base_url', 'http://localhost:8000');
        $this->timeout = config('services.ai_service.timeout', 5);
        $this->retry   = config('services.ai_service.retry', 3);
    }

    /**
     * Memanggil HTTP request standar dengan auto retry & error handling
     */
    protected function request(string $method, string $endpoint, array $data = [])
    {
        $url = rtrim($this->baseUrl, '/') . '/' . ltrim($endpoint, '/');

        try {
            $response = Http::timeout($this->timeout)
                ->retry($this->retry, 100)
                ->withHeaders([
                    'Accept' => 'application/json',
                    'Content-Type' => 'application/json',
                ])
                ->$method($url, $data);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error("AI Service Error [{$response->status()}]: " . $response->body());
            throw new Exception("AI Service HTTP Error: " . $response->status());

        } catch (Exception $e) {
            Log::emergency("Gagal menghubungi AI Microservice di {$url}: " . $e->getMessage());
            throw $e;
        }
    }

    /**
     * Prediksi Fuel Ratio Harian (XGBoost Engine)
     */
    public function getForecast(string $date, float $rainMm, float $tempC, float $windKmh, float $haulM, float $prodBcm): array
    {
        return $this->request('post', '/api/v1/forecast', [
            'date' => $date,
            'curah_hujan_mm' => $rainMm,
            'temp_max_c' => $tempC,
            'kecepatan_angin_kmh' => $windKmh,
            'haul_distance_m' => $haulM,
            'daily_prod_bcm' => $prodBcm,
        ]);
    }

    /**
     * Deteksi Lonjakan BBM Unit (PyTorch Autoencoder)
     */
    public function detectAnomalies(array $records): array
    {
        return $this->request('post', '/api/v1/anomaly-detect', [
            'records' => $records,
        ]);
    }

    /**
     * Kalkulasi Penentuan Kapasitas Armada & Solar Kombinasi Per-Unit Per-Jam
     */
    public function calculateCapacity(string $date, float $forecastProdBcm, float $rainMm, ?array $spikeMap = null): array
    {
        return $this->request('post', '/api/v1/calculate-capacity', [
            'date' => $date,
            'forecast_prod_bcm' => $forecastProdBcm,
            'curah_hujan_mm' => $rainMm,
            'nn_spike_count_by_unit' => $spikeMap,
        ]);
    }

    /**
     * Check Kesiapan Microservice
     */
    public function isReady(): bool
    {
        try {
            $res = $this->request('get', '/ready');
            return isset($res['status']) && $res['status'] === 'ready';
        } catch (Exception $e) {
            return false;
        }
    }
}
```

---

## 🗄️ 4. Pemetaan Tabel Database Laravel Terkait

Setiap panggillan API secara otomatis disinkronkan ke tabel database utama berikut:

| Endpoint REST API | Tabel Database Utama | Tabel Database Granular Per-Unit |
|:------------------|:---------------------|:---------------------------------|
| `POST /api/v1/forecast` | `daily_forecast_logs` | - |
| `POST /api/v1/anomaly-detect` | `unit_anomaly_spikes` | `equipment_catalogs` (Foreign Key `equipment_id`) |
| `POST /api/v1/calculate-capacity` | `capacity_allocations` | **`capacity_unit_allocations`** (Relasi 1:N Foreign Key `capacity_allocation_id`) |

---

## 🛡️ 5. Penanganan Failure & Resilience di Laravel

1. **Graceful Fallback**: Jika AI Service mengalami timeout/downtime, gunakan baseline default ($1.018$ L/BCM) agar aplikasi Laravel tidak crash.
2. **Logging Error**: Setiap kegagalan HTTP otomatis dicatat pada `storage/logs/laravel.log`.
3. **Automatic Retry**: Laravel HTTP Client secara otomatis akan mencoba ulang hingga 3 kali dengan selisih waktu 100ms.
