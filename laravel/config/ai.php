<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Gemini API & AI Microservice Configuration
    |--------------------------------------------------------------------------
    |
    | Konfigurasi integrasi Google Gemini API via SSE Streaming & Python AI Service.
    |
    */

    'gemini' => [
        'api_key' => env('GEMINI_API_KEY', ''),
        'model' => env('GEMINI_MODEL', 'gemini-1.5-flash'),
        'base_url' => env('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta'),
        'max_history_length' => 10,
    ],

    'ai_service_url' => env('AI_SERVICE_URL', 'http://localhost:8000'),

];
