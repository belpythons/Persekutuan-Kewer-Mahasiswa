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

watch([rainfallMm, tempMaxC, windKmh, haulDistanceM, targetBcm], () => {
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
  <VCard class="d-flex flex-column h-100 pa-2">
    <VCardItem class="pb-2">
      <template #prepend>
        <VAvatar
          color="secondary"
          variant="tonal"
          size="44"
          rounded
        >
          <VIcon
            icon="bx-slider-alt"
            size="24"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-bold">
        What-If Scenario Simulator
      </VCardTitle>
      <VCardSubtitle class="text-caption">Simulasi variabel cuaca, jarak angkut, dan target produksi</VCardSubtitle>
      <template #append>
        <div class="d-flex align-center gap-2">
          <VChip
            v-if="aiStatus === 'live'"
            color="success"
            size="small"
            variant="tonal"
            class="font-weight-medium"
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
            class="font-weight-medium"
          >
            Fallback Mode
          </VChip>
          <VBtn
            size="small"
            variant="tonal"
            color="secondary"
            prepend-icon="bx-reset"
            @click="resetDefaults"
          >
            Reset
          </VBtn>
        </div>
      </template>
    </VCardItem>

    <!-- Loading indicator at top of panel -->
    <VProgressLinear
      v-if="isLoading"
      indeterminate
      color="secondary"
      height="3"
    />

    <VCardText class="flex-grow-1 d-flex flex-column justify-space-between pt-3 pb-2">
      <!-- SPACIOUS 2-COLUMN SLIDER GRID -->
      <VRow class="gy-4 gx-6">
        <!-- Curah Hujan -->
        <VCol cols="12" sm="6">
          <div class="d-flex justify-space-between align-center mb-1">
            <span class="text-body-2 text-medium-emphasis d-flex align-center gap-1 font-weight-medium">
              <VIcon icon="bx-water" size="18" color="secondary" />
              Curah Hujan (mm/hr)
            </span>
            <strong style="color: #1E88E5;">{{ rainfallMm }} mm</strong>
          </div>
          <VSlider
            v-model="rainfallMm"
            :min="0"
            :max="150"
            :step="0.5"
            color="secondary"
            thumb-label
            hide-details
            density="comfortable"
          />
        </VCol>

        <!-- Suhu Maksimum -->
        <VCol cols="12" sm="6">
          <div class="d-flex justify-space-between align-center mb-1">
            <span class="text-body-2 text-medium-emphasis d-flex align-center gap-1 font-weight-medium">
              <VIcon icon="bx-thermometer" size="18" color="primary" />
              Suhu Maksimum (°C)
            </span>
            <strong style="color: #E53935;">{{ tempMaxC }} °C</strong>
          </div>
          <VSlider
            v-model="tempMaxC"
            :min="20"
            :max="45"
            :step="0.5"
            color="primary"
            thumb-label
            hide-details
            density="comfortable"
          />
        </VCol>

        <!-- Kecepatan Angin -->
        <VCol cols="12" sm="6">
          <div class="d-flex justify-space-between align-center mb-1">
            <span class="text-body-2 text-medium-emphasis d-flex align-center gap-1 font-weight-medium">
              <VIcon icon="bx-wind" size="18" color="info" />
              Kecepatan Angin (km/h)
            </span>
            <strong>{{ windKmh }} km/h</strong>
          </div>
          <VSlider
            v-model="windKmh"
            :min="0"
            :max="50"
            :step="1"
            color="info"
            thumb-label
            hide-details
            density="comfortable"
          />
        </VCol>

        <!-- Jarak Angkut -->
        <VCol cols="12" sm="6">
          <div class="d-flex justify-space-between align-center mb-1">
            <span class="text-body-2 text-medium-emphasis d-flex align-center gap-1 font-weight-medium">
              <VIcon icon="bx-map" size="18" color="primary" />
              Jarak Angkut (m)
            </span>
            <strong style="color: #E53935;">{{ haulDistanceM.toLocaleString('id-ID') }} m</strong>
          </div>
          <VSlider
            v-model="haulDistanceM"
            :min="1000"
            :max="10000"
            :step="100"
            color="primary"
            thumb-label
            hide-details
            density="comfortable"
          />
        </VCol>

        <!-- Target Produksi -->
        <VCol cols="12">
          <div class="d-flex justify-space-between align-center mb-1">
            <span class="text-body-2 text-medium-emphasis d-flex align-center gap-1 font-weight-medium">
              <VIcon icon="bx-bar-chart-alt-2" size="18" color="secondary" />
              Target Produksi (BCM)
            </span>
            <strong style="color: #1E88E5;">{{ targetBcm.toLocaleString('id-ID') }} BCM</strong>
          </div>
          <VSlider
            v-model="targetBcm"
            :min="10000"
            :max="350000"
            :step="5000"
            color="secondary"
            thumb-label
            hide-details
            density="comfortable"
          />
        </VCol>
      </VRow>

      <!-- RESULTS SHEET (SPACIOUS LAYOUT & CLEAR VISUAL ACCENT) -->
      <VSheet
        rounded="lg"
        class="pa-4 border mt-5 result-sheet"
        :style="{
          backgroundColor: status.color === 'error' ? 'rgba(229, 57, 53, 0.06)' : status.color === 'warning' ? 'rgba(255, 180, 0, 0.06)' : 'rgba(86, 202, 0, 0.06)',
          borderLeftColor: status.color === 'error' ? '#E53935' : status.color === 'warning' ? '#FFB400' : '#56CA00',
          borderLeftWidth: '4px',
          borderLeftStyle: 'solid',
        }"
      >
        <VRow align="center" class="gy-2 gx-4">
          <VCol
            cols="12"
            sm="5"
          >
            <div class="text-caption text-medium-emphasis mb-1 font-weight-medium">
              Predicted Fuel Ratio
            </div>
            <div class="d-flex align-baseline gap-2">
              <span
                class="text-h5 font-weight-bold"
                :class="`text-${status.color}`"
              >
                {{ predictedFr.toFixed(4) }}
              </span>
              <span class="text-caption text-medium-emphasis font-weight-medium">L/BCM</span>
            </div>
          </VCol>

          <VCol
            cols="12"
            sm="4"
          >
            <div class="text-caption text-medium-emphasis mb-1 font-weight-medium">
              Predicted Fuel Requirement
            </div>
            <div class="d-flex align-baseline gap-2">
              <span class="text-h5 font-weight-bold text-high-emphasis">
                {{ predictedFuelL.toLocaleString('id-ID') }}
              </span>
              <span class="text-caption text-medium-emphasis font-weight-medium">L/hari</span>
            </div>
          </VCol>

          <VCol
            cols="12"
            sm="3"
            class="text-sm-right text-left"
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

.result-sheet {
  transition: background-color 0.3s ease, border-color 0.3s ease;
}
</style>
