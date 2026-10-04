<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'
import type { ReadyResponse, ModelMetricsResponse } from '@/composables/useAiApi'

const { fetchAiReady, fetchModelMetrics } = useAiApi()

const isLoading = ref(true)
const aiReady = ref<ReadyResponse | null>(null)
const modelMetrics = ref<ModelMetricsResponse | null>(null)
const hasError = ref(false)

const metrics = computed(() => {
  const xgb = modelMetrics.value?.xgboost?.metrics
  const ae = modelMetrics.value?.autoencoder

  const items = []

  if (xgb) {
    items.push({
      label: 'XGBoost R² Score',
      value: xgb.final_full_r2 !== undefined ? xgb.final_full_r2.toFixed(4) : 'N/A',
      change: xgb.avg_cv_r2 !== undefined ? `CV R²: ${xgb.avg_cv_r2.toFixed(4)}` : '',
      color: 'success',
      icon: 'bx-line-chart',
    })
    items.push({
      label: 'XGBoost MAE',
      value: xgb.final_full_mae !== undefined ? `${xgb.final_full_mae.toFixed(5)} L/BCM` : 'N/A',
      change: xgb.avg_cv_mae !== undefined ? `CV MAE: ${xgb.avg_cv_mae.toFixed(5)}` : '',
      color: 'primary',
      icon: 'bx-crosshair',
    })
  }

  if (ae) {
    items.push({
      label: 'Autoencoder Precision',
      value: ae.evaluation.precision !== undefined ? `${(ae.evaluation.precision * 100).toFixed(1)}%` : 'N/A',
      change: `Recall: ${ae.evaluation.recall !== undefined ? (ae.evaluation.recall * 100).toFixed(1) : 'N/A'}%`,
      color: 'warning',
      icon: 'bx-shield-quarter',
    })
  }

  items.push({
    label: 'Service Status',
    value: aiReady.value?.status === 'ready' ? 'Online' : 'Offline',
    change: aiReady.value?.status === 'ready' ? 'Production Ready' : 'AI Service Unavailable',
    color: aiReady.value?.status === 'ready' ? 'info' : 'error',
    icon: aiReady.value?.status === 'ready' ? 'bx-check-double' : 'bx-x-circle',
  })

  return items
})

const serviceStatus = computed(() => {
  if (isLoading.value) return 'loading'
  if (hasError.value) return 'offline'
  return aiReady.value?.status === 'ready' ? 'ready' : 'not_ready'
})

async function load() {
  isLoading.value = true
  hasError.value = false
  try {
    const [readyResult, metricsResult] = await Promise.allSettled([
      fetchAiReady(),
      fetchModelMetrics(),
    ])
    aiReady.value = readyResult.status === 'fulfilled' ? readyResult.value : null
    modelMetrics.value = metricsResult.status === 'fulfilled' ? metricsResult.value : null
    // Metrics come from a file written at training time — their absence doesn't mean the
    // service is down, only that no model has been trained yet. Treat it as empty, not error.
    hasError.value = readyResult.status === 'rejected'
  } catch {
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

onMounted(load)
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
          AI Engine Online — Metrik evaluasi dari training terakhir
        </template>
        <template v-else-if="isLoading">
          Checking AI service readiness...
        </template>
        <template v-else>
          AI Engine Offline
        </template>
      </VCardSubtitle>
      <template v-if="!isLoading && hasError" #append>
        <VBtn size="small" variant="tonal" color="primary" @click="load">
          Coba Lagi
        </VBtn>
      </template>
    </VCardItem>

    <VCardText class="pa-4">
      <div v-if="isLoading" class="d-flex justify-center my-6">
        <VProgressCircular indeterminate color="primary" />
      </div>
      <div v-else-if="hasError" class="d-flex flex-column align-center justify-center text-center py-6">
        <VIcon icon="bx-error-circle" size="40" class="text-error mb-3" />
        <p class="text-body-2 text-medium-emphasis">Gagal memuat status & metrik AI engine.</p>
      </div>
      <VRow v-else class="gy-4 gx-4">
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
            <h6 class="text-h6 font-weight-bold text-tabular-nums">
              {{ item.value }}
            </h6>
            <span
              class="text-caption text-tabular-nums"
              :class="`text-${item.color}`"
            >{{ item.change }}</span>
          </VCard>
        </VCol>
      </VRow>
    </VCardText>
  </VCard>
</template>
