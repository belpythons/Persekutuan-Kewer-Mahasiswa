<script setup lang="ts">
interface SPORow {
  activity: string
  unit_model: string
  unit_code: string
  spo_target_bcm_hr: number
  actual_bcm_hr: number
  spo_target_fc_lhr: number
  actual_fc_lhr: number
  deviasi_fc_pct: number
  total_fuel_l_day: number
  nn_spike_events: number
}

const activityFilter = ref('ALL')

const tableData = ref<SPORow[]>([
  { activity: 'LOADING', unit_model: 'PC2000-11R', unit_code: 'EX-2004', spo_target_bcm_hr: 920.0, actual_bcm_hr: 650.0, spo_target_fc_lhr: 100.0, actual_fc_lhr: 185.53, deviasi_fc_pct: 85.5, total_fuel_l_day: 10900.0, nn_spike_events: 9 },
  { activity: 'LOADING', unit_model: 'EX2600-6', unit_code: 'EX-2601', spo_target_bcm_hr: 920.0, actual_bcm_hr: 880.0, spo_target_fc_lhr: 187.0, actual_fc_lhr: 192.28, deviasi_fc_pct: 2.8, total_fuel_l_day: 17428.4, nn_spike_events: 366 },
  { activity: 'HAULING', unit_model: 'HD785-7', unit_code: 'DT-042', spo_target_bcm_hr: 483.57, actual_bcm_hr: 450.0, spo_target_fc_lhr: 77.0, actual_fc_lhr: 80.78, deviasi_fc_pct: 4.9, total_fuel_l_day: 1615.6, nn_spike_events: 366 },
  { activity: 'HAULING', unit_model: 'HD785-8', unit_code: 'DT-416', spo_target_bcm_hr: 520.0, actual_bcm_hr: 495.0, spo_target_fc_lhr: 85.0, actual_fc_lhr: 88.5, deviasi_fc_pct: 4.1, total_fuel_l_day: 1770.0, nn_spike_events: 5 },
  { activity: 'LOADING', unit_model: 'PC1250', unit_code: 'EX-1203', spo_target_bcm_hr: 350.0, actual_bcm_hr: 280.0, spo_target_fc_lhr: 65.0, actual_fc_lhr: 72.0, deviasi_fc_pct: 10.8, total_fuel_l_day: 1440.0, nn_spike_events: 3 },
])

const filteredData = computed(() => {
  if (activityFilter.value === 'ALL') return tableData.value
  return tableData.value.filter(r => r.activity === activityFilter.value)
})

const headers = [
  { title: 'Activity', key: 'activity' },
  { title: 'Model', key: 'unit_model' },
  { title: 'Unit Code', key: 'unit_code' },
  { title: 'SPO BCM/hr', key: 'spo_target_bcm_hr', align: 'end' as const },
  { title: 'Actual BCM/hr', key: 'actual_bcm_hr', align: 'end' as const },
  { title: 'SPO FC', key: 'spo_target_fc_lhr', align: 'end' as const },
  { title: 'Actual FC', key: 'actual_fc_lhr', align: 'end' as const },
  { title: 'Deviasi %', key: 'deviasi_fc_pct', align: 'end' as const },
  { title: 'Solar (L/Day)', key: 'total_fuel_l_day', align: 'end' as const },
  { title: 'Spikes', key: 'nn_spike_events', align: 'center' as const },
]

const activityColor = (a: string) => a === 'LOADING' ? 'primary' : a === 'HAULING' ? 'info' : 'warning'
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>SPO Compliance Audit — Detail Unit</VCardTitle>
      <VCardSubtitle>Kepatuhan konsumsi solar terhadap Standar Prosedur Operasional</VCardSubtitle>
    </VCardItem>
    <VCardText>
      <VRow class="mb-4">
        <VCol
          cols="12"
          sm="4"
        >
          <VSelect
            v-model="activityFilter"
            :items="['ALL', 'LOADING', 'HAULING']"
            label="Filter Activity"
            density="compact"
          />
        </VCol>
      </VRow>

      <VDataTable
        :headers="headers"
        :items="filteredData"
        :items-per-page="10"
        density="compact"
        class="text-no-wrap"
      >
        <template #item.activity="{ item }">
          <VChip
            :color="activityColor(item.activity)"
            size="small"
            variant="tonal"
          >
            {{ item.activity }}
          </VChip>
        </template>
        <template #item.unit_model="{ item }">
          <strong>{{ item.unit_model }}</strong>
        </template>
        <template #item.unit_code="{ item }">
          <code>{{ item.unit_code }}</code>
        </template>
        <template #item.spo_target_bcm_hr="{ item }">
          <span class="text-medium-emphasis">{{ item.spo_target_bcm_hr.toFixed(1) }}</span>
        </template>
        <template #item.actual_bcm_hr="{ item }">
          <span :class="item.actual_bcm_hr < item.spo_target_bcm_hr * 0.8 ? 'text-error font-weight-bold' : ''">
            {{ item.actual_bcm_hr.toFixed(1) }}
          </span>
        </template>
        <template #item.spo_target_fc_lhr="{ item }">
          <span class="text-medium-emphasis">{{ item.spo_target_fc_lhr.toFixed(1) }}</span>
        </template>
        <template #item.actual_fc_lhr="{ item }">
          <span :class="item.actual_fc_lhr > item.spo_target_fc_lhr ? 'text-error font-weight-bold' : ''">
            {{ item.actual_fc_lhr.toFixed(2) }}
          </span>
        </template>
        <template #item.deviasi_fc_pct="{ item }">
          <VChip
            :color="item.deviasi_fc_pct > 15 ? 'error' : item.deviasi_fc_pct > 5 ? 'warning' : 'success'"
            size="small"
            variant="flat"
          >
            +{{ item.deviasi_fc_pct.toFixed(1) }}%
          </VChip>
        </template>
        <template #item.total_fuel_l_day="{ item }">
          <strong>{{ item.total_fuel_l_day.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }}</strong>
        </template>
        <template #item.nn_spike_events="{ item }">
          <VChip
            :color="item.nn_spike_events > 5 ? 'error' : 'default'"
            size="small"
            :variant="item.nn_spike_events > 5 ? 'flat' : 'outlined'"
          >
            {{ item.nn_spike_events }}
          </VChip>
        </template>
      </VDataTable>
    </VCardText>
  </VCard>
</template>
