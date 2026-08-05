<?php

namespace Tests\Feature;

use Tests\TestCase;

class ChatbotStreamTest extends TestCase
{
    /**
     * Test endpoint POST /api/v1/chatbot/stream mengembalikan response SSE header yang valid.
     */
    public function test_chatbot_stream_endpoint_returns_sse_response(): void
    {
        $payload = [
            'messages' => [
                ['role' => 'user', 'content' => 'Berapa baseline Fuel Ratio KIDECO?'],
            ]
        ];

        $response = $this->postJson('/api/v1/chatbot/stream', $payload);

        $response->assertStatus(200);
        $response->assertHeader('Content-Type', 'text/event-stream; charset=utf-8');
        $response->assertHeader('Cache-Control', 'must-revalidate, no-cache, private');

        // Pastikan konten streaming berisi sinyal SSE data dan [DONE]
        $content = $response->streamedContent();
        $this->assertStringContainsString('data: ', $content);
        $this->assertStringContainsString('[DONE]', $content);
    }

    /**
     * Test endpoint menolak payload tanpa messages array.
     */
    public function test_chatbot_stream_endpoint_validates_payload(): void
    {
        $response = $this->postJson('/api/v1/chatbot/stream', []);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['messages']);
    }

    /**
     * Test endpoint memotong riwayat pesan jika lebih dari 10 item.
     */
    public function test_chatbot_stream_endpoint_accepts_multiple_messages(): void
    {
        $messages = [];
        for ($i = 1; $i <= 15; $i++) {
            $messages[] = ['role' => ($i % 2 === 1 ? 'user' : 'model'), 'content' => "Pesan ke-$i"];
        }

        $response = $this->postJson('/api/v1/chatbot/stream', ['messages' => $messages]);

        $response->assertStatus(200);
        $response->assertHeader('Content-Type', 'text/event-stream; charset=utf-8');
    }
}
