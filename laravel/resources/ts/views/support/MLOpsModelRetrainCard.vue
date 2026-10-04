<script setup lang="ts">
import { useAiApi, AiApiError } from '@/composables/useAiApi'
import type { ReadyResponse, ModelMetricsResponse } from '@/composables/useAiApi'

const { fetchAiReady, fetchModelMetrics, retrainModels } = useAiApi()

const isRetraining = ref(false)
const retrainError = ref('')
const statusMessage = ref('')

const aiReady = ref<ReadyResponse | null>(null)
const modelMetrics = ref<ModelMetricsResponse | null>(null)
const isLoadingStatus = ref(true)

async function loadStatus() {
  isLoadingStatus.value = true
  try {
    const [readyResult, metricsResult] = await Promise.allSettled([fetchAiReady(), fetchModelMetrics()])
    aiReady.value = readyResult.status === 'fulfilled' ? readyResult.value : null
    modelMetrics.value = metricsResult.status === 'fulfilled' ? metricsResult.value : null
  } finally {
    isLoadingStatus.value = false
  }
}

onMounted(loadStatus)

async function triggerRetrain() {
  isRetraining.value = true
  retrainError.value = ''
  statusMessage.value = 'Melatih ulang XGBoost & PyTorch Autoencoder dari data terkini...'
  try {
    const result = await retrainModels()
    if (result.errors.length > 0)
      statusMessage.value = `Retrain selesai dengan peringatan: ${result.errors.join('; ')}`
    else
      statusMessage.value = 'Retraining selesai — model & metrik telah diperbarui.'

    await loadStatus()
  } catch (e: unknown) {
    retrainError.value = e instanceof AiApiError ? e.message : 'Gagal menjalankan retraining'
    statusMessage.value = ''
  } finally {
    isRetraining.value = false
  }
}

const xgboostStatus = computed(() => {
  if (isLoadingStatus.value) return 'Checking...'
  if (!aiReady.value || aiReady.value.error) return 'Offline'
  return aiReady.value.warmup_details.xgboost_warmed_up ? 'Trained' : 'Not Loaded'
})

const pytorchStatus = computed(() => {
  if (isLoadingStatus.value) return 'Checking...'
  if (!aiReady.value || aiReady.value.error) return 'Offline'
  return aiReady.value.warmup_details.pytorch_autoencoder_warmed_up ? 'Trained' : 'Not Loaded'
})

const xgbMetrics = computed(() => modelMetrics.value?.xgboost?.metrics ?? null)
const aeEvaluation = computed(() => modelMetrics.value?.autoencoder?.evaluation ?? null)
</script>

<template>
  <VCard>
    <VCardItem>
      <template #prepend>
        <VAvatar
          color="info"
          variant="tonal"
          size="48"
          rounded
        >
          <VIcon
            icon="bx-brain"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        MLOps AI Model Control Panel
      </VCardTitle>
      <VCardSubtitle>Retraining Pipeline & Status Evaluasi Riil</VCardSubtitle>
      <template #append>
        <VChip
          v-if="!isLoadingStatus && aiReady && !aiReady.error"
          color="success"
          size="small"
          variant="tonal"
        >
          <VIcon icon="bx-check-circle" start size="14" />
          Live AI
        </VChip>
      </template>
    </VCardItem>

    <VCardText>
      <VRow class="mb-2">
        <VCol cols="12" sm="6">
          <VCard variant="outlined" class="pa-3">
            <div class="d-flex align-center justify-space-between mb-1">
              <span class="font-weight-bold">XGBoost Regressor</span>
              <VChip
                :color="xgboostStatus === 'Trained' ? 'success' : 'warning'"
                size="small"
                variant="tonal"
              >
                {{ xgboostStatus }}
              </VChip>
            </div>
            <div class="text-caption text-medium-emphasis">
              Formula: BCM, Fuel & FR Forecasting
            </div>
            <div class="d-flex justify-space-between mt-2 text-caption text-tabular-nums">
              <span>R² Score: <strong>{{ xgbMetrics?.final_full_r2 !== undefined ? xgbMetrics.final_full_r2.toFixed(4) : 'N/A' }}</strong></span>
              <span>MAE: <strong>{{ xgbMetrics?.final_full_mae !== undefined ? `${xgbMetrics.final_full_mae.toFixed(5)} L/BCM` : 'N/A' }}</strong></span>
            </div>
          </VCard>
        </VCol>

        <VCol cols="12" sm="6">
          <VCard variant="outlined" class="pa-3">
            <div class="d-flex align-center justify-space-between mb-1">
              <span class="font-weight-bold">PyTorch Autoencoder</span>
              <VChip
                :color="pytorchStatus === 'Trained' ? 'success' : 'warning'"
                size="small"
                variant="tonal"
              >
                {{ pytorchStatus }}
              </VChip>
            </div>
            <div class="text-caption text-medium-emphasis">
              Normal Data (NN_Anomaly_Spike == 0)
            </div>
            <div class="d-flex justify-space-between mt-2 text-caption text-tabular-nums">
              <span>Precision: <strong>{{ aeEvaluation?.precision !== undefined ? `${(aeEvaluation.precision * 100).toFixed(1)}%` : 'N/A' }}</strong></span>
              <span>Recall: <strong>{{ aeEvaluation?.recall !== undefined ? `${(aeEvaluation.recall * 100).toFixed(1)}%` : 'N/A' }}</strong></span>
            </div>
          </VCard>
        </VCol>
      </VRow>

      <VAlert v-if="retrainError" type="error" variant="tonal" density="compact" class="my-3">
        {{ retrainError }}
      </VAlert>
      <div v-else-if="statusMessage" class="d-flex align-center my-3 text-caption text-medium-emphasis">
        <span>Status: <strong class="text-info">{{ statusMessage }}</strong></span>
      </div>

      <VProgressLinear
        v-if="isRetraining"
        indeterminate
        color="primary"
        height="6"
        rounded
        class="mb-3"
      />

      <VBtn
        color="info"
        variant="tonal"
        block
        prepend-icon="bx-refresh"
        :loading="isRetraining"
        :disabled="isRetraining"
        @click="triggerRetrain"
      >
        Trigger Model Retraining Pipeline
      </VBtn>
    </VCardText>
  </VCard>
</template>
