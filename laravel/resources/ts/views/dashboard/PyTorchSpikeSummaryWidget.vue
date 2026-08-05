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
  <VCard>
    <VCardItem>
      <template #prepend>
        <VAvatar
          color="error"
          variant="tonal"
          size="48"
          rounded
        >
          <VIcon
            icon="bx-pulse"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        PyTorch Anomaly Detector
      </VCardTitle>
      <VCardSubtitle>Neural Network Spike Scanner</VCardSubtitle>
    </VCardItem>

    <VCardText>
      <div v-if="isLoading" class="d-flex justify-center my-4">
        <VProgressCircular indeterminate color="primary" />
      </div>
      <template v-else>
        <div class="d-flex align-center gap-4 mb-3">
          <div>
            <div class="d-flex align-center gap-2 mb-1">
              <h3 class="text-h3 font-weight-bold text-error">
                {{ props.totalSpikes }}
              </h3>
              <div class="spike-pulse-dot" />
            </div>
            <span class="text-body-2 text-medium-emphasis">Spike Events Detected</span>
          </div>
        </div>

        <VDivider class="mb-3" />

        <div class="d-flex justify-space-between text-body-2">
          <div>
            <VIcon
              icon="bx-cog"
              size="16"
              class="me-1"
            />
            <span class="text-medium-emphasis">Anomalous Units:</span>
            <strong class="ms-1 text-error">{{ props.anomalousUnitsCount }}</strong>
          </div>
          <div>
            <span class="text-medium-emphasis">Anomaly Ratio:</span>
            <VChip
              color="error"
              size="small"
              variant="tonal"
              class="ms-1"
            >
              {{ anomalyRatio }}% Fleet
            </VChip>
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
  block-size: 12px;
  border-radius: 50%;
  inline-size: 12px;
  animation: pulse-anim 1.5s ease-in-out infinite;
}

@keyframes pulse-anim {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: 0.5;
    transform: scale(1.4);
  }
}
</style>
