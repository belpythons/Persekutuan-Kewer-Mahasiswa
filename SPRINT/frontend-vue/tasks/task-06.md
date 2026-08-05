# TASK-FE-06: Support, Dewatering, Weather Risk & MLOps Control Page

## 📌 Sprint Target
**Sprint 9 - 10**

---

## 📝 Description & Context
Pengembangan modul **Support, Dewatering, Weather Risk & MLOps Control** (`laravel/resources/ts/pages/support-weather-mlops.vue`). Modul ini mengawasi konsumsi solar non-produksi (Zero-BCM burden dari unit Support dan Dewatering pump), mengintegrasikan peringatan cuaca dari Open-Meteo API, menyediakan pengisian anggaran Effective Working Hours (EWH), serta menyajikan panel kontrol retraining model Machine Learning (MLOps) dan konfigurasi ambang batas alert dinamis.

---

## ✅ Acceptance Criteria (AC)
- [ ] Widget `OpenMeteoWeatherCard.vue` menampilkan data prediksi curah hujan (mm), kecepatan angin (km/jam), dan risiko operasional tambang berbasis integrasi API cuaca.
- [ ] Card `SupportEwhBudgetCard.vue` & `DewateringEwhBudgetCard.vue` menyajikan pemantauan anggaran jam kerja efektif (EWH) vs realisasi konsumsi solar Zero-BCM.
- [ ] Chart `NonProductionFuelBurdenDonut.vue` memvisualisasikan proporsi beban BBM unit non-produksi (Dozer Support, Grader, Water Truck, Dewatering Pump).
- [ ] Tabel `SupportDewateringEwhTable.vue` menyajikan log konsumsi BBM per unit support.
- [ ] Card `DynamicThresholdConfigCard.vue` memfasilitasi pengubahan persentase Warning (+8%) dan Critical (+18%) threshold.
- [ ] Card `MLOpsModelRetrainCard.vue` memicu trigger re-training model XGBoost / Autoencoder serta menampilkan status kesehatan microservice (`fetchAiHealth`, `fetchAiReady`).

---

## 🛠️ Technical Implementation Details

### File & Path Target
- **Page Container**: `laravel/resources/ts/pages/support-weather-mlops.vue`
- **Support Views**:
  - `laravel/resources/ts/views/support/OpenMeteoWeatherCard.vue`
  - `laravel/resources/ts/views/support/SupportEwhBudgetCard.vue`
  - `laravel/resources/ts/views/support/DewateringEwhBudgetCard.vue`
  - `laravel/resources/ts/views/support/NonProductionFuelBurdenDonut.vue`
  - `laravel/resources/ts/views/support/SupportDewateringEwhTable.vue`
  - `laravel/resources/ts/views/support/DynamicThresholdConfigCard.vue`
  - `laravel/resources/ts/views/support/MLOpsModelRetrainCard.vue`

### Composable / API Client Used
- `useAiApi.ts` -> `fetchAiHealth()`, `fetchAiReady()`

---

## 🎯 Definition of Done (DoD)
- [ ] Integrasi MLOps Control Card berhasil menampilkan indikator readiness status XGBoost & PyTorch Autoencoder.
- [ ] Pengisian EWH budget tervalidasi secara komprehensif.
- [ ] Lolos verifikasi type check TypeScript.
