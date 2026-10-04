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
| Fix fabricated weather data di `sync-bmkg` (ditemukan saat D2) | ✅ Selesai | `fabae03` |
| EWH Budget endpoint & widget (D2) | ✅ Selesai | `9b690b6` |
| Threshold Config table/endpoint + Retrain endpoint (D3, backend) | ✅ Selesai | `085bfe2` |
| Laravel passthrough EWH/threshold-config/retrain | ✅ Selesai | `729869a` |
| Frontend wiring D2+D3 + halaman baru `/support-weather-mlops` | ✅ Selesai | `adc1048` |
| AI Co-pilot copywriting + XGBoost feature contributions (G) | ✅ Selesai | `9ac741e` |

**Seluruh fase dari rencana yang disetujui (Objektif 1 + Objektif 2 Fase A–G) telah selesai diimplementasikan dan diverifikasi.**

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

## 7. Temuan Tak Terduga: `sync-bmkg` Memfabrikasi Data Cuaca (`fabae03`)

Saat mengerjakan D2, ditemukan `POST /api/v1/weather/sync-bmkg` (dipanggil `OpenMeteoWeatherCard.vue` sebagai background sync) ternyata **mengisi `weather_daily_logs` dengan `random.uniform()`** untuk hampir semua field, diberi label `"OPEN_METEO_PASER_LIVE"` seolah data riil dari API eksternal. Karena `weather_daily_logs` dibaca langsung oleh `forecasting_service` untuk prediksi FR hari-hari mendatang, ini berarti **forecast bisa dihitung dari curah hujan/suhu/angin fiktif** tanpa disadari siapapun.

**Perbaikan:** Endpoint kini memanggil Open-Meteo daily-forecast API sungguhan (koordinat Paser yang sama dipakai frontend), meng-upsert persis nilai yang dikembalikan API — tanpa randomness sama sekali. Kegagalan upstream → HTTP 502 (bukan commit data fiktif secara diam-diam). Ditambahkan `tests/test_weather_sync.py` yang mem-mock `requests.get` untuk membuktikan baris yang tersimpan identik dengan response API.

---

## 8. Equipment Working Hours (EWH) Budget — Endpoint & Widget Riil (D2, `9b690b6` + `adc1048`)

**Endpoint baru:** `GET /api/v1/ewh-budget?forecast_prod_bcm=<n>` menggabungkan:
- `supporting_units_baseline` / `dewatering_units_baseline` (kolom `pa`/`ua`, **sebelumnya tidak dipakai di manapun** — dikonfirmasi lewat pencarian seluruh codebase) → formula standar `EWH = 24 jam × PA% × UA%`.
- `equipment_catalogs` (qty & fc_lhr riil per model, difilter `activity IN (SUPPORT, DEWATERING)` dan `qty > 0`) → breakdown per-model.

Skema asli (`supporting_units_baseline`/`dewatering_units_baseline`) **hanya punya 1 baris per sektor** — jauh lebih sedikit dibanding daftar 6+4 model fiktif yang dipakai dummy sebelumnya. Formula diterapkan secara merata ke semua equipment riil di sektor tersebut (satu-satunya interpretasi yang jujur terhadap skema yang ada).

**Frontend:** `SupportEwhBudgetCard.vue` di-generalisasi menerima `EwhSector` apapun; `DewateringEwhBudgetCard.vue` jadi thin-wrapper; `SupportDewateringEwhTable.vue` flatten dari `sectors[].equipment[]`.

---

## 9. Dynamic Threshold Config + Model Retrain (D3, `085bfe2` + `729869a` + `adc1048`)

**Tabel baru:** `cfg_system_mlops` (model `SystemMlopsConfig`) — generic key/value, **sesuai desain yang sudah ada di `SPRINT/sprint pages/Page_03_Support_Dewatering_dan_Weather_MLOps.md`** (tabel ini direncanakan tim tapi belum pernah diimplementasikan). Default value di-seed otomatis (lazy init) persis sama dengan konstanta lama (`1.018`, `+8%`, `+18%`) sehingga perilaku tidak berubah sampai seseorang mengubahnya lewat endpoint baru.

**Endpoint baru:**
- `GET`/`PUT /api/v1/threshold-config` — baca/ubah budget baseline & persentase warning/critical.
- `POST /api/v1/model/retrain` — melatih ulang XGBoost + PyTorch Autoencoder dari data DB terkini (±9 detik untuk ukuran dataset saat ini), reload model XGBoost yang aktif di memory, kembalikan metrik hasil retrain yang riil.

