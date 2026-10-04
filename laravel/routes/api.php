<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\ForecastController;
use App\Http\Controllers\Api\AnomalyController;
use App\Http\Controllers\Api\CapacityController;
use App\Http\Controllers\Api\ChatbotController;
use App\Http\Controllers\Api\HealthController;
use App\Http\Controllers\Api\MlopsController;

/*
|--------------------------------------------------------------------------
| API Routes — AI Microservice Proxy
|--------------------------------------------------------------------------
|
| Proxy endpoints yang meneruskan request dari Vue frontend ke
| python-ai-service. Prefix: /api/v1
|
*/

Route::prefix('v1')->group(function () {
    // Fuel Ratio Forecast (XGBoost)
    Route::post('/forecast', [ForecastController::class, 'forecast']);
    Route::post('/forecast-7days', [ForecastController::class, 'forecast7Days']);
    Route::get('/forecast-history', [ForecastController::class, 'forecastHistory']);
    Route::get('/model-metrics', [ForecastController::class, 'modelMetrics']);

    // Anomaly Detection (PyTorch Autoencoder)
    Route::post('/anomaly-detect', [AnomalyController::class, 'detect']);

    // Combined Capacity Determination
    Route::post('/calculate-capacity', [CapacityController::class, 'calculate']);
    Route::post('/global-capacity-tuning', [CapacityController::class, 'globalTuning']);

    // Realtime BMKG Weather Sync
    Route::post('/weather/sync-bmkg', [CapacityController::class, 'syncBmkg']);

    // Equipment Working Hours & Fuel Budget (Support/Dewatering)
    Route::get('/ewh-budget', [CapacityController::class, 'ewhBudget']);

    // Dynamic Threshold Config & Model Retraining (MLOps)
    Route::get('/threshold-config', [MlopsController::class, 'getThresholdConfig']);
    Route::put('/threshold-config', [MlopsController::class, 'updateThresholdConfig']);
    Route::post('/model/retrain', [MlopsController::class, 'retrain']);

    // Mining Fuel AI Chatbot Assistant
    Route::post('/chatbot/query', [ChatbotController::class, 'query']);

    // AI Microservice Health & Readiness
    Route::get('/ai-health', [HealthController::class, 'health']);
    Route::get('/ai-ready', [HealthController::class, 'ready']);
});
