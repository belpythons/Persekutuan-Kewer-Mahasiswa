# Frontend React — Dekomposisi Sprint 1 hingga Sprint 18

Dokumen ini berisi panduan implementasi teknis mendetail per sprint untuk sub-proyek **`frontend-react/`** (Inertia.js + React + Tailwind CSS + Chatbot Widget) berdasarkan acuan `implementation_plan.md` dan `prd.md`.

---

## 📅 Matriks Ringkasan Sprint `frontend-react/`

| Sprint | Judul / Fokus Utama | Output / Deliverable | Target Celah |
|:-------|:-------------------|:---------------------|:-------------|
| **Sprint 1-3** | App Scaffolding & Layouts | App Shell, Navigation, Vite Config | Baseline Setup |
| **Sprint 8** | RBAC UI Protection | `usePermission` Custom Hook | #12 (RBAC UI) |
| **Sprint 9** | Interactive Dashboard Page | ApexCharts (Forecast & Anomaly Map) | Dashboard UI |
| **Sprint 10**| Reports & Export Interface | Report Datatables & Export PDF/Excel | Report UI |
| **Sprint 11-12**| Conversational Chatbot Widget | Chat Widget + SSE Token Stream + Pill Buttons | #8 (Disambiguasi UI) |
| **Sprint 13-15**| Responsive Tuning & UX Audit | Mobile/Tablet Layout & UX Tuning | User Experience |

---

## 🛠️ Detil Instruksi Pengerjaan Per Sprint

### 📌 Sprint 1 - 3: Setup Components & Shell
**Folder Target:** `frontend-react/` (atau `resources/js/` pada struktur Laravel Inertia)
- **Langkah Pengerjaan:**
  1. Inisialisasi React Inertia Frontend.
  2. Setup Tailwind CSS (`tailwind.config.js`).
  3. Install UI Icon & Charting packages:
     `npm install lucide-react apexcharts react-apexcharts clsx tailwind-merge`
  4. Buat komponen dasar:
     - `Layouts/AppLayout.jsx`
     - `Components/Navigation/Sidebar.jsx`
     - `Components/Navigation/Header.jsx`
     - `Components/UI/Card.jsx`
     - `Components/UI/Button.jsx`

---

### 📌 Sprint 8: RBAC Custom Hook (Solusi Celah #12)
- **Langkah Pengerjaan:**
  1. Buat `Hooks/usePermission.js`:
     ```javascript
     import { usePage } from '@inertiajs/react';

     export function usePermission() {
         const { auth } = usePage().props;
         const permissions = auth.user.permissions || [];
         const roles = auth.user.roles || [];

         const hasPermission = (perm) => permissions.includes(perm);
         const hasRole = (role) => roles.includes(role);

         return { hasPermission, hasRole, roles, permissions };
     }
     ```
  2. Lindungi tombol/komponen sensitif (seperti tombol Import atau Setting Threshold) menggunakan hook `hasPermission()`.

---

### 📌 Sprint 9: Interactive Dashboard Views
- **Langkah Pengerjaan:**
  1. Buat Halaman `Pages/Dashboard/Index.jsx`.
  2. Implementasikan Component `ForecastChart.jsx` (ApexCharts Line Chart):
     - Seri 1: Actual Fuel Ratio (Hitam terputus).
     - Seri 2: XGBoost Forecast FR (Biru).
     - Annotations: Warning Threshold (+8% / Oranye) & Critical Threshold (+18% / Merah).
  3. Implementasikan Component `AnomalyMapChart.jsx` (ApexCharts Scatter Plot):
     - Sumbu X: Tanggal, Sumbu Y: Tipe Unit, Titik Merah: NN Anomaly Spike.
  4. Implementasikan Component `CapacityBarChart.jsx` (Bar Chart alokasi BBM per aktivitas).

---

### 📌 Sprint 11 & 12: Chatbot Streaming & Disambiguation UI (Solusi Celah #8)
- **Langkah Pengerjaan:**
  1. Buat Komponen `Components/Chatbot/ChatbotWidget.jsx` (Floating Chat Window).
  2. Implementasikan SSE Token Streaming:
     ```javascript
     const sendMessage = async (userText) => {
         const response = await fetch('/api/chatbot/stream', {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({ message: userText })
         });
         const reader = response.body.getReader();
         const decoder = new TextDecoder();
         while (true) {
             const { value, done } = await reader.read();
             if (done) break;
             const chunk = decoder.decode(value);
             // Append token to message state
         }
     };
     ```
  3. Buat Komponen `Components/Chatbot/DisambiguationPills.jsx`:
     - Tampilkan tombol pill jika backend mengembalikan respons klarifikasi (misal: `[HD785-7]` vs `[HD785-8]`).
     - Saat diklik, otomatis mengirimkan jawaban klarifikasi ke chatbot.
