<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\GeminiChatbotService;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\StreamedResponse;

class ChatbotController extends Controller
{
    protected GeminiChatbotService $chatbotService;

    public function __construct(GeminiChatbotService $chatbotService)
    {
        $this->chatbotService = $chatbotService;
    }

    /**
     * Endpoint SSE Streaming untuk Gemini AI Chatbot.
     * POST /api/v1/chatbot/stream
     */
    public function stream(Request $request): StreamedResponse
    {
        // 1. Validasi Input Request Payload
        $validated = $request->validate([
            'messages' => 'required|array|min:1',
            'messages.*.role' => 'required|string|in:user,model,assistant,system',
            'messages.*.content' => 'required|string',
        ]);

        // 2. Delegasikan seluruh proses pemformatan & streaming ke GeminiChatbotService
        return $this->chatbotService->streamChat($validated['messages']);
    }
}
