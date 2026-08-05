<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\FuelRatioAiClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Exception;

class CapacityController extends Controller
{
    public function __construct(
        protected FuelRatioAiClient $aiClient
    ) {}

    /**
     * POST /api/v1/calculate-capacity
     * Proxy ke AI service capacity calculation endpoint
     */
    public function calculate(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'date' => 'required|date_format:Y-m-d',
            'forecast_prod_bcm' => 'nullable|numeric|min:0',
            'curah_hujan_mm' => 'nullable|numeric|min:0',
            'nn_spike_count_by_unit' => 'nullable|array',
        ]);

        try {
            $forecastProdBcm = (float) ($validated['forecast_prod_bcm'] ?? 40000.0);
            $curahHujanMm = (float) ($validated['curah_hujan_mm'] ?? 0.0);

            $result = $this->aiClient->calculateCapacity(
                $validated['date'],
                $forecastProdBcm,
                $curahHujanMm,
                $validated['nn_spike_count_by_unit'] ?? null,
            );

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service tidak tersedia',
                'message' => $e->getMessage(),
                'fallback' => true,
                'log_date' => $validated['date'],
                'forecast_prod_bcm' => $validated['forecast_prod_bcm'],
                'activity_breakdown' => [],
                'unit_breakdown' => [],
            ], 503);
        }
    }

    /**
     * POST /api/v1/global-capacity-tuning
     */
    public function globalTuning(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'date' => 'nullable|date_format:Y-m-d',
            'forecast_prod_bcm' => 'nullable|numeric|min:0',
            'curah_hujan_mm' => 'nullable|numeric|min:0',
            'auto_scan_anomalies' => 'nullable|boolean',
        ]);

        try {
            $payload = [
                'date' => $validated['date'] ?? date('Y-m-d'),
                'forecast_prod_bcm' => (float) ($validated['forecast_prod_bcm'] ?? 40000.0),
                'curah_hujan_mm' => (float) ($validated['curah_hujan_mm'] ?? 5.0),
                'auto_scan_anomalies' => $validated['auto_scan_anomalies'] ?? true,
            ];

            $result = $this->aiClient->globalCapacityTuning($payload);

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service tidak tersedia',
                'message' => $e->getMessage(),
                'fallback' => true,
            ], 503);
        }
    }

    /**
     * POST /api/v1/weather/sync-bmkg
     */
    public function syncBmkg(Request $request): JsonResponse
    {
        try {
            $result = $this->aiClient->syncBmkgWeather();

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service tidak tersedia',
                'message' => $e->getMessage(),
                'fallback' => true,
            ], 503);
        }
    }
}

