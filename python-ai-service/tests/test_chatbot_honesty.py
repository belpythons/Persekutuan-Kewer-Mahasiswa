"""
Self-check for routes_chatbot.py's fallback engine (used when GEMINI_API_KEY isn't configured).

Locks in two fixes:
1. anomalous_units_sample is empty when there are genuinely no spikes — not two fabricated
   unit codes ("EX2600-6", "PC2000-11R") presented as if detected.
2. The anomaly-query response never claims a maintenance work order was filed automatically
   (it never was) — it recommends an action instead of asserting one was taken.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes_chatbot import _generate_smart_db_context_response


def _ctx(anomalous_spikes_detected=0, anomalous_units_sample=None, **overrides):
    base = {
        "forecast_fr": 1.02, "actual_fr": 1.02, "forecast_status": "NORMAL",
        "warning_threshold": 1.0994, "critical_threshold": 1.2012,
        "daily_prod_bcm": 40000.0, "haul_distance_m": 3900.0,
        "curah_hujan_mm": 0.0, "temp_max_c": 30.0,
        "installed_prod_bcmhr": 20927.88, "effective_prod_bcmday": 418557.6,
        "fleet_utilization_pct": 10.0, "operating_units": 33, "combined_fuel_lday": 24097.4,
        "anomalous_spikes_detected": anomalous_spikes_detected,
        "anomalous_units_sample": anomalous_units_sample or [],
    }
    base.update(overrides)
    return base


def test_no_fabricated_units_when_zero_spikes_detected():
    response = _generate_smart_db_context_response("ada anomali unit hari ini?", _ctx())
    assert "EX2600-6" not in response
    assert "PC2000-11R" not in response
    assert "0 Unit" in response


def test_no_false_claim_of_automated_work_order():
    # With spikes present, the response may recommend an action...
    with_spikes = _generate_smart_db_context_response(
        "unit mana yang spike?", _ctx(anomalous_spikes_detected=2, anomalous_units_sample=["HD785-7"]))
    assert "otomatis telah diterbitkan" not in with_spikes

    # ...and with none, it must say so plainly instead of recommending action on nothing.
    without_spikes = _generate_smart_db_context_response("unit mana yang spike?", _ctx())
    assert "otomatis telah diterbitkan" not in without_spikes
    assert "Tidak ada spike" in without_spikes


if __name__ == "__main__":
    test_no_fabricated_units_when_zero_spikes_detected()
    test_no_false_claim_of_automated_work_order()
    print("OK: chatbot honesty self-checks passed")
