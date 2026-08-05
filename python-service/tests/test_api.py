import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_predict_fuel_ratio_success(client):
    payload = {
        "equipment_id": "EXCA-001",
        "operating_hours": 10.5,
        "fuel_consumed_liters": 250.0,
        "load_tonnage": 100.0
    }
    headers = {"X-API-KEY": "secret-ai-key-2026"}
    response = client.post('/api/v1/predict-fuel-ratio', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json['calculated_fuel_ratio'] == 2.5
    assert response.json['status'] == 'success'
