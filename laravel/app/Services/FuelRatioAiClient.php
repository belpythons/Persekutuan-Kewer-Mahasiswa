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
    public function getForecast(string $date, float $rainMm, float $tempC, float $windKmh, float $haulM, float $prodBcm): array
    {
        return $this->request('post', '/api/v1/forecast', [
            'date' => $date,
            'curah_hujan_mm' => $rainMm,
            'temp_max_c' => $tempC,
            'kecepatan_angin_kmh' => $windKmh,
            'haul_distance_m' => $haulM,
            'daily_prod_bcm' => $prodBcm,
        ]);
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
