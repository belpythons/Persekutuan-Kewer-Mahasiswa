<script setup lang="ts">
interface Props {
  criticalUnitsCount: number
  totalWasteFuel: number
}

const props = withDefaults(defineProps<Props>(), {
  criticalUnitsCount: 14,
  totalWasteFuel: 14820,
})
</script>

<template>
  <VAlert
    type="error"
    variant="tonal"
    border="start"
    prominent
    class="mb-0"
  >
    <template #prepend>
      <VIcon
        icon="bx-error-circle"
        size="32"
      />
    </template>
    <VAlertTitle class="text-body-1 font-weight-bold mb-1">
      ⚠️ {{ props.criticalUnitsCount }} Unit Beroperasi di Bawah SPO
    </VAlertTitle>
    <div class="text-body-2">
      Deviasi Konsumsi BBM > +15% atau Produktivitas < -20% dari standar operasional.
      <br>
      <strong>Total Potensi Pemborosan Solar Fleet Produksi: +{{ props.totalWasteFuel.toLocaleString('id-ID') }} Liter / Hari</strong>
    </div>
  </VAlert>
</template>
