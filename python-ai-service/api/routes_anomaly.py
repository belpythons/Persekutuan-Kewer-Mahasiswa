from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database import get_db
from services.autoencoder import autoencoder_service

router = APIRouter(prefix="/api/v1", tags=["Anomaly Detection Engine"])

class UnitRecordInput(BaseModel):
    Date: str = Field(..., example="2026-08-05", description="Tanggal catatan (YYYY-MM-DD)")
    Unit: str = Field(..., example="HD785-7", description="Kode/Nama Unit Alat")
    Activity: str = Field(..., example="HAULING", description="Kategori Aktivitas (LOADING, HAULING, SUPPORT, DEWATERING)")
    FC_Actual: float = Field(..., ge=0.0, example=78.5, description="Konsumsi BBM Aktual per Jam (L/hr)")
    Unit_Fuel_L_Day: float = Field(..., ge=0.0, example=1570.0, description="Total BBM Harian Unit (L/day)")
    Unit_FR: float = Field(..., ge=0.0, example=0.285, description="Fuel Ratio individual unit (L/BCM)")
    Rain_mm: float = Field(0.0, ge=0.0, example=5.0, description="Curah hujan harian (mm)")

class AnomalyScanRequest(BaseModel):
    records: List[UnitRecordInput]

@router.post("/anomaly-detect", status_code=status.HTTP_200_OK)
def detect_unit_fuel_anomalies(request: AnomalyScanRequest, db: Session = Depends(get_db)):
    """
    Scans unit fuel consumption records and detects uncharacteristic fuel spikes (anomalies)
    using PyTorch Deep Autoencoder trained exclusively on normal baseline operation data.
    """
    if not request.records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Daftar catatan unit (records) tidak boleh kosong."
        )
        
    try:
        raw_records = [r.dict() for r in request.records]
        result = autoencoder_service.detect_anomalies_for_records(raw_records, db_session=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memindai anomali unit: {str(e)}"
        )
