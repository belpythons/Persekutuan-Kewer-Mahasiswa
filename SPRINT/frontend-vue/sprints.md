# Frontend Vue — Dekomposisi Sprint 1 hingga Sprint 18

Dokumen ini berisi panduan implementasi teknis mendetail per sprint untuk sub-proyek **`frontend-vue/`** (Inertia.js + Vue 3 + Tailwind CSS + Vue ApexCharts + Chatbot Widget) berdasarkan acuan `implementation_plan.md` dan `prd.md`.

---

## 📅 Matriks Ringkasan Sprint `frontend-vue/`

| Sprint | Judul / Fokus Utama | Output / Deliverable | Target Celah |
|:-------|:-------------------|:---------------------|:-------------|
| **Sprint 1-3** | App Scaffolding & Layouts | App Shell, Navigation, Vite Config (Vue 3) | Baseline Setup |
| **Sprint 8** | RBAC UI Protection | `usePermission` Composable | #12 (RBAC UI) |
| **Sprint 9** | Interactive Dashboard Page | Vue ApexCharts (Forecast & Anomaly Map) | Dashboard UI |
| **Sprint 10**| Reports & Export Interface | Report Datatables & Export PDF/Excel | Report UI |
| **Sprint 11-12**| Conversational Chatbot Widget | Vue Chat Widget + SSE Token Stream + Pill Buttons | #8 (Disambiguasi UI) |
| **Sprint 13-15**| Responsive Tuning & UX Audit | Mobile/Tablet Layout & UX Tuning | User Experience |

---

## 🛠️ Detil Instruksi Pengerjaan Per Sprint

### 📌 Sprint 1 - 3: Setup Components & Shell (Vue 3 + Inertia)
**Folder Target:** `frontend-vue/` (atau `resources/js/` pada Laravel Inertia Vue 3)
- **Langkah Pengerjaan:**
  1. Inisialisasi Vue 3 Inertia Frontend dengan `@inertiajs/vue3` & Vite (`@vitejs/plugin-vue`).
  2. Setup Tailwind CSS (`tailwind.config.js`).
  3. Install UI Icon & Charting packages:
     `npm install @inertiajs/vue3 vue3-apexcharts lucide-vue-next clsx tailwind-merge`
  4. Buat komponen dasar dengan Vue 3 Composition API (`<script setup>`):
     - `Layouts/AppLayout.vue`
     - `Components/Navigation/Sidebar.vue`
     - `Components/Navigation/Header.vue`
     - `Components/UI/Card.vue`
     - `Components/UI/Button.vue`

---

### 📌 Sprint 8: RBAC Custom Composable Vue 3 (Solusi Celah #12)
- **Langkah Pengerjaan:**
  1. Buat `Composables/usePermission.js`:
     ```javascript
     import { usePage } from '@inertiajs/vue3';
     import { computed } from 'vue';

     export function usePermission() {
         const page = usePage();
         
         const permissions = computed(() => page.props.auth?.user?.permissions || []);
         const roles = computed(() => page.props.auth?.user?.roles || []);

         const hasPermission = (perm) => permissions.value.includes(perm);
         const hasRole = (role) => roles.value.includes(role);

         return { hasPermission, hasRole, roles, permissions };
     }
     ```
  2. Lindungi tombol/komponen sensitif menggunakan `v-if="hasPermission('import-data')"`.

---

### 📌 Sprint 9: Interactive Dashboard Views (Vue 3 + Vue ApexCharts)
- **Langkah Pengerjaan:**
  1. Buat Halaman `Pages/Dashboard/Index.vue`.
  2. Implementasikan Component `ForecastChart.vue` (Vue3 ApexCharts Line Chart):
     ```vue
     <script setup>
     import { computed } from 'vue';
     import VueApexCharts from 'vue3-apexcharts';

     const props = defineProps({
         dates: Array,
         actualFr: Array,
         forecastFr: Array,
         warningThreshold: Number,
         criticalThreshold: Number
     });

     const chartOptions = computed(() => ({
         chart: { type: 'line', toolbar: { show: true } },
         stroke: { curve: 'smooth', width: [2, 2], dashArray: [5, 0] },
         colors: ['#1e293b', '#0ea5e9'],
         xaxis: { categories: props.dates },
         annotations: {
             yaxis: [
                 { y: props.warningThreshold, borderColor: '#f97316', label: { text: 'Warning (+8%)', style: { color: '#fff', background: '#f97316' } } },
                 { y: props.criticalThreshold, borderColor: '#ef4444', label: { text: 'Critical (+18%)', style: { color: '#fff', background: '#ef4444' } } }
             ]
         }
     }));

     const series = computed(() => [
         { name: 'Actual FR', data: props.actualFr },
         { name: 'XGBoost Forecast FR', data: props.forecastFr }
     ]);
     </script>

     <template>
         <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-100">
             <h3 class="text-base font-bold text-slate-800 mb-4">1. XGBoost Forecasting & Dynamic Thresholds</h3>
             <VueApexCharts type="line" height="350" :options="chartOptions" :series="series" />
         </div>
     </template>
     ```
  3. Implementasikan Component `AnomalyMapChart.vue` (Vue3 ApexCharts Scatter Plot per unit).
  4. Implementasikan Component `CapacityBarChart.vue` (Bar Chart alokasi BBM per aktivitas).

