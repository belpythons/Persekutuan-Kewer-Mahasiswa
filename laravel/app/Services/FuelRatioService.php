<?php

namespace App\Services;

use App\Repositories\Contracts\FuelRatioRepositoryInterface;
use Illuminate\Support\Facades\Http;
use Exception;
use Illuminate\Http\Client\ConnectionException;

class FuelRatioService
{
    protected $repository;

    public function __construct(FuelRatioRepositoryInterface $repository)
    {
        $this->repository = $repository;
    }

    public function calculateAndSave(array $data)
    {
        $flaskUrl = config('services.python_ai.url', 'http://localhost:5000') . '/api/v1/predict-fuel-ratio';
        $apiKey = config('services.python_ai.key', 'secret-ai-key-2026');

        try {
            $response = Http::timeout(3)
                ->retry(2, 100) // Retry twice with 100ms delay on connection failure
                ->withHeaders(['X-API-KEY' => $apiKey])
                ->post($flaskUrl, [
                    'equipment_id' => $data['equipment_id'],
                    'operating_hours' => (float)$data['operating_hours'],
                    'fuel_consumed_liters' => (float)$data['fuel_consumed_liters'],
                    'load_tonnage' => (float)$data['load_tonnage'],
                ]);

            if ($response->failed()) {
                throw new Exception("Flask AI Service error status: " . $response->status() . " - " . $response->body());
            }

            $result = $response->json();
            $calculatedRatio = $result['calculated_fuel_ratio'] ?? round($data['fuel_consumed_liters'] / $data['load_tonnage'], 2);

        } catch (ConnectionException $e) {
            // Graceful fallback calculation if Python service is completely offline
            $calculatedRatio = round($data['fuel_consumed_liters'] / $data['load_tonnage'], 2);
        }

        return $this->repository->create([
            'equipment_id' => $data['equipment_id'],
            'operating_hours' => $data['operating_hours'],
            'fuel_consumed_liters' => $data['fuel_consumed_liters'],
            'load_tonnage' => $data['load_tonnage'],
            'calculated_fuel_ratio' => $calculatedRatio,
        ]);
    }
}
