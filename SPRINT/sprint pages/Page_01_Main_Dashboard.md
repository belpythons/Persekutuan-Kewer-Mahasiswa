# DESIGN SYSTEM BREAKDOWN: PAGE 1 - MAIN EXECUTIVE DASHBOARD
## SYSTEM MONITORING FUEL RATIO (FR) BASIS OPERASIONAL & CAPACITY MANAGEMENT TAMBANG
**Route File:** `/dashboard`  
**Target User:** Operational Manager, Mining General Manager, Mine Dispatcher  
**Tujuan Utama:** Memberikan gambaran seketika (*at-a-glance*) tentang kesehatan Fuel Ratio tambang hari ini, alert ambang batas dinamis, ringkasan unit bermasalah (*spike anomaly*), dan perbandingan data aktual vs prediksi.

---

## 1. LAYOUT STRUCTURE & WIREFRAME ASCII

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER SYSTEM NAVBAR: Logo Tambang | Real-Time Weather Widget | Date Selector | User Profile     │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 1: HERO SECTION - ALERT & ANOMALY ENGINE                                                   │
│ ┌───────────────────────────┐ ┌───────────────────────────┐ ┌──────────────────────────────────┐ │
│ │ COMPONENT: Threshold Alert│ │ COMPONENT: PyTorch Spike  │ │ COMPONENT: Top Anomalous Units   │ │
│ │ Current FR: 1.280 L/BCM   │ │ 375 Spike Events Detected │ │ Leaderboard (5 Unit Teratas)     │ │
│ │ Status: ⚠️ WARNING (+8%)   │ │ Anomaly Ratio: 7.2% Fleet │ │ HD785-7 (366 Spike / +4.2% Fuel) │ │
│ └───────────────────────────┘ └───────────────────────────┘ └──────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 2: VISUAL ANALYTICS WIDGETS                                                                 │
│ ┌────────────────────────────────────────────────────────┐ ┌────────────────────────────────────┐ │
│ │ COMPONENT: FR Trend 30-Day Line Chart                  │ │ COMPONENT: Activity Fuel Donut     │ │
│ │ Actual FR vs Target Budget vs Warning & Critical Line   │ │ Hauling 64.1% | Supporting 15.5%   │ │
│ └────────────────────────────────────────────────────────┘ └────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 3: MAIN DATA TABLE - ACTUAL VS FORECAST SIDE-BY-SIDE                                        │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: SideBySideDataTable                                                               │ │
│ │ Filter Bar: Search Date | Status Filter (Normal/Warning/Critical) | Export CSV Button        │ │
│ │ [Table Column: Date | Rainfall | Haul Dist | ACTUAL DATA | FORECAST DATA | Variance | Status] │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. BREAKDOWN KOMPONEN UI & SPESIFIKASI DESIGN SYSTEM

### Komponen 1.1: `DynamicThresholdAlertWidget`
- **Tipe Komponen:** Executive Status Card & Radial Gauge
- **Peran:** Menampilkan nilai Fuel Ratio hari ini dan status kesehatan terhadap budget baseline (1.1576 L/BCM).
- **Spesifikasi Visual & Warna:**
  - **NORMAL Status:** Background Green Tint (`#E6F4EA`), Text/Border Solid Green (`#137333`). FR < 1.2503 L/BCM.
  - **WARNING Status (+8%):** Background Yellow Tint (`#FEF7E0`), Text/Border Solid Amber (`#B06000`). 1.2503 L/BCM ≤ FR < 1.3660 L/BCM.
  - **CRITICAL Status (+18%):** Background Red Tint (`#FCE8E6`), Text/Border Solid Red (`#C5221F`). FR ≥ 1.3660 L/BCM.
- **Data Binding:**
  - `actual_fr_today` (float, e.g., `1.2800`)
  - `budget_baseline` (constant, `1.1576`)
  - `warning_threshold` (constant, `1.2503`)
  - `critical_threshold` (constant, `1.3660`)
  - `excess_fuel_liters` (calculated: `(actual_fr_today - budget_baseline) * daily_bcm`)

