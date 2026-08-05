<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\FuelRatioAiClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Exception;

class ForecastController extends Controller
{
    public function __construct(
        protected FuelRatioAiClient $aiClient
    ) {}

    /**
     * POST /api/v1/forecast
     * Proxy ke AI service forecast endpoint (XGBoost Regressor)
     */
    public function forecast(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'date' => 'required|date_format:Y-m-d',
            'curah_hujan_mm' => 'required|numeric|min:0',
            'temp_max_c' => 'required|numeric',
            'kecepatan_angin_kmh' => 'required|numeric|min:0',
            'haul_distance_m' => 'required|numeric|min:0',
            'daily_prod_bcm' => 'required|numeric|min:0',
        ]);

        try {
            $result = $this->aiClient->getForecast(
                $validated['date'],
                $validated['curah_hujan_mm'],
                $validated['temp_max_c'],
                $validated['kecepatan_angin_kmh'],
                $validated['haul_distance_m'],
                $validated['daily_prod_bcm'],
            );

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service tidak tersedia',
                'message' => $e->getMessage(),
                'fallback' => true,
                'log_date' => $validated['date'],
                'forecast_fr' => 1.018,
                'status' => 'NORMAL',
                'budget_baseline' => 1.018,
                'warning_threshold' => 1.0994,
                'critical_threshold' => 1.2012,
            ], 503);
        }
    }
}
