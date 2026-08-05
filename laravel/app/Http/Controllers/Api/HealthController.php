<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\FuelRatioAiClient;
use Illuminate\Http\JsonResponse;
use Exception;

class HealthController extends Controller
{
    public function __construct(
        protected FuelRatioAiClient $aiClient
    ) {}

    /**
     * GET /api/v1/ai-health
     * Proxy health check ke AI microservice
     */
    public function health(): JsonResponse
    {
        try {
            $result = $this->aiClient->healthCheck();

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'status' => 'unavailable',
                'error' => $e->getMessage(),
            ], 503);
        }
    }

    /**
     * GET /api/v1/ai-ready
     * Proxy readiness probe ke AI microservice
     */
    public function ready(): JsonResponse
    {
        try {
            $result = $this->aiClient->readinessCheck();

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'status' => 'not_ready',
                'error' => $e->getMessage(),
                'warmup_details' => [
                    'status' => 'not_ready',
                    'xgboost_warmed_up' => false,
                    'pytorch_autoencoder_warmed_up' => false,
                    'database_status' => 'unknown',
                ],
            ], 503);
        }
    }
}
