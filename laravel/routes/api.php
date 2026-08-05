<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\ForecastController;
use App\Http\Controllers\Api\AnomalyController;
use App\Http\Controllers\Api\CapacityController;
use App\Http\Controllers\Api\HealthController;
use App\Http\Controllers\Api\ChatbotController;

/*
|--------------------------------------------------------------------------
| API Routes — AI Microservice Proxy & Gemini SSE Chatbot
|--------------------------------------------------------------------------
|
| Proxy endpoints yang meneruskan request dari Vue frontend ke
| python-ai-service serta endpoint Gemini SSE Streaming Chatbot. Prefix: /api/v1
|
*/

Route::prefix('v1')->group(function () {
    // Fuel Ratio Forecast (XGBoost)
    Route::post('/forecast', [ForecastController::class, 'forecast']);

    // Anomaly Detection (PyTorch Autoencoder)
    Route::post('/anomaly-detect', [AnomalyController::class, 'detect']);

    // Combined Capacity Determination
    Route::post('/calculate-capacity', [CapacityController::class, 'calculate']);

    // Gemini AI Chatbot SSE Stream
    Route::post('/chatbot/stream', [ChatbotController::class, 'stream']);

    // AI Microservice Health & Readiness
    Route::get('/ai-health', [HealthController::class, 'health']);
    Route::get('/ai-ready', [HealthController::class, 'ready']);
});
