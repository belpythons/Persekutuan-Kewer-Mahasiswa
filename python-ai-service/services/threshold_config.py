"""
Dynamic Fuel Ratio threshold configuration, backed by cfg_system_mlops (generic key/value
system config table). Replaces the hardcoded BASE_TOTAL_FR_BUDGET / +8% / +18% constants
that were duplicated across forecasting.py and three frontend components.

Defaults match the values those constants already had, so existing behavior is unchanged
until someone edits the config through PUT /api/v1/threshold-config.
"""
from sqlalchemy.orm import Session
from models_db import SystemMlopsConfig

DEFAULTS = {
    "fr_budget_baseline": "1.018",
    "fr_warning_pct": "8.0",
    "fr_critical_pct": "18.0",
}


def get_threshold_config(db: Session) -> dict:
    """
    Mengembalikan konfigurasi threshold aktif. Baris yang belum ada di DB di-seed otomatis
    dengan nilai default pada pemanggilan pertama (lazy init, tidak perlu migration terpisah).
    """
    rows = db.query(SystemMlopsConfig).filter(SystemMlopsConfig.config_key.in_(DEFAULTS.keys())).all()
    values = {r.config_key: r.config_value for r in rows}

    missing = {k: v for k, v in DEFAULTS.items() if k not in values}
    for key, value in missing.items():
        db.add(SystemMlopsConfig(config_key=key, config_value=value))
        values[key] = value
    if missing:
        db.commit()

    return {
        "budget_baseline": float(values["fr_budget_baseline"]),
        "warning_pct": float(values["fr_warning_pct"]),
        "critical_pct": float(values["fr_critical_pct"]),
    }


def update_threshold_config(db: Session, budget_baseline: float = None, warning_pct: float = None, critical_pct: float = None) -> dict:
    """
    Memperbarui satu atau lebih nilai konfigurasi. Parameter yang None tidak diubah.
    """
    updates = {}
    if budget_baseline is not None:
        updates["fr_budget_baseline"] = str(budget_baseline)
    if warning_pct is not None:
        updates["fr_warning_pct"] = str(warning_pct)
    if critical_pct is not None:
        updates["fr_critical_pct"] = str(critical_pct)

    get_threshold_config(db)  # ensure rows exist before updating

    for key, value in updates.items():
        row = db.query(SystemMlopsConfig).filter(SystemMlopsConfig.config_key == key).first()
        row.config_value = value

    if updates:
        db.commit()

    return get_threshold_config(db)
