<script setup lang="ts">
interface Props {
  fleetType: 'Loading' | 'Hauling'
  totalUnits: number
  activeUnits: number
  utilisation: number
  fleetBcmHr: number
  fleetFuelHr: number
  dailyFuelAllocation: number
  models: string
}

const props = withDefaults(defineProps<Props>(), {
  fleetType: 'Loading',
  totalUnits: 70,
  activeUnits: 22,
  utilisation: 27.12,
  fleetBcmHr: 37660,
  fleetFuelHr: 5836,
  dailyFuelAllocation: 50952.2,
  models: 'EX2600-6: 3, PC1250: 30, PC2000: 34, PC3400: 3',
})

const fleetColor = computed(() => props.fleetType === 'Loading' ? 'primary' : 'info')
const fleetIcon = computed(() => props.fleetType === 'Loading' ? 'bx-loader-circle' : 'bx-car')
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
      <VCardSubtitle>{{ props.models }}</VCardSubtitle>
    </VCardItem>

    <VCardText>
      <div class="d-flex align-center gap-4 mb-4">
        <div class="text-center">
          <h4 class="text-h4 font-weight-bold">
            {{ props.totalUnits }}
          </h4>
          <span class="text-caption text-medium-emphasis">Total Unit</span>
        </div>
        <VDivider vertical />
        <div class="text-center">
          <h4
            class="text-h4 font-weight-bold"
            :class="`text-${fleetColor}`"
          >
            {{ props.activeUnits }}
          </h4>
          <span class="text-caption text-medium-emphasis">Active</span>
        </div>
        <VDivider vertical />
        <div class="text-center">
          <h4 class="text-h4 font-weight-bold text-warning">
            {{ props.utilisation }}%
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
          <strong>{{ props.fleetBcmHr.toLocaleString('id-ID') }} BCM/jam</strong>
        </div>
        <div class="d-flex justify-space-between">
          <span class="text-medium-emphasis">
            <VIcon
              icon="bx-gas-pump"
              size="16"
              class="me-1"
            />Fuel Rate
          </span>
          <strong>{{ props.fleetFuelHr.toLocaleString('id-ID') }} L/jam</strong>
        </div>
        <div class="d-flex justify-space-between">
          <span class="text-medium-emphasis">
            <VIcon
              icon="bx-calendar"
              size="16"
              class="me-1"
            />Alokasi Harian
          </span>
          <strong class="text-primary">{{ props.dailyFuelAllocation.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} L/hari</strong>
        </div>
      </div>
    </VCardText>
  </VCard>
</template>
