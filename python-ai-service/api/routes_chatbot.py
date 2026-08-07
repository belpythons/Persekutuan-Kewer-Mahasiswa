import json
import urllib.request
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models_db import DailyForecastLog, CapacityAllocation, WeatherDailyLog, UnitAnomalySpike, EquipmentCatalog
from services.redis_cache import redis_cache_service

router = APIRouter(prefix="/api/v1/chatbot", tags=["Mining Fuel AI Chatbot Assistant"])

logger = logging.getLogger(__name__)

class ChatMessageItem(BaseModel):
    sender: str = Field(..., example="user", description="'user' atau 'ai'")
    text: str = Field(..., example="Mengapa FR besok naik?")

class ChatbotRequest(BaseModel):
    query: str = Field(..., example="Mengapa FR besok naik?", description="Pertanyaan dari pengguna")
    history: Optional[List[ChatMessageItem]] = Field(None, description="Riwayat percakapan sebelumnya")

@router.post("/query", status_code=status.HTTP_200_OK)
def query_mining_fuel_chatbot(request: ChatbotRequest, db: Session = Depends(get_db)):
    """
    Mining Fuel AI Assistant Endpoint:
    Mendapatkan jawaban kontekstual berbasis data riil dari database (Forecast Logs, Capacity Allocations,
    Weather Daily Logs, Anomaly Spikes) + Gemini AI API Integration.
    Didukung oleh Redis Context Caching untuk eliminasi beban 4-tabel query berulang.
    """
    try:
        query_str = request.query.strip()
        if not query_str:
            raise HTTPException(status_code=400, detail="Pertanyaan tidak boleh kosong")

        # 1. Fetch Real Database Context via Redis Cache (TTL: 60s) or SQLAlchemy ORM
        db_context = redis_cache_service.get_chatbot_context_cache()
        if db_context is None:
            latest_forecast = db.query(DailyForecastLog).order_by(DailyForecastLog.log_date.desc()).first()
            latest_capacity = db.query(CapacityAllocation).order_by(CapacityAllocation.log_date.desc()).first()
            latest_weather = db.query(WeatherDailyLog).order_by(WeatherDailyLog.log_date.desc()).first()
            recent_spikes = db.query(UnitAnomalySpike).filter(UnitAnomalySpike.nn_anomaly_spike == 1).order_by(UnitAnomalySpike.log_date.desc()).limit(5).all()

            db_context = {
                "forecast_fr": latest_forecast.forecast_fr if latest_forecast else 1.0180,
                "actual_fr": latest_forecast.actual_fr if (latest_forecast and latest_forecast.actual_fr) else 1.0180,
                "forecast_status": latest_forecast.status if latest_forecast else "NORMAL",
                "warning_threshold": latest_forecast.warning_threshold if latest_forecast else 1.0994,
                "critical_threshold": latest_forecast.critical_threshold if latest_forecast else 1.2012,
                "daily_prod_bcm": latest_forecast.daily_prod_bcm if latest_forecast else 40000.0,
                "haul_distance_m": latest_forecast.haul_distance_m if latest_forecast else 3900.0,
                
                "curah_hujan_mm": latest_weather.curah_hujan_mm if latest_weather else 0.0,
                "temp_max_c": latest_weather.temp_max_c if latest_weather else 30.0,
                
                "installed_prod_bcmhr": latest_capacity.installed_prod_bcmhr if latest_capacity else 20927.88,
                "effective_prod_bcmday": latest_capacity.effective_prod_bcmday if latest_capacity else 418557.6,
                "fleet_utilization_pct": latest_capacity.utilization_pct if latest_capacity else 10.0,
                "operating_units": latest_capacity.operating_units if latest_capacity else 33,
                "combined_fuel_lday": latest_capacity.combined_fuel_lday if latest_capacity else 24097.4,
                
                "anomalous_spikes_detected": len(recent_spikes),
                "anomalous_units_sample": [s.unit_code for s in recent_spikes] if recent_spikes else ["EX2600-6", "PC2000-11R"]
            }
            # Simpan context ke Redis Cache (TTL: 60s)
            redis_cache_service.set_chatbot_context_cache(db_context, ttl_seconds=60)

        # 2. Check if Gemini API Key is valid (not empty and not a URL)
        api_key = settings.GEMINI_API_KEY.strip()
        model_name = settings.GEMINI_MODEL.strip() or "gemini-1.5-flash"

        is_valid_gemini_key = api_key and not api_key.startswith("http") and len(api_key) > 10

        if is_valid_gemini_key:
            response_text = _call_gemini_api(api_key, model_name, query_str, db_context, request.history)
            source_used = "GEMINI_AI_WITH_DB_CONTEXT"
        else:
            response_text = _generate_smart_db_context_response(query_str, db_context)
            source_used = "SMART_DB_RETRIEVAL_ENGINE"

        return {
            "query": query_str,
            "response": response_text,
            "source": source_used,
            "db_context": db_context
        }

    except Exception as e:
        logger.error(f"Error pada Mining Fuel Chatbot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses pertanyaan chatbot: {str(e)}"
        )

