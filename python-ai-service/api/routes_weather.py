from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database import get_db
from services.bmkg_service import bmkg_service
from models_db import WeatherDailyLog

router = APIRouter(prefix="/api/v1/weather", tags=["BMKG Real-Time Weather Service"])

class BMKGSyncResponse(BaseModel):
    status: str = Field(..., example="success")
    source: str = Field(..., example="BMKG_OFFICIAL_XML")
    location: str = Field(..., example="Paser / Batu Kajang, Kalimantan Timur")
    records_synced: int = Field(..., example=7)
    data: List[Dict[str, Any]]

@router.post("/sync-bmkg", status_code=status.HTTP_200_OK)
def sync_bmkg_weather_data(db: Session = Depends(get_db)):
    """
    Menarik data prakiraan cuaca real-time & 7-hari ke depan langsung dari API BMKG (Paser, Kalimantan Timur),
    lalu menyinkronkannya ke tabel database weather_daily_logs Supabase.
    """
    result = bmkg_service.sync_bmkg_weather_to_db(db_session=db)
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyinkronkan cuaca BMKG: {result.get('message')}"
        )
    return result

@router.get("/latest", status_code=status.HTTP_200_OK)
def get_latest_weather_logs(limit: int = 7, db: Session = Depends(get_db)):
    """
    Mengambil logs data cuaca harian terbaru dari database Supabase.
    """
    logs = db.query(WeatherDailyLog).order_by(WeatherDailyLog.log_date.desc()).limit(limit).all()
    return [
        {
            "log_date": l.log_date.strftime("%Y-%m-%d"),
            "curah_hujan_mm": float(l.curah_hujan_mm),
            "temp_max_c": float(l.temp_max_c),
            "kecepatan_angin_kmh": float(l.kecepatan_angin_kmh)
        }
        for l in logs
    ]
