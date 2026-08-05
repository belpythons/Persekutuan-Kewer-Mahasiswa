# Dokumentasi Penyelesaian Task 5 — Combined Capacity Engine & FastAPI Endpoints

Dokumen ini mencatat penyelesaian teknis untuk **Task 5 (Sprint 7)** pada folder `python-ai-service/`.

---

## 📌 Ringkasan Pekerjaan Task 5

Task 5 berfokus pada:
1. Pembuatan Combined Capacity Engine (`services/capacity_engine.py`) yang mengintegrasikan:
   - Forecast Produksi BCM Harian (dari XGBoost Engine).
   - Penyesuaian Anomali Lonjakan BBM (dari PyTorch Autoencoder).
   - Derating Hujan Non-Linear (Solusi Celah #9).
2. Pemhitungan Utilisasi Armada, Unit Operasional Efektif, dan Alokasi Solar Kombinasi Harian.
3. Penyelarasan hasil perhitungan ke tabel database `capacity_allocations`.
4. Pendaftaran REST API Endpoint `POST /api/v1/calculate-capacity` pada `api/routes_capacity.py` dan `main.py`.
5. Pembuatan Automated Test Suite `tests/test_task_5.py` yang memverifikasi 100% fungsionalitas rumus derating non-linear, kalkulasi kapasitas, database sync, dan API response HTTP 200 OK.

---

## 📂 File yang Dibuat & Diperbarui

```
python-ai-service/
├── api/
│   └── routes_capacity.py             # FastAPI REST Endpoint POST /api/v1/calculate-capacity
├── services/
│   └── capacity_engine.py             # Service Combined Capacity Engine & Non-linear Derating
├── tests/
│   └── test_task_5.py                 # Automated PyTest suite untuk Task 5
├── main.py                            # Pendaftaran routes_capacity router
└── TASK_5_DOCUMENTATION.md            # Dokumentasi teknis penyelesaian Task 5
```

---

## 🛠️ Detail Rincian Komponen Task 5

### 1. Formulasi Derating Hujan Non-Linear (`calculate_rain_derating_non_linear`)
Sesuai spesifikasi dokumen bisnis (Solusi Celah #9):
- **Curah Hujan $\le 5$ mm:** $\text{Derating} = 1.0$ (Tanpa penurunan)
- **Curah Hujan $5 - 20$ mm:** $\text{Derating} = 1.0 - 0.01 \times (\text{Rain} - 5)^{1.3}$
- **Curah Hujan $20 - 50$ mm:** $\text{Derating} = \max(0.65, 0.82 - 0.005 \times (\text{Rain} - 20)^{1.1})$
- **Curah Hujan $> 50$ mm:** $\text{Derating} = 0.60$ (Kapasitas minimum operasional)

### 2. Logika Penentuan Kapasitas & Alokasi Solar
- $\text{Kapasitas Terpasang (BCM/hr)} = \sum (\text{Qty} \times \text{Prod\_BCMhr})$
- $\text{Kapasitas Efektif (BCM/day)} = \text{Installed Cap} \times 20 \text{ jam} \times \text{Rain Derating}$
- $\text{Utilisasi \%} = \min(100.0, (\text{Forecast Daily Prod BCM} / \text{Effective Prod Cap}) \times 100\%)$
- $\text{Unit Operasional} = \lceil (\text{Utilisasi \%} / 100) \times \text{Total Fleet Qty} \rceil$
- $\text{Alokasi BBM Kombinasi (L/day)} = \text{Base Fuel} + (\text{NN Spike Count} \times 15\% \text{ Buffer BBM})$

### 3. REST API Endpoint (`api/routes_capacity.py` & `main.py`)
- Endpoint: `POST /api/v1/calculate-capacity`
- Request Schema (Pydantic): `CapacityRequest` (`date`, `forecast_prod_bcm`, `curah_hujan_mm`, `equipment_list`, `nn_spike_count_by_unit`).
- Response Schema: `log_date`, `forecast_prod_bcm`, `rain_derating_factor`, `installed_prod_bcmhr`, `effective_prod_bcmday`, `utilization_pct`, `operating_units`, `total_combined_fuel_lday`, `activity_breakdown`.

---

## 🧪 Verifikasi & Hasil PyTest

Pengujian otomatis dijalankan dengan script `tests/test_task_5.py`:

```bash
python tests/test_task_5.py
```

### Hasil Testing Formula & API:
- `test_non_linear_rain_derating_calculator`: ✅ **PASSED**
  - Hujan 0 mm $\rightarrow$ 1.00
  - Hujan 15 mm $\rightarrow$ 0.80
  - Hujan 35 mm $\rightarrow$ 0.72
  - Hujan 60 mm $\rightarrow$ 0.60
- `test_capacity_engine_calculation_and_db_save`: ✅ **PASSED** (Perhitungan utilisasi, unit aktif, alokasi BBM kombi, dan penyelarasan ke DB `capacity_allocations` berjalan presisi).
- `test_fastapi_calculate_capacity_endpoint`: ✅ **PASSED** (Endpoint HTTP `POST /api/v1/calculate-capacity` mengembalikan status `200 OK` dengan response valid).

Output Terminal:
```
Derating non-linear tests: 0mm -> 1.00, 15mm -> 0.80, 35mm -> 0.72, 60mm -> 0.60
 [OK] SELURUH PYTEST TASK 5 PASSED 100%!
```

---

## 🏁 Ringkasan Status Seluruh Task Python AI Service (Task 1 s/d 5)

| Task # | Nama Task | Status | PyTest Verification |
|:-------|:----------|:-------|:---------------------|
| **Task 1** | Environment & DB Connection Setup | ✅ Completed | 100% PASS |
| **Task 2** | Data Pipeline, 13-Features & DB Seeding | ✅ Completed | 100% PASS |
| **Task 3** | XGBoost Forecasting & TimeSeriesSplit CV | ✅ Completed | 100% PASS ($R^2=0.9678$) |
| **Task 4** | PyTorch Autoencoder Anomaly Detector | ✅ Completed | 100% PASS (Recall=100%, Prec=84.78%) |
| **Task 5** | Combined Capacity Engine & REST API | ✅ Completed | 100% PASS |
