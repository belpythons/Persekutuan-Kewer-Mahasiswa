# Gemini AI Chatbot SSE Streaming — Vue 3 Frontend Integration Spec

Dokumen ini berisi spesifikasi teknis integrasi Server-Sent Events (SSE) streaming untuk komponen **Vue 3 Chatbot Widget** (`MiningFuelChatbotWidget.vue`) yang mengonsumsi endpoint `POST /api/v1/chatbot/stream` pada Laravel Web Portal.

---

## 📡 1. Endpoint Specification

- **Endpoint**: `POST /api/v1/chatbot/stream`
- **Content-Type**: `application/json`
- **Response Type**: `text/event-stream`
- **Headers**:
  ```http
  Accept: text/event-stream
  Content-Type: application/json
  ```

### 📩 Request Body Payload
Frontend mengelola riwayat percakapan secara *ephemeral/stateless* di memori komponen Vue. Maksimum **10 pesan terakhir** dikirimkan pada payload request:

```json
{
  "messages": [
    {"role": "user", "content": "Berapa Fuel Ratio rata-rata untuk unit HD785-7 pada kondisi hujan 15mm?"},
    {"role": "assistant", "content": "Pada curah hujan 15mm, faktor derating hujan adalah 0.887..."},
    {"role": "user", "content": "Bagaimana rekomendasi alokasi unitnya?"}
  ]
}
```

---

## 🌊 2. Server-Sent Events (SSE) Output Chunk Format

Backend mengirimkan potongan teks token per baris SSE dengan format:
`data: {"text": "chunk_string"}\n\n`

Sinyal penutup streaming SSE:
`data: [DONE]\n\n`

### Contoh SSE Event Stream Raw Output:
```http
data: {"text":"Berdasarkan "}

data: {"text":"perhitungan "}

data: {"text":"Derating Calculator KIDECO, "}

data: {"text":"pada curah hujan 15mm..."}

data: [DONE]
```

---

## 💻 3. Vue 3 Integration Code Snippet (`MiningFuelChatbotWidget.vue`)

Gunakan API `fetch()` dengan `ReadableStream` reader pada Vue 3 script setup untuk membaca stream token secara real-time:

```vue
<script setup>
import { ref, nextTick } from 'vue';

const messages = ref([]);
const userInput = ref('');
const isStreaming = ref(false);

const sendMessage = async () => {
  if (!userInput.value.trim() || isStreaming.value) return;

  const userQuery = userInput.value.trim();
  userInput.value = '';

  // 1. Tambahkan pesan user ke state lokal
  messages.value.push({ role: 'user', content: userQuery });

  // Batasi riwayat di frontend maks 10 pesan terakhir
  if (messages.value.length > 10) {
    messages.value = messages.value.slice(-10);
  }

  // 2. Siapkan slot pesan assistant kosong untuk menampung stream
  const assistantMsgIndex = messages.value.push({ role: 'assistant', content: '' }) - 1;
  isStreaming.value = true;

  try {
    const response = await fetch('/api/v1/chatbot/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({
        messages: messages.value.slice(0, -1) // Kirim seluruh riwayat sebelum slot pesan assistant baru
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const chunk of lines) {
        const line = chunk.trim();
        if (line.startsWith('data: ')) {
          const dataStr = line.replace('data: ', '').trim();
          if (dataStr === '[DONE]') {
            isStreaming.value = false;
            break;
          }

          try {
            const parsed = JSON.parse(dataStr);
            if (parsed.text) {
              messages.value[assistantMsgIndex].content += parsed.text;
              await nextTick();
            }
          } catch (err) {
            console.error('SSE Chunk JSON Parse Error:', err);
          }
        }
      }
    }
  } catch (error) {
    console.error('Chatbot Streaming Error:', error);
    messages.value[assistantMsgIndex].content = 'Maaf, terjadi kesalahan saat menghubungi server AI Chatbot.';
  } finally {
    isStreaming.value = false;
  }
};
</script>
```

---

## 🛡️ 4. Key Security & Performance Guarantees

1. **Zero Database I/O**: Tidak ada percakapan yang disimpan ke basis data Laravel (Stateless & Ephemeral).
2. **Payload Protection**: Pesan riwayat dipangkas maksimal 10 item baik di frontend maupun di backend controller (`$maxHistory = 10`).
3. **No-Buffering Reverse Proxy Header**: Menggunakan `X-Accel-Buffering: no` untuk memastikan Nginx tidak menahan token SSE stream.
