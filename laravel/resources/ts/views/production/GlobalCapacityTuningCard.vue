<script setup lang="ts">
import type { GlobalCapacityTuningResponse } from '@/composables/useAiApi'

interface Props {
  tuningData: GlobalCapacityTuningResponse | null
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  tuningData: null,
  isLoading: false,
})

const statusColor = computed(() => {
  const status = props.tuningData?.global_fuel_tuning_summary?.global_tuning_status
  if (status === 'OPTIMAL') return 'success'
  if (status === 'WARNING') return 'warning'
  return 'error'
})

const getActivityColor = (activity: string) => {
  const act = activity.toUpperCase()
  if (act.includes('LOADING')) return 'primary'
  if (act.includes('HAULING')) return 'secondary'
  if (act.includes('SUPPORT')) return 'warning'
  return 'info'
}
</script>

<template>
  <VCard class="tuning-card">
    <VCardItem class="pb-3">
      <template #prepend>
        <div class="header-icon-box me-3">
          <VIcon icon="bx-slider-alt" size="24" class="text-primary" />
        </div>
      </template>

      <VCardTitle class="d-flex align-center flex-wrap gap-2 text-h6 font-weight-bold tracking-tight">
        <span>Global Fleet Capacity Tuning & Fuel Variance Analysis</span>
        <VChip
          color="primary"
          size="x-small"
          variant="tonal"
          class="font-weight-medium ms-1"
        >
          324 Fleet Units Tuned
        </VChip>
      </VCardTitle>

      <VCardSubtitle class="text-caption text-medium-emphasis">
        Analisis alokasi BBM teoritis vs konsumsi harian aktual seluruh armada Kideco
      </VCardSubtitle>

      <template #append>
        <VChip
          :color="statusColor"
          variant="tonal"
          class="font-weight-bold px-3"
        >
          <VIcon icon="bx-check-shield" start size="16" />
          {{ props.tuningData?.global_fuel_tuning_summary?.global_tuning_status ?? 'OPTIMAL' }}
        </VChip>
      </template>
    </VCardItem>

    <VCardText class="pt-2">
      <div v-if="props.isLoading" class="d-flex justify-center my-6">
        <VProgressCircular indeterminate color="primary" />
      </div>

      <template v-else>
        <!-- CLEAN METRIC SUMMARY CARDS -->
        <VRow class="mb-4" density="comfortable">
          <!-- KAPASITAS EFEKTIF BCM/DAY -->
          <VCol cols="12" sm="6" md="3">
            <div class="metric-item border rounded-lg p-3">
              <span class="text-caption text-medium-emphasis font-weight-medium">Effective Capacity</span>
              <h4 class="text-h5 font-weight-bold text-high-emphasis my-1">
                {{ (props.tuningData?.global_capacity_summary?.effective_cap_bcmday ?? 418557.6).toLocaleString('id-ID') }}
                <span class="text-caption text-medium-emphasis">BCM/day</span>
              </h4>
              <span class="text-caption text-primary font-weight-medium">
                Utilisasi Armada: {{ props.tuningData?.global_capacity_summary?.fleet_utilization_pct ?? 10.0 }}%
              </span>
            </div>
          </VCol>

          <!-- REQUIRED OPERATING UNITS -->
          <VCol cols="12" sm="6" md="3">
            <div class="metric-item border rounded-lg p-3">
              <span class="text-caption text-medium-emphasis font-weight-medium">Operating vs Standby</span>
              <h4 class="text-h5 font-weight-bold text-high-emphasis my-1">
                {{ props.tuningData?.global_capacity_summary?.required_operating_units ?? 33 }}
                <span class="text-caption text-medium-emphasis">/ {{ props.tuningData?.global_capacity_summary?.total_fleet_units ?? 324 }} Unit</span>
              </h4>
              <span class="text-caption text-medium-emphasis">
                Standby Unit: <strong>{{ props.tuningData?.global_capacity_summary?.standby_units ?? 291 }} Unit</strong>
              </span>
            </div>
          </VCol>

          <!-- TUNED VS ACTUAL FUEL -->
          <VCol cols="12" sm="6" md="3">
            <div class="metric-item border rounded-lg p-3">
              <span class="text-caption text-medium-emphasis font-weight-medium">Tuned vs Actual Fuel</span>
              <h4 class="text-h5 font-weight-bold text-high-emphasis my-1">
                {{ (props.tuningData?.global_fuel_tuning_summary?.actual_total_fuel_lday ?? 25200.0).toLocaleString('id-ID') }}
                <span class="text-caption text-medium-emphasis">L/day</span>
              </h4>
              <span class="text-caption text-medium-emphasis">
                Tuned Target: <strong class="text-primary">{{ (props.tuningData?.global_fuel_tuning_summary?.tuned_combined_fuel_lday ?? 24097.4).toLocaleString('id-ID') }} L</strong>
              </span>
            </div>
          </VCol>

          <!-- NET FUEL VARIANCE -->
          <VCol cols="12" sm="6" md="3">
            <div class="metric-item border rounded-lg p-3">
              <span class="text-caption text-medium-emphasis font-weight-medium">Net Fuel Variance</span>
              <h4 class="text-h5 font-weight-bold text-warning my-1">
                +{{ (props.tuningData?.global_fuel_tuning_summary?.net_fuel_variance_lday ?? 1102.6).toLocaleString('id-ID') }}
                <span class="text-caption text-medium-emphasis">Liter</span>
              </h4>
              <span class="text-caption font-weight-medium text-warning">
                Selisih Variansi: +{{ props.tuningData?.global_fuel_tuning_summary?.overall_variance_pct ?? 4.57 }}%
              </span>
            </div>
          </VCol>
        </VRow>

        <!-- TABLE UNIT TUNING COMPARISON -->
        <div class="border rounded-lg overflow-hidden">
          <VTable density="compact" class="text-no-wrap">
            <thead>
              <tr class="bg-surface" style="background-color: rgba(229, 57, 53, 0.04) !important;">
                <th class="text-left font-weight-bold text-caption">UNIT TYPE</th>
                <th class="text-left font-weight-bold text-caption">AKTIVITAS</th>
                <th class="text-center font-weight-bold text-caption">QTY</th>
                <th class="text-right font-weight-bold text-caption">STD FC (L/HR)</th>
                <th class="text-right font-weight-bold text-caption">TUNED FUEL (L/DAY)</th>
                <th class="text-right font-weight-bold text-caption">ACTUAL FUEL (L/DAY)</th>
                <th class="text-right font-weight-bold text-caption">VARIANCE (L)</th>
                <th class="text-center font-weight-bold text-caption">STATUS TUNING</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, idx) in props.tuningData?.unit_tuning_comparison ?? []"
                :key="idx"
              >
                <td class="font-weight-semibold text-high-emphasis">
                  {{ item.unit_name }}
                </td>
                <td>
                  <VChip
                    size="x-small"
                    :color="getActivityColor(item.activity)"
                    variant="tonal"
                    class="font-weight-medium"
                  >
                    {{ item.activity }}
                  </VChip>
                </td>
                <td class="text-center font-weight-medium text-medium-emphasis">
                  {{ item.fleet_qty }}
                </td>
                <td class="text-right font-weight-medium text-medium-emphasis">
                  {{ item.std_fc_lhr.toFixed(1) }}
                </td>
                <td class="text-right font-weight-medium text-high-emphasis">
                  {{ item.tuned_fuel_allocation_lday.toLocaleString('id-ID') }}
                </td>
                <td class="text-right font-weight-medium text-high-emphasis">
                  {{ item.actual_fuel_consumed_lday.toLocaleString('id-ID') }}
                </td>
                <td class="text-right font-weight-medium text-warning">
                  +{{ item.variance_liters.toLocaleString('id-ID') }} ({{ item.variance_pct }}%)
                </td>
                <td class="text-center">
                  <VChip
                    :color="item.tuning_status === 'EFFICIENT' ? 'success' : 'warning'"
                    size="x-small"
                    variant="tonal"
                    class="font-weight-semibold"
                  >
                    {{ item.tuning_status }}
                  </VChip>
                </td>
              </tr>
            </tbody>
          </VTable>
        </div>
      </template>
    </VCardText>
  </VCard>
</template>

<style scoped>
.tuning-card {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.header-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: rgba(var(--v-theme-primary), 0.08);
}

.metric-item {
  background-color: rgba(var(--v-theme-surface), 0.5);
  border-color: rgba(var(--v-border-color), var(--v-border-opacity)) !important;
  transition: border-color 0.2s ease;
}

.metric-item:hover {
  border-color: rgba(var(--v-theme-primary), 0.3) !important;
}

.tracking-tight {
  letter-spacing: -0.3px;
}
</style>
