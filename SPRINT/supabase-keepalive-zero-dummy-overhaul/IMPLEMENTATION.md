# Implementasi: Supabase Keep-Alive & Zero-Dummy UI Overhaul

> Dokumen ini dicatat **per commit**, diperbarui setiap fase implementasi selesai.
> Rencana lengkap: lihat riwayat percakapan / plan file sesi ini.
> Branch: `ui/red-blue-design-system-integration`

## Ringkasan Objektif

1. **Objektif 1** — GitHub Actions workflow untuk mencegah Supabase project free-tier auto-pause.
2. **Objektif 2** — Overhaul UI/UX ke "Industrial Console" design hallmark + eliminasi total data dummy/hardcoded di seluruh widget frontend, menggantinya dengan data riil dari Laravel → python-ai-service → Supabase/SQLite.

---

## Status Fase

| Fase | Status | Commit |
|---|---|---|
| Perbaikan file rusak (uncommitted WIP) | ✅ Selesai | `7cbe285` |
| Fix root-cause fallback-masquerading-as-live | ✅ Selesai | `7cbe285` |
| Objektif 1: Supabase keep-alive workflow | ✅ Selesai | `c792495` |
| Palette industrial + radius scale + tabular nums + dark mode | ✅ Selesai | `8994e16` |
| Hapus demo page & fake identity (account-settings) | ✅ Selesai | `90092ae` |
| Rewiring 5 widget dummy ke endpoint riil (D1) | ✅ Selesai | `94e052f` |
| Endpoint model-metrics riil + fix GlobalCapacityTuningCard | ✅ Selesai | `15a21c1` |
| EWH Budget endpoint & widget (D2) | ⏳ Berjalan | — |
| Threshold Config table/endpoint + Retrain endpoint (D3) | ⏳ Direncanakan | — |
| AI Co-pilot copywriting + XGBoost feature contributions (G) | ⏳ Direncanakan | — |

---

## 1. Perbaikan File Rusak & Root-Cause Fallback Bug (`7cbe285`)

**Masalah ditemukan:** Dua file di working tree rusak akibat edit yang belum di-commit:
- `OpenMeteoWeatherCard.vue` — tag `<VCardItem>`/`<VCardText>` tidak seimbang (template tidak bisa compile).
- `DynamicThresholdAlertWidget.vue` — memanggil method `fetchData` yang tidak pernah ada.

**Root-cause bug:** `useAiApi.ts`'s `apiRequest()` tidak pernah mengecek `response.ok`. Semua controller Laravel (`ForecastController`, `CapacityController`, dll.) mengembalikan `{ fallback: true, ... }` dengan HTTP 503 saat AI service down — tapi karena tidak dicek, response fallback ini diperlakukan sama seperti data live oleh hampir semua widget.

**Perbaikan:**
- `apiRequest()` kini melempar `AiApiError` (class baru, exported) pada status non-2xx, membawa body response asli (termasuk payload fallback Laravel) untuk konsumen yang butuh membedakan.
- Fixed type drift: `ForecastResponse` punya field `features_used`/`budget_baseline` yang **tidak pernah ada** di response API asli — field asli adalah `features_input`, `daily_prod_bcm`, `haul_distance_m`.
- 4-state (loading/error+retry/empty/live) diterapkan ke: `OpenMeteoWeatherCard`, `DynamicThresholdAlertWidget`, `TopAnomalousLeaderboard`, `ScenarioSimulatorControls`, `TimeSeriesForecastChart`, `dashboard.vue`.
- Hardcoded hex colors diganti dengan theme tokens di beberapa file (`ActivityFuelDonutChart`, `PyTorchSpikeSummaryWidget`, dll).

**File diubah:** 9 file (lihat commit `7cbe285`).

---

## 2. Objektif 1 — Supabase Keep-Alive Workflow (`c792495`)

**File baru:** `.github/workflows/supabase-keepalive.yml`

- Trigger: `cron: '0 3 */3 * *'` (setiap 3 hari) + `workflow_dispatch` manual.
- Satu step `curl` memanggil `GET {SUPABASE_URL}/rest/v1/weather_daily_logs?select=id&limit=1` dengan header `apikey`/`Authorization` dari secrets `SUPABASE_URL`/`SUPABASE_KEY`.
- `weather_daily_logs` dipilih karena tabel operasional riil terkecil (365 baris, 5 kolom).
- Gagal (non-2xx atau secret kosong) → job fail, terlihat jelas di tab Actions.

**Temuan terkait (belum diperbaiki, di luar scope):** `python-ai-service/config.py` meng-hardcode default URL+key Supabase sebagai default Pydantic, dan `.env` memakai nama variabel (`NEXT_PUBLIC_SUPABASE_*`) yang berbeda dari yang dibaca `config.py` (`SUPABASE_URL`/`SUPABASE_KEY`) — sehingga service selalu fallback ke default hardcoded tsb tanpa disadari.

**Setup yang dibutuhkan dari user:** Tambahkan repository secrets `SUPABASE_URL` dan `SUPABASE_KEY` (gunakan service-role key agar tidak terblokir RLS) di GitHub repo settings.

---

## 3. Industrial Console Palette & Design Tokens (`8994e16`)

