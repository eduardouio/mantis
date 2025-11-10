<script setup>
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';

const sheetProjectsStore = UseSheetProjectsStore();

const sheetProjects = computed(() => sheetProjectsStore.sheetProjects);

const hasInProgressSheet = computed(() => {
  return sheetProjects.value.some(sheet => sheet.status === 'IN_PROGRESS');
});

const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ'
  }).format(value);
};

const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Intl.DateTimeFormat('es-GT').format(new Date(date));
};
</script>

<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center mb-4">
      <h2 class="font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-file-invoice-dollar text-blue-600"></i>
        Planillas del Proyecto
      </h2>
      <RouterLink 
        v-if="!hasInProgressSheet"
        to="/sheet/form" 
        class="btn btn-primary btn-sm"
      >
        <i class="las la-plus"></i>
        Crear Nueva Planilla
      </RouterLink>
      <div v-else class="text-warning">
        <i class="las la-exclamation-triangle"></i>
        Hay una planilla en ejecución
      </div>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-base-200">
            <th class="p-2">#</th>
            <th class="p-2">Serie</th>
            <th class="p-2">Estado</th>
            <th class="p-2">Fecha Emisión</th>
            <th class="p-2">Período Inicio</th>
            <th class="p-2">Período Fin</th>
            <th class="p-2">Tipo Servicio</th>
            <th class="p-2 text-right">Galones</th>
            <th class="p-2 text-right">Barriles</th>
            <th class="p-2 text-right">M³</th>
            <th class="p-2 text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="sheetProjects.length === 0">
            <tr>
              <td colspan="11" class="text-center text-gray-500 py-8">
                <i class="las la-inbox text-4xl"></i>
                <p>No hay planillas registradas para este proyecto</p>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="sheet in sheetProjects" :key="sheet.id">
              <td class="p-2">{{ sheet.id }}</td>
              <td class="p-2 font-mono">{{ sheet.series_code }}</td>
              <td class="p-2">{{ sheet.status }}</td>
              <td class="p-2">{{ formatDate(sheet.issue_date) }}</td>
              <td class="p-2">{{ formatDate(sheet.period_start) }}</td>
              <td class="p-2">{{ formatDate(sheet.period_end) }}</td>
              <td class="p-2">{{ sheet.service_type }}</td>
              <td class="p-2 text-right">{{ sheet.total_gallons.toLocaleString() }}</td>
              <td class="p-2 text-right">{{ sheet.total_barrels.toLocaleString() }}</td>
              <td class="p-2 text-right">{{ sheet.total_cubic_meters.toFixed(1) }}</td>
              <td class="p-2 text-center">
                <div class="flex gap-1 justify-center">
                  <button class="btn btn-ghost btn-xs" title="Ver detalles">
                    <i class="las la-eye"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs" title="Editar">
                    <i class="las la-edit"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs text-error" title="Eliminar">
                    <i class="las la-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
