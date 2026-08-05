<script setup lang="ts">
const baselineFr = ref(1.1576)
const warningPct = ref(8.0)
const criticalPct = ref(18.0)
const isSaved = ref(false)

const warningThreshold = computed(() => {
  return baselineFr.value * (1 + warningPct.value / 100)
})

const criticalThreshold = computed(() => {
  return baselineFr.value * (1 + criticalPct.value / 100)
})

const handleSave = () => {
  isSaved.value = true
  setTimeout(() => {
    isSaved.value = false
  }, 3000)
}
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
      <VCardSubtitle>Pengaturan Parameter Batas Toleransi Fuel Ratio</VCardSubtitle>
    </VCardItem>

    <VCardText>
      <VRow>
        <VCol
          cols="12"
          sm="4"
        >
          <VTextField
            v-model.number="baselineFr"
            type="number"
            step="0.0001"
            label="Baseline Budget FR (L/BCM)"
            density="compact"
            prepend-inner-icon="bx-target-lock"
          />
        </VCol>
        <VCol
          cols="12"
          sm="4"
        >
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
        <VCol
          cols="12"
          sm="4"
        >
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

      <VCard
        variant="tonal"
        color="secondary"
        class="pa-3 my-3"
      >
        <div class="d-flex justify-space-between flex-wrap gap-2 text-body-2">
          <div>
            <span class="text-medium-emphasis">Calculated Warning:</span>
            <strong class="ms-1 text-warning">{{ warningThreshold.toFixed(4) }} L/BCM</strong>
          </div>
          <div>
            <span class="text-medium-emphasis">Calculated Critical:</span>
            <strong class="ms-1 text-error">{{ criticalThreshold.toFixed(4) }} L/BCM</strong>
          </div>
        </div>
      </VCard>

      <div class="d-flex align-center justify-space-between">
        <VBtn
          color="primary"
          prepend-icon="bx-save"
          @click="handleSave"
        >
          Simpan Threshold Config
        </VBtn>

        <VChip
          v-if="isSaved"
          color="success"
          variant="flat"
          size="small"
        >
          <VIcon
            icon="bx-check"
            start
          />
          Konfigurasi berhasil disimpan
        </VChip>
      </div>
    </VCardText>
  </VCard>
</template>
