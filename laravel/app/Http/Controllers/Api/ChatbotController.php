<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\FuelRatioAiClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Exception;

class ChatbotController extends Controller
{
    public function __construct(
        protected FuelRatioAiClient $aiClient
    ) {}

    /**
     * POST /api/v1/chatbot/query
     * Proxy ke AI service Mining Fuel Chatbot endpoint
     */
    public function query(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'query' => 'required|string|min:1',
            'history' => 'nullable|array',
        ]);

        try {
            $result = $this->aiClient->queryChatbot(
                $validated['query'],
                $validated['history'] ?? []
            );

            return response()->json($result);
        } catch (Exception $e) {
            return response()->json([
                'error' => 'AI Service Chatbot tidak tersedia',
                'message' => $e->getMessage(),
                'response' => "Maaf, sistem AI Chatbot sedang offline. Silakan coba beberapa saat lagi.",
                'fallback' => true,
            ], 503);
        }
    }
}
