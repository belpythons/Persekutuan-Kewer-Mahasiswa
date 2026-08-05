# AGENTS.md — Rules & Behavioral Guidelines for KIDECO Fuel Ratio Project

## 1. MATA UANG UTAMA: STRICT PLAN & GROUND-TRUTH COMPLIANCE
- Anda DILARANG KERAS mengesampingkan dokumen rujukan: `implementation_plan.md`, `prd.md`, dan `bussiness-logic.md`.
- Setiap perubahan kode, migrasi database, atau pembuatan API WAJIB mengacu pada spesifikasi di dokumen plan.
- DILARANG mengutip atau mengasumsikan nama kolom/tabel/variabel tanpa memeriksa schema migrasi yang ada.

## 2. ATURAN BEBAS HALUSINASI (ANTI-HALLUCINATION PROTOCOL)
- Jika suatu data atau fitur belum ada di plan atau kode asli, JANGAN MENELURUSI ASUMSI SENDIRI. Tanyakan kepada user atau tandai sebagai `TODO: Need Clarification`.
- DILARANG membuat dummy data acak di production code.
- DILARANG menggunakan `np.random` atau data sintetis pada modul production AI Engine.

## 3. ATURAN KEAMANAN & ANTI SQL INJECTION (MANDATORY)
- Pada seluruh modul AI Chatbot Retrieval, DILARANG MENGGUNAKAN Raw SQL Queries (`DB::raw`, `PDO::query`).
- SEMUA kueri ke database WAJIB menggunakan Eloquent ORM terparameterisasi dan lolos dari `QueryWhitelistGuard`.

## 4. ATURAN AKURASI MODEL AI
- Model PyTorch Autoencoder WAJIB di-train HANYA pada data normal (`Is_Known_Anomaly == 0`).
- Model XGBoost WAJIB dievaluasi menggunakan `TimeSeriesSplit` (DILARANG random 80/20 train_test_split).
- Derating hujan WAJIB menggunakan formula non-linear `DeratingCalculator`.
