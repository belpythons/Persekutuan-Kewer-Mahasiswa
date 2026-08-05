# TASK-FE-07: Reports DataTables, Export Interfaces & Responsive UX Audit

## 📌 Sprint Target
**Sprint 10 & Sprint 13 - 15**

---

## 📝 Description & Context
Pengembangan modul **Laporan & Ekspor Data** (`Pages/Reports/...`) serta pelaksanaan **UX & Responsive Audit** untuk memastikan tampilan aplikasi Vue 3 berjalan lancar di berbagai perangkat (desktop monitor, laptop, tablet, hingga *ruggedized smartphone* di lapangan). Modul ini menyediakan laporan spike anomali per unit, laporan aktivitas, serta fasilitas cetak/ekspor dokumen PDF dan Excel via backend endpoint.

---

## ✅ Acceptance Criteria (AC)
- [ ] Tersedia halaman laporan per unit (`SpikeReport.vue`), laporan per aktivitas (`ActivityReport.vue`), dan laporan utilisasi armada (`CapacityReport.vue`).
- [ ] Tombol "Export PDF" dan "Export Excel" pada setiap tabel laporan mengirimkan request ke backend Laravel API endpoint (`/api/v1/reports/export-pdf`, `/api/v1/reports/export-excel`).
- [ ] Implementasi DataTables responsif mendukung pencarian (*searching*), penyaringan (*filtering* berdasarkan rentang tanggal / pit / unit), serta pengurutan kolom (*sorting*).
- [ ] Seluruh komponen dashboard, forecasting, dan capacity di-audit dan disesuaikan breakpoint Tailwind / Vuetify (`sm`, `md`, `lg`, `xl`) untuk kerapian tampilan mobile.

---

## 🛠️ Technical Implementation Details

### File & Path Target
- `laravel/resources/ts/pages/tables.vue`
- `laravel/resources/ts/pages/FuelRatioAnalytics.vue`
- `laravel/resources/ts/views/dashboard/ActualVsForecastTable.vue`
- Layout & Breakpoint Styles: `laravel/resources/ts/@layouts/` & Vuetify Grid

### Composable / API Client Used
- Axios / Fetch Client untuk trigger file download (Blob response).

---

## 🎯 Definition of Done (DoD)
- [ ] File PDF dan Excel yang diunduh berformat valid dan dapat dibuka tanpa corrupt.
- [ ] Tampilan antarmuka pada viewport $360\text{px}$ (mobile) hingga $1920\text{px}$ (desktop) tidak memiliki *horizontal scrollbar* tak terduga.
- [ ] Bebas dari error TypeScript dan warning console Vue.
