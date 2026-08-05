---
name: plan-executor-anti-hallucination
description: Skill eksekusi kode proyek KIDECO Fuel Ratio dengan pencegahan halusinasi, validasi ground-truth, dan kepatuhan ketat pada implementation_plan.md dan prd.md.
---

# Plan Executor & Anti-Hallucination Skill

Saat memproses tugas pembuatan atau pengeditan kode untuk proyek KIDECO Fuel Ratio:

1. **Langkah 1: Verifikasi Dokumen Rujukan**
   - Sebelum menulis kode, periksa file `implementation_plan.md` dan `prd.md` menggunakan `view_file`.
   - Pastikan nama kelas, method, endpoint, dan kolom database 100% sesuai spesifikasi plan.

2. **Langkah 2: Cek Celah Keamanan Teridentifikasi**
   - Pastikan kode yang ditulis TIDAK mengulangi 13 celah yang ada di gap analysis (terutama SQL injection pada Chatbot, data leakage di Autoencoder, dan hardcoded Excel parser index).

3. **Langkah 3: Jalankan Verification Testing**
   - Setelah menulis kode Laravel: Jalankan `php artisan test` atau PHPUnit.
   - Setelah menulis kode Python: Jalankan `pytest`.
   - JANGAN mendeklarasikan tugas selesai sebelum testing berjalan hijau (0 error).
