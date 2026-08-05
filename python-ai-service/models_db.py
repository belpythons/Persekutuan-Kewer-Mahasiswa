from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from database import Base

class EquipmentCatalog(Base):
    __tablename__ = "equipment_catalogs"

    id = Column(Integer, primary_key=True, index=True)
    unit_name = Column(String(100), nullable=False, unique=True, index=True)
    qty = Column(Integer, nullable=False, default=1)
    activity = Column(String(50), nullable=False, index=True)  # LOADING, HAULING, SUPPORT, DEWATERING
    fc_lhr = Column(Float, nullable=False)  # Fuel Consumption L/hr

class LoadingUnitBaseline(Base):
    __tablename__ = "loading_units_baseline"

    id = Column(Integer, primary_key=True, index=True)
    unit_code = Column(String(100), nullable=False, unique=True, index=True)
    activity = Column(String(50), nullable=False, default="Loading")
    fc_lhr = Column(Float, nullable=False)
    prod_bcmhr = Column(Float, nullable=False)

class HaulingUnitBaseline(Base):
    __tablename__ = "hauling_units_baseline"

    id = Column(Integer, primary_key=True, index=True)
    unit_code = Column(String(100), nullable=False, unique=True, index=True)
    activity = Column(String(50), nullable=False, default="Hauling")
    fc_lhr = Column(Float, nullable=False)
    prod_bcmhr = Column(Float, nullable=False)

class SupportingUnitBaseline(Base):
    __tablename__ = "supporting_units_baseline"

    id = Column(Integer, primary_key=True, index=True)
    unit_code = Column(String(100), nullable=False, unique=True, index=True)
    activity = Column(String(50), nullable=False, default="Supporting")
    pa = Column(Float, nullable=True)  # Physical Availability %
    ua = Column(Float, nullable=True)  # Use of Availability %
    fc_lhr = Column(Float, nullable=False)

class DewateringUnitBaseline(Base):
    __tablename__ = "dewatering_units_baseline"

    id = Column(Integer, primary_key=True, index=True)
    unit_code = Column(String(100), nullable=False, unique=True, index=True)
    activity = Column(String(50), nullable=False, default="Dewatering")
    pa = Column(Float, nullable=True)
    ua = Column(Float, nullable=True)
    fc_lhr = Column(Float, nullable=False)

class WeatherDailyLog(Base):
    __tablename__ = "weather_daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False, unique=True, index=True)
    curah_hujan_mm = Column(Float, nullable=False, default=0.0)
    temp_max_c = Column(Float, nullable=False, default=32.0)
    kecepatan_angin_kmh = Column(Float, nullable=False, default=12.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DailyForecastLog(Base):
    __tablename__ = "daily_forecast_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False, unique=True, index=True)
    actual_fr = Column(Float, nullable=True)
    forecast_fr = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="NORMAL", index=True)  # NORMAL, WARNING, CRITICAL
    warning_threshold = Column(Float, nullable=False)
    critical_threshold = Column(Float, nullable=False)
    daily_prod_bcm = Column(Float, nullable=False)
    haul_distance_m = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_forecast_date_status", "log_date", "status"),
    )

class UnitAnomalySpike(Base):
    __tablename__ = "unit_anomaly_spikes"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False, index=True)
    unit_code = Column(String(100), nullable=False, index=True)
    activity = Column(String(50), nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_catalogs.id", ondelete="SET NULL"), nullable=True, index=True)
    fc_actual = Column(Float, nullable=False)
    unit_fuel_day = Column(Float, nullable=False)
    unit_fr = Column(Float, nullable=False)
    nn_anomaly_spike = Column(Integer, nullable=False, default=0, index=True)  # 0 or 1
    reconstruction_error = Column(Float, nullable=True)

    __table_args__ = (
        Index("idx_unit_anomaly_date_unit", "log_date", "unit_code"),
        Index("idx_unit_anomaly_date_act", "log_date", "activity"),
        Index("idx_unit_anomaly_spike_date", "log_date", "nn_anomaly_spike"),
    )

class CapacityAllocation(Base):
    __tablename__ = "capacity_allocations"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False, unique=True, index=True)
    installed_prod_bcmhr = Column(Float, nullable=False)
    effective_prod_bcmday = Column(Float, nullable=False)
    utilization_pct = Column(Float, nullable=False)
    operating_units = Column(Integer, nullable=False)
    combined_fuel_lday = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CapacityUnitAllocation(Base):
    """
    Rincian Alokasi Kapasitas & BBM Solar Per-Unit & Per-Jam untuk Setiap Aktivitas (3NF Granular)
    """
    __tablename__ = "capacity_unit_allocations"

    id = Column(Integer, primary_key=True, index=True)
    capacity_allocation_id = Column(Integer, ForeignKey("capacity_allocations.id", ondelete="CASCADE"), nullable=False, index=True)
    log_date = Column(Date, nullable=False, index=True)
    unit_name = Column(String(100), nullable=False, index=True)
    activity = Column(String(50), nullable=False, index=True)
    total_qty = Column(Integer, nullable=False)
    operating_units = Column(Integer, nullable=False)
    
    # Rincian Produktivitas Per Jam & Per Hari (BCM)
    prod_bcm_hr_unit = Column(Float, nullable=False)     # BCM/hr per 1 unit
    prod_bcm_hr_total = Column(Float, nullable=False)    # BCM/hr total unit aktif
    prod_bcm_day_total = Column(Float, nullable=False)   # BCM/day efektif (setelah derating hujan)
    
    # Rincian BBM Solar Per Jam & Per Hari (Liter)
    fuel_l_hr_unit = Column(Float, nullable=False)      # Liter/hr per 1 unit (FC Baseline)
    fuel_l_hr_total = Column(Float, nullable=False)     # Liter/hr total unit aktif
    fuel_l_day_total = Column(Float, nullable=False)    # Liter/day total (termasuk buffer spike)
    
    # Fuel Ratio Unit
    unit_fr = Column(Float, nullable=False)             # Fuel Ratio L/BCM
    spike_count_nn = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_cap_unit_date_unit", "log_date", "unit_name"),
        Index("idx_cap_unit_date_act", "log_date", "activity"),
    )
