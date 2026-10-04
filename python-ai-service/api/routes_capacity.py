from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database import get_db
from services.capacity_engine import capacity_engine
from models_db import EquipmentCatalog, SupportingUnitBaseline, DewateringUnitBaseline
from services.forecasting import BASE_TOTAL_FR_BUDGET

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

@router.get("/ewh-budget", status_code=status.HTTP_200_OK)
def get_ewh_budget(forecast_prod_bcm: float = 40000.0, db: Session = Depends(get_db)):
    """
    Menghitung Equipment Working Hours (EWH) & alokasi solar harian untuk fleet Support &
    Dewatering, menggabungkan baseline PA/UA (supporting_units_baseline, dewatering_units_baseline)
    dengan daftar model & kuantitas riil (equipment_catalogs). EWH = 24 jam x PA% x UA%, formula
    standar mining availability — bukan tabel hardcoded di frontend.
    """
    def build_sector(activity_label: str, baseline_model):
        baseline = db.query(baseline_model).first()
        if not baseline:
            return None

        daily_ewh_hrs = round(24.0 * (baseline.pa / 100.0) * (baseline.ua / 100.0), 2)

        equipment_rows = db.query(EquipmentCatalog).filter(
            EquipmentCatalog.activity == activity_label,
            EquipmentCatalog.qty > 0,
        ).order_by(EquipmentCatalog.unit_name).all()

        equipment = []
        total_daily_fuel = 0.0
        for eq in equipment_rows:
            daily_fuel = eq.qty * eq.fc_lhr * daily_ewh_hrs
            annual_ewh = round(daily_ewh_hrs * 365, 1)
            fr_burden_l_bcm = round(daily_fuel / forecast_prod_bcm, 4) if forecast_prod_bcm > 0 else 0.0
            total_daily_fuel += daily_fuel
            equipment.append({
                "equipment_model": eq.unit_name,
                "active_qty": eq.qty,
                "fc_rate_l_hr": round(eq.fc_lhr, 2),
                "daily_ewh_hrs": daily_ewh_hrs,
                "annual_budgeted_ewh": annual_ewh,
                "daily_fuel_allocation_liters": round(daily_fuel, 1),
                "annual_fuel_budget_liters": round(daily_fuel * 365, 1),
                "fr_burden_l_bcm": fr_burden_l_bcm,
                "fr_burden_pct": round((fr_burden_l_bcm / BASE_TOTAL_FR_BUDGET) * 100, 2) if BASE_TOTAL_FR_BUDGET else 0.0,
            })

        total_fr_burden_l_bcm = round(total_daily_fuel / forecast_prod_bcm, 4) if forecast_prod_bcm > 0 else 0.0

        return {
            "sector": activity_label,
            "baseline_unit_code": baseline.unit_code,
            "pa_pct": baseline.pa,
            "ua_pct": baseline.ua,
            "daily_ewh_hrs": daily_ewh_hrs,
            "total_units": sum(e["active_qty"] for e in equipment),
            "total_daily_fuel_liters": round(total_daily_fuel, 1),
            "total_fr_burden_l_bcm": total_fr_burden_l_bcm,
            "total_fr_burden_pct": round((total_fr_burden_l_bcm / BASE_TOTAL_FR_BUDGET) * 100, 2) if BASE_TOTAL_FR_BUDGET else 0.0,
            "equipment": equipment,
        }

    sectors = [
        s for s in [
            build_sector("SUPPORT", SupportingUnitBaseline),
            build_sector("DEWATERING", DewateringUnitBaseline),
        ] if s is not None
    ]

    return {
        "forecast_prod_bcm": forecast_prod_bcm,
        "sectors": sectors,
    }


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

PASER_LATITUDE = -1.82
PASER_LONGITUDE = 115.89

@router.post("/weather/sync-bmkg", status_code=status.HTTP_200_OK)
def sync_bmkg_weather(db: Session = Depends(get_db)):
    """
    Menarik prakiraan cuaca 7-hari ke depan dari Open-Meteo (sama seperti yang dipakai
    OpenMeteoWeatherCard.vue di frontend) dan menyimpannya ke tabel weather_daily_logs,
    sehingga forecasting_service punya data cuaca riil untuk hari-hari mendatang alih-alih
    harus fallback ke konstanta default.
    """
    import requests
    from models_db import WeatherDailyLog
    import datetime

    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": PASER_LATITUDE,
                "longitude": PASER_LONGITUDE,
                "daily": "precipitation_sum,temperature_2m_max,wind_speed_10m_max",
                "timezone": "Asia/Makassar",
                "forecast_days": 7,
            },
            timeout=10,
        )
        resp.raise_for_status()
        daily = resp.json()["daily"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gagal mengambil prakiraan cuaca dari Open-Meteo: {str(e)}"
        )

    try:
        synced_logs = []
        for i, date_str in enumerate(daily["time"]):
            d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            rain = round(float(daily["precipitation_sum"][i] or 0.0), 1)
            temp = round(float(daily["temperature_2m_max"][i]), 1)
            wind = round(float(daily["wind_speed_10m_max"][i]), 1)

            w_log = db.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == d).first()
            if w_log:
                w_log.curah_hujan_mm = rain
                w_log.temp_max_c = temp
                w_log.kecepatan_angin_kmh = wind
            else:
                db.add(WeatherDailyLog(
                    log_date=d,
                    curah_hujan_mm=rain,
                    temp_max_c=temp,
                    kecepatan_angin_kmh=wind
                ))

            synced_logs.append({
                "date": date_str,
                "curah_hujan_mm": rain,
                "temp_max_c": temp,
                "kecepatan_angin_kmh": wind,
                "source": "OPEN_METEO_FORECAST_API"
            })

        db.commit()
        return {
            "status": "success",
            "source": "OPEN_METEO_FORECAST_API",
            "location": "Paser / Batu Kajang, Kalimantan Timur",
            "records_synced": len(synced_logs),
            "data": synced_logs
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyimpan hasil sync cuaca ke database: {str(e)}"
        )

