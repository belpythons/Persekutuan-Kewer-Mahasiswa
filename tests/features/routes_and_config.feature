Feature: Service Routes, HTTP Statuses, Security and Configuration Validation
  As a DevOps/MLOps Engineer
  I want to verify that API routes, API Key security, status codes, and configuration parameters are correctly set up
  So that inter-service communication and prediction APIs function reliably.

  Scenario: Predict Fuel Ratio with Valid Payload and Valid API Key
    Given the Flask AI Service is running on "http://localhost:5000"
    And I set the header "X-API-KEY" to "secret-ai-key-2026"
    When I send a POST request to "/api/v1/predict-fuel-ratio" with payload:
      """
      {
        "equipment_id": "EXCA-001",
        "operating_hours": 10.5,
        "fuel_consumed_liters": 250.0,
        "load_tonnage": 100.0
      }
      """
    Then the response status code should be 200
    And the response JSON should contain "calculated_fuel_ratio" with value 2.5
    And the response JSON "status" should be "success"

  Scenario: Predict Fuel Ratio without API Key
    Given the Flask AI Service is running on "http://localhost:5000"
    And I clear the header "X-API-KEY"
    When I send a POST request to "/api/v1/predict-fuel-ratio" with payload:
      """
      {
        "equipment_id": "EXCA-001",
        "operating_hours": 10.5,
        "fuel_consumed_liters": 250.0,
        "load_tonnage": 100.0
      }
      """
    Then the response status code should be 401
    And the response JSON should contain "error"

  Scenario: Predict Fuel Ratio with Invalid Payload
    Given the Flask AI Service is running on "http://localhost:5000"
    And I set the header "X-API-KEY" to "secret-ai-key-2026"
    When I send a POST request to "/api/v1/predict-fuel-ratio" with payload:
      """
      {
        "equipment_id": "EXCA-001",
        "operating_hours": 0
      }
      """
    Then the response status code should be 400
    And the response JSON should contain "error"

  Scenario: Requesting Non-Existent Route
    Given the Flask AI Service is running on "http://localhost:5000"
    When I send a GET request to "/api/v1/undefined-endpoint"
    Then the response status code should be 404

  Scenario: Method Not Allowed on Prediction Route
    Given the Flask AI Service is running on "http://localhost:5000"
    When I send a GET request to "/api/v1/predict-fuel-ratio"
    Then the response status code should be 405
