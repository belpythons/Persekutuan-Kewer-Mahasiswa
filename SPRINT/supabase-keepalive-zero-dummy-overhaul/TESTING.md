# Testing & Verification: Supabase Keep-Alive & Zero-Dummy UI Overhaul

> Dibuat setelah seluruh fase (Objektif 1 + Objektif 2 Fase A–G) selesai diimplementasikan.
> Lihat [IMPLEMENTATION.md](./IMPLEMENTATION.md) untuk rincian per fase.
> Branch: `ui/red-blue-design-system-integration` — 16 commit.

## Ringkasan Strategi Verifikasi

Setiap commit (bukan hanya di akhir) diverifikasi dengan kombinasi:
1. **Typecheck** (`vue-tsc --noEmit`) — menangkap drift tipe antara frontend dan response API riil.
2. **Production build** (`vite build`) — menangkap error template yang lolos dari type-checker (ini persis bagaimana dua file rusak di awal sesi ditemukan).
3. **PHP lint** (`php -l`) pada setiap file controller/service Laravel yang diubah.
4. **Pytest** (`python -m pytest tests/ -q`) di `python-ai-service` setelah setiap perubahan backend.
5. **Smoke test manual** via `TestClient`/`curl` untuk endpoint baru sebelum menulis test otomatis untuknya.
6. Revert manual `python-ai-service/models/*.pkl|*.pth|metadata.json` setiap kali test suite memicu training ulang, supaya artifact model yang ter-regenerate oleh proses testing tidak ikut ter-commit sebagai side-effect yang tidak disengaja.

---

## 1. Frontend — Typecheck & Build

Dijalankan ulang setelah **setiap** commit frontend (bukan hanya di akhir):

```bash
cd laravel
npx vue-tsc --noEmit
npx vite build
```

**Hasil akhir (setelah commit terakhir):** build sukses, 0 error baru. 5 error yang tersisa di `vue-tsc` adalah **pre-existing** dan tidak terkait pekerjaan ini — dikonfirmasi dengan `git stash` lalu menjalankan typecheck yang sama sebelum perubahan apapun dimulai:

| File | Error | Status |
|---|---|---|
| `@core/components/cards/CardStatisticsHorizontal.vue` | `kFormatter` tidak ada di type instance | Pre-existing, template core Sneat |
| `@layouts/components/VerticalNavGroup.vue` | Icon prop type mismatch | Pre-existing, template core Sneat |
| `@layouts/components/VerticalNavLink.vue` | Icon prop type mismatch | Pre-existing, template core Sneat |
| `pages/production-capacity.vue:92` | `fleetType` prop wajib tidak dikirim ke komponen | Pre-existing (di luar scope plan ini) |
| `plugins/iconify/build-icons.ts` | Missing type declaration `@iconify/utils` | Pre-existing, build-time script only |

Satu error type **yang sempat ada di awal sesi** (`ForecastPayload` punya field wajib yang API sebenarnya opsional, dipakai di `dashboard.vue`/`global-capacity.vue`/`production-capacity.vue`) **sudah diperbaiki** sebagai bagian dari fix root-cause `useAiApi.ts` — dikonfirmasi tidak muncul lagi di typecheck akhir.

---

## 2. Backend — PHP Lint

Dijalankan untuk setiap file PHP yang disentuh:

```bash
cd laravel
php -l app/Services/FuelRatioAiClient.php
php -l app/Http/Controllers/Api/ForecastController.php
php -l app/Http/Controllers/Api/CapacityController.php
php -l app/Http/Controllers/Api/MlopsController.php
php -l app/Http/Controllers/Api/ChatbotController.php
php -l routes/api.php
```

**Hasil:** `No syntax errors detected` pada seluruh file, setiap kali dijalankan.

---

## 3. Backend — Python Test Suite

```bash
cd python-ai-service
python -m pytest tests/ -q
```

