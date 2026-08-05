<script setup lang="ts">
interface Message {
  id: number
  sender: 'user' | 'ai'
  text: string
  timestamp: string
}

const quickPrompts = [
  'Mengapa prediksi FR besok naik ke 1.285 L/BCM?',
  'Simulasi matikan 5 unit HD785-7 anomali spike',
  'Tampilkan unit excavator di bawah SPO hari ini',
]

const messages = ref<Message[]>([
  {
    id: 1,
    sender: 'ai',
    text: 'Halo! Saya **Mining Fuel AI Assistant**. Saya tersambung ke FMS Sensor, XGBoost Regressor, dan PyTorch Anomaly Engine. Ada yang bisa saya bantu analisa hari ini?',
    timestamp: '10:00 WITA',
  },
  {
    id: 2,
    sender: 'user',
    text: 'Mengapa prediksi Fuel Ratio untuk besok naik menjadi 1.285 L/BCM dan berstatus WARNING?',
    timestamp: '10:02 WITA',
  },
  {
    id: 3,
    sender: 'ai',
    text: `Berdasarkan model prediktif XGBoost Regressor, kenaikan FR besok (**1.285 L/BCM** vs Baseline **1.1576 L/BCM**) dipicu oleh 3 faktor utama:

1. 🌧️ **Prakiraan Curah Hujan:** API Open-Meteo mendeteksi hujan sebesar **35.2 mm** di pit Bontang.
2. 🛣️ **Ekspansi Jarak Angkut:** Jarak angkut Hauling HD785 membengkak dari 3,900m menjadi **4,181m** (+281m akibat jalan licin).
3. 💧 **Lonjakan Dewatering:** Beban solar pompa Dewatering melonjak +158.4% (membutuhkan tambahan **+24,670 Liter** solar).

💡 **Saran Mitigasi:** Kurangi 12 unit Hauling HD785-7 yang berada di pit berlumpur dan alokasikan solar ke pompa EWP420.`,
    timestamp: '10:02 WITA',
  },
])

const inputQuery = ref('')
const isTyping = ref(false)

const handleSend = (queryText?: string) => {
  const query = queryText || inputQuery.value.trim()
  if (!query) return

  messages.value.push({
    id: Date.now(),
    sender: 'user',
    text: query,
    timestamp: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA',
  })

  inputQuery.value = ''
  isTyping.value = true

  setTimeout(() => {
    isTyping.value = false
    let responseText = ''

    if (query.toLowerCase().includes('matikan') || query.toLowerCase().includes('simulasi')) {
      responseText = `Melakukan kalkulasi pada Combined Capacity Engine...

- 🚜 **Unit EX2600-6 (EX-2601):** Menghemat konsumsi anomali 192.28 L/jam (**3.845,6 L/hari**).
- 🚛 **5 Unit HD785-7 (Anomali Spike):** Menghemat rerata konsumsi 80.78 L/jam/unit (total **8.078,0 L/hari**).

📉 **Total Penghematan Solar:** **11.923,6 Liter / Hari**.
💰 **Estimasi Penghematan Biaya** (BBM Industri Rp 14.500/L): **Rp 172.892.200,- per hari**.

Target BCM harian tetap aman karena utilisasi kapasitas hauling saat ini baru **22.46%**.`
    } else if (query.toLowerCase().includes('excavator') || query.toLowerCase().includes('spo')) {
      responseText = `Berikut adalah 3 Unit Excavator yang beroperasi di bawah SPO hari ini:

1. **PC2000-11R (EX-2004)** | FC Actual: **185.53 L/hr** (SPO: 100.0 L/hr | Deviasi **+85.5%**) | Total: **10.900,0 L/hari**.
2. **PC2000-8 (EX-2012)** | FC Actual: **180.75 L/hr** (SPO: 100.0 L/hr | Deviasi **+80.8%**) | Total: **10.800,0 L/hari**.
3. **EX2600-6 (EX-2601)** | FC Actual: **192.28 L/hr** (SPO: 187.0 L/hr | Deviasi **+2.8%**) | Total: **17.428,4 L/hari**.

📋 **Rekomendasi:** WO Maintenance telah dibuat otomatis untuk pemeriksaan kelayakan sistem hidrolik dan injektor EX-2004 & EX-2012.`
    } else {
      responseText = `Berdasarkan FMS database dan model inferensi XGBoost/PyTorch:
      
- Fuel Ratio Aktual: **1.2800 L/BCM** (Status: **WARNING +8%**)
- Unit Terdeteksi Anomali: **61 Unit** (375 Spike Events)
- Open-Meteo Weather: **0.0 mm/hr** (Haul Dist standard: 3,900m)

Silakan ajukan simulasi skenario lain atau tanyakan rincian SPO armada.`
    }

    messages.value.push({
      id: Date.now() + 1,
      sender: 'ai',
      text: responseText,
      timestamp: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA',
    })
  }, 800)
}

