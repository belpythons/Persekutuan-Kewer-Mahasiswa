<script setup lang="ts">
import { useAiApi, AiApiError } from '@/composables/useAiApi'
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

const predictedFr = computed(() => aiResult.value?.forecast_fr ?? 0)

const predictedFuelL = computed(() => Math.round(targetBcm.value * predictedFr.value))

const warningThreshold = computed(() => aiResult.value?.warning_threshold ?? 1.2503)
const criticalThreshold = computed(() => aiResult.value?.critical_threshold ?? 1.3660)

const status = computed(() => {
  if (predictedFr.value >= criticalThreshold.value) return { label: 'CRITICAL (+18%)', color: 'error', icon: 'bx-error-circle' }
  if (predictedFr.value >= warningThreshold.value) return { label: 'WARNING (+8%)', color: 'warning', icon: 'bx-error' }
  return { label: 'NORMAL', color: 'success', icon: 'bx-check-circle' }
})

// Human-readable labels for the model's 13 input features, for the transparency panel below.
const FEATURE_LABELS: Record<string, string> = {
  Curah_Hujan_mm: 'Rain Derating',
  Temp_Max_C: 'Max Temperature',
  Kecepatan_Angin_kmh: 'Wind Speed',
  Haul_Distance_m: 'Haul Distance',
  Daily_Prod_BCM: 'Production Target',
  DayOfWeek: 'Day of Week',
  Month: 'Month',
  IsWeekend: 'Weekend',
  Rain_Lag1: 'Rain (Yesterday)',
  Rain_Lag2: 'Rain (2 Days Ago)',
  FR_Lag1: 'FR (Yesterday)',
  FR_Lag2: 'FR (2 Days Ago)',
  RollingAvg_FR_7d: 'FR 7-Day Average',
}

// Real XGBoost SHAP-style contributions (pred_contribs) from the backend — not a guess. Top 3
// by absolute magnitude, excluding the model's base_value (bias term, not a feature).
const topContributors = computed(() => {
  const contribs = aiResult.value?.feature_contributions
  if (!contribs) return []
  return Object.entries(contribs)
    .filter(([key]) => key !== 'base_value')
    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
    .slice(0, 3)
    .map(([key, value]) => ({ label: FEATURE_LABELS[key] || key, value }))
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
  } catch (e: unknown) {
    // AI service down (including Laravel's 503 "fallback" response) is treated as a real error —
    // it has nothing honest to simulate with, so it should say so rather than invent a number.
    aiResult.value = null
    errorMsg.value = e instanceof AiApiError ? e.message : 'Gagal menghubungi AI Service'
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
            v-if="aiResult"
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
            v-else-if="errorMsg"
            color="error"
            size="small"
            variant="tonal"
            class="font-weight-medium"
          >
            <VIcon icon="bx-error-circle" start size="14" />
            AI Service Offline
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
            <strong class="text-secondary">{{ rainfallMm }} mm</strong>
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
            <strong class="text-primary">{{ tempMaxC }} °C</strong>
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
            <strong class="text-primary">{{ haulDistanceM.toLocaleString('id-ID') }} m</strong>
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
            <strong class="text-secondary">{{ targetBcm.toLocaleString('id-ID') }} BCM</strong>
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
        v-if="errorMsg && !aiResult"
        rounded="lg"
        class="pa-4 border mt-5 d-flex flex-column align-center text-center"
      >
        <VIcon icon="bx-error-circle" size="32" class="text-error mb-2" />
        <p class="text-body-2 text-medium-emphasis mb-2">{{ errorMsg }}</p>
        <VBtn size="small" variant="tonal" color="primary" :loading="isLoading" @click="runForecast">
          Coba Lagi
        </VBtn>
      </VSheet>

      <VSheet
        v-else-if="aiResult"
        rounded="lg"
        class="pa-4 border mt-5 result-sheet"
        :style="{
          backgroundColor: `rgba(var(--v-theme-${status.color}), 0.06)`,
          borderInlineStartColor: `rgb(var(--v-theme-${status.color}))`,
          borderInlineStartWidth: '4px',
          borderInlineStartStyle: 'solid',
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
                class="text-h5 font-weight-bold text-tabular-nums"
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
              <span class="text-h5 font-weight-bold text-high-emphasis text-tabular-nums">
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

        <!-- XGBoost Feature Contributions: real SHAP-style values from the model, not a guess -->
        <template v-if="topContributors.length > 0">
          <VDivider class="my-3" />
          <div class="text-caption text-medium-emphasis mb-2 font-weight-medium">
            Kontributor Utama Prediksi (XGBoost Feature Contribution)
          </div>
          <div class="d-flex flex-wrap gap-2">
            <VChip
              v-for="item in topContributors"
              :key="item.label"
              size="small"
              variant="tonal"
              :color="item.value >= 0 ? 'error' : 'success'"
            >
              <VIcon :icon="item.value >= 0 ? 'bx-up-arrow-alt' : 'bx-down-arrow-alt'" start size="14" />
              {{ item.label }}: {{ item.value >= 0 ? '+' : '' }}{{ item.value.toFixed(4) }}
            </VChip>
          </div>
        </template>
      </VSheet>

      <VSheet
        v-else
        rounded="lg"
        class="pa-4 border mt-5 d-flex align-center justify-center"
      >
        <VProgressCircular indeterminate color="secondary" size="24" class="me-3" />
        <span class="text-caption text-medium-emphasis">Menghitung prediksi...</span>
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
