from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from database import get_db
from services.forecasting import forecasting_service

router = APIRouter(prefix="/api/v1", tags=["Forecasting Engine"])

class ForecastRequest(BaseModel):
    date: str = Field(..., example="2026-08-05", description="Tanggal operasional (YYYY-MM-DD)")
    curah_hujan_mm: float = Field(0.0, ge=0.0, le=200.0, example=12.5, description="Prakiraan curah hujan (mm)")
    temp_max_c: float = Field(32.0, ge=10.0, le=50.0, example=33.5, description="Suhu maksimum (°C)")
    kecepatan_angin_kmh: float = Field(12.0, ge=0.0, le=100.0, example=15.0, description="Kecepatan angin (km/h)")
    haul_distance_m: float = Field(3900.0, ge=500.0, le=15000.0, example=4100.0, description="Jarak angkut (meter)")
    daily_prod_bcm: float = Field(40000.0, ge=1000.0, le=150000.0, example=42000.0, description="Target produksi harian (BCM)")
    rain_lag1: Optional[float] = Field(0.0, ge=0.0, example=5.0)
    rain_lag2: Optional[float] = Field(0.0, ge=0.0, example=0.0)
    fr_lag1: Optional[float] = Field(1.018, ge=0.1, example=1.025)
    fr_lag2: Optional[float] = Field(1.018, ge=0.1, example=1.015)
    rolling_avg_fr_7d: Optional[float] = Field(1.018, ge=0.1, example=1.020)

class ForecastResponse(BaseModel):
    log_date: str
    forecast_fr: float
    status: str
    warning_threshold: float
    critical_threshold: float
    daily_prod_bcm: float
    haul_distance_m: float
    features_input: Dict[str, Any]

@router.post("/forecast", response_model=ForecastResponse, status_code=status.HTTP_200_OK)
def predict_daily_fuel_ratio(request: ForecastRequest, db: Session = Depends(get_db)):
    """
    Predicts daily Total Fuel Ratio (L/BCM) and evaluates operational alert status (NORMAL, WARNING, CRITICAL)
    using trained XGBoost Regressor and TimeSeriesSplit feature pipeline.
    """
    try:
        result = forecasting_service.forecast_single_day(
            date_str=request.date,
            curah_hujan_mm=request.curah_hujan_mm,
            temp_max_c=request.temp_max_c,
            kecepatan_angin_kmh=request.kecepatan_angin_kmh,
            haul_distance_m=request.haul_distance_m,
            daily_prod_bcm=request.daily_prod_bcm,
            rain_lag1=request.rain_lag1,
            rain_lag2=request.rain_lag2,
            fr_lag1=request.fr_lag1,
            fr_lag2=request.fr_lag2,
            rolling_avg_fr_7d=request.rolling_avg_fr_7d,
            db_session=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan inferensi forecasting: {str(e)}"
        )