---

### 📌 Sprint 10: Reports & Export Interface
- **Langkah Pengerjaan:**
  1. Buat Halaman `Pages/Reports/SpikeReport.vue` (Tabel sortable per unit dengan Vue reactive state).
  2. Buat Halaman `Pages/Reports/ActivityReport.vue` (Tabel agregat per aktivitas).
  3. Buat Halaman `Pages/Reports/CapacityReport.vue` (Tabel alokasi & utilisasi armada).
  4. Tombol "Export PDF" dan "Export Excel" yang memanggil endpoint Laravel backend.

---

### 📌 Sprint 11 & 12: Conversational Chatbot Widget & Disambiguation UI Vue 3 (Solusi Celah #8)
- **Langkah Pengerjaan:**
  1. Buat Komponen `Components/Chatbot/ChatbotWidget.vue` (Vue 3 Floating Chat Window):
     ```vue
     <script setup>
     import { ref } from 'vue';

     const isOpen = ref(false);
     const inputMessage = ref('');
     const messages = ref([]);
     const isStreaming = ref(false);

     const sendMessage = async () => {
         if (!inputMessage.value.trim() || isStreaming.value) return;

         const userText = inputMessage.value;
         messages.value.push({ sender: 'user', text: userText });
         inputMessage.value = '';
         
         const assistantMsgIndex = messages.value.length;
         messages.value.push({ sender: 'assistant', text: '', pills: [] });
         isStreaming.value = true;

         try {
             const response = await fetch('/api/chatbot/stream', {
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
                 body: JSON.stringify({ message: userText })
             });
             const reader = response.body.getReader();
             const decoder = new TextDecoder();

             while (true) {
                 const { value, done } = await reader.read();
                 if (done) break;
                 const chunk = decoder.decode(value);
                 messages.value[assistantMsgIndex].text += chunk;
             }
         } catch (err) {
             messages.value[assistantMsgIndex].text = "Terjadi kesalahan koneksi.";
         } finally {
             isStreaming.value = false;
         }
     };

     const selectPill = (pillValue) => {
         inputMessage.value = pillValue;
         sendMessage();
     };
     </script>

     <template>
         <div class="fixed bottom-6 right-6 z-50">
             <!-- Chat Toggle Button -->
             <button @click="isOpen = !isOpen" class="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition">
                 AI Assistant
             </button>

             <!-- Chat Popup Window -->
             <div v-if="isOpen" class="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
                 <div class="bg-slate-900 text-white p-4 font-bold flex justify-between items-center">
                     <span>Direct DB Chatbot</span>
                     <button @click="isOpen = false" class="text-slate-400 hover:text-white">✕</button>
                 </div>

                 <div class="flex-1 p-4 overflow-y-auto space-y-3">
                     <div v-for="(msg, idx) in messages" :key="idx" :class="msg.sender === 'user' ? 'text-right' : 'text-left'">
                         <div :class="msg.sender === 'user' ? 'bg-blue-600 text-white inline-block p-3 rounded-2xl text-sm' : 'bg-slate-100 text-slate-800 inline-block p-3 rounded-2xl text-sm'">
                             {{ msg.text }}
                         </div>
                         <!-- Disambiguation Pill Buttons (Celah #8) -->
                         <div v-if="msg.pills && msg.pills.length" class="mt-2 flex flex-wrap gap-1">
                             <button v-for="pill in msg.pills" :key="pill" @click="selectPill(pill)" class="text-xs bg-blue-50 text-blue-600 border border-blue-200 px-2 py-1 rounded-full hover:bg-blue-100">
                                 {{ pill }}
                             </button>
                         </div>
                     </div>
                 </div>

                 <div class="p-3 border-t border-slate-100 flex gap-2">
                     <input v-model="inputMessage" @keyup.enter="sendMessage" placeholder="Tanyakan data FR / unit..." class="flex-1 text-sm border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:border-blue-500" />
                     <button @click="sendMessage" :disabled="isStreaming" class="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
                         Kirim
                     </button>
                 </div>
             </div>
         </div>
     </template>
     ```
