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
