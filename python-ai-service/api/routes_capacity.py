from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database import get_db
from services.capacity_engine import capacity_engine

router = APIRouter(prefix="/api/v1", tags=["Capacity Determination Engine"])

class EquipmentInput(BaseModel):
    unit_name: str = Field(..., example="HD785-7", description="Nama/Tipe Alat Heavy Equipment")
    qty: int = Field(..., ge=1, example=205, description="Jumlah populasi unit")
    activity: str = Field(..., example="HAULING", description="Aktivitas (LOADING, HAULING, SUPPORT, DEWATERING)")
    fc_lhr: float = Field(..., ge=0.0, example=75.0, description="Konsumsi BBM standar (L/hr)")
    prod_bcmhr: Optional[float] = Field(0.0, ge=0.0, example=109.56, description="Kapasitas produksi per jam (BCM/hr)")

class CapacityRequest(BaseModel):
    date: str = Field(..., example="2026-08-05", description="Tanggal operasional (YYYY-MM-DD)")
    forecast_prod_bcm: float = Field(40000.0, ge=1000.0, le=150000.0, example=40000.0, description="Hasil forecast produksi BCM harian")
    curah_hujan_mm: float = Field(0.0, ge=0.0, example=12.5, description="Prakiraan curah hujan (mm)")
    equipment_list: Optional[List[EquipmentInput]] = Field(None, description="Daftar armada (Opsional, jika kosong mengambil dari DB)")
    nn_spike_count_by_unit: Optional[Dict[str, int]] = Field(None, example={"HD785-7MUD": 2}, description="Map bobot anomali spike unit hasil Autoencoder")

@router.post("/calculate-capacity", status_code=status.HTTP_200_OK)
def calculate_combined_capacity_allocation(request: CapacityRequest, db: Session = Depends(get_db)):
    """
    Calculates dynamic effective fleet capacity, required operating units, utilization percentage,
    and combined daily fuel allocation by integrating XGBoost Forecast + PyTorch Autoencoder Spikes + Non-linear Rain Derating.
    """
    try:
        eq_list = [e.dict() for e in request.equipment_list] if request.equipment_list else None
        
        result = capacity_engine.calculate_fleet_capacity(
            date_str=request.date,
            forecast_prod_bcm=request.forecast_prod_bcm,
            curah_hujan_mm=request.curah_hujan_mm,
            equipment_list=eq_list,
            nn_spike_count_by_unit=request.nn_spike_count_by_unit,
            db_session=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghitung alokasi kapasitas armada: {str(e)}"
        )

class GlobalTuningRequest(BaseModel):
    date: str = Field(..., example="2026-08-05", description="Tanggal operasional (YYYY-MM-DD)")
    forecast_prod_bcm: Optional[float] = Field(None, example=40000.0, description="Target produksi BCM (Opsional, otomatis dari DB jika kosong)")
    curah_hujan_mm: Optional[float] = Field(None, example=10.0, description="Prakiraan curah hujan mm (Opsional, otomatis dari DB jika kosong)")
    auto_scan_anomalies: bool = Field(True, description="Otomatis menyertakan data spike anomali Autoencoder harian")

@router.post("/global-capacity-tuning", status_code=status.HTTP_200_OK)
def perform_global_capacity_tuning(request: GlobalTuningRequest, db: Session = Depends(get_db)):
    """
    Melakukan Global Tuning & Analisis Variansi Kapasitas & BBM seluruh armada (324 unit)
    pada tanggal operasional tertentu, dibandingkan dengan pemakaian harian aktual per-unit dari database.
    """
    try:
        result = capacity_engine.perform_global_tuning(
            date_str=request.date,
            forecast_prod_bcm=request.forecast_prod_bcm,
            curah_hujan_mm=request.curah_hujan_mm,
            auto_scan_anomalies=request.auto_scan_anomalies,
            db_session=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan global capacity tuning: {str(e)}"
        )

@router.get("/capacity-factual-comparison/{date_str}", status_code=status.HTTP_200_OK)
def get_capacity_factual_comparison_and_tag_anomalies(
    date_str: str,
    auto_tag_training_anomalies: bool = True,
    db: Session = Depends(get_db)
):
    """
    Dynamic GET Endpoint Komparasi Faktual vs Kapasitas Cuaca BMKG:
    Mengambil data unit armada & data faktual riil (termasuk cuaca BMKG) berdasarkan tanggal,
    membandingkannya dengan batas toleransi kapasitas efisiensi cuaca,
    serta otomatis menandai keborosan MURNI TIDAK DIPENGARUHI CUACA sebagai sampel data training anomali.
    """
    try:
        result = capacity_engine.compare_factual_capacity_and_tag_anomalies(
            date_str=date_str,
            auto_tag_training_anomalies=auto_tag_training_anomalies,
            db_session=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses komparasi faktual & tagging sampel training anomali: {str(e)}"
        )
