<script setup lang="ts">
import type { GlobalCapacityTuningResponse } from '@/composables/useAiApi'

interface Props {
  tuningData: GlobalCapacityTuningResponse | null
  isLoading?: boolean
  isError?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  tuningData: null,
  isLoading: false,
  isError: false,
})

const emit = defineEmits<{ retry: [] }>()

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
          v-if="props.tuningData"
          color="primary"
          size="x-small"
          variant="tonal"
          class="font-weight-medium ms-1"
        >
          {{ props.tuningData.global_capacity_summary.total_fleet_units }} Fleet Units Tuned
        </VChip>
      </VCardTitle>

      <VCardSubtitle class="text-caption text-medium-emphasis">
        Analisis alokasi BBM teoritis vs konsumsi harian aktual seluruh armada Kideco
      </VCardSubtitle>

      <template v-if="props.tuningData" #append>
        <VChip
          :color="statusColor"
          variant="tonal"
          class="font-weight-bold px-3"
        >
          <VIcon icon="bx-check-shield" start size="16" />
          {{ props.tuningData.global_fuel_tuning_summary.global_tuning_status }}
        </VChip>
      </template>
    </VCardItem>

    <VCardText class="pt-2">
      <div v-if="props.isLoading" class="d-flex justify-center my-6">
        <VProgressCircular indeterminate color="primary" />
      </div>

      <div v-else-if="props.isError || !props.tuningData" class="d-flex flex-column align-center justify-center text-center py-8">
        <VIcon icon="bx-error-circle" size="40" class="text-error mb-3" />
        <p class="text-body-2 text-medium-emphasis mb-3">Gagal memuat data tuning kapasitas global.</p>
        <VBtn variant="tonal" color="primary" size="small" :loading="props.isLoading" @click="emit('retry')">
          Coba Lagi
        </VBtn>
      </div>

      <template v-else>
        <!-- CLEAN METRIC SUMMARY CARDS -->
        <VRow class="mb-4" density="comfortable">
          <!-- KAPASITAS EFEKTIF BCM/DAY -->
          <VCol cols="12" sm="6" md="3">
            <div class="metric-item border rounded-lg p-3">
              <span class="text-caption text-medium-emphasis font-weight-medium">Effective Capacity</span>
              <h4 class="text-h5 font-weight-bold text-high-emphasis my-1">
                {{ (props.tuningData?.global_capacity_summary?.effective_cap_bcmday ?? 0).toLocaleString('id-ID') }}
                <span class="text-caption text-medium-emphasis">BCM/day</span>
              </h4>
              <span class="text-caption text-primary font-weight-medium">
                Utilisasi Armada: {{ props.tuningData?.global_capacity_summary?.fleet_utilization_pct ?? 0 }}%
              </span>
            </div>
          </VCol>

          <!-- REQUIRED OPERATING UNITS -->
          <VCol cols="12" sm="6" md="3">
            <div class="metric-item border rounded-lg p-3">
              <span class="text-caption text-medium-emphasis font-weight-medium">Operating vs Standby</span>
              <h4 class="text-h5 font-weight-bold text-high-emphasis my-1">
                {{ props.tuningData?.global_capacity_summary?.required_operating_units ?? 0 }}
                <span class="text-caption text-medium-emphasis">/ {{ props.tuningData?.global_capacity_summary?.total_fleet_units ?? 0 }} Unit</span>
              </h4>
              <span class="text-caption text-medium-emphasis">
                Standby Unit: <strong>{{ props.tuningData?.global_capacity_summary?.standby_units ?? 0 }} Unit</strong>
              </span>
            </div>
          </VCol>

          <!-- TUNED VS ACTUAL FUEL -->
          <VCol cols="12" sm="6" md="3">
            <div class="metric-item border rounded-lg p-3">
              <span class="text-caption text-medium-emphasis font-weight-medium">Tuned vs Actual Fuel</span>
              <h4 class="text-h5 font-weight-bold text-high-emphasis my-1">
                {{ (props.tuningData?.global_fuel_tuning_summary?.actual_total_fuel_lday ?? 0).toLocaleString('id-ID') }}
                <span class="text-caption text-medium-emphasis">L/day</span>
              </h4>
              <span class="text-caption text-medium-emphasis">
                Tuned Target: <strong class="text-primary">{{ (props.tuningData?.global_fuel_tuning_summary?.tuned_combined_fuel_lday ?? 0).toLocaleString('id-ID') }} L</strong>
              </span>
            </div>
          </VCol>

          <!-- NET FUEL VARIANCE -->
          <VCol cols="12" sm="6" md="3">
            <div class="metric-item border rounded-lg p-3">
              <span class="text-caption text-medium-emphasis font-weight-medium">Net Fuel Variance</span>
              <h4 class="text-h5 font-weight-bold text-warning my-1">
                +{{ (props.tuningData?.global_fuel_tuning_summary?.net_fuel_variance_lday ?? 0).toLocaleString('id-ID') }}
                <span class="text-caption text-medium-emphasis">Liter</span>
              </h4>
              <span class="text-caption font-weight-medium text-warning">
                Selisih Variansi: +{{ props.tuningData?.global_fuel_tuning_summary?.overall_variance_pct ?? 0 }}%
              </span>
            </div>
          </VCol>
        </VRow>

        <!-- TABLE UNIT TUNING COMPARISON -->
        <div class="border rounded-lg overflow-hidden">
          <VTable density="compact" class="text-no-wrap">
            <thead>
              <tr class="bg-surface" style="background-color: rgba(var(--v-theme-primary), 0.04) !important;">
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
                <td
                  class="text-right font-weight-medium text-tabular-nums"
                  :class="item.variance_liters > 0 ? 'text-error' : 'text-success'"
                >
                  {{ item.variance_liters > 0 ? '+' : '' }}{{ item.variance_liters.toLocaleString('id-ID') }} ({{ item.variance_pct }}%)
                </td>
                <td class="text-center">
                  <VChip
                    :color="item.tuning_status === 'EFFICIENT' ? 'success' : item.tuning_status === 'OVER_CONSUMPTION' ? 'error' : 'warning'"
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