### 3.1 Test baru yang ditambahkan dalam pekerjaan ini (16 test function, 8 file)

| File | Jumlah Test | Memverifikasi |
|---|---|---|
| `tests/test_weather_sync.py` | 3 | `sync-bmkg` menyimpan **persis** nilai dari response Open-Meteo yang di-mock (bukan `random.uniform()`); kegagalan upstream → HTTP 502, bukan commit data fiktif; `model-metrics` mengembalikan metadata training riil |
| `tests/test_ewh_budget.py` | 2 | Response `ewh-budget` dibangun dari baris DB riil (`supporting_units_baseline`/`dewatering_units_baseline`/`equipment_catalogs`), bukan daftar hardcoded; matematika alokasi BBM konsisten (`qty × fc_lhr × ewh_hrs`) |
| `tests/test_threshold_config.py` | 2 | Default config persis sama dengan konstanta lama (`1.018`/`8%`/`18%`) sehingga perubahan ini **behavior-preserving**; mengubah config benar-benar mengubah threshold yang dikembalikan `/forecast` |
| `tests/test_feature_contributions.py` | 1 | Properti aditif SHAP (`Σ feature_contributions + base_value ≈ forecast_fr`) |
| `tests/test_chatbot_honesty.py` | 2 | Tidak ada unit fiktif saat 0 spike terdeteksi; tidak ada klaim "WO Maintenance otomatis diterbitkan" |

### 3.2 Hasil akhir: 30 passed, 3 failed — ketiganya **pre-existing**, dikonfirmasi lewat 2 metode:

**a) `test_database_connection_and_seeding`** (mismatch jumlah `equipment_catalogs`: diharapkan ≥38, didapat 19)
Dikonfirmasi pre-existing dengan `git stash` sebelum perubahan apapun dimulai — tes ini sudah gagal di titik awal sesi. Soal data seed Excel vs isi SQLite lokal, tidak terkait perubahan apapun di pekerjaan ini.

**b) `test_pytorch_autoencoder_training_on_normal_data`, `test_autoencoder_spike_isolation`, `test_autoencoder_training_and_serialization`, `test_autoencoder_anomaly_detection_logic`** (flaky — kombinasi yang gagal berubah-ubah antar run)
Root cause: `services/autoencoder.py`'s `AutoencoderAnomalyService.train()` **tidak memiliki `torch.manual_seed()`** di manapun, sehingga precision/recall PyTorch bervariasi antar run (diamati: precision 0.88 di satu run, 0.36 di run lain, dengan kode & data identik). `pipelines/train_xgboost.py` sudah punya `random_state=42` tapi sisi PyTorch tidak. **Tidak diperbaiki di pekerjaan ini** (di luar scope plan) — sudah di-flag sebagai background task terpisah (`task_90c628da`, "Seed PyTorch autoencoder training for reproducible tests").

**Praktik selama sesi:** setiap kali test suite men-trigger training ulang (baik lewat test files atau smoke-test manual `/api/v1/model/retrain`), file `models/*.pkl`, `*.pth`, `metadata.json` yang ter-regenerate di-`git checkout --` agar tidak ikut ter-commit sebagai perubahan tak disengaja.

---

## 4. Smoke Test Manual (sebelum menulis automated test)

Setiap endpoint baru diuji manual via `TestClient`/`curl` terlebih dahulu untuk memvalidasi bentuk response sebelum menulis test otomatis:

| Endpoint | Hasil |
|---|---|
| `GET /api/v1/model-metrics` | 200, mengembalikan `metrics.final_full_r2`, `avg_cv_mae`, dll. riil dari `metadata.json` |
| `GET /api/v1/ewh-budget` | 200, 2 sektor (`SUPPORT`, `DEWATERING`) dengan breakdown per-equipment riil |
| `GET`/`PUT /api/v1/threshold-config` | 200; perubahan `warning_pct` langsung berefek pada `/forecast` berikutnya |
| `POST /api/v1/model/retrain` | 200, ±8.8 detik untuk ukuran dataset saat ini, mengembalikan metrik hasil retrain riil |
| `POST /api/v1/weather/sync-bmkg` (setelah fix) | 200 dengan data Open-Meteo sungguhan; 502 saat API eksternal disimulasikan down |
| `POST /api/v1/forecast` (dengan `feature_contributions`) | 200, 13 fitur + `base_value`, jumlah ≈ `forecast_fr` |

