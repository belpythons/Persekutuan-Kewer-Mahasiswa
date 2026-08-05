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
            'forecast_prod_bcm' => 'required|numeric|min:0',
            'curah_hujan_mm' => 'required|numeric|min:0',
            'nn_spike_count_by_unit' => 'nullable|array',
        ]);

        try {
            $result = $this->aiClient->calculateCapacity(
                $validated['date'],
                $validated['forecast_prod_bcm'],
                $validated['curah_hujan_mm'],
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
}
