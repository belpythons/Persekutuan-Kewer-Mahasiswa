<script setup lang="ts">
import { useAiApi, AiApiError } from '@/composables/useAiApi'

const { fetchThresholdConfig, updateThresholdConfig } = useAiApi()

const isLoading = ref(true)
const isSaving = ref(false)
const errorMsg = ref('')
const isSaved = ref(false)

const baselineFr = ref(1.018)
const warningPct = ref(8.0)
const criticalPct = ref(18.0)

const warningThreshold = computed(() => baselineFr.value * (1 + warningPct.value / 100))
const criticalThreshold = computed(() => baselineFr.value * (1 + criticalPct.value / 100))

async function load() {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const cfg = await fetchThresholdConfig()
    baselineFr.value = cfg.budget_baseline
    warningPct.value = cfg.warning_pct
    criticalPct.value = cfg.critical_pct
  } catch (e: unknown) {
    errorMsg.value = e instanceof AiApiError ? e.message : 'Gagal memuat konfigurasi threshold'
  } finally {
    isLoading.value = false
  }
}

async function handleSave() {
  isSaving.value = true
  errorMsg.value = ''
  isSaved.value = false
  try {
    const cfg = await updateThresholdConfig({
      budget_baseline: baselineFr.value,
      warning_pct: warningPct.value,
      critical_pct: criticalPct.value,
    })
    baselineFr.value = cfg.budget_baseline
    warningPct.value = cfg.warning_pct
    criticalPct.value = cfg.critical_pct
    isSaved.value = true
    setTimeout(() => { isSaved.value = false }, 3000)
  } catch (e: unknown) {
    errorMsg.value = e instanceof AiApiError ? e.message : 'Gagal menyimpan konfigurasi threshold'
  } finally {
    isSaving.value = false
  }
}

onMounted(load)
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
            icon="bx-slider-alt"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        Dynamic Alert Threshold Config
      </VCardTitle>
      <VCardSubtitle>Pengaturan Parameter Batas Toleransi Fuel Ratio (cfg_system_mlops)</VCardSubtitle>
    </VCardItem>

    <VCardText>
      <div v-if="isLoading" class="d-flex justify-center my-6">
        <VProgressCircular indeterminate color="primary" />
      </div>
      <template v-else>
        <VAlert v-if="errorMsg" type="error" variant="tonal" density="compact" class="mb-3">
          {{ errorMsg }}
          <template #append>
            <VBtn size="x-small" variant="text" @click="load">Coba Lagi</VBtn>
          </template>
        </VAlert>

        <VRow>
          <VCol cols="12" sm="4">
            <VTextField
              v-model.number="baselineFr"
              type="number"
              step="0.0001"
              label="Baseline Budget FR (L/BCM)"
              density="compact"
              prepend-inner-icon="bx-target-lock"
            />
          </VCol>
          <VCol cols="12" sm="4">
            <VTextField
              v-model.number="warningPct"
              type="number"
              step="0.5"
              label="Warning Delta (+%)"
              density="compact"
              prepend-inner-icon="bx-error"
              suffix="%"
            />
          </VCol>
          <VCol cols="12" sm="4">
            <VTextField
              v-model.number="criticalPct"
              type="number"
              step="0.5"
              label="Critical Delta (+%)"
              density="compact"
              prepend-inner-icon="bx-error-circle"
              suffix="%"
            />
          </VCol>
        </VRow>

        <VCard variant="tonal" color="secondary" class="pa-3 my-3">
          <div class="d-flex justify-space-between flex-wrap gap-2 text-body-2">
            <div>
              <span class="text-medium-emphasis">Calculated Warning:</span>
              <strong class="ms-1 text-warning text-tabular-nums">{{ warningThreshold.toFixed(4) }} L/BCM</strong>
            </div>
            <div>
              <span class="text-medium-emphasis">Calculated Critical:</span>
              <strong class="ms-1 text-error text-tabular-nums">{{ criticalThreshold.toFixed(4) }} L/BCM</strong>
            </div>
          </div>
        </VCard>

        <div class="d-flex align-center justify-space-between">
          <VBtn
            color="primary"
            prepend-icon="bx-save"
            :loading="isSaving"
            @click="handleSave"
          >
            Simpan Threshold Config
          </VBtn>

          <VChip v-if="isSaved" color="success" variant="flat" size="small">
            <VIcon icon="bx-check" start />
            Konfigurasi berhasil disimpan
          </VChip>
        </div>
      </template>
    </VCardText>
  </VCard>
</template>
