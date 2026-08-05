# 📄 Panduan Lengkap Alur Sistem & Formulasi Perhitungan AI Microservice

Dokumen ini berisi penjelasan lengkap mengenai alur kerja sistem, komponen kecerdasan buatan (FastAPI + XGBoost + PyTorch Autoencoder), dan **seluruh formulasi matematika perhitungan** pada **Microservice Python AI Engine** (`python-ai-service/`).

---

## 📌 Ringkasan Eksekutif & Arsitektur Microservice

Microservice Python AI Engine dirancang khusus untuk mengolah data operasional penambangan batu bara PT Kideco Jaya Agung. Service ini menyediakan 3 kapabilitas utama berbasis AI:
1. **Prediksi Fuel Ratio Harian (XGBoost Regressor Model)** dengan penyesuaian faktor cuaca dan jarak angkut.
2. **Deteksi Anomali Lonjakan BBM Unit Alat Berat (PyTorch Deep Autoencoder Neural Network)** dengan Adaptive MAD Threshold per aktivitas.
3. **Penentuan Alokasi Kapasitas Efektif & Solar Kombinasi (Combined Capacity Engine)** yang menghitung rincian per-unit dan per-jam untuk 4 aktivitas (`LOADING`, `HAULING`, `SUPPORT`, `DEWATERING`) menggunakan **Derating Hujan Non-Linear**.

---

## 🔄 Diagram Alur Kerja Utama Microservice (System Workflow)

```
[STEP 1: INGESTION] Input parameter dari Laravel Portal (Tanggal, Curah Hujan, Temp, Wind, Haul Distance, Target Prod).
       │
       ▼
[STEP 2: QUALITY CHECK & FEATURE ENGINEERING] Imputasi missing values, outlier clipping, pembentukan 13 fitur ML (Rain Lags, FR Lags, Rolling 7d Avg).
       │
       ▼
[STEP 3: XGBOOST INFERENCE] Model XGBoost menghitung prediksi Fuel Ratio Harian (L/BCM) & mengevaluasi status (NORMAL / WARNING / CRITICAL).
       │
       ▼
[STEP 4: PYTORCH AUTOENCODER SCAN] Scan log unit harian. Autoencoder menghitung MSE reconstruction error & menguji terhadap Adaptive MAD Threshold per aktivitas.
       │
       ▼
[STEP 5: CAPACITY & RAIN DERATING ENGINE] Menghitung derating hujan non-linear, utilisasi %, unit operasional, serta alokasi BBM kombi per-unit per-jam.
       │
       ▼
[STEP 6: DATABASE SYNC & REST RESPONSE] Penyelarasan log ke tabel DB daily_forecast_logs, unit_anomaly_spikes, & capacity_unit_allocations.
```

---

## 📐 Formulasi Perhitungan Detail & Rumus Matematika

### 1. Formulasi 13 Fitur Machine Learning (Feature Engineering)

Model XGBoost Regressor menggunakan 13 fitur yang diturunkan dari data historis operasional dan meteorologi:

