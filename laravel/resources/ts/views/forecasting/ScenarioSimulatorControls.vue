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

let timer: any = null
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

const debouncedRunForecast = () => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(runForecast, 300)
}

watch([rainfallMm, haulDistanceM, targetBcm], () => {
  debouncedRunForecast()
})

const resetDefaults = () => {
  rainfallMm.value = 0
  tempMaxC.value = 32.0
  windKmh.value = 14.2
  haulDistanceM.value = 3900
  targetBcm.value = 250072
  aiResult.value = null
  errorMsg.value = ''
  runForecast()
}

onMounted(() => {
  runForecast()
})
</script>

<template>
  <VCard class="d-flex flex-column h-100">
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

    <VCardText class="flex-grow-1 d-flex flex-column justify-space-between">
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

      <!-- RESULTS SHEET (AUTOMATIC RECALCULATION ON SLIDER CHANGE) -->
      <VSheet
        rounded="lg"
        class="pa-4 border mt-4"
        :class="`bg-${status.color}-lighten-5 border-${status.color}`"
      >
        <VRow align="center">
          <VCol
            cols="12"
            sm="5"
          >
            <div class="text-caption text-medium-emphasis mb-1">
              Predicted Fuel Ratio
            </div>
            <div class="d-flex align-baseline gap-2">
              <span
                class="text-h3 font-weight-bold"
                :class="`text-${status.color}`"
              >
                {{ predictedFr.toFixed(4) }}
              </span>
              <span class="text-body-2 text-medium-emphasis">L/BCM</span>
            </div>
          </VCol>

          <VCol
            cols="12"
            sm="5"
          >
            <div class="text-caption text-medium-emphasis mb-1">
              Predicted Fuel Requirement
            </div>
            <div class="d-flex align-baseline gap-2">
              <span class="text-h4 font-weight-bold text-high-emphasis">
                {{ predictedFuelL.toLocaleString('id-ID') }}
              </span>
              <span class="text-body-2 text-medium-emphasis">L/hari</span>
            </div>
          </VCol>

          <VCol
            cols="12"
            sm="2"
            class="text-right"
          >
            <VChip
              :color="status.color"
              class="font-weight-bold"
              size="large"
            >
              <VIcon
                :icon="status.icon"
                start
              />
              {{ status.label }}
            </VChip>
          </VCol>
        </VRow>
      </VSheet>
    </VCardText>
  </VCard>
</template>

<style scoped>
.h-100 {
  height: 100%;
}
</style>