---

## 5. Verifikasi Manual End-to-End di Browser (dijalankan, hasil nyata)

Dijalankan setelah permintaan eksplisit untuk debug sesuai dokumen ini. Setup: `python-ai-service` via `python main.py` (port 8002), Laravel via `php artisan serve --port=8010` (port 8000 & 5173 default sudah dipakai proyek lain di mesin ini), serta production build (`npx vite build`) di-serve langsung oleh Laravel (file `public/hot` basi dari sesi lain dihapus agar tidak mencoba connect ke Vite dev server yang salah). Konfigurasi disimpan di `.claude/launch.json` untuk sesi berikutnya.

| Langkah | Hasil |
|---|---|
| `/dashboard` — semua widget | **Live.** Weather card sync ke Open-Meteo asli, Fuel Ratio Status NORMAL dengan data real (1.0182 L/BCM), PyTorch Anomaly 5/5 unit, donut solar per aktivitas, TimeSeriesForecastChart dengan threshold zones, leaderboard 5 unit nyata. Tidak ada data dummy terlihat. |
| `/production-capacity` | **Live.** Loading/Hauling Fleet card, FleetCapacityOptimizerGrid ("Target Produksi: 102.000,0 BCM/hari" — dihitung, bukan hardcoded), NonProductionFuelBurdenDonut 11.0%, HourlyFleetCapacityMatrix 19 baris data riil. |
| `/global-capacity` | **Live.** "397 Fleet Units Tuned" dinamis dari response, tabel SPO Compliance 19 unit — semua "Compliant" (variance ~4.5-4.6%), tidak ada CriticalEquipmentAlertBanner (0 unit over-consumption → banner benar-benar tersembunyi, bukan ditampilkan kosong). |
| `/forecasting-ai` | **Live.** Scenario Simulator menghasilkan prediksi real + **chip "Kontributor Utama Prediksi" menampilkan 3 feature contribution asli** (Rain Derating +0.1201, Haul Distance +0.0030, Production Target -0.0014) yang berubah mengikuti slider. ModelMetricsCard: R² 0.9988, MAE 0.00029 — metrik asli. Chatbot menyapa sebagai "KIDECO Dispatch & Fuel Co-pilot" dengan status "AI Engine Connected" real. |
| `/support-weather-mlops` | **Live.** EWH card Supporting (14 unit) & Dewatering (96 unit) dengan angka dari `equipment_catalogs` riil, tabel EWH 6 baris real. |
| **Dark mode** (navbar switcher) | **Berhasil.** Toggle light→dark→light mulus, palet Mining Blue/Slate konsisten di kedua mode, semua teks tetap kontras dan terbaca. |
| **Threshold config live-edit** | **Berhasil.** Ubah Warning Delta 8%→15%, Simpan → chip "Konfigurasi berhasil disimpan" muncul, `GET /api/v1/threshold-config` via curl mengonfirmasi `warning_pct:15` tersimpan. Dikembalikan ke 8% setelah tes. |
| **Chatbot — quick prompt anomali** | **Berhasil, fix terkonfirmasi.** Respons menampilkan 5 unit kode asli (HD785-7, HD785-SPIKE, HD785-7MUD, EX2600-6, EX2600-SPIKE) dari leaderboard — bukan 2 unit fiktif lama. Baris aksi: "Rekomendasi: Jadwalkan pemeriksaan ... ajukan WO Maintenance secara manual bila diperlukan" — tidak ada lagi klaim "WO otomatis telah diterbitkan". |
| **Chatbot — XSS fix** | **Berhasil, fix terkonfirmasi.** Mengetik `<img src=x onerror=alert('xss')> <b>bold test</b>` ke chat input: tidak ada alert yang muncul, tag `<b>` tidak di-bold-kan (ter-escape sebagai teks literal), dikonfirmasi lewat `get_page_text` dan console log (tidak ada error/alert). |
| **Trigger Model Retraining** | **Berhasil end-to-end.** Klik tombol → ~9 detik → chip "Status: Retraining selesai — model & metrik telah diperbarui." muncul, metrik di kartu berubah ke nilai baru hasil retrain riil (R² 0.9988→0.9984, Precision 85.1%→86.3%, Recall 97.6%→81.5% — variasi ini justru mengonfirmasi temuan `task_90c628da` soal missing random seed). Model artifact yang ter-regenerate di-revert via `git checkout` setelahnya. |

