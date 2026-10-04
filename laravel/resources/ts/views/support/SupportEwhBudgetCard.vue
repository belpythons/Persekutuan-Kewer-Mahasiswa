<script setup lang="ts">
import type { EwhSector } from '@/composables/useAiApi'

interface Props {
  sector: EwhSector | null
  label?: string
  icon?: string
  color?: string
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  sector: null,
  label: 'Supporting',
  icon: 'bx-wrench',
  color: 'warning',
  isLoading: false,
})

const annualBudgetEwh = computed(() => props.sector ? Math.round(props.sector.daily_ewh_hrs * 365 * props.sector.total_units) : 0)
</script>

<template>
  <VCard>
    <VCardItem>
      <template #prepend>
        <VAvatar
          :color="props.color"
          variant="tonal"
          size="48"
          rounded
        >
          <VIcon
            :icon="props.icon"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        {{ props.label }} Fleet EWH & Fuel
      </VCardTitle>
      <VCardSubtitle>Non-Production Zero-BCM Burden</VCardSubtitle>
      <template v-if="sector" #append>
        <VChip
          :color="props.color"
          size="small"
          variant="tonal"
        >
          {{ sector.total_units }} Units
        </VChip>
      </template>
    </VCardItem>

    <VCardText>
      <div v-if="isLoading" class="d-flex justify-center my-6">
        <VProgressCircular indeterminate color="primary" />
      </div>
      <div v-else-if="!sector" class="d-flex flex-column align-center justify-center text-medium-emphasis py-6">
        <VIcon icon="bx-info-circle" size="32" class="mb-2 opacity-50" />
        <span class="text-caption">Belum ada baseline PA/UA untuk sektor ini di database.</span>
      </div>
      <template v-else>
        <div class="d-flex align-center justify-space-between mb-3">
          <div>
            <span class="text-caption text-medium-emphasis">Daily Fuel Allocation</span>
            <h4
              class="text-h4 font-weight-bold text-tabular-nums"
              :class="`text-${props.color}`"
            >
              {{ sector.total_daily_fuel_liters.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} L/hari
            </h4>
          </div>
          <div class="text-end">
            <span class="text-caption text-medium-emphasis">FR Burden</span>
            <h5 class="text-h5 font-weight-bold text-error text-tabular-nums">
              +{{ sector.total_fr_burden_l_bcm.toFixed(4) }} L/BCM
            </h5>
            <span class="text-caption text-error text-tabular-nums">({{ sector.total_fr_burden_pct.toFixed(2) }}% dari Total FR)</span>
          </div>
        </div>

        <VDivider class="mb-3" />

        <div class="d-flex justify-space-between text-body-2">
          <div>
            <span class="text-medium-emphasis">Annual Budget EWH:</span>
            <strong class="ms-1 text-tabular-nums">{{ annualBudgetEwh.toLocaleString('id-ID') }} Jam/thn</strong>
          </div>
          <div>
            <span class="text-medium-emphasis">Rerata Jam/Hari:</span>
            <strong class="ms-1 text-tabular-nums">{{ sector.daily_ewh_hrs.toFixed(1) }} Jam/unit</strong>
          </div>
        </div>
      </template>
    </VCardText>
  </VCard>
</template>
