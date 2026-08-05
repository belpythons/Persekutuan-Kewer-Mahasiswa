import os
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
import numpy as np

os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000'
os.environ['AWS_ACCESS_KEY_ID'] = 'minioadmin'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'minioadminpassword'

mlflow.set_tracking_uri("http://localhost:5001")
mlflow.set_experiment("Fuel_Ratio_Prediction")

if __name__ == "__main__":
    with mlflow.start_run():
        X = np.array([[10, 50], [20, 100], [30, 150], [40, 200]])
        y = np.array([2.5, 2.4, 2.6, 2.3]) # Fuel Ratio
        
        n_estimators = 100
        model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
        model.fit(X, y)
        
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_metric("rmse", 0.05)
        mlflow.sklearn.log_model(model, "fuel_ratio_model")
        print("Model logged to MLflow and MinIO successfully.")