**`forecasting_service.forecast_single_day()`** kini membaca threshold dari `cfg_system_mlops` saat `db_session` tersedia (fallback ke konstanta lama jika tidak) — dikonfirmasi tidak merusak test `test_forecasting_service_dynamic_thresholds` yang sudah ada karena nilai default identik.

**Halaman baru:** `/support-weather-mlops` (route + nav item baru) — menyatukan `OpenMeteoWeatherCard`, `SupportEwhBudgetCard`, `DewateringEwhBudgetCard`, `NonProductionFuelBurdenDonut`, `SupportDewateringEwhTable`, `DynamicThresholdConfigCard`, `MLOpsModelRetrainCard` persis sesuai wireframe yang sudah direncanakan di sprint docs tapi belum pernah dibangun.

**Loose ends ditutup:** 2 dari 3 komentar `ponytail:` yang sebelumnya menandai `budget-baseline` sebagai konstanta hardcoded sementara (`dashboard.vue`, `TimeSeriesForecastChart.vue`) kini membaca nilai riil dari `/api/v1/threshold-config`.

---

## 10. AI Co-pilot Honesty Pass & XGBoost Feature Contributions (Phase G, `9ac741e`)

**AI Co-pilot:**
- Rename konsisten "Mining Fuel AI Assistant" → **"KIDECO Dispatch & Fuel Co-pilot"** di widget frontend maupun system prompt Gemini & fallback engine backend.
- Status "Gemini AI & Real DB Context Connected" yang **selalu tampil terlepas dari status AI service sebenarnya** kini membaca `GET /api/v1/ai-ready` secara riil.
- Suggested prompt yang membawa angka fiktif (`"...naik ke 1.285 L/BCM?"`) diganti pertanyaan genuine.
- Backend fallback engine (`routes_chatbot.py`): `anomalous_units_sample` sebelumnya default ke **2 unit kode fiktif** (`EX2600-6`, `PC2000-11R`) setiap kali 0 spike terdeteksi — sekarang kosong secara jujur. Klaim **"WO Maintenance otomatis telah diterbitkan"** (yang tidak pernah benar-benar terjadi) dihapus, diganti rekomendasi tindakan (bukan klaim tindakan sudah diambil).
- **Temuan keamanan:** pesan chat dirender via `v-html` setelah hanya transformasi markdown bold/newline, **tanpa HTML-escaping** — pesan pengguna sendiri (termasuk query yang di-echo balik) bisa menyisipkan markup mentah. Diperbaiki: escape dulu, baru terapkan transformasi markdown.

**XGBoost Transparency:**
- `forecasting_service.forecast_single_day()` kini menghitung **feature contributions riil** via `pred_contribs` XGBoost booster (nilai aditif/gaya-SHAP — jumlah seluruh kontribusi + base_value = hasil prediksi), bukan feature_importance global atau rekayasa. Diekspos sebagai `feature_contributions` di `/api/v1/forecast` & `/api/v1/forecast-7days`.
- `ScenarioSimulatorControls.vue` menampilkan 3 kontributor utama (berdasarkan magnitude absolut) sebagai chip di kartu hasil.

**Temuan di luar scope, diflag terpisah (spawn_task):**
- PyTorch Autoencoder training tidak memiliki random seed → `tests/test_task_4.py` flaky antar run (precision bisa 0.88 atau 0.36 dengan kode & data identik).
- `spike_report_per_unit.avg_fc_normal` dari endpoint anomaly-detect kadang kembali 0, itulah sebabnya `TopAnomalousLeaderboard.vue` masih punya `stdFcMap` sebagai fallback client-side.

---

## Verifikasi yang Dijalankan Setiap Commit

- `cd laravel && npx vue-tsc --noEmit` — typecheck bersih (kecuali error pre-existing yang tidak terkait: `CardStatisticsHorizontal`, `VerticalNavGroup/Link`, `build-icons.ts`, `fleetType` di `production-capacity.vue`).
- `cd laravel && npx vite build` — build production berhasil di setiap commit.
- `cd python-ai-service && python -m pytest tests/ -q` — 24 passed, 1 pre-existing failure (`test_database_connection_and_seeding`, soal jumlah seed data Excel — tidak terkait perubahan di dokumen ini, dikonfirmasi gagal juga sebelum perubahan apapun).
- Model artifacts (`.pkl`/`.pth`/`metadata.json`) yang ter-regenerate akibat menjalankan test suite di-revert (`git checkout`) agar tidak ikut ter-commit sebagai side-effect yang tidak disengaja.
