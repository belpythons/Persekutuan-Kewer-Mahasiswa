<?php

return [

    /*
    |--------------------------------------------------------------------------
    | KIDECO Gemini AI Chatbot Dedicated Configuration
    |--------------------------------------------------------------------------
    |
    | File konfigurasi tersendiri untuk mengontrol seluruh parameter integrasi
    | Google Gemini API, batasan riwayat percakapan, generasi token, dan fallback.
    |
    */

    // Gemini API Credentials & Endpoint Configuration
    'api_key' => env('GEMINI_API_KEY', ''),
    'model' => env('GEMINI_MODEL', 'gemini-1.5-flash'),
    'base_url' => env('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta'),

    // Batasan Riwayat Pesan (Stateless Payload Guard)
    'max_history_length' => (int) env('CHATBOT_MAX_HISTORY', 10),

    // Konfigurasi Parameter Generasi Model Gemini
    'generation_config' => [
        'temperature' => (float) env('CHATBOT_TEMPERATURE', 0.4),
        'maxOutputTokens' => (int) env('CHATBOT_MAX_TOKENS', 1500),
    ],

    // Konfigurasi Fallback Streamer (Saat API Key belum diisi)
    'fallback' => [
        'enabled' => true,
        'chunk_size' => 15,
        'delay_us' => 30000, // 30ms
    ],

    // Reference Class System Prompt Pengetahuan Domain ML
    'system_prompt_class' => \App\Services\ChatbotSystemPrompt::class,

];
