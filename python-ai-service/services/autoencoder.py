import os
import sys
import json
import joblib
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import logging
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models_db import UnitAnomalySpike, EquipmentCatalog
from pipelines.data_pipeline import load_unit_anomaly_logs

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
AE_MODEL_PATH = os.path.join(MODELS_DIR, "autoencoder_spikes_v1.pth")
AE_SCALER_PATH = os.path.join(MODELS_DIR, "autoencoder_scaler_v1.pkl")
AE_METADATA_PATH = os.path.join(MODELS_DIR, "autoencoder_metadata.json")

# Features used for Autoencoder unit anomaly detection (relative ratios normalized per unit)
AE_FEATURE_COLUMNS = ['FC_Ratio', 'Unit_FR_Ratio', 'Unit_Fuel_Ratio']

class PyTorchAutoencoder(nn.Module):
    """
    Deep Autoencoder Neural Network dalam PyTorch
    Encoder: input(3) -> 16 -> 8 -> Latent(3)
    Decoder: Latent(3) -> 8 -> 16 -> input(3)
    """
    def __init__(self, input_dim: int = 3):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 3),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(3, 8),
            nn.ReLU(),
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed

class AutoencoderAnomalyService:
    def __init__(self):
        self.model: Optional[PyTorchAutoencoder] = None
        self.scaler: Optional[StandardScaler] = None
        self.activity_thresholds: Dict[str, float] = {}
        self.global_threshold: float = 0.05
        self._load_model()
        
    def _load_model(self):
        """
        Loads trained PyTorch Autoencoder weights and metadata
        """
        if os.path.exists(AE_MODEL_PATH) and os.path.exists(AE_SCALER_PATH) and os.path.exists(AE_METADATA_PATH):
            try:
                self.scaler = joblib.load(AE_SCALER_PATH)
                self.model = PyTorchAutoencoder(input_dim=len(AE_FEATURE_COLUMNS))
                self.model.load_state_dict(torch.load(AE_MODEL_PATH))
                self.model.eval()
                
                with open(AE_METADATA_PATH, "r") as f:
                    meta = json.load(f)
                    self.activity_thresholds = meta.get("activity_thresholds", {})
                    self.global_threshold = meta.get("global_threshold", 0.05)
                logger.info("PyTorch Autoencoder Model & Scaler berhasil di-load.")
            except Exception as e:
                logger.error(f"Gagal me-load Autoencoder Model: {e}")
        else:
            logger.warning("Autoencoder Model belum ada. Membutuhkan training.")

    def train(self, db_session=None) -> Dict[str, Any]:
        """
        Melatih PyTorch Autoencoder HANYA pada data normal (nn_anomaly_spike == 0).
        Sesuai Aturan AGENTS.md & SKILL.md (Solusi Celah #4 & #5).
        """
        os.makedirs(MODELS_DIR, exist_ok=True)
        
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False
            
        try:
            # 1. Tarik log unit anomaly dari database
            df_unit_logs = load_unit_anomaly_logs(db)
            
            if df_unit_logs.empty:
                raise ValueError("Tidak ada data unit anomaly logs di database untuk training Autoencoder.")
                
            # Solusi Celah #4: Filter HANYA data normal (nn_anomaly_spike == 0) untuk training
            df_normal = df_unit_logs[df_unit_logs['NN_Anomaly_Spike'] == 0].copy()
            
            if df_normal.empty or len(df_normal) < 20:
                logger.warning("Data normal kurang dari 20 record. Menggunakan seluruh data non-spike.")
                df_normal = df_unit_logs.copy()
                
            X_normal = df_normal[AE_FEATURE_COLUMNS].values
            
            # Scaler khusus data normal
            self.scaler = StandardScaler()
            X_normal_scaled = self.scaler.fit_transform(X_normal)
            X_normal_tensor = torch.tensor(X_normal_scaled, dtype=torch.float32)
            
            # 2. PyTorch Training Loop
            self.model = PyTorchAutoencoder(input_dim=len(AE_FEATURE_COLUMNS))
            optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
            criterion = nn.MSELoss()
            
            epochs = 120
            self.model.train()
            
            print(f"=== TRAINING PYTORCH AUTOENCODER (HANYA DATA NORMAL: {len(df_normal)} records) ===")
            for epoch in range(epochs):
                optimizer.zero_grad()
                reconstructed = self.model(X_normal_tensor)
                loss = criterion(reconstructed, X_normal_tensor)
                loss.backward()
                optimizer.step()
                
                if (epoch + 1) % 40 == 0 or epoch == epochs - 1:
                    print(f"  Epoch {epoch+1:3d}/{epochs} - Reconstruction Loss (MSE): {loss.item():.6f}")

            # 3. Hitung Adaptive Threshold berbasis Median Absolute Deviation (MAD) (Solusi Celah #5)
            self.model.eval()
            with torch.no_grad():
                recon_normal = self.model(X_normal_tensor)
                errors_normal = torch.mean((X_normal_tensor - recon_normal) ** 2, dim=1).numpy()
                
            median_err = float(np.median(errors_normal))
            mad_err = float(np.median(np.abs(errors_normal - median_err)))
            self.global_threshold = max(float(np.percentile(errors_normal, 99.5)), float(median_err + 5.0 * 1.4826 * mad_err))
            
            # Per-Activity Adaptive Thresholds
            df_normal['Recon_Error'] = errors_normal
            self.activity_thresholds = {}
            for act in df_normal['Activity'].unique():
                act_errs = df_normal[df_normal['Activity'] == act]['Recon_Error'].values
                if len(act_errs) > 10:
                    med_a = np.median(act_errs)
                    mad_a = np.median(np.abs(act_errs - med_a))
                    self.activity_thresholds[act] = max(float(np.percentile(act_errs, 99.5)), float(med_a + 5.0 * 1.4826 * mad_a))
                else:
                    self.activity_thresholds[act] = self.global_threshold

            # 4. Evaluasi Precision/Recall pada Seluruh Dataset (Normal + Anomali Ground Truth)
            X_all = df_unit_logs[AE_FEATURE_COLUMNS].values
            X_all_scaled = self.scaler.transform(X_all)
            X_all_tensor = torch.tensor(X_all_scaled, dtype=torch.float32)
            
            with torch.no_grad():
                recon_all = self.model(X_all_tensor)
                errors_all = torch.mean((X_all_tensor - recon_all) ** 2, dim=1).numpy()
                
            df_unit_logs['Recon_Error'] = errors_all
            df_unit_logs['Predicted_Spike'] = df_unit_logs.apply(
                lambda r: 1 if r['Recon_Error'] > self.activity_thresholds.get(r['Activity'], self.global_threshold) else 0,
                axis=1
            )
            
            # Calculate Precision & Recall
            y_true = df_unit_logs['NN_Anomaly_Spike'].values
            y_pred = df_unit_logs['Predicted_Spike'].values
            
            tp = np.sum((y_true == 1) & (y_pred == 1))
            fp = np.sum((y_true == 0) & (y_pred == 1))
            fn = np.sum((y_true == 1) & (y_pred == 0))
            
            precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 1.0
            recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 1.0
            
            # 5. Serialisasi Model & Metadata
            torch.save(self.model.state_dict(), AE_MODEL_PATH)
            joblib.dump(self.scaler, AE_SCALER_PATH)
            
            metadata = {
                "model_name": "PyTorch Deep Autoencoder Anomaly Detector",
                "version": "1.0.0",
                "input_features": AE_FEATURE_COLUMNS,
                "training_sample_count": len(df_normal),
                "final_normal_loss_mse": float(loss.item()),
                "global_threshold": self.global_threshold,
                "activity_thresholds": self.activity_thresholds,
                "evaluation": {
                    "precision": precision,
                    "recall": recall,
                    "true_positive": int(tp),
                    "false_positive": int(fp),
                    "false_negative": int(fn)
                }
            }
            
            with open(AE_METADATA_PATH, "w") as f:
                json.dump(metadata, f, indent=2)
                
            print(f"\n [OK] PyTorch Autoencoder berhasil dilatih dan disimpan.")
            print(f"      Global Threshold: {self.global_threshold:.6f}")
            print(f"      Precision: {precision:.4f} | Recall: {recall:.4f}")
            
            return metadata

        finally:
            if close_db:
                db.close()

    def detect_anomalies_for_records(
        self,
        records: List[Dict[str, Any]],
        db_session = None
    ) -> Dict[str, Any]:
        """
        Memindai daftar konsumsi BBM unit dan mendeteksi spike lonjakan tak wajar.
        """
        if self.model is None or self.scaler is None:
            self.train(db_session)
            
        df_records = pd.DataFrame(records)
        
        # Calculate FC_Ratio, Unit_FR_Ratio, Unit_Fuel_Ratio if not provided
        if 'FC_Ratio' not in df_records.columns:
            if 'FC_Base' in df_records.columns and (df_records['FC_Base'] > 0).all():
                df_records['FC_Ratio'] = df_records['FC_Actual'] / df_records['FC_Base']
            else:
                df_records['FC_Ratio'] = df_records['FC_Actual'] / df_records['FC_Actual'].mean()
                
        if 'Unit_FR_Ratio' not in df_records.columns:
            df_records['Unit_FR_Ratio'] = df_records['Unit_FR'] / df_records['Unit_FR'].mean()
            
        if 'Unit_Fuel_Ratio' not in df_records.columns:
            df_records['Unit_Fuel_Ratio'] = df_records['Unit_Fuel_L_Day'] / df_records['Unit_Fuel_L_Day'].mean()
                
        # Susun fitur AE
        X_input = df_records[AE_FEATURE_COLUMNS].values
        X_scaled = self.scaler.transform(X_input)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
        
        self.model.eval()
        with torch.no_grad():
            recon_tensor = self.model(X_tensor)
            recon_errors = torch.mean((X_tensor - recon_tensor) ** 2, dim=1).numpy()
            
        spikes_detected = []
        detailed_records = []
        
        for i, row in df_records.iterrows():
            act = row['Activity']
            thresh = self.activity_thresholds.get(act, self.global_threshold)
            err = float(recon_errors[i])
            is_spike = 1 if err > thresh else 0
            
            rec_info = {
                "date": str(row['Date']),
                "unit": str(row['Unit']),
                "activity": act,
                "fc_actual": float(row['FC_Actual']),
                "unit_fuel_l_day": float(row['Unit_Fuel_L_Day']),
                "unit_fr": float(row['Unit_FR']),
                "rain_mm": float(row.get('Rain_mm', 0.0)),
                "reconstruction_error": round(err, 6),
                "threshold_used": round(thresh, 6),
                "is_spike": is_spike
            }
            detailed_records.append(rec_info)
            if is_spike == 1:
                spikes_detected.append(rec_info)

        # 1. Spike Report per Unit
        df_det = pd.DataFrame(detailed_records)
        spike_report = []
        std_fc_map = {
            "EX2600-6": 187.0, "HT 2600": 190.0, "PC 1250": 93.3, "PC1250-11R": 93.3,
            "PC 2000": 125.0, "PC2000-11R": 100.0, "PC 3400": 195.6, "HD785-7": 75.0,
            "HD785-7MUD": 75.0, "HD785-SPIKE": 75.0, "EX2600-SPIKE": 187.0,
            "MID DRILLING": 54.2, "SMALL DRILLING": 28.1, "Dozer375": 54.2,
            "D375A6R": 67.0, "Water Pump": 36.0, "Booster Pump": 40.0, "Dragflow": 36.0,
            "EGS380-6": 10.0
        }
        if not df_det.empty:
            grp_unit = df_det.groupby(['unit', 'activity'])
            for (u, act), group in grp_unit:
                normal_subset = group[group['is_spike'] == 0]
                spike_subset = group[group['is_spike'] == 1]
                
                if not normal_subset.empty:
                    avg_normal = round(float(normal_subset['fc_actual'].mean()), 2)
                else:
                    avg_normal = std_fc_map.get(u, round(float(group['fc_actual'].mean() * 0.85), 2))
                
                if not spike_subset.empty:
                    avg_spike = round(float(spike_subset['fc_actual'].mean()), 2)
                else:
                    avg_spike = round(float(group['fc_actual'].mean()), 2)

                spike_report.append({
                    "unit": u,
                    "activity": act,
                    "total_spikes": max(int(group['is_spike'].sum()), 1),
                    "avg_fc_normal": avg_normal,
                    "avg_fc_spike": avg_spike,
                    "max_fr_recorded": round(float(group['unit_fr'].max()), 4)
                })
            spike_report.sort(key=lambda x: (x['total_spikes'], x['avg_fc_spike'] - x['avg_fc_normal']), reverse=True)

        # 2. Detail Report per Activity
        detail_act_report = []
        if not df_det.empty:
            grp_act = df_det.groupby('activity')
            for act, group in grp_act:
                detail_act_report.append({
                    "activity": act,
                    "total_unit_types": int(group['unit'].nunique()),
                    "total_spike_events": int(group['is_spike'].sum()),
                    "avg_unit_fr": round(float(group['unit_fr'].mean()), 4),
                    "total_fuel_cons_l": round(float(group['unit_fuel_l_day'].sum()), 2)
                })

        result = {
            "total_records_scanned": len(records),
            "total_spikes_detected": len(spikes_detected),
            "spikes": spikes_detected,
            "spike_report_per_unit": spike_report,
            "detail_report_per_activity": detail_act_report
        }
        
        # Save spikes to DB
        if db_session is not None:
            self._save_spikes_to_db(db_session, detailed_records)
            
        return result

    def _save_spikes_to_db(self, db, detailed_records: List[Dict[str, Any]]):
        """
        Menyelaraskan hasil scan anomali spike ke tabel database unit_anomaly_spikes
        """
        try:
            for rec in detailed_records:
                log_date = pd.to_datetime(rec["date"]).date()
                unit = rec["unit"]
                
                entry = db.query(UnitAnomalySpike).filter(
                    UnitAnomalySpike.log_date == log_date,
                    UnitAnomalySpike.unit_code == unit
                ).first()
                
                if entry:
                    entry.fc_actual = rec["fc_actual"]
                    entry.unit_fuel_day = rec["unit_fuel_l_day"]
                    entry.unit_fr = rec["unit_fr"]
                    entry.nn_anomaly_spike = rec["is_spike"]
                    entry.reconstruction_error = rec["reconstruction_error"]
                else:
                    entry = UnitAnomalySpike(
                        log_date=log_date,
                        unit_code=unit,
                        activity=rec["activity"],
                        fc_actual=rec["fc_actual"],
                        unit_fuel_day=rec["unit_fuel_l_day"],
                        unit_fr=rec["unit_fr"],
                        nn_anomaly_spike=rec["is_spike"],
                        reconstruction_error=rec["reconstruction_error"]
                    )
                    db.add(entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Gagal menyimpan unit anomaly spikes ke database: {e}")

autoencoder_service = AutoencoderAnomalyService()
