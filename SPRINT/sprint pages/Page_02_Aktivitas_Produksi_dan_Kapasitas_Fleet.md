# DESIGN SYSTEM BREAKDOWN: PAGE 2 - AKTIVITAS PRODUKSI & KAPASITAS FLEET
## SYSTEM MONITORING FUEL RATIO (FR) BASIS OPERASIONAL & CAPACITY MANAGEMENT TAMBANG
**Route File:** `/production-capacity`  
**Target User:** Mine Dispatcher, Fleet Superintendent, Production Planner, Maintenance Manager  
**Tujuan Utama:** Memantau aktivitas fleet produksi (Loading & Hauling) secara live, mendeteksi unit kritis beroperasi di bawah SPO, mengoptimalkan penentuan kapasitas armada aktif berbasis AI (Combined XGBoost + PyTorch), dan mengaudit kapasitas matriks per jam per unit equipment.

---

## 1. LAYOUT STRUCTURE & WIREFRAME ASCII

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: Live Production & Capacity Optimizer | Shift Selector (Shift 1 / Shift 2) | Fleet Filter  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 1: REKAPITULASI FLEET PRODUKSI (LOADING & HAULING SUMMARY CARDS)                            │
│ ┌──────────────────────────────────────────────┐ ┌────────────────────────────────────────────┐ │
│ │ COMPONENT: LoadingFleetSummaryCard           │ │ COMPONENT: HaulingFleetSummaryCard         │ │
│ │ Total: 70 Units | Active: 22 (27.12% Util)   │ │ Total: 415 Units | Active: 94 (22.46% Util)│ │
│ │ Fleet BCM/hr: 37,660 | Fleet Fuel: 5,836 L/hr│ │ Fleet BCM/hr: 45,469.57| Fuel: 31,955 L/hr│ │
│ └──────────────────────────────────────────────┘ └────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 2: CRITICAL EQUIPMENT DETECTOR & SPO COMPLIANCE RADAR                                       │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: CriticalEquipmentAlertBanner                                                      │ │
│ │ ⚠️ 14 Unit Beroperasi di Bawah SPO (Deviasi Konsumsi BBM > +15% / Produktivitas < -20%)      │ │
│ │ Total Potensi Pemborosan Solar Fleet Produksi: +14,820 Liter / Hari                           │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 3: COMBINED FLEET CAPACITY & FUEL ALLOCATION OPTIMIZER (AI ALLOCATION ENGINE)                │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: FleetCapacityOptimizerGrid                                                        │ │
│ │ Target Prod: 250,072 BCM/day | Derating Hujan: 0 mm/hr | Calculated Fuel: 1,016,902.8 L/day    │ │
│ │ [Card: Loading Fleet Sizing] [Card: Hauling Fleet Sizing] [Card: Combined Fuel Quota]        │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 4: TABEL AUDIT SPO COMPLIANCE & KONSUMSI LITER HARIAN (COMPLIANCE TABLE)                   │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: SPOComplianceTable                                                                │ │
│ │ Controls: Fleet Filter (All / Loading / Hauling) | Search Unit Code | Severity Filter        │ │
│ │ [Table: Activity | Model | Unit Code | Target SPO BCM/hr | Actual BCM/hr | Target SPO FC   │ │
│ │        | Actual FC | Deviasi % | Total Solar (L/Day) | Spike Count | Dispatch Action]        │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 5: HOURLY FLEET CAPACITY MATRIX TABLE (MATRIKS KAPASITAS OPERASIONAL PER JAM - SHEET V1)     │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: HourlyFleetCapacityMatrixTable                                                    │ │
│ │ Summary Header: Total Fleet Output: 83,129.57 BCM/hr | Total Fuel Rate: 53,196.0 L/hr        │ │
│ │ [Table: Activity | Model | Unit Code | Qty | FC Rate (L/hr) | BCM/hr Rate | Total BCM/hr   │ │
│ │        | Total Fuel L/hr | Fleet Contribution %]                                             │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. BREAKDOWN KOMPONEN UI & SPESIFIKASI DESIGN SYSTEM

