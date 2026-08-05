# Task Breakdown - Laravel Web Portal (Vue 3 + Laravel 11)

## Overview
Dokumen ini berisi rincian task teknis untuk pengembangan Laravel Web Portal yang bertindak sebagai API Orchestrator dan Frontend Dashboard untuk sistem analitik Fuel Ratio.

---

## Sprint 1: Foundation, API Client, & Authentication Setup
- [x] **Task 1.1: Environment & Base Setup**
  - [x] Konfigurasi `.env.example` dan `.env` untuk endpoint FastAPI (`AI_SERVICE_URL`).
  - [x] Set up Vuetify 3 dan Auto-imports TypeScript (`auto-imports.d.ts`, `components.d.ts`).
- [ ] **Task 1.2: FuelRatioAiClient Service Implementation**
  - [x] Buat service `app/Services/FuelRatioAiClient.php` menggunakan Guzzle/Http Client Laravel.
  - [ ] Implementasikan retry mechanism, error handling, dan logging saat koneksi ke FastAPI gagal.
- [ ] **Task 1.3: Health Check API Integration**
  - [x] Implementasi `HealthController.php`.
  - [ ] Buat endpoint status untuk memeriksa koneksi antara Laravel dan Python AI Service.

---

## Sprint 2: Real-time Dashboard & Anomaly Widget Implementation
- [x] **Task 2.1: Controller & API Routing for Dashboard**
  - [x] Buat controller `AnomalyController.php` untuk memformat data anomali.
- [ ] **Task 2.2: Vue 3 Dashboard Components**
  - [x] Integrasikan `DynamicThresholdAlertWidget.vue`.
  - [x] Integrasikan `FrTrendLineChart.vue`.
  - [x] Integrasikan `TopAnomalousLeaderboard.vue`.
  - [x] Integrasikan `ActivityFuelDonutChart.vue`.
  - [ ] Tambahkan loading state, skeleton loader, dan error state pada semua widget dashboard saat mengambil data dari API.

---

## Sprint 3: Forecasting & Scenario Simulator Module
- [x] **Task 3.1: ForecastController API Integration**
  - [x] Implementasi `ForecastController.php` untuk proxy permintaan forecasting ke AI Service.
- [ ] **Task 3.2: Forecasting Vue Page Development**
  - [x] Buat komponen `TimeSeriesForecastChart.vue` dengan ApexCharts.
  - [x] Buat `ScenarioSimulatorControls.vue` untuk input variabel simulator.
  - [x] Buat `ModelMetricsCard.vue` untuk menampilkan MAE, RMSE, dan MAPE.
  - [ ] Hubungkan kontrol simulasi skenario secara reaktif dengan chart peramalan.

---

## Sprint 4: Production Capacity & Interactive AI Assistant
- [x] **Task 4.1: CapacityController Implementation**
  - [x] Implementasi `CapacityController.php` untuk kalkulasi ritase dan kuota produksi.
- [x] **Task 4.2: Capacity Page & Chatbot Widget**
  - [x] Buat halaman `production-capacity.vue`.
  - [x] Buat widget `MiningFuelChatbotWidget.vue`.
  - [x] Sempurnakan siklus request-response interaktif chatbot dengan streaming SSE token dari Gemini API (`POST /api/v1/chatbot/stream`).

---

## Sprint 5: Testing, Polish, & Integration Readiness
- [ ] **Task 5.1: Unit & End-to-End Testing**
  - [ ] Tulis unit test untuk `FuelRatioAiClientTest.php`.
  - [ ] Tulis Feature Test untuk API Controller (`ForecastControllerTest`, `AnomalyControllerTest`).
- [ ] **Task 5.2: UI/UX & Responsive Polish**
  - [ ] Verifikasi kejelasan tampilan dalam mode Light & Dark theme.
  - [ ] Pastikan seluruh chart dan tabel kompatibel dengan tampilan resolusi layar kecil (mobile/tablet).
