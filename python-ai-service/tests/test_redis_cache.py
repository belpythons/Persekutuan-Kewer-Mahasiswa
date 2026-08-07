import pytest
import fakeredis
from fastapi.testclient import TestClient

from main import app
from services.redis_cache import RedisCacheService, redis_cache_service
from services.forecasting import forecasting_service
from services.capacity_engine import capacity_engine

client = TestClient(app)

@pytest.fixture
def fake_redis_service():
    """
    Fixture yang menyediakan instance RedisCacheService dengan FakeRedis backend
    """
    fake_client = fakeredis.FakeRedis(decode_responses=True)
    service = RedisCacheService(custom_client=fake_client)
    return service

def test_redis_generic_get_set_delete(fake_redis_service):
    """
    Menguji fungsionalitas JSON get, set, delete, dan delete_pattern pada Redis service
    """
    test_key = "kideco:test:key1"
    test_data = {"date": "2026-08-08", "forecast_fr": 1.0185, "status": "NORMAL"}
    
    # 1. Set JSON
    assert fake_redis_service.set_json(test_key, test_data, ttl_seconds=60) is True
    
    # 2. Get JSON
    cached = fake_redis_service.get_json(test_key)
    assert cached is not None
    assert cached["forecast_fr"] == 1.0185
    assert cached["status"] == "NORMAL"
    
    # 3. Delete
    assert fake_redis_service.delete(test_key) is True
    assert fake_redis_service.get_json(test_key) is None

def test_redis_graceful_fallback_when_offline():
    """
    Menguji Graceful Degradation: Ketika Redis offline (client None), fungsi get/set/lock
    harus mengembalikan None/False/yield tanpa melempar Exception atau HTTP 500 error.
    """
    # Service dengan client None yang merepresentasikan kondisi Redis Server offline
    offline_service = RedisCacheService()
    offline_service._client = None
    offline_service._is_connected = False
    offline_service._custom_client = None

    # Operasi dasar tidak boleh melempar error
    assert offline_service.get_json("any_key") is None
    assert offline_service.set_json("any_key", {"data": 123}) is False
    assert offline_service.delete("any_key") is False
    assert offline_service.delete_pattern("kideco:*") == 0
    assert offline_service.get_forecast_cache("2026-08-08", "abc") is None
    assert offline_service.get_lag_features_cache("2026-08-08") is None
    assert offline_service.get_chatbot_context_cache() is None

    # Distributed lock fallback
    with offline_service.acquire_lock("training_job") as acquired:
        assert isinstance(acquired, bool)

    # Health check reporting
    health = offline_service.check_connection()
    assert health["status"] in ["disconnected_fallback", "disabled", "connected"]

def test_redis_feature_lag_caching(fake_redis_service):
    """
    Menguji penyimpanan dan pembacaan autoregressive feature lags pada Redis Feature Store
    """
    date_str = "2026-08-08"
    lags = {
        "rain_lag1": 4.5,
        "rain_lag2": 0.0,
        "fr_lag1": 1.025,
        "fr_lag2": 1.018,
        "rolling_avg_fr_7d": 1.021
    }
    
    # Save to cache
    success = fake_redis_service.set_lag_features_cache(date_str, lags, ttl_seconds=3600)
    assert success is True
    
    # Read from cache
    fetched = fake_redis_service.get_lag_features_cache(date_str)
    assert fetched is not None
    assert fetched["rain_lag1"] == 4.5
    assert fetched["rolling_avg_fr_7d"] == 1.021

def test_redis_forecast_result_caching(fake_redis_service):
    """
    Menguji caching hasil inferensi XGBoost single forecast & 7-day horizon
    """
    date_str = "2026-08-08"
    params_hash = "test_hash_123"
    forecast_result = {
        "log_date": date_str,
        "forecast_fr": 1.0192,
        "status": "NORMAL",
        "cached": False
    }
    
    # Single Forecast
    assert fake_redis_service.set_forecast_cache(date_str, params_hash, forecast_result) is True
    cached_res = fake_redis_service.get_forecast_cache(date_str, params_hash)
    assert cached_res is not None
    assert cached_res["forecast_fr"] == 1.0192

    # 7-Day Horizon Forecast
    horizon_result = {
        "start_date": date_str,
        "forecast_horizon_days": 7,
        "summary": {"avg_forecast_fr": 1.021}
    }
    assert fake_redis_service.set_forecast_7days_cache(date_str, horizon_result) is True
    cached_horizon = fake_redis_service.get_forecast_7days_cache(date_str)
    assert cached_horizon is not None
    assert cached_horizon["summary"]["avg_forecast_fr"] == 1.021

def test_redis_capacity_caching(fake_redis_service):
    """
    Menguji caching hasil Combined Capacity & Global Tuning
    """
    date_str = "2026-08-08"
    params_hash = "cap_hash_456"
    cap_result = {
        "log_date": date_str,
        "operating_units": 33,
        "total_combined_fuel_lday": 24097.4,
        "cached": False
    }
    
    assert fake_redis_service.set_capacity_cache(date_str, params_hash, cap_result) is True
    cached_cap = fake_redis_service.get_capacity_cache(date_str, params_hash)
    assert cached_cap is not None
    assert cached_cap["operating_units"] == 33

def test_redis_chatbot_context_caching(fake_redis_service):
    """
    Menguji caching Database Context untuk Mining Chatbot
    """
    context_data = {
        "forecast_fr": 1.0180,
        "curah_hujan_mm": 5.2,
        "operating_units": 33
    }
    
    assert fake_redis_service.set_chatbot_context_cache(context_data, ttl_seconds=60) is True
    cached_ctx = fake_redis_service.get_chatbot_context_cache()
    assert cached_ctx is not None
    assert cached_ctx["forecast_fr"] == 1.0180
    assert cached_ctx["curah_hujan_mm"] == 5.2

def test_redis_mutex_lock(fake_redis_service):
    """
    Menguji Redis distributed lock acquisition & release
    """
    lock_name = "test_model_train"
    
    with fake_redis_service.acquire_lock(lock_name, timeout_seconds=10) as acquired:
        assert acquired is True
        
        # Second attempt should fail while lock is held
        client = fake_redis_service.client
        assert client.get(f"kideco:lock:{lock_name}") is not None

    # Lock must be released after context exit
    assert fake_redis_service.client.get(f"kideco:lock:{lock_name}") is None

def test_health_check_endpoint_redis_integration():
    """
    Menguji endpoint /health FastAPI mengembalikan struktur redis status dengan benar
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data
    assert "status" in data["redis"]
