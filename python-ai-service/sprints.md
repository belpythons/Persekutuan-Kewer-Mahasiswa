# Python AI Service — Dekomposisi Sprint 1 hingga Sprint 18

Dokumen ini berisi panduan implementasi teknis mendetail per sprint untuk sub-proyek **`python-ai-service/`** (FastAPI + XGBoost + PyTorch Autoencoder + MLOps) berdasarkan acuan `implementation_plan.md` dan `prd.md`.

---

## 📅 Matriks Ringkasan Sprint `python-ai-service/`

| Sprint | Judul / Fokus Utama | Output / Deliverable | Target Celah |
|:-------|:-------------------|:---------------------|:-------------|
| **Sprint 1-3** | FastAPI Setup & DB Connection | Microservice Scaffold & DB Interface | Baseline Setup |
| **Sprint 4** | Data Pipeline & Feature Engineering | 13+ Fitur (Kecepatan Angin & Lag) | #13 (Fitur Angin) |
| **Sprint 5** | XGBoost Engine & TimeSeriesSplit | XGBoost Model & Walk-Forward CV | #6 (Split Realistis) |
| **Sprint 6** | PyTorch Autoencoder Anomaly Detector | Trained Autoencoder + Adaptive Threshold | #4 (Data Normal), #5 (Adaptive) |
| **Sprint 7** | Combined Capacity Engine & REST API | FastAPI REST Endpoints (`/forecast`, `/capacity`) | API Interface |
| **Sprint 13** | Latency Optimization & Warm-up | Model Warm-up & Benchmark (<2s) | Performance |
| **Sprint 14** | PyTest AI Suite | Test Pipeline & Model Assertions | #11 (Testing) |
| **Sprint 17** | MLOps Retraining & Drift Pipeline | `retrain_pipeline.py` & Drift Monitoring | #3 (Retraining MLOps) |

---

## 🛠️ Detil Instruksi Pengerjaan Per Sprint

### 📌 Sprint 1 - 3: Setup Microservice & Data Interface
**Folder Target:** `python-ai-service/`
- **Langkah Pengerjaan:**
  1. Buat struktur folder:
     ```
     python-ai-service/
     ├── api/
     ├── models/
     ├── pipelines/
     ├── services/
     ├── main.py
     └── requirements.txt
     ```
  2. Isi `requirements.txt`:
     ```txt
     fastapi==0.110.0
     uvicorn==0.28.0
     xgboost==2.0.3
     torch==2.2.1
     scikit-learn==1.4.1
     pandas==2.2.1
     numpy==1.26.4
     pydantic==2.6.4
     psycopg2-binary==2.9.9
     optuna==3.5.0
     pytest==8.0.2
     ```
  3. Buat `database.py` dengan koneksi SQLAlchemy / Psycopg2 ke PostgreSQL.

---