### Temuan baru dari verifikasi manual ini (diperbaiki, commit `16dc47c`)

1. **`Excess Fuel` di dashboard selalu `0`** — bukan dihitung, hardcoded `:excess-fuel-liters="0"` di `dashboard.vue`. Diperbaiki: `max(0, forecast_fr - budget_baseline) × daily_prod_bcm`, memakai data yang sudah ada di halaman.
2. **Kolom "Jarak (m)" di `ActualVsForecastTable.vue` menampilkan float mentah** (`3842.0841720377575`) karena tidak ada template slot `#item.haul_distance_m`. Ditambahkan, sekarang tampil `3.842`.

### Dicatat, bukan bug (data riil, bukan dummy)

Pada `/support-weather-mlops`, **Dewatering Fleet FR Burden = +1.6978 L/BCM (166.78% dari Total FR)** — angka ini lebih besar dari total budget FR seluruh tambang. Ini **bukan kesalahan kode**: 85 unit "Water Pump" riil di `equipment_catalogs` × 40 L/hr × 17.3 jam/hari EWH memang menghasilkan konsumsi solar sebesar itu secara matematis. Kemungkinan ini mengindikasikan data seed `qty=85` untuk Water Pump tidak realistis — tapi itu soal kualitas data seed, bukan sesuatu yang kode ini boleh "perbaiki" secara diam-diam (itu justru akan melanggar mandat zero-dummy/anti-hallucination). Perlu ditinjau oleh pemilik data ground-truth.

### Langkah yang masih memerlukan aksi manual user (di luar kemampuan sesi ini)

Trigger workflow `.github/workflows/supabase-keepalive.yml` secara manual (`workflow_dispatch`) di tab Actions GitHub setelah menambahkan secret `SUPABASE_URL`/`SUPABASE_KEY` — memerlukan akses ke repository settings GitHub yang tidak tersedia dari sesi lokal ini.

---

## 6. Temuan yang Diflag untuk Pekerjaan Terpisah (di luar scope plan ini)

| Temuan | Task ID | Alasan Tidak Diperbaiki di Sini |
|---|---|---|
| PyTorch Autoencoder training tanpa random seed (flaky test) | `task_90c628da` | Perbaikan model training, bukan bagian dari zero-dummy/keep-alive scope |
| `spike_report_per_unit.avg_fc_normal` kadang 0, memaksa `TopAnomalousLeaderboard.vue` menyimpan `stdFcMap` sebagai fallback | `task_bcccb1d6` | Memerlukan perubahan logic endpoint anomaly-detect, bukan sekadar wiring ulang |
| `python-ai-service/config.py` hardcode default Supabase URL+key; `.env` pakai nama variabel (`NEXT_PUBLIC_SUPABASE_*`) berbeda dari yang dibaca `config.py` | — (dicatat di IMPLEMENTATION.md §2) | Di luar scope Objektif 1 (workflow keep-alive berjalan independen dari config ini) |