const renderMarkdown = (text: string) => {
  // Simple markdown renderer for bold, lists, and linebreaks
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}
</script>

<template>
  <VCard class="d-flex flex-column" style="height: 600px;">
    <!-- Chat Header -->
    <VCardItem class="border-b py-3">
      <template #prepend>
        <VAvatar
          color="primary"
          variant="tonal"
          size="40"
          rounded
        >
          <VIcon
            icon="bx-bot"
            size="24"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-bold">
        Mining Fuel AI Assistant
      </VCardTitle>
      <VCardSubtitle class="d-flex align-center gap-1 text-caption">
        <span class="online-indicator" />
        <span>Connected to FMS & XGBoost Engine</span>
      </VCardSubtitle>
    </VCardItem>

    <!-- Chat Messages Scroll Area -->
    <VCardText class="flex-grow-1 overflow-y-auto pa-4">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="d-flex flex-column mb-4"
        :class="msg.sender === 'user' ? 'align-end' : 'align-start'"
      >
        <div
          class="pa-3 rounded-lg text-body-2"
          :class="msg.sender === 'user' ? 'bg-primary text-white' : 'bg-surface border'"
          style="max-width: 85%;"
          v-html="renderMarkdown(msg.text)"
        />
        <span class="text-caption text-medium-emphasis mt-1 px-1">
          {{ msg.timestamp }}
        </span>
      </div>

      <div
        v-if="isTyping"
        class="d-flex align-center gap-2 text-caption text-medium-emphasis"
      >
        <VProgressCircular
          indeterminate
          size="16"
          width="2"
          color="primary"
        />
        <span>AI sedang menganalisis data FMS & model prediktif...</span>
      </div>
    </VCardText>

    <!-- Quick Prompts Chips -->
    <div class="px-4 py-2 border-t d-flex gap-2 flex-wrap bg-surface">
      <VChip
        v-for="(prompt, idx) in quickPrompts"
        :key="idx"
        size="small"
        variant="tonal"
        color="primary"
        class="cursor-pointer"
        @click="handleSend(prompt)"
      >
        {{ prompt }}
      </VChip>
    </div>

    <!-- Input Bar -->
    <VCardActions class="pa-3 border-t">
      <VTextField
        v-model="inputQuery"
        placeholder="Tanyakan analisa / simulasi BBM (misal: 'Penyebab FR naik?')..."
        density="compact"
        hide-details
        @keydown.enter="handleSend()"
      >
        <template #append-inner>
          <VBtn
            icon="bx-send"
            color="primary"
            variant="text"
            size="small"
            :disabled="!inputQuery.trim()"
            @click="handleSend()"
          />
        </template>
      </VTextField>
    </VCardActions>
  </VCard>
</template>

<style lang="scss" scoped>
.online-indicator {
  display: inline-block;
  background: #34A853;
  block-size: 8px;
  border-radius: 50%;
  inline-size: 8px;
}
</style>
