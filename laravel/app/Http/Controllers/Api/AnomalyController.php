<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\FuelRatioAiClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Exception;

class AnomalyController extends Controller
{
    public function __construct(
        protected FuelRatioAiClient $aiClient
    ) {}

    /**
     * POST /api/v1/anomaly-detect
     * Proxy ke AI service anomaly detection endpoint (PyTorch Autoencoder)
     */
    public function detect(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'records' => 'present|array',
            'records.*.Date' => 'required|string',
            'records.*.Unit' => 'required|string',
            'records.*.Activity' => 'required|string',
            'records.*.FC_Actual' => 'required|numeric',
            'records.*.Unit_Fuel_L_Day' => 'required|numeric',
            'records.*.Unit_FR' => 'required|numeric',
            'records.*.Rain_mm' => 'required|numeric',
        ]);

        try {
            $result = $this->aiClient->detectAnomalies($validated['records']);

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service tidak tersedia',
                'message' => $e->getMessage(),
                'fallback' => true,
                'total_records_scanned' => count($validated['records']),
                'total_spikes_detected' => 0,
                'spikes' => [],
                'spike_report_per_unit' => [],
                'detail_report_per_activity' => [],
            ], 503);
        }
    }
}
