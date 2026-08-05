<?php

namespace App\Services;

use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\StreamedResponse;

class GeminiChatbotService
{
    /**
     * Mengeksekusi streaming respons SSE dari Google Gemini API atau Fallback Stream.
     */
    public function streamChat(array $rawMessages): StreamedResponse
    {
        // 1. Ambil Konfigurasi dari config/chatbot.php
        $maxHistory = config('chatbot.max_history_length', 10);
        $apiKey = config('chatbot.api_key', '');
        $model = config('chatbot.model', 'gemini-1.5-flash');
        $baseUrl = config('chatbot.base_url', 'https://generativelanguage.googleapis.com/v1beta');
        $genConfig = config('chatbot.generation_config', ['temperature' => 0.4, 'maxOutputTokens' => 1500]);
        $systemPromptClass = config('chatbot.system_prompt_class', ChatbotSystemPrompt::class);

        // 2. Pemotongan Riwayat Pesan (Maksimal N Pesan Terakhir)
        if (count($rawMessages) > $maxHistory) {
            $rawMessages = array_slice($rawMessages, -$maxHistory);
        }

        // 3. Formatkan Riwayat Pesan ke Skema Gemini API (user / model)
        $contents = $this->formatMessagesForGemini($rawMessages);

        // 4. Bangun Payload Utama Gemini API
        $systemPromptText = method_exists($systemPromptClass, 'getSystemPrompt')
            ? $systemPromptClass::getSystemPrompt()
            : '';

        $geminiPayload = [
            'system_instruction' => [
                'parts' => [
                    ['text' => $systemPromptText]
                ]
            ],
            'contents' => $contents,
            'generationConfig' => $genConfig,
        ];

        // 5. Kembalikan StreamedResponse dengan Header SSE
        return response()->stream(function () use ($apiKey, $model, $baseUrl, $geminiPayload) {
            // Unbuffer output PHP (hanya saat runtime web server)
            if (ob_get_level() > 0 && !app()->runningUnitTests()) {
                ob_end_clean();
            }

            // Jika API Key belum terkonfigurasi, jalankan Fallback Intelligent Streamer
            if (empty($apiKey) || $apiKey === 'your_gemini_api_key_here') {
                $this->executeFallbackStream();
                return;
            }

            // Jalankan Gemini Streaming API via cURL
            $this->executeGeminiStream($baseUrl, $model, $apiKey, $geminiPayload);
        }, 200, [
            'Content-Type' => 'text/event-stream; charset=utf-8',
            'Cache-Control' => 'must-revalidate, no-cache, private',
            'Connection' => 'keep-alive',
            'X-Accel-Buffering' => 'no',
        ]);
    }

    /**
     * Memformat array pesan request menjadi format yang valid untuk Gemini API.
     */
    protected function formatMessagesForGemini(array $rawMessages): array
    {
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

        // Gemini API mewajibkan pesan pertama ber-role 'user'
        if (!empty($contents) && $contents[0]['role'] !== 'user') {
            array_unshift($contents, [
                'role' => 'user',
                'parts' => [['text' => 'Halo, mohon bantu analisa operasional Fuel Ratio KIDECO.']]
            ]);
        }

        return $contents;
    }

    /**
     * Memanggil endpoint Stream Gemini API via HTTP cURL dan memancarkan token SSE.
     */
    protected function executeGeminiStream(string $baseUrl, string $model, string $apiKey, array $geminiPayload): void
    {
        $streamUrl = "{$baseUrl}/models/{$model}:streamGenerateContent?key={$apiKey}&alt=sse";

        $ch = curl_init($streamUrl);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($geminiPayload));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, false);
        curl_setopt($ch, CURLOPT_WRITEFUNCTION, function ($ch, $data) {
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
                        $textChunk = $decoded['candidates'][0]['content']['parts'][0]['text'];
                        echo "data: " . json_encode(['text' => $textChunk]) . "\n\n";
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
    }

    /**
     * Fallback Streamer simulasi token saat API Key belum diisi.
     */
    protected function executeFallbackStream(): void
    {
        $chunkSize = config('chatbot.fallback.chunk_size', 15);
        $delayUs = config('chatbot.fallback.delay_us', 30000);

        $fallbackText = "Sistem KIDECO Fuel Ratio Chatbot siap membantu Anda. Silakan konfigurasi `GEMINI_API_KEY` pada `.env` untuk inferensi real-time Google Gemini.\n\n"
            . "**Ringkasan Status Operasional Tambang KIDECO:**\n"
            . "- **Baseline FR**: 1.018 L/BCM\n"
            . "- **Alert Status**: NORMAL (< 1.08), WARNING (1.08 - 1.12), CRITICAL (>= 1.12 L/BCM)\n"
            . "- **Detection Model**: PyTorch Deep Autoencoder (Spike MAD Threshold)\n"
            . "- **Forecasting Model**: XGBoost Regressor (13 Fitur Cuaca & Lag)";

        $chunks = str_split($fallbackText, $chunkSize);
        foreach ($chunks as $chunk) {
            echo "data: " . json_encode(['text' => $chunk]) . "\n\n";
            flush();
            usleep($delayUs);
        }
        echo "data: [DONE]\n\n";
        flush();
    }
}
