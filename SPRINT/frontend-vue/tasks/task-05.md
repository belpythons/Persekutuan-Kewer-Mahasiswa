# TASK-FE-05: Production Capacity & Fleet Allocation Monitoring Page

## 📌 Sprint Target
**Sprint 9 - 10**

---

## 📝 Description & Context
Pengembangan modul **Aktivitas Produksi & Kapasitas Fleet** (`laravel/resources/ts/pages/production-capacity.vue`) untuk memantau performa alat berat (Excavator / Loading units dan Hauler / Dump Truck), kepatuhan Standard Operating Procedure (SPO), optimasi alokasi BBM berbasis formula derating hujan non-linear, serta matriks kapasitas unit jam-jaman (*hourly fleet capacity matrix*).

---

## ✅ Acceptance Criteria (AC)
- [ ] Header kontrol menyediakan pemilih Shift (`Shift 1 (Day)`, `Shift 2 (Night)`) dan tombol "Sync FMS" untuk sinkronisasi data Fleet Management System secara real-time.
- [ ] Ringkasan armada Loading (`LoadingFleetSummaryCard.vue`) dan Hauling (`HaulingFleetSummaryCard.vue`) menyajikan statistik unit beroperasi, efisiensi BCM/jam, dan konsumsi solar L/jam.
- [ ] Banner peringatan `CriticalEquipmentAlertBanner.vue` menyorot alat berat yang mengalami penurunan efisiensi terdeteksi anomali.
- [ ] Grid optimasi `FleetCapacityOptimizerGrid.vue` menampilkan hasil perhitungan `fetchCalculateCapacity` mencakup faktor *rain derating*, utilisasi %, dan efektivitas BCM/day.
- [ ] Tabel `SPOComplianceTable.vue` dan `HourlyFleetCapacityMatrix.vue` menampilkan rincian alokasi per unit, breakdown aktivitas, serta status spike NN Autoencoder.

---

## 🛠️ Technical Implementation Details

### File & Path Target
- **Page Container**: `laravel/resources/ts/pages/production-capacity.vue`
- **Production Views**:
  - `laravel/resources/ts/views/production/LoadingFleetSummaryCard.vue`
  - `laravel/resources/ts/views/production/HaulingFleetSummaryCard.vue`
  - `laravel/resources/ts/views/production/CriticalEquipmentAlertBanner.vue`
  - `laravel/resources/ts/views/production/FleetCapacityOptimizerGrid.vue`
  - `laravel/resources/ts/views/production/SPOComplianceTable.vue`
  - `laravel/resources/ts/views/production/HourlyFleetCapacityMatrix.vue`

### Composable / API Client Used
- `useAiApi.ts` -> `fetchCalculateCapacity(payload: CapacityPayload)`

### State Management & Data Flow
- `selectedShift`: `ref<string>('Shift 1 (Day)')`
- `capacityData`: `ref<CapacityResponse | null>(null)`
- `syncData()`: Memanggil `fetchCalculateCapacity` dengan payload tanggal hari ini, estimasi BCM, dan curah hujan harian.

---

## 🎯 Definition of Done (DoD)
- [ ] Pembaruan Shift atau trigger "Sync FMS" sukses memuat ulang data kapasitas.
- [ ] Matriks alokasi armada menampilkan perhitungannya secara akurat tanpa pembulatan error pada persentase utilisasi.
- [ ] Komponen vue kompatibel dengan tema Vuetify 3.
- [ ] Lolos verifikasi TypeScript.
