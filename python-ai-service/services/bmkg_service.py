import os
import sys
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models_db import WeatherDailyLog

logger = logging.getLogger(__name__)

# Koordinat & Wilayah Tambang KIDECO Batu Kajang, Kabupaten Paser, Kalimantan Timur
KIDECO_PASER_LAT = -1.8700
KIDECO_PASER_LON = 116.0300
BMKG_KALTIM_XML_URL = "https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-KalimantanTimur.xml"
OPEN_METEO_FALLBACK_URL = f"https://api.open-meteo.com/v1/forecast?latitude={KIDECO_PASER_LAT}&longitude={KIDECO_PASER_LON}&daily=temperature_2m_max,windspeed_10m_max,precipitation_sum&timezone=Asia%2FMakassar"

class BMKGWeatherService:
    """
    Service Integrasi BMKG Real-Time Weather Data untuk Wilayah Tambang KIDECO (Paser, Kaltim).
    Mendukung Auto-Sync BMKG XML Open Data & Open-Meteo Fallback ke database Supabase.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KIDECO-FuelRatio-AIService/1.0 (Mining Operational AI Engine)"
        })

    def sync_bmkg_weather_to_db(self, db_session = None) -> Dict[str, Any]:
        """
        Mengambil data cuaca real-time & 7-hari ke depan dari BMKG (atau Open-Meteo fallback),
        lalu melakukan upsert ke tabel weather_daily_logs di Supabase.
        """
        if db_session is None:
            db = SessionLocal()
            close_db = True
        else:
            db = db_session
            close_db = False

        try:
            weather_records = self._fetch_bmkg_or_fallback()
            synced_count = 0

            for rec in weather_records:
                log_date = pd.to_datetime(rec["date"]).date()
                entry = db.query(WeatherDailyLog).filter(WeatherDailyLog.log_date == log_date).first()

                if entry:
                    entry.curah_hujan_mm = float(rec["curah_hujan_mm"])
                    entry.temp_max_c = float(rec["temp_max_c"])
                    entry.kecepatan_angin_kmh = float(rec["kecepatan_angin_kmh"])
                else:
                    entry = WeatherDailyLog(
                        log_date=log_date,
                        curah_hujan_mm=float(rec["curah_hujan_mm"]),
                        temp_max_c=float(rec["temp_max_c"]),
                        kecepatan_angin_kmh=float(rec["kecepatan_angin_kmh"])
                    )
                    db.add(entry)
                synced_count += 1

            db.commit()
            logger.info(f"Berhasil menyinkronkan {synced_count} hari data cuaca BMKG/Live ke Supabase DB.")

            return {
                "status": "success",
                "source": weather_records[0].get("source", "BMKG_API") if weather_records else "BMKG_API",
                "location": "Paser / Batu Kajang, Kalimantan Timur",
                "records_synced": synced_count,
                "data": weather_records
            }
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            logger.error(f"Gagal menyinkronkan data cuaca BMKG ke database: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
        finally:
            if close_db and 'db' in locals():
                db.close()

    def _fetch_bmkg_or_fallback(self) -> List[Dict[str, Any]]:
        """
        Tarik data dari BMKG XML. Jika BMKG offline / maintenance, gunakan Open-Meteo API fallback.
        """
        try:
            logger.info("Menghubungi BMKG MEWS API (DigitalForecast Kalimantan Timur)...")
            res = self.session.get(BMKG_KALTIM_XML_URL, timeout=8)
            if res.status_code == 200:
                parsed_bmkg = self._parse_bmkg_xml(res.content)
                if parsed_bmkg:
                    return parsed_bmkg
        except Exception as e:
            logger.warning(f"Koneksi ke BMKG XML Gagal/Timeout ({e}). Mengalihkan ke Open-Meteo Live API Fallback...")

        return self._fetch_open_meteo_fallback()

    def _parse_bmkg_xml(self, xml_content: bytes) -> List[Dict[str, Any]]:
        """
        Parsing XML BMKG untuk area Paser / Batu Kajang.
        """
        try:
            root = ET.fromstring(xml_content)
            results_by_date = {}

            # Cari area Paser
            for area in root.findall(".//area"):
                description = area.get("description", "").lower()
                name = area.find("name")
                area_name = name.text.lower() if name is not None and name.text else ""

                if "paser" in description or "paser" in area_name or "batu kajang" in description:
                    # Parse Parameter Suhu (t), Angin (ws), Hujan (weather)
                    temp_max = 32.0
                    wind_speed = 12.0
                    rain_mm = 0.0

                    # Parse Temperature
                    t_param = area.find("./parameter[@id='tmax']")
                    if t_param is not None:
                        val = t_param.find(".//value")
                        if val is not None and val.text:
                            temp_max = float(val.text)

                    # Parse Wind Speed
                    ws_param = area.find("./parameter[@id='ws']")
                    if ws_param is not None:
                        val = ws_param.find(".//value[@unit='Kmh']")
                        if val is not None and val.text:
                            wind_speed = float(val.text)

                    # Parse Weather Code (Rain estimation)
                    weather_param = area.find("./parameter[@id='weather']")
                    if weather_param is not None:
                        val = weather_param.find(".//value")
                        if val is not None and val.text:
                            w_code = int(val.text)
                            # BMKG Weather Code: 60=Hujan Ringan, 61=Hujan Sedang, 63=Hujan Lebat, 95=Hujan Petir
                            if w_code in [60, 61]:
                                rain_mm = 8.5
                            elif w_code in [63, 95]:
                                rain_mm = 25.0
                            elif w_code in [97]:
                                rain_mm = 55.0

                    today_str = date.today().strftime("%Y-%m-%d")
                    return [{
                        "date": today_str,
                        "curah_hujan_mm": rain_mm,
                        "temp_max_c": temp_max,
                        "kecepatan_angin_kmh": wind_speed,
                        "source": "BMKG_OFFICIAL_XML"
                    }]
            return []
        except Exception as e:
            logger.warning(f"Gagal parse XML BMKG: {e}")
            return []

    def _fetch_open_meteo_fallback(self) -> List[Dict[str, Any]]:
        """
        Fallback Provider: Open-Meteo High-Resolution Live Forecast API (Batu Kajang - Paser).
        """
        try:
            logger.info("Mengambil prakiraan cuaca 7-hari Paser dari Open-Meteo Provider...")
            res = self.session.get(OPEN_METEO_FALLBACK_URL, timeout=8)
            if res.status_code == 200:
                data = res.json()
                daily = data.get("daily", {})
                dates = daily.get("time", [])
                t_max = daily.get("temperature_2m_max", [])
                wind_max = daily.get("windspeed_10m_max", [])
                precip = daily.get("precipitation_sum", [])

                records = []
                for i in range(len(dates)):
                    records.append({
                        "date": dates[i],
                        "curah_hujan_mm": float(precip[i] if i < len(precip) and precip[i] is not None else 0.0),
                        "temp_max_c": float(t_max[i] if i < len(t_max) and t_max[i] is not None else 32.0),
                        "kecepatan_angin_kmh": float(wind_max[i] if i < len(wind_max) and wind_max[i] is not None else 12.0),
                        "source": "OPEN_METEO_PASER_LIVE"
                    })
                return records
        except Exception as e:
            logger.error(f"Fallback Open-Meteo juga gagal: {e}")

        # Static Safety Fallback jika internet mati total
        today = date.today()
        return [{
            "date": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
            "curah_hujan_mm": 5.0,
            "temp_max_c": 32.0,
            "kecepatan_angin_kmh": 12.0,
            "source": "OFFLINE_SAFETY_DEFAULT"
        } for i in range(7)]

bmkg_service = BMKGWeatherService()
