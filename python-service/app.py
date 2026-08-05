import os
import mlflow.sklearn
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.getenv('AI_SERVICE_API_KEY', 'secret-ai-key-2026')
MLFLOW_MODEL_URI = os.getenv('MLFLOW_MODEL_URI', 'runs:/latest/fuel_ratio_model')

# Attempt to load ML model from MLflow
model = None
try:
    if os.getenv('MLFLOW_TRACKING_URI'):
        mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
        model = mlflow.sklearn.load_model(MLFLOW_MODEL_URI)
        print("Successfully loaded ML model from MLflow.")
except Exception as e:
    print(f"MLflow model load failed or offline: {e}. Falling back to formula engine.")

@app.route('/api/v1/predict-fuel-ratio', methods=['POST'])
def predict_fuel_ratio():
    # 1. API Key Validation
    provided_key = request.headers.get('X-API-KEY')
    if provided_key != API_KEY:
        return jsonify({'error': 'Unauthorized: Invalid or missing API Key'}), 401

    data = request.get_json() or {}
    
    equipment_id = data.get('equipment_id')
    operating_hours = data.get('operating_hours')
    fuel_consumed = data.get('fuel_consumed_liters')
    load_tonnage = data.get('load_tonnage')
    
    if not all([equipment_id, operating_hours, fuel_consumed, load_tonnage]) or load_tonnage <= 0 or operating_hours <= 0:
        return jsonify({'error': 'Invalid payload or zero/negative values'}), 400

    # 2. Inference Logic (ML Model vs Fallback Formula)
    if model is not None:
        try:
            prediction = model.predict([[operating_hours, fuel_consumed]])
            calculated_ratio = round(float(prediction[0]), 2)
        except Exception:
            calculated_ratio = round(fuel_consumed / load_tonnage, 2)
    else:
        calculated_ratio = round(fuel_consumed / load_tonnage, 2)
    
    return jsonify({
        'equipment_id': equipment_id,
        'calculated_fuel_ratio': calculated_ratio,
        'status': 'success'
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
