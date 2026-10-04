<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Exception;

class FuelRatioAiClient
{
    protected string $baseUrl;
    protected int $timeout;
    protected int $retry;

    public function __construct()
    {
        $this->baseUrl = config('services.ai_service.base_url', 'http://localhost:8001');
        $this->timeout = config('services.ai_service.timeout', 5);
        $this->retry   = config('services.ai_service.retry', 3);
    }

    /**
     * Memanggil HTTP request standar dengan auto retry & error handling
     */
    protected function request(string $method, string $endpoint, array $data = [])
    {
        $url = rtrim($this->baseUrl, '/') . '/' . ltrim($endpoint, '/');

        try {
            $response = Http::timeout($this->timeout)
                ->retry($this->retry, 100)
                ->withHeaders([
                    'Accept' => 'application/json',
                    'Content-Type' => 'application/json',
                ])
                ->$method($url, $data);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error("AI Service Error [{$response->status()}]: " . $response->body());
            throw new Exception("AI Service HTTP Error: " . $response->status());

        } catch (Exception $e) {
            Log::emergency("Gagal menghubungi AI Microservice di {$url}: " . $e->getMessage());
            throw $e;
        }
    }

    /**
     * Prediksi Fuel Ratio Harian (XGBoost Engine)
     */
    public function getForecast(string $date, ?float $rainMm = null, ?float $tempC = null, ?float $windKmh = null, ?float $haulM = null, ?float $prodBcm = null): array
    {
        $payload = array_filter([
            'date' => $date,
            'curah_hujan_mm' => $rainMm,
            'temp_max_c' => $tempC,
            'kecepatan_angin_kmh' => $windKmh,
            'haul_distance_m' => $haulM,
            'daily_prod_bcm' => $prodBcm,
        ], fn($v) => $v !== null);

        return $this->request('post', '/api/v1/forecast', $payload);
    }

    /**
     * Prediksi Horizon 7 Hari Fuel Ratio (XGBoost Engine)
     */
    public function getForecast7Days(?string $startDate = null): array
    {
        $payload = array_filter([
            'start_date' => $startDate ?? date('Y-m-d'),
        ], fn($v) => $v !== null);

        return $this->request('post', '/api/v1/forecast-7days', $payload);
    }

    /**
     * Ambil Log Historis Fuel Ratio Harian dari Database
     */
    public function getForecastHistory(int $days = 30): array
    {
        return $this->request('get', "/api/v1/forecast-history?days={$days}");
    }

    /**
     * Metrik Evaluasi Model Riil (R², MAE) dari Training Pipeline Terakhir
     */
    public function getModelMetrics(): array
    {
        return $this->request('get', '/api/v1/model-metrics');
    }

    /**
     * Deteksi Lonjakan BBM Unit (PyTorch Autoencoder)
     */
    public function detectAnomalies(array $records): array
    {
        return $this->request('post', '/api/v1/anomaly-detect', [
            'records' => $records,
        ]);
    }

    /**
     * Kalkulasi Penentuan Kapasitas Armada & Solar Kombinasi Per-Unit Per-Jam
     */
    public function calculateCapacity(string $date, float $forecastProdBcm, float $rainMm, ?array $spikeMap = null): array
    {
        return $this->request('post', '/api/v1/calculate-capacity', [
            'date' => $date,
            'forecast_prod_bcm' => $forecastProdBcm,
            'curah_hujan_mm' => $rainMm,
            'nn_spike_count_by_unit' => $spikeMap,
        ]);
    }

    /**
     * Global Fleet Capacity Tuning & Variance Analysis (324 units)
     */
    public function globalCapacityTuning(array $payload): array
    {
        return $this->request('post', '/api/v1/global-capacity-tuning', $payload);
    }

    /**
     * Synchronize Real-time BMKG Weather Logs
     */
    public function syncBmkgWeather(): array
    {
        return $this->request('post', '/api/v1/weather/sync-bmkg');
    }

    /**
     * Equipment Working Hours (EWH) & Alokasi Solar Fleet Support & Dewatering
     */
    public function getEwhBudget(float $forecastProdBcm = 40000.0): array
    {
        return $this->request('get', '/api/v1/ewh-budget?forecast_prod_bcm=' . $forecastProdBcm);
    }

    /**
     * Konfigurasi Threshold Fuel Ratio Dinamis (Budget Baseline, Warning %, Critical %)
     */
    public function getThresholdConfig(): array
    {
        return $this->request('get', '/api/v1/threshold-config');
    }

    public function updateThresholdConfig(array $payload): array
    {
        return $this->request('put', '/api/v1/threshold-config', $payload);
    }

    /**
     * Retrain XGBoost & PyTorch Autoencoder — operasi lebih lama dari request biasa,
     * jadi pakai timeout terpisah yang lebih longgar alih-alih timeout default (5s).
     */
    public function retrainModels(): array
    {
        $url = rtrim($this->baseUrl, '/') . '/api/v1/model/retrain';

        try {
            $response = Http::timeout(60)
                ->withHeaders(['Accept' => 'application/json'])
                ->post($url);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error("AI Service Retrain Error [{$response->status()}]: " . $response->body());
            throw new Exception("AI Service Retrain HTTP Error: " . $response->status());
        } catch (Exception $e) {
            Log::emergency("Gagal retrain model di {$url}: " . $e->getMessage());
            throw $e;
        }
    }

    /**
     * Mining Fuel AI Chatbot Assistant Query
     */
    public function queryChatbot(string $query, array $history = []): array
    {
        return $this->request('post', '/api/v1/chatbot/query', [
            'query' => $query,
            'history' => $history,
        ]);
    }

    /**
     * Health Check Microservice
     */
    public function healthCheck(): array
    {
        return $this->request('get', '/health');
    }

    /**
     * Check Kesiapan Microservice (Model ML pre-loaded)
     */
    public function readinessCheck(): array
    {
        return $this->request('get', '/ready');
    }

    /**
     * Check Kesiapan Microservice — boolean convenience
     */
    public function isReady(): bool
    {
        try {
            $res = $this->request('get', '/ready');
            return isset($res['status']) && $res['status'] === 'ready';
        } catch (Exception $e) {
            return false;
        }
    }
}
