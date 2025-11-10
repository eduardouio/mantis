<script setup>
import { ref } from 'vue';
import { RouterLink } from 'vue-router';

// Datos ficticios basados en SheetProject
const sheetProjects = ref([
  {
    id: 1,
    series_code: 'PSL-PS-2024-1000',
    status: 'IN_PROGRESS',
    issue_date: '2024-01-15',
    period_start: '2024-01-01',
    period_end: '2024-01-31',
    service_type: 'ALQUILER Y MANTENIMIENTO',
    total_gallons: 1500,
    total_barrels: 35,
    total_cubic_meters: 5.7,
    subtotal: 15000.00,
    tax_amount: 1950.00,
    total: 16950.00
  },
  {
    id: 2,
    series_code: 'PSL-PS-2024-1001',
    status: 'INVOICED',
    issue_date: '2024-02-15',
    period_start: '2024-02-01',
    period_end: '2024-02-29',
    service_type: 'ALQUILER',
    total_gallons: 1200,
    total_barrels: 28,
    total_cubic_meters: 4.5,
    subtotal: 12000.00,
    tax_amount: 1560.00,
    total: 13560.00
  },
  {
    id: 3,
    series_code: 'PSL-PS-2024-1002',
    status: 'IN_PROGRESS',
    issue_date: '2024-03-15',
    period_start: '2024-03-01',
    period_end: '2024-03-31',
    service_type: 'MANTENIMIENTO',
    total_gallons: 2000,
    total_barrels: 47,
    total_cubic_meters: 7.6,
    subtotal: 18500.00,
    tax_amount: 2405.00,
    total: 20905.00
  }
]);

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
      <RouterLink to="/sheet/form" class="btn btn-primary btn-sm">
        <i class="las la-plus text-lg"></i>
        Crear Nueva Planilla
      </RouterLink>
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
            <th class="text-right">Subtotal</th>
            <th class="text-right">IVA</th>
            <th class="text-right">Total</th>
            <th class="text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="sheetProjects.length === 0">
            <tr>
              <td colspan="14" class="text-center text-gray-500 py-8">
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
              <td class="text-right font-semibold">{{ formatCurrency(sheet.subtotal) }}</td>
              <td class="text-right">{{ formatCurrency(sheet.tax_amount) }}</td>
              <td class="text-right font-bold text-primary">{{ formatCurrency(sheet.total) }}</td>
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
        <tfoot v-if="sheetProjects.length > 0">
          <tr class="bg-base-200 font-bold">
            <td colspan="10" class="text-right">TOTALES:</td>
            <td class="text-right">
              {{ formatCurrency(sheetProjects.reduce((sum, s) => sum + parseFloat(s.subtotal), 0)) }}
            </td>
            <td class="text-right">
              {{ formatCurrency(sheetProjects.reduce((sum, s) => sum + parseFloat(s.tax_amount), 0)) }}
            </td>
            <td class="text-right text-primary">
              {{ formatCurrency(sheetProjects.reduce((sum, s) => sum + parseFloat(s.total), 0)) }}
            </td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>
