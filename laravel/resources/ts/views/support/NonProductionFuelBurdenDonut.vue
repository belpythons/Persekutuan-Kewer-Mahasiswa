<script setup lang="ts">
import { useTheme } from 'vuetify'
import { hexToRgb } from '@core/utils/colorConverter'
import type { ActivityBreakdown } from '@/composables/useAiApi'

interface Props {
  activityBreakdown: ActivityBreakdown[] | null
  isLoading: boolean
}

const props = withDefaults(defineProps<Props>(), {
  activityBreakdown: null,
  isLoading: false,
})

const vuetifyTheme = useTheme()

// Non-production = Supporting + Dewatering fleets (support the pit but don't move BCM);
// Production = Loading + Hauling (the fleets that actually produce BCM).
const NON_PRODUCTION_ACTIVITIES = ['supporting', 'dewatering']

const breakdown = computed(() => {
  if (!props.activityBreakdown || props.activityBreakdown.length === 0) return null

  let nonProdFuel = 0
  let prodFuel = 0

  for (const a of props.activityBreakdown) {
    if (NON_PRODUCTION_ACTIVITIES.includes(a.activity.toLowerCase()))
      nonProdFuel += a.combined_fuel_lday
    else
      prodFuel += a.combined_fuel_lday
  }

  const totalFuel = nonProdFuel + prodFuel

  return {
    nonProdFuel,
    prodFuel,
    totalFuel,
    nonProdPct: totalFuel > 0 ? (nonProdFuel / totalFuel) * 100 : 0,
  }
})

const chartOptions = computed(() => {
  const currentTheme = vuetifyTheme.current.value.colors
  const variableTheme = vuetifyTheme.current.value.variables
  const primaryTextColor = `rgba(${hexToRgb(String(currentTheme['on-surface']))},${variableTheme['high-emphasis-opacity']})`
  const nonProdPct = breakdown.value?.nonProdPct ?? 0

  return {
    chart: {
      type: 'donut' as const,
    },
    labels: ['Non-Produksi (Support + Dewatering)', 'Produksi (Loading + Hauling)'],
    colors: [currentTheme.warning, currentTheme.primary],
    legend: {
      position: 'bottom' as const,
      fontSize: '12px',
      labels: { colors: primaryTextColor },
    },
    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          labels: {
            show: true,
            name: { show: true, fontSize: '13px' },
            value: { show: true, fontSize: '18px', fontWeight: 700 },
            total: {
              show: true,
              label: 'Beban Non-Produksi',
              fontSize: '12px',
              formatter: () => `${nonProdPct.toFixed(1)}%`,
            },
          },
        },
      },
    },
    dataLabels: {
      enabled: true,
      formatter: (val: number) => `${val.toFixed(1)}%`,
    },
    tooltip: {
      y: { formatter: (v: number) => `${v.toLocaleString('id-ID')} L/hari` },
    },
  }
})

const series = computed(() => breakdown.value ? [breakdown.value.nonProdFuel, breakdown.value.prodFuel] : [])
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>Non-Production Fuel Burden Analysis</VCardTitle>
      <VCardSubtitle>
        <template v-if="breakdown">
          Beban Non-Produksi: <strong>{{ breakdown.nonProdFuel.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} L/hari</strong>
          ({{ breakdown.nonProdPct.toFixed(1) }}% dari Total Solar)
        </template>
        <template v-else>
          Kontribusi solar unit Supporting & Dewatering terhadap total konsumsi BBM
        </template>
      </VCardSubtitle>
    </VCardItem>
    <VCardText>
      <div v-if="isLoading" class="d-flex justify-center align-center" style="block-size: 320px;">
        <VProgressCircular indeterminate color="primary" />
      </div>
      <div v-else-if="!breakdown || series.length === 0" class="d-flex flex-column align-center justify-center text-medium-emphasis" style="block-size: 320px;">
        <VIcon icon="bx-pie-chart-alt-2" size="36" class="mb-2 opacity-50" />
        <span class="text-caption">Tidak ada data alokasi BBM aktivitas</span>
      </div>
      <VueApexCharts
        v-else
        type="donut"
        :height="320"
        :options="chartOptions"
        :series="series"
      />
    </VCardText>
  </VCard>
</template>

<style lang="scss">
@use "@core-scss/template/libs/apex-chart.scss";
</style>
