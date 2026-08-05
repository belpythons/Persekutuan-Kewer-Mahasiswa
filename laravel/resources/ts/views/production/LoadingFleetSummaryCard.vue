<script setup lang="ts">
import type { ActivityBreakdown } from '@/composables/useAiApi'

interface Props {
  fleetType: 'Loading' | 'Hauling'
  activityData: ActivityBreakdown | null
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  fleetType: 'Loading',
  activityData: null,
  isLoading: false,
})

const fleetColor = computed(() => props.fleetType === 'Loading' ? 'primary' : 'info')
const fleetIcon = computed(() => props.fleetType === 'Loading' ? 'bx-loader-circle' : 'bx-car')

const totalUnits = computed(() => props.activityData?.total_fleet_qty ?? 0)
const activeUnits = computed(() => props.activityData?.operating_units ?? 0)
const utilisation = computed(() => {
  if (!props.activityData || props.activityData.total_fleet_qty === 0) return '0.0'
  return ((props.activityData.operating_units / props.activityData.total_fleet_qty) * 100).toFixed(1)
})
const fleetBcmHr = computed(() => props.activityData?.prod_bcm_hr_total ?? 0)
const fleetFuelHr = computed(() => props.activityData?.fuel_l_hr_total ?? 0)
const dailyFuelAllocation = computed(() => props.activityData?.combined_fuel_lday ?? 0)
</script>

<template>
  <VCard>
    <VCardItem>
      <template #prepend>
        <VAvatar
          :color="fleetColor"
          variant="tonal"
          size="48"
          rounded
        >
          <VIcon
            :icon="fleetIcon"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        {{ props.fleetType }} Fleet
      </VCardTitle>
      <VCardSubtitle>
        Live Capacity Allocation
        <VChip v-if="props.activityData" color="success" size="x-small" variant="tonal" class="ms-2">
          Live AI
        </VChip>
      </VCardSubtitle>
    </VCardItem>

    <VCardText>
      <div v-if="props.isLoading" class="d-flex justify-center my-4">
        <VProgressCircular indeterminate color="primary" />
      </div>
      <template v-else>
        <div class="d-flex align-center gap-4 mb-4">
          <div class="text-center">
            <h4 class="text-h4 font-weight-bold">
              {{ totalUnits }}
            </h4>
            <span class="text-caption text-medium-emphasis">Total Unit</span>
          </div>
          <VDivider vertical />
          <div class="text-center">
            <h4
              class="text-h4 font-weight-bold"
              :class="`text-${fleetColor}`"
            >
              {{ activeUnits }}
            </h4>
            <span class="text-caption text-medium-emphasis">Active</span>
          </div>
          <VDivider vertical />
          <div class="text-center">
            <h4 class="text-h4 font-weight-bold text-warning">
              {{ utilisation }}%
            </h4>
            <span class="text-caption text-medium-emphasis">Utilisasi</span>
          </div>
        </div>

        <VDivider class="mb-3" />

        <div class="d-flex flex-column gap-2 text-body-2">
          <div class="d-flex justify-space-between">
            <span class="text-medium-emphasis">
              <VIcon
                icon="bx-trending-up"
                size="16"
                class="me-1"
              />Fleet BCM/hr
            </span>
            <strong>{{ fleetBcmHr.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} BCM/jam</strong>
          </div>
          <div class="d-flex justify-space-between">
            <span class="text-medium-emphasis">
              <VIcon
                icon="bx-gas-pump"
                size="16"
                class="me-1"
              />Fuel Rate
            </span>
            <strong>{{ fleetFuelHr.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} L/jam</strong>
          </div>
          <div class="d-flex justify-space-between">
            <span class="text-medium-emphasis">
              <VIcon
                icon="bx-calendar"
                size="16"
                class="me-1"
              />Alokasi Harian
            </span>
            <strong class="text-primary">{{ dailyFuelAllocation.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} L/hari</strong>
          </div>
        </div>
      </template>
    </VCardText>
  </VCard>
</template>
