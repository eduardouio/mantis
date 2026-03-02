<script setup>
import { computed, defineEmits, ref } from 'vue';
import { useRouter } from 'vue-router';
import { UseProjectStore } from '@/stores/ProjectStore';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';
import { appConfig } from '@/AppConfig';
import { useTableFilter } from '@/composables/useTableFilter';
import TableControls from '@/components/common/TableControls.vue';

const router = useRouter();
const projectStore = UseProjectStore();
const sheetProjectsStore = UseSheetProjectsStore();

// Obtener las work orders con sus cadenas de custodia
const workOrders = computed(() => projectStore.workOrders || []);
const hasInProgressSheet = computed(() => {
  return workOrders.value.some(wo => wo.status === 'IN_PROGRESS');
});
const isProjectClosed = computed(() => projectStore.project?.is_closed === true);

// Calcular totales para cada work order desde sus cadenas de custodia
const enrichedWorkOrders = computed(() => {
  return workOrders.value.map(wo => {
    const custodyChains = wo.custody_chains || [];
    
    // Sumar totales desde las cadenas de custodia
    const totalGallons = custodyChains.reduce((sum, cc) => sum + (cc.total_gallons || 0), 0);
    const totalBarrels = custodyChains.reduce((sum, cc) => sum + (cc.total_barrels || 0), 0);
    const totalCubicMeters = custodyChains.reduce((sum, cc) => sum + (cc.total_cubic_meters || 0), 0);
    
    return {
      ...wo,
      calculated_total_gallons: totalGallons,
      calculated_total_barrels: totalBarrels,
      calculated_total_cubic_meters: totalCubicMeters,
      custody_chains_count: custodyChains.length
    };
  });
});

// Tabla con filtrado, búsqueda y paginación
const tableFilter = useTableFilter(enrichedWorkOrders, {
  searchFields: ['series_code', 'status', 'contact_reference', 'service_type'],
  pageSize: 10
});

const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ'
  }).format(value);
};

const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Intl.DateTimeFormat('es-EC', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(new Date(date));
};

const getStatusBadge = (status) => {
  const statusConfig = {
    'IN_PROGRESS': { 
      text: 'EN EJECUCIÓN', 
      class: 'bg-green-500 text-white' 
    },
    'INVOICED': { 
      text: 'FACTURADO', 
      class: 'bg-cyan-500 text-white' 
    },
    'CANCELLED': { 
      text: 'CANCELADO', 
      class: 'bg-orange-500 text-white' 
    }
  };
  
  return statusConfig[status] || { 
    text: status, 
    class: 'bg-gray-500 text-white' 
  };
};

const openSheetFormModal = () => {
  router.push({ name: 'sheet-project-form' });
};

const editSheet = (sheet) => {
  router.push({ 
    name: 'sheet-project-form', 
    params: { id: sheet.id } 
  });
};

const viewCustodyChains = (sheetId) => {
  router.push({ 
    name: 'sheet-project-view', 
    params: { id: sheetId } 
  });
};
</script>

<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center mb-4">
      <h2 class="font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-file-invoice-dollar text-blue-600"></i>
        Planillas del Proyecto
      </h2>
      <button
        v-if="!hasInProgressSheet && !isProjectClosed"
        @click="openSheetFormModal"
        class="btn btn-primary btn-sm"
      >
        <i class="las la-plus"></i>
        Crear Nueva Planilla
      </button>
      <div v-else-if="isProjectClosed" class="badge badge-error gap-1">
        <i class="las la-lock"></i> Proyecto Cerrado
      </div>
      <div v-else class="text-amber-700 badge bg-yellow-100">
        <i class="las la-exclamation-triangle"></i>
        PLANILLA EN EJECUCIÓN
      </div>
    </div>
    
    <TableControls :tableFilter="tableFilter" position="top" searchPlaceholder="Buscar planilla..." />

    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-gray-500 text-white">
            <th class="p-2 border border-gray-100 text-center">Serie</th>
            <th class="p-2 border border-gray-100 text-center">Estado</th>
            <th class="p-2 border border-gray-100 text-center">Período Inicio</th>
            <th class="p-2 border border-gray-100 text-center">Período Fin</th>
            <th class="p-2 border border-gray-100 text-center">Contacto Ref.</th>
            <th class="p-2 border border-gray-100 text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="enrichedWorkOrders.length === 0">
            <tr>
              <td colspan="6" class="text-center text-gray-500 py-8">
                <i class="las la-inbox text-4xl"></i>
                <p>No hay planillas registradas para este proyecto</p>
              </td>
            </tr>
          </template>
          <template v-else-if="tableFilter.paginatedData.value.length === 0">
            <tr>
              <td colspan="6" class="text-center text-gray-500 py-8">
                <i class="las la-search text-4xl"></i>
                <p>No se encontraron resultados para "{{ tableFilter.searchQuery.value }}"</p>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="sheet in tableFilter.paginatedData.value" :key="sheet.id">
              <td class="p-2 border border-gray-300">
                <div class="flex items-center gap-2">
                  <button
                    @click="editSheet(sheet)"
                    class="btn btn-xs btn-ghost p-0 min-h-0 h-auto"
                    :title="sheet.is_closed ? 'Ver planilla (cerrada)' : 'Editar planilla'"
                  >
                    <i class="las text-lg" :class="sheet.is_closed ? 'la-eye text-gray-500' : 'la-edit text-blue-500'"></i>
                  </button>
                  <a
                    class="font-mono text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                    @click="viewCustodyChains(sheet.id)"
                    :title="'Ver detalle de planilla ' + sheet.series_code"
                  >
                    {{ sheet.series_code }}
                  </a>
                </div>
              </td>
              <td class="p-2 border border-gray-300">
                <div class="flex items-center gap-1">
                  <span 
                    class="badge px-3 py-1 rounded text-xs font-medium"
                    :class="getStatusBadge(sheet.status).class"
                  >
                    {{ getStatusBadge(sheet.status).text }}
                  </span>
                  <span v-if="sheet.is_closed" class="badge badge-error badge-sm gap-1" title="Planilla cerrada">
                    <i class="las la-lock text-xs"></i> CERRADA
                  </span>
                </div>
              </td>
              <td class="p-2 border border-gray-300 text-end">{{ formatDate(sheet.period_start) }}</td>
              <td class="p-2 border border-gray-300 text-end">{{ sheet.period_end ? formatDate(sheet.period_end) : '--' }}</td>
              <td class="p-2 border border-gray-300">{{ sheet.contact_reference || 'N/A' }}</td>
              <td class="p-2 border border-gray-300 text-end">
                <div class="flex gap-2 justify-end">
                  <a
                    :href="appConfig.URLWorkSheetReport.replace('${id}', sheet.id)"
                    target="_blank"
                    class="btn btn-xs border-green-500 text-green-500 bg-white"
                    title="Descargar reporte PDF de la planilla"
                  >
                    <i class="las la-file-pdf"></i>
                    PDF
                  </a>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <TableControls :tableFilter="tableFilter" position="bottom" />
  </div>
</template>
