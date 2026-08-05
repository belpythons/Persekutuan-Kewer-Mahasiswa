# DESIGN SYSTEM BREAKDOWN: PAGE 4 - FORECASTING ANALYTICS & INTERACTIVE AI CHATBOT
## SYSTEM MONITORING FUEL RATIO (FR) BASIS OPERASIONAL & CAPACITY MANAGEMENT TAMBANG
**Route File:** `/forecasting-ai`  
**Target User:** Mining Data Analyst, Dispatcher, Mine Engineer, Management  
**Tujuan Utama:** Menyajikan visualisasi prediktif Fuel Ratio deret waktu berbasis XGBoost dan menyediakan asisten kecerdasan buatan (*Mining Fuel AI Chatbot*) yang dapat berinteraksi secara cerdas dalam bahasa alami.

---

## 1. LAYOUT STRUCTURE & WIREFRAME ASCII

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: Forecasting Analytics Center | Model Version: XGBoost v3.3 & PyTorch v2.11              │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 1: FORECAST SCENARIO SIMULATOR & MODEL METRICS                                              │
│ ┌──────────────────────────────────────────────┐ ┌────────────────────────────────────────────┐ │
│ │ COMPONENT: ScenarioSimulatorControls         │ │ COMPONENT: ModelMetricsCard                │ │
│ │ Slider Hujan: [35 mm] | Distance: [4,180 m]  │ │ XGBoost R² Score : 0.9901                  │ │
│ │ Target BCM  : [250,000 BCM]                  │ │ MAE Error Rate   : 0.0045 L/BCM            │ │
│ └──────────────────────────────────────────────┘ └────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 2: TIME-SERIES FORECAST CHART WITH THRESHOLD ZONES                                          │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: TimeSeriesForecastChart                                                           │ │
│ │ Visual: Line Actual FR | Line XGBoost Forecast | Shaded Yellow (+8% Warning) | Shaded Red (+18%)│ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ZONE 3: INTERACTIVE MINING FUEL AI CHATBOT ASSISTANT (RIGHT SIDEBAR / MODAL)                     │
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ COMPONENT: MiningFuelChatbotWidget                                                           │ │
│ │ Header: 🤖 Mining Fuel AI Assistant (Online - Connected to FMS & XGBoost Engine)             │ │
│ │ Chat Window: Scrollable Transcripts (User Prompt vs AI Analytical Response)                   │ │
│ │ Quick Prompt Pills: ["Penyebab FR Warning Besok?", "Simulasi Matikan 5 HD785 Anomali", ...]  │ │
│ │ Input Bar: [ Tanyakan analisa / simulasi BBM...                                      ] [Send]│ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. BREAKDOWN KOMPONEN UI & SPESIFIKASI DESIGN SYSTEM

### Komponen 4.1: `TimeSeriesForecastChart`
- **Tipe Komponen:** Interactive Multi-Line & Area Chart (Recharts / Chart.js / Highcharts)
- **Peran:** Visualisasi grafik deret waktu 365 hari historis + 7 hari proyeksi prediksi Fuel Ratio.
- **Elemen Visual:**
  - **Line 1 (Actual FR):** Solid Blue `#1A73E8`, stroke 2px dengan titik data.
  - **Line 2 (XGBoost Forecast):** Dashed Teal `#00897B`, stroke 2px.
  - **Shaded Area 1 (Warning Zone +8%):** Amber Tint `#FEF7E0` (FR antara `1.2503` dan `1.3660 L/BCM`).
  - **Shaded Area 2 (Critical Zone +18%):** Red Tint `#FCE8E6` (FR `≥ 1.3660 L/BCM`).
  - **Reference Line Budget:** Dotted Gray Line `#5F6368` (`1.1576 L/BCM`).

### Komponen 4.2: `MiningFuelChatbotWidget`
- **Tipe Komponen:** Floating AI Chat Interface / Split-Screen Assistant
- **Arsitektur Backend Chatbot:**
  - **Foundation LLM:** Gemini / OpenAI / Fine-tuned Mining Model.
  - **Context Engine:** RAG (Retrieval-Augmented Generation) tersambung ke FMS Database, Excel Master Data, & XGBoost/PyTorch Inference API.
