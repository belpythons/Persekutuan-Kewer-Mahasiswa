<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'
import type { ReadyResponse } from '@/composables/useAiApi'

const { fetchAiReady } = useAiApi()

const isLoading = ref(true)
const aiReady = ref<ReadyResponse | null>(null)

// Default metrics (fallback when AI service unavailable)
const defaultMetrics = [
  { label: 'XGBoost R² Score', value: '0.9901', change: '+0.002 vs baseline', color: 'success', icon: 'bx-line-chart' },
  { label: 'MAE Error Rate', value: '0.0045 L/BCM', change: '-12% residual error', color: 'primary', icon: 'bx-crosshair' },
  { label: 'PyTorch P93.5 Threshold', value: '0.0412', change: '8 Latent Dimensions', color: 'warning', icon: 'bx-shield-quarter' },
  { label: 'Model Pipeline', value: 'v3.3 / v2.11', change: 'Production Ready', color: 'info', icon: 'bx-check-double' },
]

const metrics = computed(() => {
  if (!aiReady.value || aiReady.value.error) return defaultMetrics

  const w = aiReady.value.warmup_details
  return [
    {
      label: 'XGBoost Regressor',
      value: w.xgboost_warmed_up ? 'Ready' : 'Not Loaded',
      change: w.xgboost_warmup_ms ? `Warmup: ${w.xgboost_warmup_ms.toFixed(1)}ms` : 'Pending',
      color: w.xgboost_warmed_up ? 'success' : 'error',
      icon: 'bx-line-chart',
    },
    {
      label: 'PyTorch Autoencoder',
      value: w.pytorch_autoencoder_warmed_up ? 'Ready' : 'Not Loaded',
      change: w.pytorch_warmup_ms ? `Warmup: ${w.pytorch_warmup_ms.toFixed(1)}ms` : 'Pending',
      color: w.pytorch_autoencoder_warmed_up ? 'success' : 'error',
      icon: 'bx-shield-quarter',
    },
    {
      label: 'Total Warmup',
      value: w.warmup_duration_ms ? `${w.warmup_duration_ms.toFixed(1)}ms` : 'N/A',
      change: `DB: ${w.database_status}`,
      color: aiReady.value.status === 'ready' ? 'primary' : 'warning',
      icon: 'bx-timer',
    },
    {
      label: 'Service Status',
      value: aiReady.value.status === 'ready' ? 'Online' : 'Offline',
      change: aiReady.value.status === 'ready' ? 'Production Ready' : 'Service Unavailable',
      color: aiReady.value.status === 'ready' ? 'info' : 'error',
      icon: aiReady.value.status === 'ready' ? 'bx-check-double' : 'bx-x-circle',
    },
  ]
})

const serviceStatus = computed(() => {
  if (isLoading.value) return 'loading'
  if (!aiReady.value || aiReady.value.error) return 'offline'
  return aiReady.value.status === 'ready' ? 'ready' : 'not_ready'
})

onMounted(async () => {
  try {
    aiReady.value = await fetchAiReady()
  } catch {
    aiReady.value = null
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <VCard>
    <VCardItem>
      <template #prepend>
        <VAvatar
          :color="serviceStatus === 'ready' ? 'success' : serviceStatus === 'loading' ? 'info' : 'error'"
          variant="tonal"
          size="48"
          rounded
        >
          <VProgressCircular
            v-if="isLoading"
            indeterminate
            size="24"
            width="2"
          />
          <VIcon
            v-else
            :icon="serviceStatus === 'ready' ? 'bx-check-shield' : 'bx-shield-x'"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        AI Model Performance Metrics
      </VCardTitle>
      <VCardSubtitle>
        <template v-if="serviceStatus === 'ready'">
          AI Engine Online — XGBoost & PyTorch Ready
        </template>
        <template v-else-if="isLoading">
          Checking AI service readiness...
        </template>
        <template v-else>
          AI Engine Offline — Menampilkan metrik default
        </template>
      </VCardSubtitle>
    </VCardItem>

    <VCardText class="pa-4">
      <VRow class="gy-4 gx-4">
        <VCol
          v-for="item in metrics"
          :key="item.label"
          cols="12"
          sm="6"
        >
          <VCard
            variant="outlined"
            class="pa-4 text-center h-100 d-flex flex-column justify-center align-center"
          >
            <VAvatar
              :color="item.color"
              variant="tonal"
              size="36"
              rounded
              class="mb-2"
            >
              <VIcon
                :icon="item.icon"
                size="20"
              />
            </VAvatar>
            <div class="text-caption text-medium-emphasis mb-1">
              {{ item.label }}
            </div>
            <h6 class="text-h6 font-weight-bold">
              {{ item.value }}
            </h6>
            <span
              class="text-caption"
              :class="`text-${item.color}`"
            >{{ item.change }}</span>
          </VCard>
        </VCol>
      </VRow>
    </VCardText>
  </VCard>
</template>
