import json
import logging
import hashlib
import time
from typing import Any, Dict, Optional, List, Union
from contextlib import contextmanager

try:
    import redis
    from redis.exceptions import ConnectionError, TimeoutError, RedisError
except ImportError:
    redis = None
    ConnectionError = TimeoutError = RedisError = Exception

from config import settings

logger = logging.getLogger(__name__)

# Key Prefixes
PREFIX_FORECAST_1D = "kideco:forecast:1d"
PREFIX_FORECAST_7D = "kideco:forecast:7d"
PREFIX_LAG_FEATURES = "kideco:features:lags"
PREFIX_CAPACITY = "kideco:capacity"
PREFIX_GLOBAL_TUNING = "kideco:capacity:global_tuning"
PREFIX_CHATBOT_CONTEXT = "kideco:context:chatbot_latest"
PREFIX_LOCK = "kideco:lock"

class RedisCacheService:
    """
    Redis Cache & Low-Latency Feature Store Service untuk KIDECO Fuel Ratio AI Service.
    Mendukung Connection Pooling, JSON Serialization, Domain Caching Helpers,
    dan Graceful Degradation (Fallback transparan saat Redis offline).
    """

    def __init__(self, custom_client=None):
        self._custom_client = custom_client
        self._client: Optional[Any] = None
        self._pool: Optional[Any] = None
        self._is_connected: bool = False
        self._last_connect_attempt: float = 0.0
        self._connect_retry_interval: float = 10.0  # Retry connect every 10s if down
        
        if custom_client is not None:
            self._client = custom_client
            self._is_connected = True
        else:
            self._init_client()

    def _init_client(self):
        """
        Inisialisasi Redis Connection Pool dengan parameter dari config.
        """
        if not settings.REDIS_ENABLED or redis is None:
            logger.info("Redis Caching dinonaktifkan atau modul redis tidak terinstall.")
            self._client = None
            self._is_connected = False
            return

        try:
            self._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                db=settings.REDIS_DB,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT,
                decode_responses=True,
                max_connections=20
            )
            self._client = redis.Redis(connection_pool=self._pool)
            # Test ping
            self._client.ping()
            self._is_connected = True
            logger.info(f"Terhubung ke Redis Server: {settings.REDIS_HOST}:{settings.REDIS_PORT} (DB {settings.REDIS_DB})")
        except Exception as e:
            self._is_connected = False
            logger.warning(f"Tidak dapat terhubung ke Redis Server ({e}). Menggunakan Fallback No-Cache.")

    @property
    def client(self) -> Optional[Any]:
        if self._custom_client is not None:
            return self._custom_client

        if not settings.REDIS_ENABLED or redis is None:
            return None

        # Reconnect attempt throttled
        now = time.time()
        if not self._is_connected and (now - self._last_connect_attempt > self._connect_retry_interval):
            self._last_connect_attempt = now
            self._init_client()

        return self._client if self._is_connected else None

    def check_connection(self) -> Dict[str, Any]:
        """
        Memeriksa status koneksi Redis untuk Health Check API.
        """
        if not settings.REDIS_ENABLED:
            return {
                "status": "disabled",
                "message": "Redis cache is disabled via REDIS_ENABLED=False"
            }

        client = self.client
        if client is None:
            return {
                "status": "disconnected_fallback",
                "host": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                "message": "Redis offline, microservice berjalan normal dengan Direct DB/In-Memory Fallback"
            }

        try:
            start_t = time.perf_counter()
            client.ping()
            latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
            
            info = {}
            try:
                raw_info = client.info()
                info = {
                    "redis_version": raw_info.get("redis_version", "unknown"),
                    "used_memory_human": raw_info.get("used_memory_human", "unknown"),
                    "connected_clients": raw_info.get("connected_clients", 1)
                }
            except Exception:
                pass

            return {
                "status": "connected",
                "host": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                "db": settings.REDIS_DB,
                "latency_ms": latency_ms,
                **info
            }
        except Exception as e:
            self._is_connected = False
            return {
                "status": "disconnected_fallback",
                "host": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                "error": str(e)
            }

    # ─── GENERIC CACHE OPERATIONS ──────────────────────────────────────────

    def get_json(self, key: str) -> Optional[Any]:
        """
        Mengambil value dari Redis dan me-deserialize dari JSON.
        Mengembalikan None jika key tidak ada atau Redis offline.
        """
        client = self.client
        if client is None:
            return None

        try:
            val = client.get(key)
            if val is not None:
                return json.loads(val)
        except Exception as e:
            logger.debug(f"Redis get_json error for key {key}: {e}")
        return None

    def set_json(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> bool:
        """
        Menyimpan objek serializable ke Redis dalam format JSON string dengan optional TTL.
        """
        client = self.client
        if client is None:
            return False

        try:
            serialized = json.dumps(data)
            if ttl_seconds and ttl_seconds > 0:
                client.setex(name=key, time=ttl_seconds, value=serialized)
            else:
                client.set(name=key, value=serialized)
            return True
        except Exception as e:
            logger.debug(f"Redis set_json error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Menghapus single key dari Redis.
        """
        client = self.client
        if client is None:
            return False

        try:
            client.delete(key)
            return True
        except Exception as e:
            logger.debug(f"Redis delete error for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Menghapus semua keys yang cocok dengan pola pattern (contoh: 'kideco:forecast:*').
        """
        client = self.client
        if client is None:
            return 0

        try:
            keys = client.keys(pattern)
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.debug(f"Redis delete_pattern error for pattern {pattern}: {e}")
            return 0

    # ─── DOMAIN SPECIFIC HELPERS ────────────────────────────────────────────

    @staticmethod
    def generate_hash(payload: Dict[str, Any]) -> str:
        """
        Menghasilkan MD5 hash yang konsisten dari dictionary payload input.
        """
        normalized_str = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.md5(normalized_str.encode('utf-8')).hexdigest()[:12]

    # 1. Feature Lag Cache Helpers
    def get_lag_features_cache(self, date_str: str) -> Optional[Dict[str, Any]]:
        key = f"{PREFIX_LAG_FEATURES}:{date_str}"
        return self.get_json(key)

    def set_lag_features_cache(self, date_str: str, lag_data: Dict[str, Any], ttl_seconds: int = 86400) -> bool:
        key = f"{PREFIX_LAG_FEATURES}:{date_str}"
        return self.set_json(key, lag_data, ttl_seconds=ttl_seconds)

    # 2. Forecast Cache Helpers
    def get_forecast_cache(self, date_str: str, params_hash: str) -> Optional[Dict[str, Any]]:
        key = f"{PREFIX_FORECAST_1D}:{date_str}:{params_hash}"
        return self.get_json(key)

    def set_forecast_cache(self, date_str: str, params_hash: str, result: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        key = f"{PREFIX_FORECAST_1D}:{date_str}:{params_hash}"
        return self.set_json(key, result, ttl_seconds=ttl_seconds)

    def get_forecast_7days_cache(self, start_date_str: str) -> Optional[Dict[str, Any]]:
        key = f"{PREFIX_FORECAST_7D}:{start_date_str}"
        return self.get_json(key)

    def set_forecast_7days_cache(self, start_date_str: str, result: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        key = f"{PREFIX_FORECAST_7D}:{start_date_str}"
        return self.set_json(key, result, ttl_seconds=ttl_seconds)

    # 3. Capacity Cache Helpers
    def get_capacity_cache(self, date_str: str, params_hash: str) -> Optional[Dict[str, Any]]:
        key = f"{PREFIX_CAPACITY}:{date_str}:{params_hash}"
        return self.get_json(key)

    def set_capacity_cache(self, date_str: str, params_hash: str, result: Dict[str, Any], ttl_seconds: int = 1800) -> bool:
        key = f"{PREFIX_CAPACITY}:{date_str}:{params_hash}"
        return self.set_json(key, result, ttl_seconds=ttl_seconds)

    def get_global_tuning_cache(self, date_str: str, params_hash: str) -> Optional[Dict[str, Any]]:
        key = f"{PREFIX_GLOBAL_TUNING}:{date_str}:{params_hash}"
        return self.get_json(key)

    def set_global_tuning_cache(self, date_str: str, params_hash: str, result: Dict[str, Any], ttl_seconds: int = 1800) -> bool:
        key = f"{PREFIX_GLOBAL_TUNING}:{date_str}:{params_hash}"
        return self.set_json(key, result, ttl_seconds=ttl_seconds)

    # 4. Chatbot Context Cache Helpers
    def get_chatbot_context_cache(self) -> Optional[Dict[str, Any]]:
        return self.get_json(PREFIX_CHATBOT_CONTEXT)

    def set_chatbot_context_cache(self, context: Dict[str, Any], ttl_seconds: int = 60) -> bool:
        return self.set_json(PREFIX_CHATBOT_CONTEXT, context, ttl_seconds=ttl_seconds)

    # 5. Distributed Mutex Lock Context Manager
    @contextmanager
    def acquire_lock(self, lock_name: str, timeout_seconds: int = 60):
        """
        Distributed lock berbasis Redis SETNX.
        Jika Redis offline, langsung yield (graceful bypass lock).
        """
        client = self.client
        lock_key = f"{PREFIX_LOCK}:{lock_name}"
        acquired = False

        if client is not None:
            try:
                # SET key val NX EX timeout
                val = f"locked_at_{time.time()}"
                acquired = bool(client.set(lock_key, val, nx=True, ex=timeout_seconds))
            except Exception as e:
                logger.debug(f"Gagal memperoleh Redis Lock ({e}). Mengabaikan lock.")
                acquired = True

        try:
            yield acquired
        finally:
            if acquired and client is not None:
                try:
                    client.delete(lock_key)
                except Exception:
                    pass

redis_cache_service = RedisCacheService()