- **Spesifikasi UI Chat Interface:**
  - **Header:** Status Indicator Hijau `Connected to FMS & XGBoost Pipeline`.
  - **Bubble Chat User:** Alignment Kanan, Background Primary Blue (`#1A73E8`), Teks Putih.
  - **Bubble Chat AI:** Alignment Kiri, Background Surface Card (`#F8F9FA`), Teks Dark Slate, Markdown Formatted (Tabel, Bullet Points, Emoticons, Highlighted Metrics).
  - **Quick Prompt Chips:** Tombol instan di atas input bar untuk pertanyaan umum.

---

## 3. TRANSKRIP INTERAKSI SIMULASI CHATBOT AI ASSISTANT

### Transkrip 1: Diagnostic Query (Analisis Penyebab Warning)
```markdown
💬 USER:
"Mengapa prediksi Fuel Ratio untuk besok naik menjadi 1.285 L/BCM dan berstatus WARNING?"

🤖 MINING FUEL AI ASSISTANT:
Berdasarkan model prediktif XGBoost Regressor, kenaikan FR besok (1.285 L/BCM vs Baseline 1.1576 L/BCM) dipicu oleh 3 faktor utama:

1. 🌧️ Prakiraan Curah Hujan: API Open-Meteo mendeteksi hujan sebesar 35.2 mm di pit Bontang.
2. 🛣️ Ekspansi Jarak Angkut: Jarak angkut Hauling HD785 membengkak dari 3,900m menjadi 4,181m (+281m akibat jalan licin).
3. 💧 Lonjakan Dewatering: Beban solar pompa Dewatering melonjak +158.4% (membutuhkan tambahan +24,670 Liter solar).

💡 Saran Mitigasi: Kurangi 12 unit Hauling HD785-7 yang berada di pit berlumpur dan alokasikan solar ke pompa EWP420.
```

### Transkrip 2: Prescriptive Query (Simulasi Penghematan Solar & Biaya)
```markdown
💬 USER:
"Jika saya menghentikan 5 unit HD785-7 dan 1 unit EX2600-6 yang mengalami PyTorch Spike Anomaly hari ini, berapa solar dan biaya yang bisa kita hemat?"

🤖 MINING FUEL AI ASSISTANT:
Melakukan kalkulasi pada Combined Capacity Engine...

- 🚜 Unit EX2600-6 (EX-2601): Menghemat konsumsi anomali 192.28 L/jam (3.845.6 L/hari).
- 🚛 5 Unit HD785-7 (Anomali Spike): Menghemat rerata konsumsi 80.78 L/jam/unit (total 8.078.0 L/hari).

📉 Total Penghematan Solar: 11.923,6 Liter / Hari.
💰 Estimasi Penghematan Biaya (BBM Industri Rp 14.500/L): Rp 172.892.200,- per hari.

Target BCM harian tetap aman karena utilisasi kapasitas hauling saat ini baru 22.46%.
```

### Transkrip 3: Operational Compliance Query (Audit Unit Below SPO)
```markdown
💬 USER:
"Tampilkan unit excavator mana saja yang hari ini konsumsi solarnya di atas SPO dan berikan total liternya."

🤖 MINING FUEL AI ASSISTANT:
Berikut adalah 3 Unit Excavator yang beroperasi di bawah SPO hari ini:

1. PC2000-11R (EX-2004) | FC Actual: 185.53 L/hr (SPO Target: 100.0 L/hr | Deviasi +85.5%) | Total: 10.900,0 L/hari.
2. PC2000-8 (EX-2012)   | FC Actual: 180.75 L/hr (SPO Target: 100.0 L/hr | Deviasi +80.8%) | Total: 10.800,0 L/hari.
3. EX2600-6 (EX-2601)   | FC Actual: 192.28 L/hr (SPO Target: 187.0 L/hr | Deviasi +2.8%)  | Total: 17.428,4 L/hari.

📋 Rekomendasi: WO Maintenance telah dibuat otomatis untuk pemeriksaan kelayakan sistem pembakaran mesin EX-2004 dan EX-2012.
```