### Komponen 2.1: `LoadingFleetSummaryCard`
- **Tipe Komponen:** Fleet Analytics Card
- **Peran:** Menampilkan rekapitulasi status operasional 70 unit Loading Fleet.
- **Visual & Metric Items:**
  - Total Populasi Loading: **70 Unit** (EX2600-6: 3, PC1250: 30, PC2000: 34, PC3400: 3).
  - Required Units Active: **22 Unit** (Utilisasi Kapasitas **27.12%**).
  - Installed Capacity BCM/hr: **37.660,0 BCM/jam**.
  - Hourly Fuel Consumption: **5.836,0 Liter/jam**.
  - Daily Fuel Allocation: **50.952,2 Liter/hari**.

### Komponen 2.2: `HaulingFleetSummaryCard`
- **Tipe Komponen:** Fleet Analytics Card
- **Peran:** Menampilkan rekapitulasi status operasional 415 unit Hauling Fleet.
- **Visual & Metric Items:**
  - Total Populasi Hauling: **415 Unit** (HD785-7: 400, HD785-8: 15).
  - Required Units Active: **94 Unit** (Utilisasi Kapasitas **22.46%**).
  - Installed Capacity BCM/hr: **45.469,57 BCM/jam**.
  - Hourly Fuel Consumption: **31.955,0 Liter/jam**.
  - Daily Fuel Allocation: **652.282,4 Liter/hari**.

### Komponen 2.3: `CriticalEquipmentAlertBanner`
- **Tipe Komponen:** Actionable Alert Banner
- **Peran:** Memberikan sinyal bahaya jika terdapat unit produktif yang bekerja jauh di bawah standar efisiensi SPO.
- **Aturan Pemicu Alert (Trigger Rules):**
  - FC Actual melebihi SPO Base FC > **+15%**.
  - Produktivitas BCM/hr turun di bawah SPO Target > **-20%**.
  - Memiliki PyTorch Anomaly Spike Events > **5 events/hari**.
- **Visual Style:** Border Kiri Solid Red 6px (`#C5221F`), Background Light Coral (`#FCE8E6`).

### Komponen 2.4: `FleetCapacityOptimizerGrid` (Kombinasi XGBoost + PyTorch AI Engine)
- **Tipe Komponen:** Interactive Capacity & Allocation Controller
- **Peran:** Menghitung sizing jumlah alat berat aktif yang wajib beroperasi per shift serta jatah kuota solar harian.
- **Formula Penentuan Kapasitas:**
  $$	ext{Required Units} = \left\lceil rac{	ext{Target BCM/Day}}{	ext{Capacity BCM/hr} 	imes 	ext{Working Hours} 	imes (1 - 	ext{Rain Derating})} ightceil$$
  $$	ext{Daily Fuel Allocation (L/day)} = 	ext{Required Units} 	imes 	ext{FC Rate (L/hr)} 	imes 	ext{Working Hours}$$
- **Keluaran Alokasi Armada (Combined Optimization Result):**
  - Loading Fleet Required: **22 Unit** (dari 70 populasi) -> **50.952,2 L/hari**.
  - Hauling Fleet Required: **94 Unit** (dari 415 populasi) -> **652.282,4 L/hari**.
  - Supporting Fleet Required: **183 Unit** (100% aktif) -> **200.582,4 L/hari**.
  - Dewatering Fleet Required: **175 Unit** (100% aktif) -> **113.085,8 L/hari**.
  - **Total Alokasi Solar Tambang:** **1.016.902,8 Liter/hari**.

### Komponen 2.5: `SPOComplianceTable` (Tabel Detail Kepatuhan Unit)
- **Tipe Komponen:** Advanced Data Grid dengan Cell Status Formatting
- **Peran:** Menyajikan rincian setiap unit produktif di bawah SPO lengkap dengan jumlah konsumsi solar harian dalam Liter/hari.

