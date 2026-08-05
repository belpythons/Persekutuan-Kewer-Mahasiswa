from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import datetime

from database import get_db
from models_db import WeatherDailyLog, DailyForecastLog
from services.forecasting import forecasting_service

router = APIRouter(prefix="/api/v1", tags=["Forecasting Engine"])

class ForecastRequest(BaseModel):
    date: str = Field(..., example="2026-08-05", description="Tanggal operasional (YYYY-MM-DD)")
    curah_hujan_mm: Optional[float] = Field(None, ge=0.0, le=200.0, example=12.5, description="Prakiraan curah hujan (mm) — Opsional (otomatis dari DB jika kosong)")
    temp_max_c: Optional[float] = Field(None, ge=10.0, le=50.0, example=33.5, description="Suhu maksimum (°C) — Opsional")
    kecepatan_angin_kmh: Optional[float] = Field(None, ge=0.0, le=100.0, example=15.0, description="Kecepatan angin (km/h) — Opsional")
    haul_distance_m: Optional[float] = Field(None, ge=500.0, le=15000.0, example=4100.0, description="Jarak angkut (meter) — Opsional")
    daily_prod_bcm: Optional[float] = Field(None, ge=1000.0, le=150000.0, example=42000.0, description="Target produksi harian (BCM) — Opsional")
    rain_lag1: Optional[float] = Field(None, ge=0.0, example=5.0)
    rain_lag2: Optional[float] = Field(None, ge=0.0, example=0.0)
    fr_lag1: Optional[float] = Field(None, ge=0.1, example=1.025)
    fr_lag2: Optional[float] = Field(None, ge=0.1, example=1.015)
    rolling_avg_fr_7d: Optional[float] = Field(None, ge=0.1, example=1.020)

class Forecast7DaysRequest(BaseModel):
    start_date: str = Field(..., example="2026-08-05", description="Tanggal awal forecast 7 hari (YYYY-MM-DD)")

class ForecastResponse(BaseModel):
    log_date: str
    forecast_fr: float
    status: str
    warning_threshold: float
    critical_threshold: float
    daily_prod_bcm: float
    haul_distance_m: float
    features_input: Dict[str, Any]

@router.get("/weather-by-date/{date_str}", status_code=status.HTTP_200_OK)
def get_weather_by_date(date_str: str, db: Session = Depends(get_db)):
    """
    Mengambil data log cuaca dan target operasional otomatis dari database Supabase berdasarkan tanggal.
    """
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        w = db.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == dt).first()
        f = db.query(DailyForecastLog).filter(DailyForecastLog.log_date == dt).first()

        return {
            "log_date": date_str,
            "found_in_db": w is not None or f is not None,
            "curah_hujan_mm": w.curah_hujan_mm if w else 0.0,
            "temp_max_c": w.temp_max_c if w else 32.0,
            "kecepatan_angin_kmh": w.kecepatan_angin_kmh if w else 12.0,
            "haul_distance_m": f.haul_distance_m if f else 3900.0,
            "daily_prod_bcm": f.daily_prod_bcm if f else 40000.0
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/forecast", response_model=ForecastResponse, status_code=status.HTTP_200_OK)
def predict_daily_fuel_ratio(request: ForecastRequest, db: Session = Depends(get_db)):
    """
    Predicts daily Total Fuel Ratio (L/BCM) and evaluates operational alert status (NORMAL, WARNING, CRITICAL).
    Jika variabel cuaca/operasional dikosongkan (None), sistem otomatis mengambil data dari Supabase DB.
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

@router.post("/forecast-7days", status_code=status.HTTP_200_OK)
def predict_7days_horizon_fuel_ratio(request: Forecast7DaysRequest, db: Session = Depends(get_db)):
    """
    Melakukan prediksi Fuel Ratio beruntun selama 7 HARI berturut-turut (Horizon 7-Day Forecasting)
    menggunakan data operasional & autoregressive lag pipeline dari Supabase Database.
    """
    try:
        result = forecasting_service.forecast_7days_horizon(
            start_date_str=request.start_date,
            db_session=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan inferensi 7-day horizon forecasting: {str(e)}"
        )