### 📌 Sprint 4: Data Pipeline & Feature Engineering (Solusi Celah #13)
- **Langkah Pengerjaan:**
  1. Buat `pipelines/data_pipeline.py` untuk mengambil data riil dari PostgreSQL.
  2. Implementasikan `pipelines/feature_engineering.py` dengan memasukkan fitur kecepatan angin (Celah #13):
     ```python
     import pandas as pd

     def build_features(df: pd.DataFrame) -> pd.DataFrame:
         df['DayOfWeek'] = df['Date'].dt.dayofweek
         df['Month'] = df['Date'].dt.month
         df['IsWeekend'] = df['DayOfWeek'].isin([5, 6]).astype(int)
         df['Rain_Lag1'] = df['Curah_Hujan_mm'].shift(1).fillna(0)
         df['Rain_Lag2'] = df['Curah_Hujan_mm'].shift(2).fillna(0)
         df['FR_Lag1'] = df['Actual_FR_L_BCM'].shift(1).bfill()
         df['FR_Lag2'] = df['Actual_FR_L_BCM'].shift(2).bfill()
         df['RollingAvg_FR_7d'] = df['Actual_FR_L_BCM'].shift(1).rolling(7, min_periods=1).mean()
         
         # WAJIB: Masukkan Kecepatan_Angin_kmh
         features = [
             'Curah_Hujan_mm', 'Temp_Max_C', 'Kecepatan_Angin_kmh',
             'Haul_Distance_m', 'Daily_Prod_BCM', 'DayOfWeek', 'Month',
             'IsWeekend', 'Rain_Lag1', 'Rain_Lag2', 'FR_Lag1', 'FR_Lag2', 'RollingAvg_FR_7d'
         ]
         return df[features]
     ```

---

### 📌 Sprint 5: XGBoost Engine & TimeSeriesSplit CV (Solusi Celah #6)
- **ATURAN BEBAS HALUSINASI:** DILARANG menggunakan random 80/20 train_test_split pada data time-series. WAJIB menggunakan `TimeSeriesSplit`.
- **Langkah Pengerjaan:**
  1. Buat `pipelines/train_xgboost.py`:
     ```python
     from sklearn.model_selection import TimeSeriesSplit
     import xgboost as xgb
     import joblib

     def train_model(X, y):
         tscv = TimeSeriesSplit(n_splits=5)
         for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
             X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
             y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
             
             model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)
             model.fit(X_tr, y_tr)
         
         # Fit final model
         model.fit(X, y)
         joblib.dump(model, 'models/xgboost_fr_v1.pkl')
     ```

---

### 📌 Sprint 6: PyTorch Autoencoder Anomaly Detector (Solusi Celah #4 & #5)
- **ATURAN BEBAS HALUSINASI:** Model Autoencoder HANYA di-train pada data normal (`Is_Known_Anomaly == 0`).
- **Langkah Pengerjaan:**
  1. Buat `services/autoencoder.py`:
     ```python
     import torch
     import torch.nn as nn
     import numpy as np

     class AutoencoderDetector(nn.Module):
         def __init__(self, input_dim):
             super().__init__()
             self.encoder = nn.Sequential(
                 nn.Linear(input_dim, 16), nn.ReLU(),
                 nn.Linear(16, 8), nn.ReLU(),
                 nn.Linear(8, 3), nn.ReLU()
             )
             self.decoder = nn.Sequential(
                 nn.Linear(3, 8), nn.ReLU(),
                 nn.Linear(8, 16), nn.ReLU(),
                 nn.Linear(16, input_dim)
             )

         def forward(self, x):
             return self.decoder(self.encoder(x))

     def compute_adaptive_threshold(normal_recon_errors):
         # Adaptive MAD-based Threshold (Celah #5)
         median = np.median(normal_recon_errors)
         mad = np.median(np.abs(normal_recon_errors - median))
         return median + 3.0 * 1.4826 * mad
     ```

---

### 📌 Sprint 7: Combined Capacity Engine & REST API
- **Langkah Pengerjaan:**
  1. Buat `services/capacity_engine.py` untuk mengombinasikan output XGBoost + Autoencoder + Derating Hujan.
  2. Implementasikan API endpoints pada `main.py`:
     - `POST /api/v1/forecast`: Melakukan inferensi FR harian.
     - `POST /api/v1/anomaly-detect`: Memindai lonjakan BBM unit.
     - `POST /api/v1/capacity`: Menghitung alokasi armada harian.
  3. Uji coba Swagger UI pada `http://localhost:8000/docs`.

---

### 📌 Sprint 17: MLOps Retraining & Drift Pipeline (Solusi Celah #3)
- **Langkah Pengerjaan:**
  1. Buat `pipelines/retrain_pipeline.py` yang dieksekusi bulanan secara otomatis via Cron.
  2. Tambahkan pemeriksaan Data Drift menggunakan Kolmogorov-Smirnov test pada distribusi fitur baru vs lama.
  3. Jika R² model baru lebih tinggi minimal 2%, update model registry dan simpan versi baru.
