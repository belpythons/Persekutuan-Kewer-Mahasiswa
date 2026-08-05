# TASK-FE-01: Setup Scaffolding Vue 3 + Vuetify + TypeScript & Core Composables

## 📌 Sprint Target
**Sprint 1 - 3 & Sprint 8**

---

## 📝 Description & Context
Inisialisasi dasar arsitektur frontend menggunakan Vue 3 Composition API (`<script setup lang="ts">`), Vuetify 3 UI Framework, Inertia.js, dan TypeScript. Task ini juga mencakup implementasi `useAiApi.ts` sebagai API Client tersentralisasi ke Laravel Proxy Endpoint (`/api/v1/*`) serta `usePermission.ts` untuk perlindungan Role-Based Access Control (RBAC) pada antarmuka sesuai rekomendasi penanganan Celah Keamanan #12.

---

## ✅ Acceptance Criteria (AC)
- [ ] Terkofigurasi Vite dengan plugin Vue 3 dan alias TypeScript (`@/` mengarah ke `laravel/resources/ts/`).
- [ ] Tersedia `useAiApi.ts` composable yang menangani 5 endpoint utama AI Microservice:
  - `fetchForecast(payload: ForecastPayload): Promise<ForecastResponse>`
  - `fetchAnomalyDetect(records: AnomalyRecord[]): Promise<AnomalyDetectResponse>`
  - `fetchCalculateCapacity(payload: CapacityPayload): Promise<CapacityResponse>`
  - `fetchAiHealth(): Promise<HealthResponse>`
  - `fetchAiReady(): Promise<ReadyResponse>`
- [ ] Tersedia `usePermission.ts` composable untuk pengecekan role (`hasRole`) dan permission (`hasPermission`) berbasis Inertia `page.props.auth`.
- [ ] Terintegrasi layout utama `AppLayout.vue` / `App.vue` dengan dukungan tema Vuetify dark/light mode.

---

## 🛠️ Technical Implementation Details

### File & Path Target
- `laravel/resources/ts/composables/useAiApi.ts`
- `laravel/resources/ts/composables/usePermission.ts`
- `laravel/resources/ts/main.ts`
- `laravel/resources/ts/App.vue`

### Composable / API Client Reference
- **API Endpoint Mapping**:
  - `POST /api/v1/forecast` -> `fetchForecast`
  - `POST /api/v1/anomaly-detect` -> `fetchAnomalyDetect`
  - `POST /api/v1/calculate-capacity` -> `fetchCalculateCapacity`
  - `GET /api/v1/ai-health` -> `fetchAiHealth`
  - `GET /api/v1/ai-ready` -> `fetchAiReady`

### State Management & Data Types
- Interfaces: `ForecastPayload`, `ForecastResponse`, `AnomalyRecord`, `AnomalyDetectResponse`, `CapacityPayload`, `CapacityResponse`, `HealthResponse`, `ReadyResponse`.
- Inertia Shared Props: `page.props.auth.user.permissions`, `page.props.auth.user.roles`.

---

## 🎯 Definition of Done (DoD)
- [ ] Type check TypeScript lulus tanpa error (`npm run type-check` / `vue-tsc`).
- [ ] Unit testing composable `useAiApi.ts` menggunakan Vitest/Jest berhasil dengan mock HTTP response.
- [ ] Pengecekan RBAC terverifikasi menyembunyikan/menampilkan elemen UI sesuai hak akses pengguna.
