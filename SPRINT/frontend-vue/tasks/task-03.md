# TASK-FE-03: Forecasting & Predictive Scenario Simulator Module

## 📌 Sprint Target
**Sprint 9**

---

## 📝 Description & Context
Pengembangan halaman **Forecasting Analytics & Mining Fuel AI** (`laravel/resources/ts/pages/forecasting-ai.vue`) yang memungkinkan *Mine Planner* dan *Fuel Engineer* melakukan simulasi interaktif skenario cuaca, jarak angkut (*haul distance*), serta target produksi harian (*daily production BCM*). Halaman ini menyajikan kontrol simulator skenario, grafik deret waktu interaktif, dan kartu metrik evaluasi model Machine Learning XGBoost.

---

## ✅ Acceptance Criteria (AC)
- [ ] Komponen `ScenarioSimulatorControls.vue` menyediakan input kontrol berbasis slider dan textfield untuk parameter:
  - Curah Hujan (mm)
  - Suhu Maksimum (°C)
  - Kecepatan Angin (km/jam)
  - Jarak Angkut / Haul Distance (meter)
  - Target Produksi Harian (BCM)
- [ ] Tombol "Jalankan Simulasi XGBoost" pada `ScenarioSimulatorControls.vue` memanggil `fetchForecast` di `useAiApi.ts` dan memperbarui nilai estimasi FR, status threshold, serta fitur dominan (*features used*).
- [ ] Komponen `TimeSeriesForecastChart.vue` menampilkan grafik tren historis vs hasil proyeksi simulasi interaktif.
- [ ] Komponen `ModelMetricsCard.vue` menampilkan performa model XGBoost ($R^2$ Score, MAE, RMSE, MAPE) serta Feature Importance ranking (misal: Haul Distance, Rain mm, Daily BCM).

---

## 🛠️ Technical Implementation Details

### File & Path Target
- **Page Container**: `laravel/resources/ts/pages/forecasting-ai.vue`
- **Forecasting Views**:
  - `laravel/resources/ts/views/forecasting/ScenarioSimulatorControls.vue`
  - `laravel/resources/ts/views/forecasting/TimeSeriesForecastChart.vue`
  - `laravel/resources/ts/views/forecasting/ModelMetricsCard.vue`

### Composable / API Client Used
- `useAiApi.ts` -> `fetchForecast(payload: ForecastPayload)`

### State Management & Props/Emits
- **State Simulator Controls**:
  - `curah_hujan_mm`: `ref<number>(12.5)`
  - `temp_max_c`: `ref<number>(32.0)`
  - `kecepatan_angin_kmh`: `ref<number>(14.2)`
  - `haul_distance_m`: `ref<number>(4200.0)`
  - `daily_prod_bcm`: `ref<number>(45000.0)`
- **Emits / Reactive State**:
  - Event `onSimulate(payload)` memicu re-fetch API dan menyiarkan hasil `ForecastResponse` ke komponen grafik pendukung.

---

## 🎯 Definition of Done (DoD)
- [ ] Simulasi interaktif memberikan respons balik cepat (< 500ms) saat slider/input diubah.
- [ ] Penanganan error API menunjukkan pesan toast/alert yang informatif jika microservice AI mengalami kelambatan.
- [ ] Validasi batas input parameter (misal: Curah Hujan $0 - 200$ mm, Haul Distance $100 - 15000$ m) bekerja secara ketat.
- [ ] Lolos Type checking TypeScript.
