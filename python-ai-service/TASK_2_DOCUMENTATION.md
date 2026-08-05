# Dokumentasi Penyelesaian Task 2 — Data Pipeline, 13-Feature Engineering & Database Seeding

Dokumen ini mencatat penyelesaian teknis untuk **Task 2 (Sprint 4)** dan **Database Creation & Seeding** pada folder `python-ai-service/`.

---

## 📌 Ringkasan Pekerjaan Task 2

Task 2 berfokus pada:
1. Pembuatan SQLAlchemy Database Models (`models_db.py`) untuk seluruh tabel sistem.
2. Pembuatan Data Pipeline Ingestion (`pipelines/data_pipeline.py`) untuk mengambil data historis dari database.
3. Pembuatan Feature Engineering Module (`pipelines/feature_engineering.py`) yang mengekstraksi 13+ fitur ML lengkap (termasuk `Kecepatan_Angin_kmh` - Solusi Celah #13).
4. Pembuatan Database Seeding Script (`seed_database.py`) yang membuat tabel database dan mengisinya dengan data ground-truth dari Excel `UPDATE_Fuel ratio calculation 2026 dummy data.xlsx`.
5. Pembuatan Automated PyTest Suite (`tests/test_task_2.py`) yang memverifikasi 100% fungsionalitas data pipeline dan database.

---

## 📂 File yang Dibuat

```
python-ai-service/
├── models_db.py                      # SQLAlchemy ORM Models (9 Tabel Database)
├── pipelines/
│   ├── __init__.py
│   ├── data_pipeline.py              # Ingestion data dari DB & Data Quality Check
│   └── feature_engineering.py        # Ekstraksi 13 Fitur ML (termasuk Kecepatan_Angin_kmh)
├── seed_database.py                  # Script Pembuatan & Seeding Database Ground-Truth
├── tests/
│   └── test_task_2.py                # Automated PyTest suite untuk Task 2
└── TASK_2_DOCUMENTATION.md           # Dokumentasi teknis penyelesaian Task 2
```

---

## 🛠️ Detail Rincian Komponen Task 2

### 1. File `models_db.py`
Mendefinisikan 9 tabel database relasional berbasis SQLAlchemy Base ORM:
- `EquipmentCatalog` (`equipment_catalogs`): Master data unit (38 tipe alat, Qty, Aktivitas, FC L/hr).
- `LoadingUnitBaseline` (`loading_units_baseline`): Baseline unit muat (EX2600, PC1250, PC2000, PC3400).
- `HaulingUnitBaseline` (`hauling_units_baseline`): Baseline unit angkut (HD785-7, FM9CT).
- `SupportingUnitBaseline` & `DewateringUnitBaseline`: Baseline unit pendukung & pompa air.
- `WeatherDailyLog` (`weather_daily_logs`): Histori harian curah hujan, suhu, dan kecepatan angin.
- `DailyForecastLog` (`daily_forecast_logs`): Log FR harian, status (NORMAL/WARNING/CRITICAL), target BCM, dan jarak angkut.
- `UnitAnomalySpike` (`unit_anomaly_spikes`): Log konsumsi BBM harian per unit dan indikator anomali spike.
- `CapacityAllocation` (`capacity_allocations`): Log utilisasi kapasitas armada dan alokasi BBM harian.

### 2. File `pipelines/feature_engineering.py` (Solusi Celah #13)
Menyediakan fungsi `build_features(df)` yang mengekstraksi 13 fitur wajib:
```python
FEATURE_COLUMNS = [
    'Curah_Hujan_mm',
    'Temp_Max_C',
    'Kecepatan_Angin_kmh',  # ✅ Wajib dimasukkan (Solusi Celah #13)
    'Haul_Distance_m',
    'Daily_Prod_BCM',
    'DayOfWeek',
    'Month',
    'IsWeekend',
    'Rain_Lag1',
    'Rain_Lag2',
    'FR_Lag1',
    'FR_Lag2',
    'RollingAvg_FR_7d'
]
```

### 3. File `pipelines/data_pipeline.py`
Menyediakan fungsi:
- `load_historical_weather_and_forecasts(db)`: Menarik log cuaca & forecast dari database via SQL terparameterisasi.
- `validate_and_clean_data(df)`: Data Quality Check untuk menangani missing values dan outlier clipping pada batas wajar operasional.
- `fetch_and_prepare_dataset(db)`: Menggabungkan data loading, quality check, dan ekstraksi 13 fitur ML.
- `load_unit_anomaly_logs(db)`: Menarik log konsumsi BBM & spike unit.

### 4. File `seed_database.py` (Database Creation & Seeding)
- Mengeksekusi `Base.metadata.create_all(bind=engine)` untuk membuat seluruh tabel database (PostgreSQL / SQLite fallback).
- Membaca file ground-truth Excel `konsep/UPDATE_Fuel ratio calculation 2026 dummy data.xlsx`.
- Mengisi 38 record `equipment_catalogs` (Sheet `DUMMY DATA`).
- Mengisi baseline loading & hauling units (Sheet `Summary v1`).
- Mengisi 365 hari log historis cuaca, forecast FR, dan unit anomaly spikes.

---

## 🧪 Verifikasi & Hasil PyTest

Pengujian otomatis dijalankan dengan script `tests/test_task_2.py`:

```bash
python tests/test_task_2.py
```

**Hasil Pengujian:**
- `test_database_has_seeded_data`: ✅ PASSED (365 hari data historis berhasil dibaca dari DB).
- `test_feature_engineering_13_columns`: ✅ PASSED (Tepat 13 fitur diekstraksi, termasuk `Kecepatan_Angin_kmh`).
- `test_unit_anomaly_logs_fetch`: ✅ PASSED (Data log unit spike berhasil ditarik dari DB).

Output Terminal:
```
[OK] SELURUH PYTEST TASK 2 PASSED 100%!
```

---

## 🚀 Langkah Selanjutnya (Task 3)

Setelah Task 2 dan Seeding Database selesai 100%, langkah berikutnya adalah **Task 3 (Sprint 5)**:
- Implementasi `pipelines/train_xgboost.py` menggunakan `TimeSeriesSplit(n_splits=5)` CV.
- Optuna hyperparameter tuning.
- Serialisasi model terlatih ke `models/xgboost_fr_v1.pkl`.
