<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'

interface Message {
  id: number
  sender: 'user' | 'ai'
  text: string
  timestamp: string
  source?: string
}

const { fetchChatbotQuery } = useAiApi()

const quickPrompts = [
  'Mengapa prediksi FR besok naik ke 1.285 L/BCM?',
  'Berapa total BBM kombinasi armada hari ini?',
  'Tampilkan unit excavator anomali spike hari ini',
]

const messages = ref<Message[]>([
  {
    id: 1,
    sender: 'ai',
    text: 'Halo! Saya **Mining Fuel AI Assistant**. Saya tersambung ke Database FMS, XGBoost Regressor, PyTorch Anomaly Engine, dan Gemini AI. Ada yang bisa saya bantu analisa hari ini?',
    timestamp: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA',
    source: 'KIDECO AI ENGINE',
  },
])

const inputQuery = ref('')
const isTyping = ref(false)

const handleSend = async (queryText?: string) => {
  const query = queryText || inputQuery.value.trim()
  if (!query || isTyping.value) return

  const userTimestamp = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA'

  messages.value.push({
    id: Date.now(),
    sender: 'user',
    text: query,
    timestamp: userTimestamp,
  })

  inputQuery.value = ''
  isTyping.value = true

  try {
    const res = await fetchChatbotQuery(query)
    const aiTimestamp = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA'

    messages.value.push({
      id: Date.now() + 1,
      sender: 'ai',
      text: res.response || 'Tidak ada respon dari server AI.',
      timestamp: aiTimestamp,
      source: res.source || 'DATABASE & GEMINI AI',
    })
  } catch (error) {
    console.error('Failed to query Chatbot API:', error)
    messages.value.push({
      id: Date.now() + 1,
      sender: 'ai',
      text: 'Gagal terhubung ke AI Chatbot Service. Silakan periksa koneksi backend.',
      timestamp: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA',
      source: 'ERROR',
    })
  } finally {
    isTyping.value = false
  }
}

const renderMarkdown = (text: string) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}
</script>

<template>
  <VCard class="d-flex flex-column h-100" style="min-height: 520px;">
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
        <span>Gemini AI & Real DB Context Connected</span>
      </VCardSubtitle>
    </VCardItem>

    <!-- Chat Messages Scroll Area -->
    <VCardText class="flex-grow-1 overflow-y-auto pa-4" style="max-height: 460px;">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="d-flex flex-column mb-4"
        :class="msg.sender === 'user' ? 'align-end' : 'align-start'"
      >
        <div
          class="pa-3 rounded-lg text-body-2"
          :class="msg.sender === 'user' ? 'bg-primary text-white' : 'bg-surface border'"
          style="max-width: 90%;"
          v-html="renderMarkdown(msg.text)"
        />
        <div class="d-flex align-center gap-2 mt-1 px-1 text-caption text-medium-emphasis">
          <span>{{ msg.timestamp }}</span>
          <span v-if="msg.source" class="text-primary font-weight-medium">• {{ msg.source }}</span>
        </div>
      </div>

      <div
        v-if="isTyping"
        class="d-flex align-center gap-2 text-caption text-medium-emphasis my-2"
      >
        <VProgressCircular
          indeterminate
          size="16"
          width="2"
          color="primary"
        />
        <span>AI sedang menganalisis data database & model Gemini...</span>
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
        placeholder="Tanyakan analisa BBM pertambangan..."
        density="compact"
        hide-details
        :disabled="isTyping"
        @keydown.enter="handleSend()"
      >
        <template #append-inner>
          <VBtn
            icon="bx-send"
            color="primary"
            variant="text"
            size="small"
            :disabled="!inputQuery.trim() || isTyping"
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