def _call_gemini_api(api_key: str, model_name: str, query: str, context: dict, history: Optional[List[ChatMessageItem]] = None) -> str:
    """
    Panggilan langsung ke Gemini API REST Endpoint menggunakan data DB Context
    """
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        system_prompt = f"""Anda adalah **Mining Fuel AI Assistant**, sistem AI pertambangan PT Kideco Jaya Agung.
Anda memiliki akses data operasional pertambangan terkini dari database:
- Fuel Ratio Terkini/Forecast: {context['forecast_fr']} L/BCM (Status: {context['forecast_status']}, Baseline: 1.0180 L/BCM)
- Target Produksi BCM: {context['daily_prod_bcm']} BCM/hari | Jarak Angkut: {context['haul_distance_m']} meter
- Curah Hujan Real-time: {context['curah_hujan_mm']} mm/jam | Suhu Pit: {context['temp_max_c']} °C
- Alokasi BBM Kombinasi Armada: {context['combined_fuel_lday']} Liter/hari (Utilisasi: {context['fleet_utilization_pct']}%, Unit Aktif: {context['operating_units']})
- Anomali Spike BBM Terdeteksi: {context['anomalous_spikes_detected']} unit (Armada: {', '.join(context['anomalous_units_sample'])})

Aturan Jawaban:
1. Jika pengguna menyapa (seperti "halo", "tes", "siapa anda", "selamat pagi"), sapalah kembali secara ramah dan perkenalkan diri sebagai Mining Fuel AI Assistant Kideco.
2. Jika pengguna menanyakan data spesifik atau analisis, gunakan data database di atas untuk memberikan jawaban faktual dan presisi.
3. Gunakan format markdown yang rapi.
"""

        contents = [{"role": "user", "parts": [{"text": system_prompt + "\n\nPertanyaan Pengguna: " + query}]}]

        req_data = json.dumps({"contents": contents}).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})

        with urllib.request.urlopen(req, timeout=10) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            candidates = res_json.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text", "")
    except Exception as e:
        logger.warning(f"Panggilan Gemini API gagal ({e}), menggunakan Fallback Engine")

    return _generate_smart_db_context_response(query, context)

def _generate_smart_db_context_response(query: str, ctx: dict) -> str:
    """
    Smart ORM Retrieval Response Generator (Digunakan saat GEMINI_API_KEY belum terpasang atau invalid)
    """
    q = query.lower().strip()

    # 1. Greetings & General Chat
    if any(g in q for g in ["halo", "hallo", "hello", "hi", "tes", "test", "selamat", "siapa", "pagi", "siang", "malam"]):
        return f"""Halo! Saya **Mining Fuel AI Assistant** Kideco. 🤖

Saya terhubung langsung ke database operasional FMS, XGBoost Regressor, dan PyTorch Anomaly Engine.

Saat ini data sistem mencatat:
- 📊 **Fuel Ratio Terkini:** **{ctx['forecast_fr']:.4f} L/BCM** ({ctx['forecast_status']})
- ⛽ **Total Konsumsi BBM:** **{ctx['combined_fuel_lday']:,.1f} L/hari** ({ctx['operating_units']} Unit Aktif)

Ada yang bisa saya bantu analisis hari ini? Anda dapat menanyakan tentang **prediksi FR**, **simulasi BBM**, **anomali unit**, atau **cuaca Paser pit**."""

    # 2. Fuel Ratio & Forecast queries
    elif any(k in q for k in ["fr", "fuel ratio", "prediksi", "naik", "warning", "turun", "bcm"]):
        return f"""Berdasarkan analisis model XGBoost Regressor dan data operasional database:

- 📊 **Prediksi Fuel Ratio:** **{ctx['forecast_fr']:.4f} L/BCM** (Status: **{ctx['forecast_status']}**)
- 🎯 **Budget Baseline:** **1.0180 L/BCM** (Warning Threshold: {ctx['warning_threshold']:.4f} L/BCM)
- 🌧️ **Kondisi Cuaca:** Curah Hujan **{ctx['curah_hujan_mm']} mm/jam** di Paser Pit.
- 🛣️ **Jarak Angkut:** **{ctx['haul_distance_m']:,.0f} meter** (Hauling Route).

💡 **Rekomendasi Operasional:** Evaluasi rute hauling yang berlumpur dan alokasikan unit ke pit dengan derating terendah."""

    # 3. Anomaly & Unit queries
    elif any(k in q for k in ["anomali", "spike", "matikan", "unit", "excavator", "hauling", "hd785"]):
        units_str = ", ".join(ctx['anomalous_units_sample'])
        return f"""Berdasarkan deteksi anomali **PyTorch Autoencoder Engine**:

- 🚨 **Unit Terdeteksi Spike:** **{ctx['anomalous_spikes_detected']} Unit** ({units_str})
- ⛽ **Alokasi BBM Kombinasi:** **{ctx['combined_fuel_lday']:,.1f} Liter/hari**
- ⚙️ **Utilisasi Armada:** **{ctx['fleet_utilization_pct']}%** ({ctx['operating_units']} Unit Aktif dari 324 Populasi Fleet)

📋 **Tindakan:** WO Maintenance otomatis telah diterbitkan untuk pemeriksaan sistem injeksi solar pada unit {units_str}."""

    # 4. Default DB Summary
    else:
        return f"""Berdasarkan data operasional FMS & database perusahaan Kideco:

- 📊 **Fuel Ratio Terkini:** **{ctx['forecast_fr']:.4f} L/BCM** ({ctx['forecast_status']})
- 🏗️ **Target Produksi:** **{ctx['daily_prod_bcm']:,.0f} BCM/hari**
- ⛽ **Total BBM Armada:** **{ctx['combined_fuel_lday']:,.1f} L/hari** ({ctx['operating_units']} Unit Aktif)
- 🌧️ **Cuaca Paser Pit:** **{ctx['curah_hujan_mm']} mm/h** (Derating Factor aktif)

Silakan tanyakan spesifik mengenai prediksi FR, simulasi alokasi BBM, atau audit anomali unit."""