| Nama Fitur | Simbol Matematika | Rumus / Penjelasan Formulasi |
|:-----------|:------------------|:-----------------------------|
| `Curah_Hujan_mm` | $R(t)$ | Curah hujan harian aktual / prakiraan (mm) |
| `Temp_Max_C` | $T_{\text{max}}(t)$ | Temperatur udara maksimum harian (°C) |
| `Kecepatan_Angin_kmh` | $W(t)$ | Kecepatan angin harian (km/h) (Solusi Celah #13) |
| `Haul_Distance_m` | $H(t)$ | Jarak angkut rata-rata dari pit ke ROM/dump (meter) |
| `Daily_Prod_BCM` | $P(t)$ | Total volume produksi overburden/batu bara (BCM) |
| `DayOfWeek` | $Dow(t)$ | Indeks hari dalam seminggu (0 = Senin, 6 = Minggu) |
| `Month` | $M(t)$ | Indeks bulan (1 s/d 12) |
| `IsWeekend` | $Wknd(t)$ | 1 jika $Dow(t) \in \{5, 6\}$, 0 untuk hari kerja biasa |
| `Rain_Lag1` | $R(t-1)$ | Curah hujan 1 hari sebelumnya (mm) |
| `Rain_Lag2` | $R(t-2)$ | Curah hujan 2 hari sebelumnya (mm) |
| `FR_Lag1` | $FR(t-1)$ | Fuel Ratio realisasi 1 hari sebelumnya (L/BCM) |
| `FR_Lag2` | $FR(t-2)$ | Fuel Ratio realisasi 2 hari sebelumnya (L/BCM) |
| `RollingAvg_FR_7d` | $\bar{FR}_{7d}(t)$ | Rata-rata bergerak Fuel Ratio 7 hari: $\frac{1}{7} \sum_{i=1}^7 FR(t-i)$ |

---

### 2. Model XGBoost & Evaluasi Status Threshold Dynamic

Model XGBoost dilatih menggunakan *TimeSeriesSplit (5-Fold Cross Validation)*. Hasil prediksi $FR_{\text{Forecast}}$ dibandingkan dengan threshold anggaran baseline:

- **Target Budget Baseline Total FR:** $FR_{\text{Budget}} = 1.018 \text{ L/BCM}$
- **Warning Threshold (+8%):** $FR_{\text{Warning}} = 1.018 \times 1.08 = 1.0994 \text{ L/BCM}$
- **Critical Threshold (+18%):** $FR_{\text{Critical}} = 1.018 \times 1.18 = 1.2012 \text{ L/BCM}$

**Aturan Evaluasi Status:**
$$\text{Status} = \begin{cases} \text{CRITICAL} & \text{jika } FR_{\text{Forecast}} \ge 1.2012 \\ \text{WARNING} & \text{jika } 1.0994 \le FR_{\text{Forecast}} < 1.2012 \\ \text{NORMAL} & \text{jika } FR_{\text{Forecast}} < 1.0994 \end{cases}$$

---

### 3. PyTorch Deep Autoencoder & Adaptive MAD Threshold

Untuk mendeteksi lonjakan konsumsi BBM (*spike anomaly*) yang tidak wajar pada unit alat berat:

1. **Pelatihan Hanya pada Data Normal (Solusi Celah #4):** Autoencoder di-train HANYA menggunakan record dengan `nn_anomaly_spike == 0`.
2. **Arsitektur Jaringan:** Encoder: `Input(3) -> 16 (ReLU) -> 8 (ReLU) -> Latent(3)`. Decoder: `Latent(3) -> 8 (ReLU) -> 16 (ReLU) -> Input(3)`.
3. **Fitur Rasio Relatif Unit:** Input tensor berupa `[FC_Ratio, Unit_FR_Ratio, Unit_Fuel_Ratio]` di mana $FC_{\text{Ratio}} = \frac{FC_{\text{Actual}}}{FC_{\text{Base}}}$.
4. **Mean Squared Reconstruction Error (MSE):**
   $$e_i = \frac{1}{3} \sum_{j=1}^3 (x_{i,j} - \hat{x}_{i,j})^2$$
5. **Adaptive Threshold berbasis Median Absolute Deviation (MAD) (Solusi Celah #5):**
   $$\text{MAD} = \text{Median}(|e_i - \text{Median}(e)|)$$
   $$\text{Threshold}_{\text{Activity}} = \max(\text{Percentile}_{99.5}(e_{\text{Normal}}), \text{Median}(e_{\text{Normal}}) + 5.0 \times 1.4826 \times \text{MAD})$$
6. **Isolasi Spike Anomali:** Jika $e_i > \text{Threshold}_{\text{Activity}}$, record ditandai **Is_Spike = 1** dan memicu buffer Solar sebesar +15%.

---

### 4. Combined Capacity Engine & Formulasi Derating Hujan Non-Linear

Penurunan kapasitas produksi akibat curah hujan dihitung menggunakan formula non-linear (Solusi Celah #9):

$$\text{Derating Factor } D(R) = \begin{cases} 1.0 & \text{jika } R \le 5.0 \text{ mm} \\ 1.0 - 0.01 \times (R - 5.0)^{1.3} & \text{jika } 5.0 < R \le 20.0 \text{ mm} \\ \max(0.65, 0.82 - 0.005 \times (R - 20.0)^{1.1}) & \text{jika } 20.0 < R \le 50.0 \text{ mm} \\ 0.60 & \text{jika } R > 50.0 \text{ mm} \end{cases}$$

**Formulasi Alokasi Kapasitas Per-Unit & Per-Jam:**

1. **Kapasitas Terpasang Total:**
   $$\text{Cap}_{\text{Installed}} = \sum (\text{Qty}_u \times \text{ProdBCMhr}_u) \quad (\text{BCM/hr})$$
2. **Kapasitas Efektif Harian Total:**
   $$\text{Cap}_{\text{Effective}} = \text{Cap}_{\text{Installed}} \times 20.0 \text{ jam} \times D(R) \quad (\text{BCM/day})$$
3. **Persentase Utilisasi Armada (%):**
   $$\text{Utilisation \%} = \min\left(100.0, \max\left(10.0, \frac{\text{ForecastProdBCM}}{\text{Cap}_{\text{Effective}}} \times 100\%\right)\right)$$
4. **Jumlah Unit Operasional per Tipe Alat:**
   $$\text{OperatingUnits}_u = \min\left(\text{Qty}_u, \left\lceil \frac{\text{Utilisation \%}}{100} \times \text{Qty}_u \right\rceil\right)$$
5. **Produktivitas Per Jam & Per Hari per Tipe Alat:**
   $$\text{ProdBCMhrTotal}_u = \text{OperatingUnits}_u \times \text{ProdBCMhr}_u \quad (\text{BCM/hr})$$
   $$\text{ProdBCMdayTotal}_u = \text{ProdBCMhrTotal}_u \times 20.0 \text{ jam} \times D(R) \quad (\text{BCM/day})$$
6. **Konsumsi BBM Solar Per Jam & Per Hari per Tipe Alat (Liter):**
   $$\text{FuelLhrTotal}_u = \text{OperatingUnits}_u \times \text{FCLhr}_u \quad (\text{Liter/hr})$$
   $$\text{BaseFuelDay}_u = \text{FuelLhrTotal}_u \times 20.0 \text{ jam} \times \frac{\text{Utilisation \%}}{100} \quad (\text{Liter/day})$$
   $$\text{CombinedFuelDay}_u = \text{BaseFuelDay}_u \times (1.0 + 0.15 \times \text{SpikeCount}_u) \quad (\text{Liter/day})$$
7. **Individual Unit Fuel Ratio (L/BCM):**
   $$\text{UnitFR}_u = \frac{\text{CombinedFuelDay}_u}{\max(1.0, \text{ProdBCMdayTotal}_u)} \quad (\text{L/BCM})$$

---

### 5. Formulasi IoT Machine Telemetry vs Weather Capacity Comparator Engine

Sistem ini membandingkan data telemetri aktual dari sensor mesin hardware IoT (*flowmeter* solar, Hour Meter HM, dan payload VIMS) terhadap **Kapasitas Efektif Disesuaikan Cuaca BMKG**:

1. **Weather-Adjusted Allowed Fuel (Batas Toleransi BBM Hujan):**
   $$\text{Max Allowed Fuel}_i = \text{HM}_{\text{IoT}, i} \times \text{FC}_{\text{Std}, i} \times D(R) \times (1.0 + \text{Threshold Warning 8\% / Critical 18\%})$$
2. **Kalkulasi Variansi Solar (Liters & %):**
   $$\text{Variance Liters}_i = \text{FuelConsumed}_{\text{IoT}, i} - (\text{HM}_{\text{IoT}, i} \times \text{FC}_{\text{Std}, i} \times D(R))$$
   $$\text{Variance \%}_i = \left(\frac{\text{Variance Liters}_i}{\text{HM}_{\text{IoT}, i} \times \text{FC}_{\text{Std}, i} \times D(R)}\right) \times 100\%$$
3. **Kriteria Evaluasi Anomali IoT:**
   - `NORMAL_EFFICIENT`: $\text{Variance \%}_i \le 8.0\%$
   - `WARNING_OVER_CONSUMPTION`: $8.0\% < \text{Variance \%}_i \le 18.0\%$
   - `CRITICAL_IOT_FUEL_SPIKE`: $\text{Variance \%}_i > 18.0\%$ (`is_iot_anomaly = true`)
   - `WEATHER_SLIPPAGE_ANOMALY`: Dipicu saat $D(R) < 0.85$ (hujan deras), jam kerja $\text{HM} \ge 12\text{ jam}$, tetapi muatan BCM drop akibat slip/lumpur.

---

## 🌐 Panduan Integrasi REST API untuk Aplikasi Laravel

| Endpoint HTTP | Fungsi & Kegunaan Utama | Tabel Sync Database |
|:--------------|:------------------------|:--------------------|
| `POST /api/v1/forecast` | Prediksi Fuel Ratio harian (L/BCM) XGBoost & status alert. | `daily_forecast_logs` |
| `POST /api/v1/anomaly-detect` | Scan log BBM unit & isolasi lonjakan spike anomali PyTorch. | `unit_anomaly_spikes` |
| `POST /api/v1/calculate-capacity` | Kalkulasi utilisasi %, unit aktif, & BBM per-unit per-jam. | `capacity_allocations` |
| `POST /api/v1/global-capacity-tuning` | Analisis variansi alokasi teoritis vs pemakaian harian aktual. | `capacity_allocations` |
| `POST /api/v1/weather/sync-bmkg` | Sinkronisasi otomatis data cuaca real-time BMKG Paser Kaltim. | `weather_daily_logs` |
| `POST /api/v1/iot/capacity-anomaly-audit` | Audit komparasi anomali sensor IoT vs toleransi cuaca. | `iot_telemetry_logs` |
| `GET /ready` | Readiness probe memastikan model ML ter-load di RAM (< 60ms). | RAM Cache Status |

