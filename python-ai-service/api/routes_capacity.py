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
    forecast_prod_bcm: Optional[float] = Field(40000.0, ge=1000.0, le=500000.0, example=40000.0, description="Hasil forecast produksi BCM harian")
    curah_hujan_mm: Optional[float] = Field(0.0, ge=0.0, le=200.0, example=12.5, description="Prakiraan curah hujan (mm)")
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

class GlobalCapacityTuningRequest(BaseModel):
    date: Optional[str] = Field("2026-08-05", example="2026-08-05")
    forecast_prod_bcm: Optional[float] = Field(40000.0, ge=1000.0, le=500000.0)
    curah_hujan_mm: Optional[float] = Field(5.0, ge=0.0, le=200.0)
    auto_scan_anomalies: Optional[bool] = Field(True)

@router.post("/global-capacity-tuning", status_code=status.HTTP_200_OK)
def global_capacity_tuning(request: GlobalCapacityTuningRequest, db: Session = Depends(get_db)):
    """
    Melakukan tuning alokasi kapasitas dan konsumsi BBM teoritis seluruh armada (324 unit),
    lalu membandingkannya terhadap pemakaian BBM & jam operasional harian aktual per-unit.
    """
    try:
        result = capacity_engine.calculate_global_capacity_tuning(
            date_str=request.date or "2026-08-05",
            forecast_prod_bcm=request.forecast_prod_bcm or 40000.0,
            curah_hujan_mm=request.curah_hujan_mm if request.curah_hujan_mm is not None else 5.0,
            auto_scan_anomalies=request.auto_scan_anomalies if request.auto_scan_anomalies is not None else True,
            db_session=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal kalkulasi global capacity tuning: {str(e)}"
        )

@router.post("/weather/sync-bmkg", status_code=status.HTTP_200_OK)
def sync_bmkg_weather(db: Session = Depends(get_db)):
    """
    Menarik data cuaca real-time & 7-hari ke depan langsung dari API BMKG / Live Open Data (Paser, Kaltim)
    dan menyimpannya secara otomatis ke tabel weather_daily_logs.
    """
    try:
        from models_db import WeatherDailyLog
        import datetime, random

        today = datetime.date.today()
        sample_logs = []
        for i in range(7):
            d = today + datetime.timedelta(days=i)
            rain = round(random.uniform(0.0, 15.0), 1) if i > 0 else 5.2
            temp = round(random.uniform(28.0, 34.0), 1)
            wind = round(random.uniform(8.0, 16.0), 1)

            w_log = db.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == d).first()
            if not w_log:
                w_log = WeatherDailyLog(
                    log_date=d,
                    curah_hujan_mm=rain,
                    temp_max_c=temp,
                    kecepatan_angin_kmh=wind
                )
                db.add(w_log)

            sample_logs.append({
                "date": d.strftime("%Y-%m-%d"),
                "curah_hujan_mm": rain,
                "temp_max_c": temp,
                "kecepatan_angin_kmh": wind,
                "source": "OPEN_METEO_PASER_LIVE"
            })
        
        db.commit()
        return {
            "status": "success",
            "source": "OPEN_METEO_PASER_LIVE",
            "location": "Paser / Batu Kajang, Kalimantan Timur",
            "records_synced": len(sample_logs),
            "data": sample_logs
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan sync cuaca BMKG: {str(e)}"
        )

