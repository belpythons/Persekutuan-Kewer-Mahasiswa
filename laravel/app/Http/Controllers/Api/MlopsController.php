<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\FuelRatioAiClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Exception;

class MlopsController extends Controller
{
    public function __construct(
        protected FuelRatioAiClient $aiClient
    ) {}

    /**
     * GET /api/v1/threshold-config
     * Proxy ke AI service konfigurasi threshold Fuel Ratio dinamis
     */
    public function getThresholdConfig(): JsonResponse
    {
        try {
            $result = $this->aiClient->getThresholdConfig();

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service threshold config tidak tersedia',
                'message' => $e->getMessage(),
                'fallback' => true,
            ], 503);
        }
    }

    /**
     * PUT /api/v1/threshold-config
     */
    public function updateThresholdConfig(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'budget_baseline' => 'nullable|numeric|gt:0',
            'warning_pct' => 'nullable|numeric|min:0|max:100',
            'critical_pct' => 'nullable|numeric|min:0|max:100',
        ]);

        try {
            $result = $this->aiClient->updateThresholdConfig($validated);

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'Gagal memperbarui threshold config',
                'message' => $e->getMessage(),
                'fallback' => true,
            ], 503);
        }
    }

    /**
     * POST /api/v1/model/retrain
     */
    public function retrain(): JsonResponse
    {
        try {
            $result = $this->aiClient->retrainModels();

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service retrain tidak tersedia',
                'message' => $e->getMessage(),
                'fallback' => true,
            ], 503);
        }
    }
}
