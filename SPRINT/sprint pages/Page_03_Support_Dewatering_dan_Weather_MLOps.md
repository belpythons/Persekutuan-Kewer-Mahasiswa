# DESIGN SYSTEM BREAKDOWN: PAGE 3 - SUPPORT, DEWATERING, WEATHER RISK & MLOPS CONFIG
## SYSTEM MONITORING FUEL RATIO (FR) BASIS OPERASIONAL & CAPACITY MANAGEMENT TAMBANG
**Route File:** `/support-weather-mlops`  
**Target User:** Support Superintendent, Dewatering Supervisor, Environmental Officer, MLOps Engineer  
**Tujuan Utama:** Memantau kuota jam kerja (EWH) dan persentase beban konsumsi solar non-produksi (Support & Dewatering yang bernilai Zero-BCM), mengintegrasikan risiko cuaca (Open-Meteo API), mengonfigurasi threshold alert dinamis (+8% Warning / +18% Critical), serta mengontrol retraining MLOps AI Model.

---

## 1. LAYOUT STRUCTURE & WIREFRAME ASCII

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: Non-Production Fleet, Weather Risk & MLOps Config | Location: Bontang (-0.13, 117.45)   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 1: OPEN-METEO WEATHER RISK INTEGRATION CARD (LIVE WEATHER & RAIN DERATING RADAR)            │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: OpenMeteoWeatherCard                                                              │ │
│ │ Curah Hujan: 0.00 mm/hr | Suhu: 31.5°C | Angin: 12.0 km/h | Haul Distance Impact: +0.00m      │ │
│ │ Rain Impact Status: DRY (No Fleet Derating / Haul Distance Standard 3,900m)                  │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 2: ZERO-BCM FUEL BURDEN ANALYSIS & EWH BUDGET COMPARISON                                    │
│ ┌──────────────────────────────────────────────┐ ┌────────────────────────────────────────────┐ │
│ │ COMPONENT: SupportEwhBudgetCard              │ │ COMPONENT: DewateringEwhBudgetCard         │ │
│ │ Total Populasi: 183 Units (100% Active)      │ │ Total Populasi: 175 Units (100% Active)    │ │
│ │ Annual Budget EWH: 1,337,300.0 Hours/year     │ │ Annual Budget EWH: 1,277,500.0 Hours/year   │ │
│ │ Fuel Allocation: 200,582.4 Liters/day        │ │ Fuel Allocation: 113,085.8 Liters/day      │ │
│ └──────────────────────────────────────────────┘ └────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 3: VISUALISASI DONUT CHART BEBAN SOLAR NON-PRODUKSI (ZERO-BCM FUEL BURDEN CHART)            │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: NonProductionFuelBurdenDonutChart                                                 │ │
│ │ Total Non-Production Fuel Burden: 313,668.2 Liters/day (+0.2999 L/BCM / 25.9% dari Total FR) │ │
│ │ [Supporting Burden: +0.2199 L/BCM (19.0%)] | [Dewatering Burden: +0.0800 L/BCM (6.91%)]       │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 4: TABEL EWH & KONSUMSI SOLAR SUPPORT & DEWATERING FLEET (EWH BUDGET TABLE)                 │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: SupportDewateringEwhTable                                                         │ │
│ │ [Table: Sector | Equipment Model | Active Qty | FC Rate (L/hr) | Daily EWH | Annual EWH   │ │
│ │        | Annual Fuel Budget (L) | Daily Fuel Allocation (L) | FR Burden L/BCM | Burden %]    │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 5: DYNAMIC ALERT THRESHOLD & MLOPS RETRAINING CONTROL PANEL                                 │
│ ┌──────────────────────────────────────────────┐ ┌────────────────────────────────────────────┐ │
│ │ COMPONENT: DynamicThresholdConfigCard        │ │ COMPONENT: MLOpsModelRetrainControlCard    │ │
│ │ Baseline FR Total: 1.1576 L/BCM              │ │ XGBoost Forecast: Trained (R²=0.9901)      │ │
│ │ Warning Threshold (+8%): 1.2503 L/BCM        │ │ PyTorch Autoencoder: Trained (P93.5 Threshold)│
│ │ Critical Threshold (+18%): 1.3660 L/BCM      │ │ [Button: Trigger Model Retraining Pipeline]│ │
│ └──────────────────────────────────────────────┘ └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. BREAKDOWN KOMPONEN UI & SPESIFIKASI DESIGN SYSTEM

