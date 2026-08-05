<script setup lang="ts">
import { useForm, usePage } from '@inertiajs/vue3';
import { computed } from 'vue';

interface FuelRatioLog {
  id: number;
  equipment_id: string;
  operating_hours: number;
  fuel_consumed_liters: number;
  load_tonnage: number;
  calculated_fuel_ratio: number;
  created_at?: string;
}

defineProps<{
  logs: FuelRatioLog[];
}>();

const page = usePage();
const apiError = computed(() => (page.props as any).errors?.api_error);

const form = useForm({
  equipment_id: '',
  operating_hours: null,
  fuel_consumed_liters: null,
  load_tonnage: null,
});

const submit = () => {
  form.post('/fuel-ratio/calculate', {
    onSuccess: () => form.reset(),
  });
};
</script>

<template>
  <div class="p-6 max-w-5xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Fuel Ratio & Capacity Analytics</h1>

    <!-- Error Alert -->
    <div v-if="apiError" class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
      {{ apiError }}
    </div>

    <!-- Input Form -->
    <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 bg-white p-6 rounded shadow">
      <div>
        <label class="block text-sm font-medium mb-1">Equipment ID</label>
        <input v-model="form.equipment_id" type="text" placeholder="e.g. EXCA-001" class="w-full border p-2 rounded" required />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Operating Hours</label>
        <input v-model="form.operating_hours" type="number" step="0.1" placeholder="e.g. 10.5" class="w-full border p-2 rounded" required />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Fuel Consumed (Liters)</label>
        <input v-model="form.fuel_consumed_liters" type="number" step="0.1" placeholder="e.g. 250.0" class="w-full border p-2 rounded" required />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Load Tonnage</label>
        <input v-model="form.load_tonnage" type="number" step="0.1" placeholder="e.g. 100.0" class="w-full border p-2 rounded" required />
      </div>
      <button type="submit" :disabled="form.processing" class="md:col-span-2 bg-blue-600 hover:bg-blue-700 text-white font-bold p-3 rounded transition">
        {{ form.processing ? 'Calculating...' : 'Calculate & Save Fuel Ratio' }}
      </button>
    </form>

    <!-- Logs Table -->
    <div class="bg-white rounded shadow overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-gray-100 border-b">
            <th class="p-3">Equipment ID</th>
            <th class="p-3">Operating Hours</th>
            <th class="p-3">Fuel (L)</th>
            <th class="p-3">Load (Tons)</th>
            <th class="p-3">Calculated Ratio</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id" class="border-b hover:bg-gray-50">
            <td class="p-3 font-medium">{{ log.equipment_id }}</td>
            <td class="p-3">{{ log.operating_hours }} hrs</td>
            <td class="p-3">{{ log.fuel_consumed_liters }} L</td>
            <td class="p-3">{{ log.load_tonnage }} T</td>
            <td class="p-3 font-bold text-blue-600">{{ log.calculated_fuel_ratio }}</td>
          </tr>
          <tr v-if="logs.length === 0">
            <td colspan="5" class="p-4 text-center text-gray-500">No fuel ratio logs found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