| Nama Kolom | Field Key | Tipe Data | Contoh Data | Visual Formatting Rule |
|:---|:---|:---|:---|:---|
| **Activity** | `activity` | String | `LOADING` / `HAULING` | Pill Tag Tag Blue/Teal |
| **Model** | `unit_model` | String | `EX2600-6` / `HD785-7` | Bold Text |
| **Unit Code** | `unit_code` | String | `EX-2601`, `DT-785-042` | Monospace Code Font |
| **Target SPO BCM/hr**| `spo_target_bcm_hr` | Float | `920.0 BCM/hr` | Muted Gray Text |
| **Actual BCM/hr** | `actual_bcm_hr` | Float | `650.0 BCM/hr` | Red Text jika < 80% SPO |
| **Target SPO FC** | `spo_target_fc_lhr` | Float | `187.0 L/hr` | Muted Gray Text |
| **Actual FC L/hr** | `actual_fc_lhr` | Float | `192.28 L/hr` | Bold Red Text jika > SPO |
| **Deviasi FC (%)** | `deviasi_fc_pct` | Float | **+85.5%** | Red Pill Badge jika > +15% |
| **Total Solar (L/Day)**| `total_fuel_l_day` | Float | **17,428.4 L** | Highlighted Bold Liter Text |
| **Spike Events** | `nn_spike_events` | Integer | **366 Spikes** | Glowing Pulse Badge Merah |
| **Dispatch Action** | `dispatch_action` | String | `Audit Hydro Pump` | Button Action *"Issue WO"* |

### Komponen 2.6: `HourlyFleetCapacityMatrixTable` (Parsing Summary v1 Excel Master)
- **Tipe Komponen:** High-Density Operational Master Matrix Table
- **Peran:** Menampilkan matriks kapasitas per jam per unit model seluruh 843 unit armada tambang.

| Nama Kolom | Field Key | Tipe Data | Format Visual / Contoh Data |
|:---|:---|:---|:---|
| **Activity** | `activity` | Enum | Badge Tag (`LOADING`, `HAULING`, `SUPPORTING`, `DEWATERING`) |
| **Unit Model** | `unit_model` | String | Bold Monospace (e.g. `EX2600-6`, `HD785-7`, `D375A6R`) |
| **Unit Code** | `unit_code` | String | Monospace Code (e.g. `EX-2600-6`, `DT-HD785-7`) |
| **Qty Units** | `qty_units` | Integer | Right-aligned Integer Badge (e.g. `400`, `36`, `40`) |
| **FC Rate (L/hr)** | `fuel_cons_l_per_hour` | Float | Single Unit Fuel Consumption Rate (e.g. `77.0 L/hr`) |
| **BCM/hr Rate** | `prod_capacity_bcm_per_hour` | Float | Single Unit Production Rate (e.g. `920.0 BCM/hr`) |
| **Total Fleet BCM/hr**| `fleet_total_prod_bcm_per_hour` | Float | Total Capacity Rate (`qty_units * prod_capacity`) |
| **Total Fleet Fuel L/hr**| `fleet_total_fuel_l_per_hour` | Float | Total Fuel Rate (`qty_units * fuel_cons`) |

---

## 3. INTEGRASI SUPABASE API & ENDPOINT QUEUES

```javascript
import { supabase } from '@/lib/supabaseClient';

// 1. Fetch Summary Rekapitulasi Fleet Produksi
export async function getProductionFleetSummary() {
  const { data, error } = await supabase
    .from('vw_hourly_activity_summary')
    .select('*');
  if (error) throw error;
  return data;
}

// 2. Fetch SPO Compliance Audit Report
export async function getSpoComplianceReport(activityFilter) {
  let query = supabase
    .from('vw_spo_compliance_report')
    .select('*')
    .order('deviasi_fc_pct', { ascending: false });

  if (activityFilter && activityFilter !== 'ALL') {
    query = query.eq('activity', activityFilter);
  }
  const { data, error } = await query;
  if (error) throw error;
  return data;
}

// 3. Fetch Combined Capacity Optimizer Allocation
export async function getCombinedCapacityReport() {
  const { data, error } = await supabase
    .from('vw_combined_capacity_report')
    .select('*')
    .order('capacity_fuel_l_day', { ascending: false });
  if (error) throw error;
  return data;
}

// 4. Fetch Hourly Fleet Capacity Matrix
export async function getHourlyFleetCapacityMatrix(activityFilter) {
  let query = supabase
    .from('vw_hourly_fleet_capacity_matrix')
    .select('*')
    .order('fleet_total_fuel_l_per_hour', { ascending: false });

  if (activityFilter && activityFilter !== 'ALL') {
    query = query.eq('activity', activityFilter);
  }
  const { data, error } = await query;
  if (error) throw error;
  return data;
}
```
