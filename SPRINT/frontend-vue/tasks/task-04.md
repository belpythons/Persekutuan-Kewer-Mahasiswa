# TASK-FE-04: Conversational Mining Fuel AI Chatbot Widget & Disambiguation UI

## 📌 Sprint Target
**Sprint 11 - 12**

---

## 📝 Description & Context
Pengembangan widget asisten cerdas **Mining Fuel AI Assistant** (`laravel/resources/ts/views/forecasting/MiningFuelChatbotWidget.vue`) berbasis conversational UI. Widget ini mendukung pencarian data operasional tambang, penjelasan anomali, dan query kustom berbasis SQL/Vector retrieval. Komponen ini dirancang secara khusus untuk menangani **Celah Keamanan #8 (Ambiguity in Natural Language DB Queries)** dengan menghadirkan **Disambiguation Pill Buttons** saat intent pengguna bersifat ambigu (misal: prompt "Berapa solar HD785?" yang memerlukan kejelasan periode waktu atau pit tambang).

---

## ✅ Acceptance Criteria (AC)
- [ ] Floating Chatbot Widget dapat dibuka/ditutup secara responsif di pojok kanan bawah antarmuka.
- [ ] Mendukung streaming teks balasan berbasis *Server-Sent Events* (SSE) / `ReadableStream` dari backend Laravel Chatbot Proxy (`POST /api/v1/chatbot/stream`).
- [ ] **Mitigasi Celah #8 (Disambiguation UI)**:
  - Jika respons backend memuat opsi disambiguasi (`pills: string[]`), widget merender *Pill Action Buttons* secara otomatis.
  - Mengklik tombol pill secara otomatis mengirimkan jawaban klarifikasi ke chatbot stream tanpa perlu mengetik ulang.
- [ ] Menampilkan indikator loading / typing status saat model AI sedang memproses jawaban.
- [ ] Riwayat percakapan (*chat session*) tersimpan sementara dalam state lokal / Pinia store selama sesi aktif.

---

## 🛠️ Technical Implementation Details

### File & Path Target
- `laravel/resources/ts/views/forecasting/MiningFuelChatbotWidget.vue`
- Integration Page: `laravel/resources/ts/pages/forecasting-ai.vue`

### Composable / Streaming Protocol
- Direct Fetch API dengan SSE Header:
  ```typescript
  const response = await fetch('/api/v1/chatbot/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
    body: JSON.stringify({ message: userInput })
  })
  ```

### State Management & Props/Emits
- Local Reactive State:
  - `isOpen`: `ref<boolean>(false)`
  - `inputMessage`: `ref<string>('')`
  - `messages`: `ref<Array<{ sender: 'user' | 'assistant', text: string, pills?: string[], isStreaming?: boolean }>>([])`
  - `isStreaming`: `ref<boolean>(false)`

---

## 🎯 Definition of Done (DoD)
- [ ] SSE token streaming tampil halus (*smooth typing effect*) tanpa lag atau kendala pemotongan karakter UTF-8.
- [ ] Interaksi pill disambiguasi teruji meloloskan flow klarifikasi intent user.
- [ ] Penanganan kesalahan jaringan (error fallback) teruji ketika koneksi stream terputus.
- [ ] Tidak ada penggunaan Raw SQL / bypass guard di sisi frontend, seluruh input tersanitasi.
