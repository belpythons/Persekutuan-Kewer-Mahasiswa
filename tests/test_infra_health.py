import requests
import pytest
import redis

def test_redis_connection():
    r = redis.Redis(host='localhost', port=6379, db=0)
    assert r.ping() is True

def test_minio_health():
    response = requests.get("http://localhost:9000/minio/health/live")
    assert response.status_code == 200
