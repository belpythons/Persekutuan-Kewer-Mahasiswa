<script setup lang="ts">
import type { SpikeReportPerUnit } from '@/composables/useAiApi'

interface Props {
  spikeReport: SpikeReportPerUnit[] | null
  isLoading: boolean
}

const props = withDefaults(defineProps<Props>(), {
  spikeReport: null,
  isLoading: false,
})

interface AnomalousUnit {
  rank: number
  unitCode: string
  activity: string
  spikeCount: number
  fcNormal: number
  fcSpike: number
  maxFr: number | null
}

// ponytail: stdFcMap duplicates equipment_catalogs.fc_lhr (already in the DB) as a client-side
// fallback for when the API's avg_fc_normal comes back 0. Real fix is making the backend's
// spike_report_per_unit always populate avg_fc_normal from equipment_catalogs; flagged separately.
const stdFcMap: Record<string, number> = {
  'EX2600-6': 187.0, 'HT 2600': 190.0, 'PC 1250': 93.3, 'PC1250-11R': 93.3,
  'PC 2000': 125.0, 'PC2000-11R': 100.0, 'PC 3400': 195.6, 'HD785-7': 75.0,
  'HD785-7MUD': 75.0, 'HD785-SPIKE': 75.0, 'EX2600-SPIKE': 187.0,
  'MID DRILLING': 54.2, 'SMALL DRILLING': 28.1, 'Dozer375': 54.2,
  'D375A6R': 67.0, 'Water Pump': 36.0, 'Booster Pump': 40.0, 'Dragflow': 36.0,
  'EGS380-6': 10.0,
}

const topUnits = computed<AnomalousUnit[]>(() => {
  if (!props.spikeReport || props.spikeReport.length === 0) return []

  return props.spikeReport
    .slice()
    .sort((a, b) => {
      const devA = a.avg_fc_spike - a.avg_fc_normal
      const devB = b.avg_fc_spike - b.avg_fc_normal
      return b.total_spikes - a.total_spikes || devB - devA
    })
    .slice(0, 5)
    .map((item, idx) => {
      const normal = item.avg_fc_normal > 0 ? item.avg_fc_normal : (stdFcMap[item.unit] || item.avg_fc_spike * 0.85)
      return {
        rank: idx + 1,
        unitCode: item.unit,
        activity: item.activity.charAt(0).toUpperCase() + item.activity.slice(1).toLowerCase(),
        spikeCount: item.total_spikes,
        fcNormal: Number(normal.toFixed(1)),
        fcSpike: item.avg_fc_spike,
        maxFr: item.max_fr_recorded > 0 ? item.max_fr_recorded : null,
      }
    })
})

const activityColor = (activity: string) => {
  switch (activity) {
    case 'Hauling': return 'secondary'
    case 'Loading': return 'primary'
    case 'Supporting': return 'warning'
    case 'Support': return 'warning'
    case 'Dewatering': return 'info'
    default: return 'default'
  }
}

const fcDeviation = (normal: number, spike: number) => {
  if (normal === 0) return '0.0'
  const dev = ((spike - normal) / normal) * 100
  return Math.abs(dev).toFixed(1)
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
            icon="bx-trophy"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        Top Anomalous Units
      </VCardTitle>
      <VCardSubtitle>Leaderboard Spike Tertinggi</VCardSubtitle>
    </VCardItem>

    <VCardText class="pb-1">
      <VTable
        density="compact"
        class="text-no-wrap"
      >
        <thead>
          <tr>
            <th>#</th>
            <th>Unit</th>
            <th>Activity</th>
            <th class="text-end">
              Spikes
            </th>
            <th class="text-end">
              FC Normal
            </th>
            <th class="text-end">
              FC Spike
            </th>
            <th class="text-end">
              Deviasi
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="7" class="text-center py-6">
              <VProgressCircular indeterminate color="primary" size="28" />
            </td>
          </tr>
          <tr v-else-if="topUnits.length === 0">
            <td colspan="7" class="text-center py-6 text-medium-emphasis">
              <VIcon icon="bx-check-shield" size="32" class="mb-1 text-success d-block mx-auto" />
              Tidak ada anomali spike unit terdeteksi hari ini.
            </td>
          </tr>
          <tr
            v-for="unit in topUnits"
            :key="unit.rank"
            v-else
          >
            <td>
              <VAvatar
                :color="unit.rank <= 3 ? 'error' : 'default'"
                :variant="unit.rank <= 3 ? 'tonal' : 'outlined'"
                size="28"
                rounded
              >
                <span class="text-caption font-weight-bold">{{ unit.rank }}</span>
              </VAvatar>
            </td>
            <td>
              <span class="font-weight-bold" style="font-family: monospace;">{{ unit.unitCode }}</span>
            </td>
            <td>
              <VChip
                :color="activityColor(unit.activity)"
                size="small"
                variant="tonal"
              >
                {{ unit.activity }}
              </VChip>
            </td>
            <td class="text-end">
              <VChip
                color="error"
                size="small"
                variant="flat"
              >
                {{ unit.spikeCount }}
              </VChip>
            </td>
            <td class="text-end text-medium-emphasis">
              {{ unit.fcNormal }} L/hr
            </td>
            <td class="text-end font-weight-bold text-error">
              {{ unit.fcSpike }} L/hr
            </td>
            <td class="text-end">
              <span class="text-error font-weight-medium">+{{ fcDeviation(unit.fcNormal, unit.fcSpike) }}%</span>
            </td>
          </tr>
        </tbody>
      </VTable>
    </VCardText>
  </VCard>
</template>
