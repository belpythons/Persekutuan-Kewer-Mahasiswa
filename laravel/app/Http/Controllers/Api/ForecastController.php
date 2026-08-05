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
            'curah_hujan_mm' => 'nullable|numeric|min:0',
            'temp_max_c' => 'nullable|numeric',
            'kecepatan_angin_kmh' => 'nullable|numeric|min:0',
            'haul_distance_m' => 'nullable|numeric|min:0',
            'daily_prod_bcm' => 'nullable|numeric|min:0',
        ]);

        try {
            $result = $this->aiClient->getForecast(
                $validated['date'],
                $validated['curah_hujan_mm'] ?? null,
                $validated['temp_max_c'] ?? null,
                $validated['kecepatan_angin_kmh'] ?? null,
                $validated['haul_distance_m'] ?? null,
                $validated['daily_prod_bcm'] ?? null,
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

    /**
     * POST /api/v1/forecast-7days
     * Proxy ke AI service 7-day horizon forecasting endpoint
     */
    public function forecast7Days(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'start_date' => 'nullable|date_format:Y-m-d',
        ]);

        try {
            $result = $this->aiClient->getForecast7Days($validated['start_date'] ?? null);
            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service 7-day horizon tidak tersedia',
                'message' => $e->getMessage(),
                'fallback' => true,
                'daily_forecasts' => [],
            ], 503);
        }
    }

    /**
     * GET /api/v1/forecast-history
     * Proxy ke AI service forecast history logs endpoint
     */
    public function forecastHistory(Request $request): JsonResponse
    {
        $days = (int) $request->input('days', 30);

        try {
            $result = $this->aiClient->getForecastHistory($days);
            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service forecast history tidak tersedia',
                'message' => $e->getMessage(),
                'fallback' => true,
                'total' => 0,
                'historical_logs' => [],
            ], 503);
        }
    }
}
