"""
Self-check for GET /api/v1/ewh-budget.

EWH (Equipment Working Hours) = 24h x PA% x UA%, computed from the real
supporting_units_baseline / dewatering_units_baseline rows and the real
equipment_catalogs qty/fc_lhr — not a hardcoded table of invented equipment models.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models_db import SupportingUnitBaseline, DewateringUnitBaseline, EquipmentCatalog

client = TestClient(app)


def test_ewh_budget_matches_real_db_rows():
    response = client.get("/api/v1/ewh-budget?forecast_prod_bcm=40000")
    assert response.status_code == 200
    data = response.json()

    db = SessionLocal()
    try:
        support_baseline = db.query(SupportingUnitBaseline).first()
        dewatering_baseline = db.query(DewateringUnitBaseline).first()
    finally:
        db.close()

    sectors_by_name = {s["sector"]: s for s in data["sectors"]}

    if support_baseline:
        support = sectors_by_name["SUPPORT"]
        expected_ewh = round(24.0 * (support_baseline.pa / 100.0) * (support_baseline.ua / 100.0), 2)
        assert support["daily_ewh_hrs"] == expected_ewh
        assert support["baseline_unit_code"] == support_baseline.unit_code
        # Every equipment row must come from equipment_catalogs, not an invented list.
        db2 = SessionLocal()
        try:
            real_models = {e.unit_name for e in db2.query(EquipmentCatalog).filter(
                EquipmentCatalog.activity == "SUPPORT", EquipmentCatalog.qty > 0).all()}
        finally:
            db2.close()
        assert {e["equipment_model"] for e in support["equipment"]} == real_models

    if dewatering_baseline:
        dewatering = sectors_by_name["DEWATERING"]
        expected_ewh = round(24.0 * (dewatering_baseline.pa / 100.0) * (dewatering_baseline.ua / 100.0), 2)
        assert dewatering["daily_ewh_hrs"] == expected_ewh


def test_ewh_budget_fuel_math_is_internally_consistent():
    response = client.get("/api/v1/ewh-budget?forecast_prod_bcm=40000")
    data = response.json()
    for sector in data["sectors"]:
        for eq in sector["equipment"]:
            expected_daily_fuel = round(eq["active_qty"] * eq["fc_rate_l_hr"] * eq["daily_ewh_hrs"], 1)
            assert abs(eq["daily_fuel_allocation_liters"] - expected_daily_fuel) < 1.0


if __name__ == "__main__":
    test_ewh_budget_matches_real_db_rows()
    test_ewh_budget_fuel_math_is_internally_consistent()
    print("OK: ewh-budget self-checks passed")
