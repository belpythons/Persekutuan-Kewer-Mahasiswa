from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import datetime

from database import get_db
from models_db import IoTTelemetryLog
from services.iot_capacity_comparator import iot_capacity_comparator

router = APIRouter(prefix="/api/v1/iot", tags=["IoT Telemetry & Capacity Anomaly Audit Engine"])

class IoTTelemetryItem(BaseModel):
    unit_code: str = Field(..., example="HD785-7", description="Kode/Nama Unit Alat Heavy Equipment")
    activity: str = Field(..., example="HAULING", description="Aktivitas (LOADING, HAULING, SUPPORT, DEWATERING)")
    hm_operating_hours: float = Field(..., ge=0.0, le=24.0, example=20.0, description="Jam kerja mesin dari sensor Hour Meter IoT")
    fuel_consumed_iot_l: float = Field(..., ge=0.0, example=1500.0, description="Konsumsi BBM harian dari sensor Flowmeter IoT (Liters)")
    actual_payload_bcm: float = Field(0.0, ge=0.0, example=2100.0, description="Muatan BCM aktual dari sensor VIMS IoT")

class IoTBatchTelemetryRequest(BaseModel):
    date: str = Field(..., example="2026-08-05", description="Tanggal operasional (YYYY-MM-DD)")
    telemetry_records: List[IoTTelemetryItem]

class IoTAuditRequest(BaseModel):
    date: str = Field(..., example="2026-08-05", description="Tanggal operasional (YYYY-MM-DD)")

@router.post("/telemetry", status_code=status.HTTP_200_OK)
def ingest_iot_telemetry_batch(request: IoTBatchTelemetryRequest, db: Session = Depends(get_db)):
    """
    Ingestion batch data telemetri mesin IoT (Flowmeter Solar, Hour Meter HM, Payload VIMS)
    ke data master database Supabase.
    """
    try:
        log_date = datetime.datetime.strptime(request.date, "%Y-%m-%d").date()
        saved_count = 0

        for item in request.telemetry_records:
            entry = db.query(IoTTelemetryLog).filter(
                IoTTelemetryLog.log_date == log_date,
                IoTTelemetryLog.unit_code == item.unit_code
            ).first()

            if entry:
                entry.activity = item.activity
                entry.hm_operating_hours = item.hm_operating_hours
                entry.fuel_consumed_iot_l = item.fuel_consumed_iot_l
                entry.actual_payload_bcm = item.actual_payload_bcm
            else:
                entry = IoTTelemetryLog(
                    log_date=log_date,
                    unit_code=item.unit_code,
                    activity=item.activity,
                    hm_operating_hours=item.hm_operating_hours,
                    fuel_consumed_iot_l=item.fuel_consumed_iot_l,
                    actual_payload_bcm=item.actual_payload_bcm
                )
                db.add(entry)
            saved_count += 1

        db.commit()
        return {
            "status": "success",
            "message": f"Berhasil menyimpan {saved_count} records IoT telemetry ke database.",
            "log_date": request.date
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan ingestion data IoT telemetry: {str(e)}"
        )

@router.post("/capacity-anomaly-audit", status_code=status.HTTP_200_OK)
def perform_iot_capacity_anomaly_audit(request: IoTAuditRequest, db: Session = Depends(get_db)):
    """
    Menjalankan audit komparasi anomali:
    Data Telemetri Mesin IoT vs Kapasitas Teoritis Efektif & Derating Cuaca BMKG.
    """
    try:
        result = iot_capacity_comparator.evaluate_iot_capacity_anomalies(
            date_str=request.date,
            db_session=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menjalankan audit anomali IoT vs Kapasitas: {str(e)}"
        )

@router.get("/daily-summary/{date_str}", status_code=status.HTTP_200_OK)
def get_iot_daily_summary(date_str: str, db: Session = Depends(get_db)):
    """
    Mengambil ringkasan data telemetri IoT harian dari database.
    """
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        logs = db.query(IoTTelemetryLog).filter(IoTTelemetryLog.log_date == dt).all()
        return [
            {
                "unit_code": l.unit_code,
                "activity": l.activity,
                "hm_operating_hours": float(l.hm_operating_hours),
                "fuel_consumed_iot_l": float(l.fuel_consumed_iot_l),
                "actual_payload_bcm": float(l.actual_payload_bcm)
            }
            for l in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
