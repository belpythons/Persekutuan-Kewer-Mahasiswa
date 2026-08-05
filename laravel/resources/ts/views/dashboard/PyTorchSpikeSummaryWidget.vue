<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  totalSpikes: number
  anomalousUnitsCount: number
  totalFleetUnits: number
  isLoading: boolean
}

const props = withDefaults(defineProps<Props>(), {
  totalSpikes: 0,
  anomalousUnitsCount: 0,
  totalFleetUnits: 0,
  isLoading: false,
})

const anomalyRatio = computed(() => {
  if (props.totalFleetUnits === 0) return "0.0"
  return ((props.anomalousUnitsCount / props.totalFleetUnits) * 100).toFixed(1)
})
</script>

<template>
  <VCard class="border d-flex flex-column h-100">
    <VCardItem>
      <template #prepend>
        <VAvatar
          color="error"
          variant="tonal"
          size="44"
          rounded
        >
          <VIcon
            icon="bx-pulse"
            size="24"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-bold">
        PyTorch Anomaly Detector
      </VCardTitle>
      <VCardSubtitle class="text-caption">Neural Network Spike Scanner</VCardSubtitle>
    </VCardItem>

    <VCardText class="flex-grow-1 d-flex flex-column justify-space-between">
      <div v-if="isLoading" class="d-flex justify-center my-4">
        <VProgressCircular indeterminate color="primary" />
      </div>
      <template v-else>
        <div class="d-flex align-center gap-4 mb-3">
          <div>
            <span class="text-caption text-medium-emphasis">Spike Events Detected</span>
            <div class="d-flex align-center gap-2">
              <h3 class="text-h3 font-weight-bold text-error">
                {{ props.totalSpikes }}
              </h3>
              <div class="spike-pulse-dot" />
            </div>
          </div>
        </div>

        <div>
          <VDivider class="mb-3" />

          <div class="d-flex justify-space-between text-caption flex-wrap gap-2">
            <div>
              <VIcon
                icon="bx-cog"
                size="16"
                class="me-1 text-medium-emphasis"
              />
              <span class="text-medium-emphasis">Anomalous Units:</span>
              <strong class="ms-1 text-error">{{ props.anomalousUnitsCount }}</strong>
            </div>
          </div>
        </div>
      </template>
    </VCardText>
  </VCard>
</template>

<style lang="scss" scoped>
.spike-pulse-dot {
  display: inline-block;
  background: rgb(var(--v-theme-error));
  block-size: 10px;
  border-radius: 50%;
  inline-size: 10px;
  animation: pulse-anim 1.5s ease-in-out infinite;
}

@keyframes pulse-anim {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}
</style>
