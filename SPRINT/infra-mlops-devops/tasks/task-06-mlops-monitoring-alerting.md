# [TASK-06] MLOps Metrics Scraping, Prometheus, Grafana & Drift Alerting

## 1. Metadata
- **Sprint**: Infra-MLOps-DevOps - Sprint 17
- **Kategori**: MLOps / Infrastructure
- **Status**: Ready for Implementation
- **Estimasi Effort**: 13 Story Points (~26 Jam)

## 2. Deskripsi Task
Mengembangkan arsitektur *MLOps Observability & Model Health Monitoring Stack* berbasis Prometheus dan Grafana. Modul ini menyerap (*scrape*) metrik runtime dari Python AI Service (latensi inferensi FastAPI, statistik deteksi anomali unit Autoencoder, dan performa XGBoost Regressor). Selain itu, sistem mengintegrasikan modul pendeteksi pergeseran distribusi data (**Data Drift**) berbasis uji statistik *Kolmogorov-Smirnov (KS-Test)* pada fitur operasional harian. Ketika data drift terdeteksi atau nilai $R^2$ model baru turun di bawah 0.70, sistem mengirimkan notifikasi *alerting* otomatis **(Solusi Celah #3)**.

## 3. Objective & Key Results (OKR)
- Objective: Menjamin visibilitas performa runtime AI Engine serta mendeteksi pergeseran pola data operasional tambang secara *real-time*.
- Key Results:
  - [ ] Prometheus berhasil mengekstraksi metrik dari endpoint `/metrics` FastAPI secara periodik (setiap 15s).
  - [ ] Dashboard Grafana menampilkan grafik latensi inferensi (<2.0s), jumlah spike anomali unit, dan skor $R^2$ XGBoost.
  - [ ] Pipeline `pipelines/retrain_pipeline.py` berjalan secara otomatis via Cron bulanan untuk mengevaluasi data drift via KS-Test dan memicu *model retraining* jika R² meningkat ≥ 2%.

## 4. Technical Deliverables & Specifications
- **Target Files**:
  - `infra-mlops-devops/docker-compose.monitoring.yml`
  - `infra-mlops-devops/prometheus/prometheus.yml`
  - `python-ai-service/pipelines/retrain_pipeline.py`
- **Konfigurasi Prometheus (`prometheus.yml`)**:
  ```yaml
  global:
    scrape_interval: 15s

  scrape_configs:
    - job_name: 'python-ai-service'
      metrics_path: '/metrics'
      static_configs:
        - targets: ['python-ai:8000']

    - job_name: 'laravel-web-portal'
      metrics_path: '/actuator/prometheus'
      static_configs:
        - targets: ['laravel-portal:8000']
  ```
- **MLOps Data Drift Detection Pipeline (`pipelines/retrain_pipeline.py`)**:
  ```python
  import numpy as np
  import pandas as pd
  from scipy.stats import ks_2samp
  from sklearn.metrics import r2_score
  import logging

  logger = logging.getLogger(__name__)

  def check_data_drift(reference_df: pd.DataFrame, current_df: pd.DataFrame, features: list) -> dict:
      """
      Memeriksa Data Drift menggunakan Kolmogorov-Smirnov (KS) Test 2-Sample.
      Jika p-value < 0.05, distribusi fitur baru bergeser secara signifikan dari baseline.
      """
      drift_results = {}
      drift_detected = False

      for col in features:
          if col in reference_df.columns and col in current_df.columns:
              stat, p_value = ks_2samp(reference_df[col].dropna(), current_df[col].dropna())
              is_drift = p_value < 0.05
              drift_results[col] = {
                  "ks_stat": round(float(stat), 4),
                  "p_value": round(float(p_value), 4),
                  "drift_detected": is_drift
              }
              if is_drift:
                  drift_detected = True
                  logger.warning(f"[DATA DRIFT ALERT] Fitur '{col}' terdeteksi mengalami pergeseran (p-value: {p_value:.4f})")

      return {
          "overall_drift_detected": drift_detected,
          "feature_details": drift_results
      }
  ```

## 5. Acceptance Criteria (Definition of Done)
- [ ] Service Prometheus dan Grafana dapat dijalankan via `docker-compose -f docker-compose.monitoring.yml up -d`.
- [ ] Dashboard Grafana MLOps menampilkan metrik latensi inferensi AI Service dan status *Data Drift*.
- [ ] Uji coba `retrain_pipeline.py` berhasil mendeteksi pergeseran fitur secara otomatis via KS-Test.
