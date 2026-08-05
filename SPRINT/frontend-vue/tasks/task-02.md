# TASK-FE-02: Executive Dashboard - Trend, Anomaly Leaderboard & Threshold Alert Widgets

## 📌 Sprint Target
**Sprint 9**

---

## 📝 Description & Context
Pengembangan modul **Executive Dashboard** (`laravel/resources/ts/pages/dashboard.vue`) yang berfungsi sebagai pusat kendali operasional Fuel Ratio (FR). Modul ini menampilkan analisis tren deret waktu 30-hari, alert ambang batas dinamis (+8% Warning, +18% Critical), ringkasan spike anomali dari model PyTorch Autoencoder, leaderboard unit paling anomali, distribusi konsumsi BBM per aktivitas, dan tabel rincian data aktual vs forecast.

---

## ✅ Acceptance Criteria (AC)
- [ ] Widget `DynamicThresholdAlertWidget.vue` menampilkan status real-time (`NORMAL`, `WARNING`, `CRITICAL`), baseline budget (1.1576 L/BCM), warning threshold (1.2503 L/BCM), critical threshold (1.3660 L/BCM), dan kalkulasi estimasi pemborosan BBM (*excess fuel liters*).
- [ ] Widget `PyTorchSpikeSummaryWidget.vue` menampilkan total event spike terdeteksi, jumlah unit anomali, dan total populasi unit yang dipindai.
- [ ] Komponen `TopAnomalousLeaderboard.vue` menyajikan daftar unit teratas yang mengalami lonjakan konsumsi BBM beserta aktivitas dan nilai reconstruction error / Unit FR.
- [ ] Komponen `FrTrendLineChart.vue` menampilkan grafik Vue ApexCharts smooth line 30-hari yang membandingkan *Actual FR* vs *XGBoost Forecast FR* lengkap dengan garis *annotation threshold*.
- [ ] Komponen `ActivityFuelDonutChart.vue` memvisualisasikan proporsi konsumsi solar (L/Day) per aktivitas tambang (`LOADING`, `HAULING`, `BULLDOZING`, `CRUSHING`, `BARGING`).
- [ ] Tabel `ActualVsForecastTable.vue` menyajikan breakdown data harian yang mendukung filtering dan pagination.
- [ ] Halaman `dashboard.vue` memanggil 3 endpoint AI secara paralel menggunakan `Promise.allSettled` melalui `useAiApi.ts`.

---

## 🛠️ Technical Implementation Details

### File & Path Target
- **Page Container**: `laravel/resources/ts/pages/dashboard.vue`
- **Dashboard Views**:
  - `laravel/resources/ts/views/dashboard/DynamicThresholdAlertWidget.vue`
  - `laravel/resources/ts/views/dashboard/PyTorchSpikeSummaryWidget.vue`
  - `laravel/resources/ts/views/dashboard/TopAnomalousLeaderboard.vue`
  - `laravel/resources/ts/views/dashboard/FrTrendLineChart.vue`
  - `laravel/resources/ts/views/dashboard/ActivityFuelDonutChart.vue`
  - `laravel/resources/ts/views/dashboard/ActualVsForecastTable.vue`

### Composable / API Client Used
- `useAiApi.ts` -> `fetchForecast`, `fetchAnomalyDetect`, `fetchCalculateCapacity`

### State Management & Props/Emits
- **Props `DynamicThresholdAlertWidget.vue`**:
  - `actualFr: number`
  - `budgetBaseline: number`
  - `warningThreshold: number`
  - `criticalThreshold: number`
  - `excessFuelLiters: number`
  - `isLoading: boolean`
- **Props `PyTorchSpikeSummaryWidget.vue`**:
  - `totalSpikes: number`
  - `anomalousUnitsCount: number`
  - `totalFleetUnits: number`
  - `isLoading: boolean`
- **Props `TopAnomalousLeaderboard.vue`**:
  - `spikeReport: SpikeReportPerUnit[] | null`
  - `isLoading: boolean`
- **Props `ActivityFuelDonutChart.vue`**:
  - `activityBreakdown: ActivityBreakdown[] | null`
  - `totalFuel: number | null`

---

## 🎯 Definition of Done (DoD)
- [ ] Komponen Vue dirender tanpa error pada console browser.
- [ ] Seluruh grafik Vue ApexCharts responsif terhadap perubahan ukuran layar (desktop, tablet, mobile).
- [ ] Integrasi `Promise.allSettled` menangani kondisi error/fallback API dengan gracefully tanpa memblokir seluruh widget.
- [ ] TypeScript type checking lolos tanpa error.