- **Palette:** `primary` berubah dari merah (`#E53935`, nyaris sama dengan `error` `#D32F2F`) menjadi **Precision Mining Blue** (`#1565C0`). `secondary` menjadi **Deep Slate** (`#334155`). `error`/`warning` tetap satu-satunya token merah/amber, direservasi untuk status warning/critical.
- **Dark mode dipulihkan:** `NavbarThemeSwitcher.vue` kehilangan entry `dark` akibat edit uncommitted sebelumnya — dikembalikan.
- **Radius scale direkonsiliasi:** `--radius-sm/md/lg` (CSS custom property, 4/8/12px) vs skala lama Vuetify SCSS (`sm:4/lg:8`, root:6px) digabung jadi satu skala (literal Sass angka tetap dipakai karena Vuetify melakukan math compile-time pada nilai ini — `var()` tidak bisa dipakai di situ — disinkronkan manual via komentar).
- **Tabular numerals:** class `.text-tabular-nums` baru (`font-feature-settings: "tnum"`), diterapkan ke angka KPI utama di dashboard (FR value, spike count, stat cuaca, dll).

---

## 4. Hapus Demo Page & Fake Identity (`90092ae`)

- **Dihapus:** 5 halaman demo Sneat template yang tidak pernah di-routing (`cards`, `tables`, `form-layouts`, `icons`, `typography`) beserta views pendukungnya (14 file total).
- **Dihapus:** `account-settings` (page + route + nav item + 3 view component) — satu-satunya isinya adalah data fake ("John Doe", password `12345678` prefilled, API key & device palsu). Tidak ada backend auth untuk membuat ini riil.
- **UserProfile.vue:** foto profil stok + nama "John Doe"/"Admin" diganti label netral "Operator" + icon avatar. Menu "Profile/Settings/Pricing/FAQ" yang tidak mengarah kemana pun (tidak ada `to`) dihapus. "Logout" tetap ada (mengarah ke `/login`).

---

## 5. Rewiring 5 Widget Dummy ke Data Riil (`94e052f`)

Semua lima komponen berikut sebelumnya 100% hardcoded dan **tidak pernah di-import** di manapun. Direwire ke endpoint yang **sudah ada** (tanpa perlu backend baru):

| Komponen | Sumber data riil | Dipasang di |
|---|---|---|
| `FrTrendLineChart.vue` | **Dihapus** — duplikat fungsi `TimeSeriesForecastChart` (yang sudah riil) | `TimeSeriesForecastChart` dipasang di `dashboard.vue` |
| `ActualVsForecastTable.vue` | Self-fetch `GET /forecast-history` (liter solar dihitung FR × BCM, formula yang sama dipakai di seluruh app) | `forecasting-ai.vue` |
| `CriticalEquipmentAlertBanner.vue` | `unit_tuning_comparison` difilter `OVER_CONSUMPTION` | `global-capacity.vue` |
| `NonProductionFuelBurdenDonut.vue` | `activity_breakdown` (Support+Dewatering vs Loading+Hauling) | `production-capacity.vue` |
| `SPOComplianceTable.vue` | `unit_tuning_comparison` (`EFFICIENT`→Compliant, `WARNING`→Partial, `OVER_CONSUMPTION`→Non-Compliant) | `global-capacity.vue` |

**Catatan penting (SPO Compliance):** Tidak ada ground-truth "SPO compliance" di skema database. Komponen ini di-derive dari variansi fuel-tuning yang sudah dihitung AI engine, bukan metrik baru yang diciptakan. Jika "SPO" dimaksud sebagai sesuatu yang berbeda secara operasional, perlu klarifikasi dan kemungkinan tabel baru.

**Bonus fix:** `FleetCapacityOptimizerGrid.vue` — subtitle "Target Produksi: 250.072 BCM/hari" yang hardcoded kini dihitung dari `activity_breakdown` riil.

---

## 6. Model Metrics Endpoint Riil & Fix GlobalCapacityTuningCard (`15a21c1`)

**Endpoint baru:** `GET /api/v1/model-metrics` di `python-ai-service` (`api/routes_forecast.py`), membaca `models/metadata.json` & `models/autoencoder_metadata.json` yang sudah ditulis oleh training pipeline (R², MAE, precision, recall) — tidak ada komputasi baru, hanya expose file yang sudah ada.

**Laravel passthrough:** `FuelRatioAiClient::getModelMetrics()` → `ForecastController::modelMetrics()` → route `GET /api/v1/model-metrics`.

**Frontend:**
- `ModelMetricsCard.vue` — hardcoded fallback metrics (R² `0.9901`, MAE `0.0045`, versi `v3.3/v2.11`) yang **selalu muncul saat AI service offline** diganti dengan data riil dari endpoint baru. Error state sekarang jelas berbeda dari "belum ada model".
- `GlobalCapacityTuningCard.vue` — **tidak punya error state sama sekali**: saat fetch gagal, kartu ini merender angka fabrikasi (`418557.6` BCM/day, `33/324` unit, dst.) selamanya seolah-olah data live. Ditambahkan `isError` + tombol retry. Chip status tuning diperbaiki (`OVER_CONSUMPTION` kini merah/error, sebelumnya disamakan dengan `WARNING`). Hex hardcoded terakhir diganti theme token.

---

## Verifikasi yang Dijalankan Setiap Commit

- `cd laravel && npx vue-tsc --noEmit` — typecheck bersih (kecuali error pre-existing yang tidak terkait: `CardStatisticsHorizontal`, `VerticalNavGroup/Link`, `build-icons.ts`, `fleetType` di `production-capacity.vue`).
- `cd laravel && npx vite build` — build production berhasil di setiap commit.
- `cd python-ai-service && python -m pytest tests/ -q` — 24 passed, 1 pre-existing failure (`test_database_connection_and_seeding`, soal jumlah seed data Excel — tidak terkait perubahan di dokumen ini, dikonfirmasi gagal juga sebelum perubahan apapun).
- Model artifacts (`.pkl`/`.pth`/`metadata.json`) yang ter-regenerate akibat menjalankan test suite di-revert (`git checkout`) agar tidak ikut ter-commit sebagai side-effect yang tidak disengaja.
