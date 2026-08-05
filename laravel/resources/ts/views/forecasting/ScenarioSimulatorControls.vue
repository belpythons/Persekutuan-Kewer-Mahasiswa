<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'
import type { ForecastResponse } from '@/composables/useAiApi'

const { fetchForecast } = useAiApi()

const rainfallMm = ref(35.2)
const tempMaxC = ref(32.0)
const windKmh = ref(14.2)
const haulDistanceM = ref(4181)
const targetBcm = ref(250072)

const isLoading = ref(false)
const aiResult = ref<ForecastResponse | null>(null)
const errorMsg = ref('')

// Local formula fallback (used when AI is not available or before first call)
const localPredictedFr = computed(() => {
  const rainImpact = rainfallMm.value * 0.0022
  const haulImpact = ((haulDistanceM.value - 3900) / 1000) * 0.08
  return Number((1.1576 + rainImpact + haulImpact).toFixed(4))
})

// Use AI result if available, otherwise local formula
const predictedFr = computed(() => {
  return aiResult.value ? aiResult.value.forecast_fr : localPredictedFr.value
})

const predictedFuelL = computed(() => {
  return Math.round(targetBcm.value * predictedFr.value)
})

const budgetBaseline = computed(() => aiResult.value?.budget_baseline ?? 1.1576)
const warningThreshold = computed(() => aiResult.value?.warning_threshold ?? 1.2503)
const criticalThreshold = computed(() => aiResult.value?.critical_threshold ?? 1.3660)

const status = computed(() => {
  if (predictedFr.value >= criticalThreshold.value) return { label: 'CRITICAL (+18%)', color: 'error', icon: 'bx-error-circle' }
  if (predictedFr.value >= warningThreshold.value) return { label: 'WARNING (+8%)', color: 'warning', icon: 'bx-error' }
  return { label: 'NORMAL', color: 'success', icon: 'bx-check-circle' }
})

const aiStatus = computed(() => {
  if (!aiResult.value) return aiResult.value === null ? null : 'error'
  return aiResult.value.fallback ? 'fallback' : 'live'
})

const runForecast = async () => {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const today = new Date().toISOString().slice(0, 10)
    const result = await fetchForecast({
      date: today,
      curah_hujan_mm: rainfallMm.value,
      temp_max_c: tempMaxC.value,
      kecepatan_angin_kmh: windKmh.value,
      haul_distance_m: haulDistanceM.value,
      daily_prod_bcm: targetBcm.value,
    })
    aiResult.value = result
  } catch (e: any) {
    errorMsg.value = e.message || 'Gagal menghubungi AI Service'
  } finally {
    isLoading.value = false
  }
}

const resetDefaults = () => {
  rainfallMm.value = 0
  tempMaxC.value = 32.0
  windKmh.value = 14.2
  haulDistanceM.value = 3900
  targetBcm.value = 250072
  aiResult.value = null
  errorMsg.value = ''
}

onMounted(() => {
  runForecast()
})
</script>

<template>
  <VCard>
    <VCardItem>
      <template #prepend>
        <VAvatar
          color="primary"
          variant="tonal"
          size="48"
          rounded
        >
          <VIcon
            icon="bx-slider"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        Forecast Scenario Simulator
      </VCardTitle>
      <VCardSubtitle>Simulasi variabel cuaca, jarak angkut, dan target produksi</VCardSubtitle>
      <template #append>
        <div class="d-flex gap-2">
          <VChip
            v-if="aiStatus === 'live'"
            color="success"
            size="small"
            variant="tonal"
          >
            <VIcon
              icon="bx-check-circle"
              start
              size="14"
            />
            AI Live
          </VChip>
          <VChip
            v-else-if="aiStatus === 'fallback'"
            color="warning"
            size="small"
            variant="tonal"
          >
            Fallback Mode
          </VChip>
          <VBtn
            size="small"
            variant="text"
            prepend-icon="bx-reset"
            @click="resetDefaults"
          >
            Reset
          </VBtn>
        </div>
      </template>
    </VCardItem>

    <VCardText>
      <VRow>
        <VCol
          cols="12"
          md="4"
        >
          <div class="d-flex justify-space-between mb-1">
            <span class="text-body-2 text-medium-emphasis">Curah Hujan (mm/hr)</span>
            <strong>{{ rainfallMm }} mm</strong>
          </div>
          <VSlider
            v-model="rainfallMm"
            :min="0"
            :max="80"
            :step="0.5"
            color="info"
            thumb-label
          />
        </VCol>

        <VCol
          cols="12"
          md="4"
        >
          <div class="d-flex justify-space-between mb-1">
            <span class="text-body-2 text-medium-emphasis">Jarak Angkut (m)</span>
            <strong>{{ haulDistanceM.toLocaleString('id-ID') }} m</strong>
          </div>
          <VSlider
            v-model="haulDistanceM"
            :min="3000"
            :max="6000"
            :step="50"
            color="primary"
            thumb-label
          />
        </VCol>

        <VCol
          cols="12"
          md="4"
        >
          <div class="d-flex justify-space-between mb-1">
            <span class="text-body-2 text-medium-emphasis">Target Produksi (BCM)</span>
            <strong>{{ targetBcm.toLocaleString('id-ID') }} BCM</strong>
          </div>
          <VSlider
            v-model="targetBcm"
            :min="150000"
            :max="350000"
            :step="5000"
            color="success"
            thumb-label
          />
        </VCol>
      </VRow>

      <!-- Run Forecast Button -->
      <div class="d-flex justify-end mb-3">
        <VBtn
          color="primary"
          prepend-icon="bx-brain"
          :loading="isLoading"
          @click="runForecast"
        >
          Run AI Forecast
        </VBtn>
      </div>

      <!-- Error Alert -->
      <VAlert
        v-if="errorMsg"
        type="warning"
        variant="tonal"
        density="compact"
        class="mb-3"
        closable
        @click:close="errorMsg = ''"
      >
        {{ errorMsg }} — Menampilkan hasil formula lokal
      </VAlert>

      <VCard
        variant="tonal"
        :color="status.color"
        class="pa-4 mt-2"
      >
        <div class="d-flex align-center justify-space-between flex-wrap gap-4">
          <div>
            <span class="text-caption text-medium-emphasis">Predicted Fuel Ratio</span>
            <h4
              class="text-h4 font-weight-bold"
              :class="`text-${status.color}`"
            >
              {{ predictedFr.toFixed(4) }} <span class="text-body-2">L/BCM</span>
            </h4>
          </div>

          <div>
            <span class="text-caption text-medium-emphasis">Predicted Fuel Requirement</span>
            <h4 class="text-h4 font-weight-bold">
              {{ predictedFuelL.toLocaleString('id-ID') }} <span class="text-body-2">L/hari</span>
            </h4>
          </div>

          <VChip
            :color="status.color"
            variant="elevated"
            size="large"
            class="font-weight-bold"
          >
            <VIcon
              start
              :icon="status.icon"
            />
            {{ aiResult ? aiResult.status : status.label }}
          </VChip>
        </div>

        <!-- AI Features Used Detail (shown after forecast) -->
        <div
          v-if="aiResult?.features_used"
          class="mt-3 pt-3 border-t d-flex flex-wrap gap-3"
        >
          <VChip
            v-for="(val, key) in aiResult.features_used"
            :key="key"
            size="small"
            variant="outlined"
          >
            {{ key }}: {{ val }}
          </VChip>
        </div>
      </VCard>
    </VCardText>
  </VCard>
</template>