### Komponen 3.1: `OpenMeteoWeatherCard` (Integrasi Cuaca Real-Time)
- **Tipe Komponen:** Weather Risk API Integration Widget
- **Peran:** Menghubungkan API Open-Meteo untuk lokasi pit tambang (Bontang / East Kalimantan: Lat -0.13, Lon 117.45).
- **Aturan Dampak Hujan Terhadap Jarak Angkut & Produktivitas:**
  $$	ext{Haul Distance (m)} = 3.900	ext{m} + (	ext{Rainfall mm} 	imes 8	ext{m})$$
  $$	ext{Rain Derating Factor} = \min(0.50, 	ext{Rainfall mm} 	imes 0.015)$$

### Komponen 3.2: `SupportEwhBudgetCard` & `DewateringEwhBudgetCard`
- **Tipe Komponen:** Non-Production Fleet Budget Analytics Card
- **Peran:** Menampilkan perbandingan estimasi jam kerja (EWH) dan alokasi solar harian untuk alat pendukung dan pengurasan tambang.
- **Rincian Metric:**
  - **Supporting Fleet:** 183 Unit | **1.337.300 EWH/tahun** | **200.582,4 L/hari** (+0,2199 L/BCM / 19.00% FR).
  - **Dewatering Fleet:** 175 Unit | **1.277.500 EWH/tahun** | **113.085,8 L/hari** (+0,0800 L/BCM / 6.91% FR).

### Komponen 3.3: `NonProductionFuelBurdenDonutChart`
- **Tipe Komponen:** Interactive Donut Chart Visualizer
- **Peran:** Memvisualisasikan seberapa besar beban solar non-produksi yang mengonsumsi BBM tanpa menghasilkan BCM langsung.
- **Total Non-Production Burden:** **313.668,2 Liter/hari** (+0,2999 L/BCM / **25.91%** dari Total FR 1,1576 L/BCM).

### Komponen 3.4: `SupportDewateringEwhTable`
- **Tipe Komponen:** Detailed EWH & Fuel Budget Data Table

| Nama Kolom | Field Key | Tipe Data | Contoh Data | Visual Style |
|:---|:---|:---|:---|:---|
| **Sector** | `sector` | Enum | `SUPPORTING` / `DEWATERING` | Blue/Purple Pill Tag |
| **Equipment Model** | `equipment_model` | String | `Dozer D375A6R`, `Pompa EWP420` | Bold Monospace |
| **Active Qty** | `active_qty` | Integer | `20 Unit`, `40 Unit` | Centered Integer Badge |
| **FC Rate (L/hr)** | `fc_rate_l_hr` | Float | `67.0 L/hr`, `40.0 L/hr` | Right-aligned Float |
| **Daily EWH** | `daily_ewh_hrs` | Float | `20.0 Hours/day` | Muted Gray Text |
| **Annual Budget EWH** | `annual_budgeted_ewh`| Float | `146,000 Hours/year` | Bold Integer |
| **Annual Fuel Budget**| `annual_fuel_budget_liters`| Float | `9,782,000 Liters` | Highlighted Liter Text |
| **Daily Fuel Allocation**| `daily_fuel_allocation_liters`| Float| **27,336.0 L/day** | Bold Liter Text |
| **FR Burden (L/BCM)** | `fr_burden_l_bcm` | Float | **+0.0380 L/BCM** | Warning Yellow Text |
| **Burden (%)** | `fr_burden_pct` | Float | **3.28%** | Percentage Badge |

### Komponen 3.5: `DynamicThresholdConfigCard` & `MLOpsModelRetrainControlCard`
- **Tipe Komponen:** MLOps System Configuration Panel
- **Peran:** Mengelola threshold alert Warning (+8% / 1.2503 L/BCM) & Critical (+18% / 1.3660 L/BCM) serta mengontrol eksekusi retraining model XGBoost & PyTorch Autoencoder.

---

## 3. INTEGRASI SUPABASE API & ENDPOINT QUEUES

```javascript
import { supabase } from '@/lib/supabaseClient';

// 1. Fetch Non-Production Support & Dewatering Burden Summary
export async function getNonProductionFuelBurden() {
  const { data, error } = await supabase
    .from('vw_non_production_fuel_burden')
    .select('*')
    .order('daily_fuel_allocation_liters', { ascending: false });
  if (error) throw error;
  return data;
}

// 2. Fetch System MLOps Config
export async function getSystemMlOpsConfig() {
  const { data, error } = await supabase
    .from('cfg_system_mlops')
    .select('*');
  if (error) throw error;
  return data;
}

// 3. Update Dynamic Threshold Config in Supabase
export async function updateThresholdConfig(configKey, newValue) {
  const { data, error } = await supabase
    .from('cfg_system_mlops')
    .update({ config_value: String(newValue) })
    .eq('config_key', configKey);
  if (error) throw error;
  return data;
}
```
