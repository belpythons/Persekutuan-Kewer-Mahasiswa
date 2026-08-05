<script setup lang="ts">
interface Props {
  sector: 'Supporting' | 'Dewatering'
  totalUnits: number
  annualBudgetEwh: number
  dailyFuelL: number
  frBurdenLbcm: number
  frBurdenPct: number
  icon: string
  color: string
}

const props = withDefaults(defineProps<Props>(), {
  sector: 'Supporting',
  totalUnits: 183,
  annualBudgetEwh: 1337300.0,
  dailyFuelL: 200582.4,
  frBurdenLbcm: 0.2199,
  frBurdenPct: 19.00,
  icon: 'bx-wrench',
  color: 'warning',
})
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
        {{ props.sector }} Fleet EWH & Fuel
      </VCardTitle>
      <VCardSubtitle>Non-Production Zero-BCM Burden</VCardSubtitle>
      <template #append>
        <VChip
          :color="props.color"
          size="small"
          variant="tonal"
        >
          100% Active ({{ props.totalUnits }} Units)
        </VChip>
      </template>
    </VCardItem>

    <VCardText>
      <div class="d-flex align-center justify-space-between mb-3">
        <div>
          <span class="text-caption text-medium-emphasis">Daily Fuel Allocation</span>
          <h4
            class="text-h4 font-weight-bold"
            :class="`text-${props.color}`"
          >
            {{ props.dailyFuelL.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} L/hari
          </h4>
        </div>
        <div class="text-end">
          <span class="text-caption text-medium-emphasis">FR Burden</span>
          <h5 class="text-h5 font-weight-bold text-error">
            +{{ props.frBurdenLbcm.toFixed(4) }} L/BCM
          </h5>
          <span class="text-caption text-error">({{ props.frBurdenPct.toFixed(2) }}% dari Total FR)</span>
        </div>
      </div>

      <VDivider class="mb-3" />

      <div class="d-flex justify-space-between text-body-2">
        <div>
          <span class="text-medium-emphasis">Annual Budget EWH:</span>
          <strong class="ms-1">{{ props.annualBudgetEwh.toLocaleString('id-ID') }} Jam/thn</strong>
        </div>
        <div>
          <span class="text-medium-emphasis">Rerata Jam/Hari:</span>
          <strong class="ms-1">20.0 Jam/unit</strong>
        </div>
      </div>
    </VCardText>
  </VCard>
</template>
