<script setup>
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';

const sheetProjectsStore = UseSheetProjectsStore();

const sheetProjects = computed(() => sheetProjectsStore.sheetProjects);

const hasInProgressSheet = computed(() => {
  return sheetProjects.value.some(sheet => sheet.status === 'IN_PROGRESS');
});

const getStatusBadgeClass = (status) => {
  const classes = {
    'IN_PROGRESS': 'badge-info',
    'INVOICED': 'badge-success',
    'CANCELLED': 'badge-error'
  };
  return classes[status] || 'badge-ghost';
};

const getStatusLabel = (status) => {
  const labels = {
    'IN_PROGRESS': 'EN EJECUCIÓN',
    'INVOICED': 'FACTURADO',
    'CANCELLED': 'CANCELADO'
  };
  return labels[status] || status;
};

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
      <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-file-invoice-dollar text-blue-600 text-xl"></i>
        Planillas del Proyecto
      </h2>
      <RouterLink 
        v-if="!hasInProgressSheet"
        to="/sheet/form" 
        class="btn btn-primary btn-sm"
      >
        <i class="las la-plus text-lg"></i>
        Crear Nueva Planilla
      </RouterLink>
      <div v-else class="badge badge-warning gap-2">
        <i class="las la-exclamation-triangle"></i>
        Hay una planilla en ejecución
      </div>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-base-200">
            <th>#</th>
            <th>Serie</th>
            <th>Estado</th>
            <th>Fecha Emisión</th>
            <th>Período Inicio</th>
            <th>Período Fin</th>
            <th>Tipo Servicio</th>
            <th class="text-right">Galones</th>
            <th class="text-right">Barriles</th>
            <th class="text-right">M³</th>
            <th class="text-center">Acciones</th>
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
              <td>{{ sheet.id }}</td>
              <td class="font-mono text-sm">{{ sheet.series_code }}</td>
              <td>
                <span 
                  class="badge badge-sm" 
                  :class="getStatusBadgeClass(sheet.status)"
                >
                  {{ getStatusLabel(sheet.status) }}
                </span>
              </td>
              <td>{{ formatDate(sheet.issue_date) }}</td>
              <td>{{ formatDate(sheet.period_start) }}</td>
              <td>{{ formatDate(sheet.period_end) }}</td>
              <td>{{ sheet.service_type }}</td>
              <td class="text-right">{{ sheet.total_gallons.toLocaleString() }}</td>
              <td class="text-right">{{ sheet.total_barrels.toLocaleString() }}</td>
              <td class="text-right">{{ sheet.total_cubic_meters.toFixed(1) }}</td>
              <td class="text-center">
                <div class="flex gap-1 justify-center">
                  <button class="btn btn-ghost btn-xs" title="Ver detalles">
                    <i class="las la-eye text-lg"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs" title="Editar">
                    <i class="las la-edit text-lg"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs text-error" title="Eliminar">
                    <i class="las la-trash text-lg"></i>
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