### Komponen 1.2: `PyTorchSpikeSummaryWidget`
- **Tipe Komponen:** Anomaly Metric Card & Scanner
- **Peran:** Menampilkan rekapitulasi anomali kebocoran/lonjakan BBM unit alat berat hasil inferensi model PyTorch Autoencoder.
- **Spesifikasi Visual:**
  - Badge Jumlah Anomali: Pill Badge Merah Menyala (`#D93025`) dengan animasi efek Pulse Dot.
  - Teks Indikator: Font Outfit/Inter SemiBold 24px (`375 Spike Events`).
- **Data Binding:**
  - `total_spikes_24h` (integer, e.g., `375`)
  - `anomalous_units_count` (integer, e.g., `61`)
  - `reconstruction_error_p93_5` (float threshold)

### Komponen 1.3: `TopAnomalousEquipmentLeaderboard`
- **Tipe Komponen:** Interactive Quick-Action List
- **Peran:** Ranking 5 unit alat berat penyebab lonjakan solar tertinggi untuk tindakan inspeksi mekanis (*Quick Dispatch*).
- **Elemen Tabel Mini:**
  1. `HD785-7` (Hauling) | 366 Spikes | FC Normal: 77 L/hr ➔ FC Spike: 80.78 L/hr | Max FR: 182.24
  2. `EX2600-6` (Loading) | 366 Spikes | FC Normal: 187 L/hr ➔ FC Spike: 192.28 L/hr
  3. `PC2000-11R` (Loading) | 9 Spikes | FC Normal: 100 L/hr ➔ FC Spike: 185.53 L/hr
  4. `EGS380-6` (Dewatering) | 9 Spikes | FC Normal: 10 L/hr ➔ FC Spike: 10.70 L/hr
- **Interaksi:** Hover pada unit menampilkan tooltip detail; Klik membuka drawer `UnitDrillDownModal`.

### Komponen 1.4: `SideBySideDataTable` (Utama)
- **Tipe Komponen:** Data Table Grid dengan Dual-Header Column Grouping
- **Peran:** Menyandingkan data aktual lapangan dari FMS secara presisi di samping hasil prediksi model XGBoost Regressor.
- **Struktur Kolom Data:**

| Header Group | Nama Kolom | Field Key Data | Tipe Data | Format Tampilan |
|:---|:---|:---|:---|:---|
| **General** | Tanggal | `date` | Date | `DD/MM/YYYY` |
| **Environment**| Curah Hujan | `Curah_Hujan_mm` | Float | `0.0 mm` |
| **Environment**| Jarak Angkut | `Haul_Distance_m` | Integer | `3,900 m` |
| **ACTUAL DATA (FMS)**| Actual BCM | `Actual_BCM` | Float | `250,120 BCM` |
| **ACTUAL DATA (FMS)**| Actual Fuel | `Actual_Fuel_L` | Float | `289,240 L` |
| **ACTUAL DATA (FMS)**| Actual FR | `Actual_FR_L_BCM` | Float | `1.1564 L/BCM` |
| **XGBOOST FORECAST** | Forecast BCM | `Forecast_BCM` | Float | `250,072 BCM` |
| **XGBOOST FORECAST** | Forecast Fuel | `Forecast_Fuel_L` | Float | `289,083 L` |
| **XGBOOST FORECAST** | Forecast FR | `Forecast_FR_L_BCM` | Float | `1.1560 L/BCM` |
| **Metrics** | Variance FR | `Variance_FR` | Float | `+0.0004 L/BCM` |
| **Metrics** | Status Alert | `Status_Alert` | Enum | Badge (`NORMAL` / `WARNING` / `CRITICAL`) |

---

## 3. INTEGRASI DATA API & STATE MANAGEMENT

- **Endpoint API Backend:**
  - `GET /api/v1/dashboard/summary-kpi` -> Mengembalikan KPI Hero Section.
  - `GET /api/v1/dashboard/actual-vs-forecast?start_date=...&end_date=...` -> Mengembalikan array JSON side-by-side data table.
  - `GET /api/v1/anomalies/top-leaderboard?limit=5` -> Mengembalikan top 5 anomalous units.
- **State Management (React/Vue/Svelte):**
  - `selectedDateRange`: Active date range filter.
  - `alertStatusFilter`: Filter status tabel (`ALL`, `NORMAL`, `WARNING`, `CRITICAL`).
  - `isLiveAutoRefresh`: Toggle polling interval 30 detik untuk data sensor FMS.
