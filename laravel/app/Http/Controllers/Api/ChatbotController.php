<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\ChatbotSystemPrompt;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\StreamedResponse;

class ChatbotController extends Controller
{
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

        $rawMessages = $validated['messages'];

        // 2. Batasi riwayat riil maksimal 10 item pesan terakhir (Stateless Payload Protection)
        $maxHistory = config('ai.gemini.max_history_length', 10);
        if (count($rawMessages) > $maxHistory) {
            $rawMessages = array_slice($rawMessages, -$maxHistory);
        }

        // 3. Formatkan riwayat pesan ke skema Gemini API (user / model)
        $contents = [];
        foreach ($rawMessages as $msg) {
            $role = strtolower($msg['role']);
            if ($role === 'assistant' || $role === 'system') {
                $role = 'model';
            }
            $contents[] = [
                'role' => $role,
                'parts' => [
                    ['text' => $msg['content']]
                ]
            ];
        }

        // Pastikan item pesan pertama dalam contents ber-role 'user' untuk aturan Gemini API
        if (!empty($contents) && $contents[0]['role'] !== 'user') {
            array_unshift($contents, [
                'role' => 'user',
                'parts' => [['text' => 'Halo, mohon bantu analisa operasional Fuel Ratio KIDECO.']]
            ]);
        }

        // 4. Siapkan System Instruction & Gemini Configuration
        $systemPromptText = ChatbotSystemPrompt::getSystemPrompt();
        $apiKey = config('ai.gemini.api_key');
        $model = config('ai.gemini.model', 'gemini-1.5-flash');
        $baseUrl = config('ai.gemini.base_url', 'https://generativelanguage.googleapis.com/v1beta');

        $geminiPayload = [
            'system_instruction' => [
                'parts' => [
                    ['text' => $systemPromptText]
                ]
            ],
            'contents' => $contents,
            'generationConfig' => [
                'temperature' => 0.4,
                'maxOutputTokens' => 1500,
            ]
        ];

        // 5. Stream SSE Response ke Client Frontend (Vue 3)
        return response()->stream(function () use ($apiKey, $model, $baseUrl, $geminiPayload) {
            // Unbuffer output PHP (hanya saat runtime web server)
            if (ob_get_level() > 0 && !app()->runningUnitTests()) {
                ob_end_clean();
            }

            // Jika API Key belum terkonfigurasi / placeholder, gunakan fallback intelligent streamer
            if (empty($apiKey) || $apiKey === 'your_gemini_api_key_here') {
                $fallbackText = "Sistem KIDECO Fuel Ratio Chatbot siap membantu Anda. Silakan konfigurasi `GEMINI_API_KEY` pada `.env` untuk inferensi real-time Google Gemini.\n\n"
                    . "**Ringkasan Status Operasional Tambang KIDECO:**\n"
                    . "- **Baseline FR**: 1.018 L/BCM\n"
                    . "- **Alert Status**: NORMAL (< 1.08), WARNING (1.08 - 1.12), CRITICAL (>= 1.12 L/BCM)\n"
                    . "- **Detection Model**: PyTorch Deep Autoencoder (Spike MAD Threshold)\n"
                    . "- **Forecasting Model**: XGBoost Regressor (13 Fitur Cuaca & Lag)";

                $chunks = str_split($fallbackText, 15);
                foreach ($chunks as $chunk) {
                    echo "data: " . json_encode(['text' => $chunk]) . "\n\n";
                    flush();
                    usleep(30000); // 30ms delay simulated streaming
                }
                echo "data: [DONE]\n\n";
                flush();
                return;
            }

            // Panggil Gemini Stream API via cURL / Stream
            $streamUrl = "{$baseUrl}/models/{$model}:streamGenerateContent?key={$apiKey}&alt=sse";

            $ch = curl_init($streamUrl);
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($geminiPayload));
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, false);
            curl_setopt($ch, CURLOPT_WRITEFUNCTION, function ($ch, $data) {
                // Parse baris SSE dari Google Gemini API
                $lines = explode("\n", $data);
                foreach ($lines as $line) {
                    $line = trim($line);
                    if (str_starts_with($line, 'data: ')) {
                        $jsonStr = substr($line, 6);
                        if ($jsonStr === '[DONE]') {
                            continue;
                        }
                        $decoded = json_decode($jsonStr, true);
                        if (isset($decoded['candidates'][0]['content']['parts'][0]['text'])) {
                            $extractedText = $decoded['candidates'][0]['content']['parts'][0]['text'];
                            echo "data: " . json_encode(['text' => $extractedText]) . "\n\n";
                            flush();
                        }
                    }
                }
                return strlen($data);
            });

            curl_exec($ch);

            if (curl_errno($ch)) {
                $err = curl_error($ch);
                Log::error("Gemini API Stream Error: {$err}");
                echo "data: " . json_encode(['text' => "\n\n[ERROR: Gagal terhubung ke Gemini API - {$err}]"]) . "\n\n";
                flush();
            }

            curl_close($ch);

            // Sinyal penutup SSE stream
            echo "data: [DONE]\n\n";
            flush();
        }, 200, [
            'Content-Type' => 'text/event-stream',
            'Cache-Control' => 'no-cache, must-revalidate',
            'Connection' => 'keep-alive',
            'X-Accel-Buffering' => 'no',
        ]);
    }
}
