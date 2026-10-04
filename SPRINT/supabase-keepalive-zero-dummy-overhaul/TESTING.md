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

## 5. Verifikasi Manual yang Direkomendasikan di Browser (belum dijalankan di sesi ini)

Sesi ini tidak menjalankan dev server/browser untuk klik-per-klik. Sebelum deploy, disarankan verifikasi manual berikut:

1. `npm run dev` di `laravel/`, jalankan `python-ai-service` secara lokal (`uvicorn main:app`).
2. Buka `/dashboard`, `/production-capacity`, `/global-capacity`, `/forecasting-ai`, `/support-weather-mlops` — pastikan ke-4 state (loading/error/empty/live) tampil sesuai dengan mematikan/menyalakan `python-ai-service`.
3. Ganti tema light ↔ dark via navbar switcher (dipulihkan di komit `8994e16`) — pastikan palet baru (Mining Blue/Slate) konsisten di kedua mode.
4. Di `/support-weather-mlops`: ubah nilai di **Dynamic Threshold Config**, klik Simpan, lalu refresh `/dashboard` — pastikan widget forecast memakai threshold baru. Klik **Trigger Model Retraining** dan tunggu (~9 detik) hingga metrik di kartu MLOps berubah.
5. Di `/forecasting-ai`: geser slider di **Scenario Simulator**, perhatikan chip "Kontributor Utama Prediksi" berubah sesuai variabel yang digeser.
6. Trigger workflow `.github/workflows/supabase-keepalive.yml` secara manual (`workflow_dispatch`) di tab Actions GitHub setelah menambahkan secret `SUPABASE_URL`/`SUPABASE_KEY`, untuk memverifikasi kredensial sebelum mempercayakannya ke jadwal cron.

---

## 6. Temuan yang Diflag untuk Pekerjaan Terpisah (di luar scope plan ini)

| Temuan | Task ID | Alasan Tidak Diperbaiki di Sini |
|---|---|---|
| PyTorch Autoencoder training tanpa random seed (flaky test) | `task_90c628da` | Perbaikan model training, bukan bagian dari zero-dummy/keep-alive scope |
| `spike_report_per_unit.avg_fc_normal` kadang 0, memaksa `TopAnomalousLeaderboard.vue` menyimpan `stdFcMap` sebagai fallback | `task_bcccb1d6` | Memerlukan perubahan logic endpoint anomaly-detect, bukan sekadar wiring ulang |
| `python-ai-service/config.py` hardcode default Supabase URL+key; `.env` pakai nama variabel (`NEXT_PUBLIC_SUPABASE_*`) berbeda dari yang dibaca `config.py` | — (dicatat di IMPLEMENTATION.md §2) | Di luar scope Objektif 1 (workflow keep-alive berjalan independen dari config ini) |
