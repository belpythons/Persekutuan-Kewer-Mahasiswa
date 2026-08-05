<script setup lang="ts">
import type { ActivityBreakdown } from '@/composables/useAiApi'

interface Props {
  activityBreakdown: ActivityBreakdown[] | null
  totalFuel: number | null
}

const props = withDefaults(defineProps<Props>(), {
  activityBreakdown: null,
  totalFuel: null,
})

interface FleetAllocation {
  activity: string
  color: string
  requiredUnits: number
  totalPopulation: number
  dailyFuelL: number
  icon: string
}

// Default data (fallback)
const defaultAllocations: FleetAllocation[] = [
  { activity: 'Loading', color: 'primary', requiredUnits: 22, totalPopulation: 70, dailyFuelL: 50952.2, icon: 'bx-loader-circle' },
  { activity: 'Hauling', color: 'info', requiredUnits: 94, totalPopulation: 415, dailyFuelL: 652282.4, icon: 'bx-car' },
  { activity: 'Supporting', color: 'warning', requiredUnits: 183, totalPopulation: 183, dailyFuelL: 200582.4, icon: 'bx-wrench' },
  { activity: 'Dewatering', color: 'secondary', requiredUnits: 175, totalPopulation: 175, dailyFuelL: 113085.8, icon: 'bx-droplet' },
]

const activityIcon = (activity: string) => {
  const map: Record<string, string> = {
    loading: 'bx-loader-circle',
    hauling: 'bx-car',
    supporting: 'bx-wrench',
    dewatering: 'bx-droplet',
  }
  return map[activity.toLowerCase()] || 'bx-cog'
}

const activityColor = (activity: string) => {
  const map: Record<string, string> = {
    loading: 'primary',
    hauling: 'info',
    supporting: 'warning',
    dewatering: 'secondary',
  }
  return map[activity.toLowerCase()] || 'default'
}

const allocations = computed<FleetAllocation[]>(() => {
  if (!props.activityBreakdown || props.activityBreakdown.length === 0) return defaultAllocations

  return props.activityBreakdown.map(item => ({
    activity: item.activity.charAt(0).toUpperCase() + item.activity.slice(1).toLowerCase(),
    color: activityColor(item.activity),
    requiredUnits: item.operating_units,
    totalPopulation: item.total_fleet_qty,
    dailyFuelL: item.combined_fuel_lday,
    icon: activityIcon(item.activity),
  }))
})

const computedTotalFuel = computed(() => {
  return props.totalFuel ?? allocations.value.reduce((sum, a) => sum + a.dailyFuelL, 0)
})
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>Combined Fleet Capacity & Fuel Allocation</VCardTitle>
      <VCardSubtitle>
        Target Produksi: 250.072 BCM/hari | Total Alokasi Solar:
        <strong class="text-primary">{{ computedTotalFuel.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} L/hari</strong>
        <VChip
          v-if="activityBreakdown"
          color="success"
          size="x-small"
          variant="tonal"
          class="ms-2"
        >
          Live AI
        </VChip>
      </VCardSubtitle>
    </VCardItem>

    <VCardText>
      <VRow>
        <VCol
          v-for="alloc in allocations"
          :key="alloc.activity"
          cols="12"
          sm="6"
          md="3"
        >
          <VCard
            variant="outlined"
            :style="{ borderTop: `4px solid rgb(var(--v-theme-${alloc.color}))` }"
          >
            <VCardText class="text-center">
              <VAvatar
                :color="alloc.color"
                variant="tonal"
                size="44"
                rounded
                class="mb-3"
              >
                <VIcon
                  :icon="alloc.icon"
                  size="24"
                />
              </VAvatar>

              <h6 class="text-h6 mb-1">
                {{ alloc.activity }}
              </h6>

              <div class="d-flex justify-center gap-4 mb-2">
                <div>
                  <span class="text-h5 font-weight-bold" :class="`text-${alloc.color}`">{{ alloc.requiredUnits }}</span>
                  <div class="text-caption text-medium-emphasis">
                    Required
                  </div>
                </div>
                <VDivider vertical />
                <div>
                  <span class="text-h5 font-weight-bold">{{ alloc.totalPopulation }}</span>
                  <div class="text-caption text-medium-emphasis">
                    Populasi
                  </div>
                </div>
              </div>

              <VChip
                :color="alloc.color"
                variant="tonal"
                size="small"
              >
                <VIcon
                  icon="bx-gas-pump"
                  start
                  size="14"
                />
                {{ alloc.dailyFuelL.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} L/hari
              </VChip>
            </VCardText>
          </VCard>
        </VCol>
      </VRow>
    </VCardText>
  </VCard>
</template>
