<script setup>
import { computed, defineEmits, ref } from 'vue';
import { useRouter } from 'vue-router';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';

const router = useRouter();
const sheetProjectsStore = UseSheetProjectsStore();

const sheetProjects = computed(() => sheetProjectsStore.sheetProjects);
const hasInProgressSheet = computed(() => sheetProjectsStore.hasInProgressSheet);

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

const emit = defineEmits(['open-sheet-form', 'edit-sheet']);

const openSheetFormModal = () => {
  emit('open-sheet-form');
};

const editSheet = (sheet) => {
  emit('edit-sheet', sheet);
};

const confirmingCloseId = ref(null);

const handleCloseClick = (sheetId) => {
  if (confirmingCloseId.value === sheetId) {
    // Segunda vez: ejecutar el cierre
    closeSheet(sheetId);
    confirmingCloseId.value = null;
  } else {
    // Primera vez: mostrar confirmación
    confirmingCloseId.value = sheetId;
    // Resetear después de 3 segundos si no confirma
    setTimeout(() => {
      if (confirmingCloseId.value === sheetId) {
        confirmingCloseId.value = null;
      }
    }, 3000);
  }
};

const closeSheet = async (sheetId) => {
  try {
    console.log('Cerrando planilla:', sheetId);
    await sheetProjectsStore.closeSheetProject(sheetId);
    confirmingCloseId.value = null;
  } catch (error) {
    console.error('Error al cerrar planilla:', error);
    // Opcional: mostrar notificación de error
  }
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
        v-if="!hasInProgressSheet"
        @click="openSheetFormModal"
        class="btn btn-primary btn-sm"
      >
        <i class="las la-plus"></i>
        Crear Nueva Planilla
      </button>
      <div v-else class="text-amber-700 badge bg-yellow-100">
        <i class="las la-exclamation-triangle"></i>
        PLANILLA EN EJECUCIÓN
      </div>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-gray-500 text-white">
            <th class="p-2 border border-gray-100 text-center">#</th>
            <th class="p-2 border border-gray-100 text-center">Serie</th>
            <th class="p-2 border border-gray-100 text-center">Estado</th>
            <th class="p-2 border border-gray-100 text-center">Fecha Emisión</th>
            <th class="p-2 border border-gray-100 text-center">Período Inicio</th>
            <th class="p-2 border border-gray-100 text-center">Período Fin</th>
            <th class="p-2 border border-gray-100 text-center">Contacto Ref.</th>
            <th class="p-2 border border-gray-100 text-center">Teléfono</th>
            <th class="p-2 border border-gray-100 text-center">Tipo Servicio</th>
            <th class="p-2 border border-gray-100 text-center">Galones</th>
            <th class="p-2 border border-gray-100 text-center">Barriles</th>
            <th class="p-2 border border-gray-100 text-center">M³</th>
            <th class="p-2 border border-gray-100 text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="sheetProjects.length === 0">
            <tr>
              <td colspan="13" class="text-center text-gray-500 py-8">
                <i class="las la-inbox text-4xl"></i>
                <p>No hay planillas registradas para este proyecto</p>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="sheet in sheetProjects" :key="sheet.id">
              <td class="p-2 border border-gray-300">{{ sheet.id }}</td>
              <td class="p-2 border border-gray-300 font-mono">{{ sheet.series_code }}</td>
              <td class="p-2 border border-gray-300">
                <span 
                  class="badge px-3 py-1 rounded text-xs font-medium"
                  :class="getStatusBadge(sheet.status).class"
                >
                  {{ getStatusBadge(sheet.status).text }}
                </span>
              </td>
              <td class="p-2 border border-gray-300 text-end">{{ formatDate(sheet.issue_date) }}</td>
              <td class="p-2 border border-gray-300 text-end">{{ formatDate(sheet.period_start) }}</td>
              <td class="p-2 border border-gray-300 text-end">{{ sheet.period_end ? formatDate(sheet.period_end) : '--' }}</td>
              <td class="p-2 border border-gray-300">{{ sheet.contact_reference || 'N/A' }}</td>
              <td class="p-2 border border-gray-300">{{ sheet.contact_phone_reference || 'N/A' }}</td>
              <td class="p-2 border border-gray-300">{{ sheet.service_type }}</td>
              <td class="p-2 border border-gray-300 text-right">{{ sheet.total_gallons.toLocaleString() }}</td>
              <td class="p-2 border border-gray-300 text-right">{{ sheet.total_barrels.toLocaleString() }}</td>
              <td class="p-2 border border-gray-300 text-right">{{ sheet.total_cubic_meters.toFixed(1) }}</td>
              <td class="p-2 border border-gray-300 text-end">
                <div class="flex gap-2 justify-end">
                  <button 
                    @click="editSheet(sheet)"
                    class="btn btn-xs border-blue-500 text-teal-500 bg-white" 
                    title="Editar planilla"
                  >
                    <i class="las la-edit"></i>
                    EDITAR
                  </button>
                  <button
                    @click="viewCustodyChains(sheet.id)"
                    class="btn btn-xs border-purple-500 text-purple-500 bg-white"
                    title="Ver cadenas de custodia"
                  >
                    <i class="las la-link"></i>
                    C. CUSTODIA
                  </button>
                  <button
                    @click="handleCloseClick(sheet.id)"  
                    class="btn btn-xs bg-white"
                    :class="confirmingCloseId === sheet.id ? 'border-orange-500 text-orange-500' : 'border-red-500 text-red-500'"
                    :title="confirmingCloseId === sheet.id ? 'Haz clic nuevamente para confirmar' : 'Cerrar planilla'"
                  >
                    <i class="las la-times"></i>
                    {{ confirmingCloseId === sheet.id ? 'CONFIRMAR' : 'CERRAR' }}
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
