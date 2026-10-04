<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'

interface Message {
  id: number
  sender: 'user' | 'ai'
  text: string
  timestamp: string
  source?: string
}

const { fetchChatbotQuery, fetchAiReady } = useAiApi()

const quickPrompts = [
  'Kenapa prediksi FR besok naik dibanding hari ini?',
  'Berapa total BBM kombinasi armada hari ini?',
  'Tampilkan unit excavator anomali spike hari ini',
]

function timestamp() {
  return new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA'
}

const messages = ref<Message[]>([
  {
    id: 1,
    sender: 'ai',
    text: 'Halo! Saya **KIDECO Dispatch & Fuel Co-pilot**. Tanyakan prediksi Fuel Ratio, alokasi solar armada, atau unit yang terdeteksi anomali konsumsi BBM hari ini.',
    timestamp: timestamp(),
    source: 'KIDECO AI ENGINE',
  },
])

const inputQuery = ref('')
const isTyping = ref(false)

// Real connection status instead of a status line that was always on regardless of whether
// Gemini/the AI service was actually reachable.
const isConnected = ref(false)
const isCheckingStatus = ref(true)

onMounted(async () => {
  try {
    const ready = await fetchAiReady()
    isConnected.value = ready.status === 'ready'
  } catch {
    isConnected.value = false
  } finally {
    isCheckingStatus.value = false
  }
})

const handleSend = async (queryText?: string) => {
  const query = queryText || inputQuery.value.trim()
  if (!query || isTyping.value) return

  messages.value.push({
    id: Date.now(),
    sender: 'user',
    text: query,
    timestamp: timestamp(),
  })

  inputQuery.value = ''
  isTyping.value = true

  try {
    const res = await fetchChatbotQuery(query)
    messages.value.push({
      id: Date.now() + 1,
      sender: 'ai',
      text: res.response || 'Tidak ada respon dari server AI.',
      timestamp: timestamp(),
      source: res.source || 'DATABASE & GEMINI AI',
    })
  } catch (error) {
    console.error('Failed to query Chatbot API:', error)
    messages.value.push({
      id: Date.now() + 1,
      sender: 'ai',
      text: 'Gagal terhubung ke AI Chatbot Service. Silakan periksa koneksi backend.',
      timestamp: timestamp(),
      source: 'ERROR',
    })
  } finally {
    isTyping.value = false
  }
}

const escapeHtml = (text: string) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// Escape first so raw HTML/script in a user message or an echoed query can never execute,
// then apply the only two markdown constructs this chat actually produces (bold, line breaks).
const renderMarkdown = (text: string) => {
  return escapeHtml(text)
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
        KIDECO Dispatch & Fuel Co-pilot
      </VCardTitle>
      <VCardSubtitle class="d-flex align-center gap-1 text-caption">
        <span v-if="!isCheckingStatus" class="online-indicator" :class="{ 'online-indicator--offline': !isConnected }" />
        <span>
          <template v-if="isCheckingStatus">Memeriksa koneksi AI Engine...</template>
          <template v-else-if="isConnected">AI Engine Connected</template>
          <template v-else>AI Engine Offline — respons fallback</template>
        </span>
      </VCardSubtitle>
    </VCardItem>

    <!-- Chat Messages Scroll Area -->
    <VCardText class="flex-grow-1 overflow-y-auto pa-4 d-flex flex-column gap-3" style="max-height: 440px;">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="d-flex flex-column"
        :class="msg.sender === 'user' ? 'align-end' : 'align-start'"
      >
        <div
          class="pa-3 rounded-lg text-body-2 lh-relaxed"
          :class="msg.sender === 'user' ? 'bg-primary text-white' : 'bg-surface border'"
          style="max-width: 90%; line-height: 1.5;"
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
        <span>AI sedang menganalisis data database...</span>
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
  background: rgb(var(--v-theme-success));
  block-size: 8px;
  border-radius: 50%;
  inline-size: 8px;
}

.online-indicator--offline {
  background: rgb(var(--v-theme-error));
}
</style>
