Feature: Laravel Web Portal Routes, HTTP Statuses, Validation, and Configuration Validation
  As a Fullstack QA Engineer
  I want to verify that Laravel routes, Inertia views, validation rules, and configuration parameters are correct
  So that the web portal user interface and backend integration operate reliably.

  Scenario: Access Fuel Ratio Analytics Page Successfully
    Given the Laravel Web Portal is running on "http://localhost:8000"
    When I send a GET request to "/fuel-ratio"
    Then the response status code should be 200
    And the response body should contain "Fuel Ratio & Capacity Analytics"

  Scenario: Calculate Fuel Ratio with Valid Payload
    Given the Laravel Web Portal is running on "http://localhost:8000"
    When I send a POST request to "/fuel-ratio/calculate" with JSON payload:
      """
      {
        "equipment_id": "EXCA-001",
        "operating_hours": 10.5,
        "fuel_consumed_liters": 250.0,
        "load_tonnage": 100.0
      }
      """
    Then the response status code should be 302
    And a log record should exist in the database for equipment "EXCA-001"

  Scenario: Calculate Fuel Ratio with Invalid Payload (Validation Error)
    Given the Laravel Web Portal is running on "http://localhost:8000"
    When I send a POST request to "/fuel-ratio/calculate" with JSON payload:
      """
      {
        "equipment_id": "",
        "operating_hours": 0
      }
      """
    Then the response status code should be 302
    And the session should contain validation errors for "equipment_id"

  Scenario: Requesting Non-Existent Laravel Route
    Given the Laravel Web Portal is running on "http://localhost:8000"
    When I send a GET request to "/fuel-ratio/undefined-route"
    Then the response status code should be 404

  Scenario: Verify Python AI Service Configuration Binding in Laravel
    Given the Laravel application configuration for "services.python_ai.url" is loaded
    Then the configuration value should not be empty
    And the configuration value should match pattern "http://*"
