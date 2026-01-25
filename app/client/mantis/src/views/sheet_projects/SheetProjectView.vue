<script setup>
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { UseProjectStore } from '@/stores/ProjectStore';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';
import { appConfig } from '@/AppConfig';

const route = useRoute();
const router = useRouter();
const projectStore = UseProjectStore();
const sheetProjectsStore = UseSheetProjectsStore();

// Obtener el ID de la planilla desde la ruta
const sheetId = computed(() => parseInt(route.params.id));

// Obtener datos del proyecto desde el store
const project = computed(() => projectStore.project);

// Obtener la planilla específica
const sheetProject = computed(() => {
  return sheetProjectsStore.getSheetProjectById(sheetId.value);
});

// Obtener cadenas de custodia de la planilla
const custodyChains = computed(() => {
  return sheetProjectsStore.getCustodyChainsForSheet(sheetId.value);
});

const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Intl.DateTimeFormat('es-GT').format(new Date(date));
};

const formatTime = (time) => {
  if (!time) return 'N/A';
  return time;
};

const getStatusBadge = (status) => {
  const statusConfig = {
    'IN_PROGRESS': { text: 'EN EJECUCIÓN', class: 'badge-success' },
    'INVOICED': { text: 'FACTURADO', class: 'badge-info' },
    'CANCELLED': { text: 'CANCELADO', class: 'badge-warning' }
  };
  return statusConfig[status] || { text: status, class: 'badge-ghost' };
};

const getCustodyChainStatusBadge = (status) => {
  const statusConfig = {
    'DRAFT': { text: 'BORRADOR', class: 'badge-warning' },
    'CLOSE': { text: 'CERRADO', class: 'badge-success' }
  };
  return statusConfig[status] || { text: status, class: 'badge-ghost' };
};

const totalGallons = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + (cc.total_gallons || 0), 0);
});

const totalBarrels = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + (cc.total_barrels || 0), 0);
});

const totalCubicMeters = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + (cc.total_cubic_meters || 0), 0);
});

const totalHours = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + parseFloat(cc.time_duration || 0), 0).toFixed(2);
});

const goBack = () => {
  router.push({ name: 'projects-detail' });
};

const viewCustodyChainDetail = (id) => {
  router.push({ 
    name: 'custody-chain-form', 
    params: { id } 
  });
};

const createNewCustodyChain = () => {
  router.push({ 
    name: 'custody-chain-form',
    query: { sheet_id: sheetProject.value?.id }
  });
};

const viewCustodyChainPDF = (id) => {
  const pdfUrl = appConfig.PDFCustodyChainReport.replace('${id}', id);
  window.open(pdfUrl, '_blank');
};

onMounted(async () => {
  // Si no hay datos, cargar el proyecto completo
  if (!project.value.id) {
    await projectStore.fetchProjectData();
  }
});
</script>

<template>
  <div class="w-[95%] mx-auto p-4">
    <!-- Header con información del proyecto y planilla -->
    <div class="bg-white rounded-2xl shadow-md border border-blue-300 border-t-[15px] border-t-blue-300 p-6 mb-6">
      <div class="flex justify-between items-center border-b-blue-500 border-b pb-3 mb-4">
        <h1 class="text-xl font-semibold text-blue-500">
          <i class="las la-link text-2xl"></i>
          Cadenas de Custodia - Planilla {{ sheetProject?.series_code || 'N/A' }}
        </h1>
        <div class="flex gap-3">
          <button @click="createNewCustodyChain" class="btn btn-primary btn-sm">
            <i class="las la-plus"></i>
            Nueva Cadena de Custodia
          </button>
          <button @click="goBack" class="btn btn-outline btn-sm">
            <i class="las la-arrow-left"></i>
            Volver
          </button>
        </div>
      </div>

      <!-- Información de Proyecto y Planilla en Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Información del Proyecto -->
        <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <h3 class="font-semibold text-blue-700 mb-3 flex items-center gap-2">
            <i class="las la-building"></i>
            Información del Proyecto #{{ project?.id || 'N/A' }}
          </h3>
          <div class="space-y-2 text-sm">
            <div>
              <span class="font-medium">Cliente:</span>
              <span class="ml-2">{{ project?.partner_name || 'N/A' }}</span>
            </div>
            <div>
              <span class="font-medium">Ubicación:</span>
              <span class="ml-2">{{ project?.location || 'N/A' }}{{ project?.cardinal_point ? ' - ' + project.cardinal_point : '' }}</span>
            </div>
            <div>
              <span class="font-medium">Contacto:</span>
              <span class="ml-2">{{ project?.contact_name || 'N/A' }} ({{ project?.contact_phone || 'N/A' }})</span>
            </div>
            <div>
              <span class="font-medium">Fecha Inicio:</span>
              <span class="ml-2">{{ formatDate(project?.start_date) }}</span>
            </div>
          </div>
        </div>

        <!-- Información de la Planilla -->
        <div class="bg-sky-50 rounded-lg p-4 border border-sky-200">
          <h3 class="font-semibold text-sky-700 mb-3 flex items-center gap-2">
            <i class="las la-file-invoice"></i>
            Información de la Planilla
          </h3>
          <div class="space-y-2 text-sm">
            <div>
              <span class="font-medium">Serie:</span>
              <span class="ml-2 font-mono">{{ sheetProject?.series_code || 'N/A' }}</span>
            </div>
            <div>
              <span class="font-medium">Estado:</span>
              <span class="ml-2 badge" :class="getStatusBadge(sheetProject?.status).class">
                {{ getStatusBadge(sheetProject?.status).text }}
              </span>
            </div>
            <div>
              <span class="font-medium">Tipo Servicio:</span>
              <span class="ml-2">{{ sheetProject?.service_type || 'N/A' }}</span>
            </div>
            <div>
              <span class="font-medium">Período:</span>
              <span class="ml-2">
                {{ formatDate(sheetProject?.period_start) }} - 
                {{ sheetProject?.period_end ? formatDate(sheetProject.period_end) : 'En curso' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabla de Cadenas de Custodia -->
    <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6">
      <h2 class="font-semibold text-lg mb-4 flex items-center gap-2 text-gray-800">
        <i class="las la-list text-blue-600"></i>
        Listado de Cadenas de Custodia ({{ custodyChains.length }})
      </h2>

      <div class="overflow-x-auto">
        <table class="table table-zebra w-full">
          <thead>
            <tr class="bg-gray-500 text-white">
              <th class="p-2 border border-gray-100 text-center">#</th>
              <th class="p-2 border border-gray-100 text-center">Consecutivo</th>
              <th class="p-2 border border-gray-100 text-center">Estado</th>
              <th class="p-2 border border-gray-100 text-center">Fecha Actividad</th>
              <th class="p-2 border border-gray-100 text-center">Hora Inicio</th>
              <th class="p-2 border border-gray-100 text-center">Hora Fin</th>
              <th class="p-2 border border-gray-100 text-center">Minutos</th>
              <th class="p-2 border border-gray-100 text-center">Ubicación</th>
              <th class="p-2 border border-gray-100 text-center">Técnico</th>
              <th class="p-2 border border-gray-100 text-center">Vehículo</th>
              <th class="p-2 border border-gray-100 text-center">Galones</th>
              <th class="p-2 border border-gray-100 text-center">Barriles</th>
              <th class="p-2 border border-gray-100 text-center">M³</th>
              <th class="p-2 border border-gray-100 text-center">Recursos</th>
              <th class="p-2 border border-gray-100 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="custodyChains.length === 0">
              <tr>
                <td colspan="15" class="text-center text-gray-500 py-8">
                  <i class="las la-inbox text-4xl"></i>
                  <p>No hay cadenas de custodia registradas para esta planilla</p>
                </td>
              </tr>
            </template>
            <template v-else>
              <tr v-for="cc in custodyChains" :key="cc.id">
                <td class="p-2 border border-gray-300 text-center">{{ cc.id }}</td>
                <td class="p-2 border border-gray-300 font-mono">{{ cc.consecutive }}</td>
                <td class="p-2 border border-gray-300 text-center">
                  <span class="badge" :class="getCustodyChainStatusBadge(cc.status).class">
                    {{ getCustodyChainStatusBadge(cc.status).text }}
                  </span>
                </td>
                <td class="p-2 border border-gray-300 text-center">{{ formatDate(cc.activity_date) }}</td>
                <td class="p-2 border border-gray-300 text-center font-mono">{{ formatTime(cc.start_time) }}</td>
                <td class="p-2 border border-gray-300 text-center font-mono">{{ formatTime(cc.end_time) }}</td>
                <td class="p-2 border border-gray-300 text-center font-semibold">{{ cc.time_duration || 0 }}</td>
                <td class="p-2 border border-gray-300">{{ cc.location || 'N/A' }}</td>
                <td class="p-2 border border-gray-300">
                  <div class="text-xs" v-if="cc.technical">
                    <div class="font-semibold">{{ cc.technical.first_name }} {{ cc.technical.last_name }}</div>
                  </div>
                  <span v-else class="text-gray-400">N/A</span>
                </td>
                <td class="p-2 border border-gray-300">
                  <div class="text-xs" v-if="cc.vehicle">
                    <div class="font-semibold">{{ cc.vehicle.no_plate }}</div>
                    <div class="text-gray-500">{{ cc.vehicle.brand }}</div>
                  </div>
                  <span v-else class="text-gray-400">N/A</span>
                </td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ cc.total_gallons || 0 }}</td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ cc.total_barrels || 0 }}</td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ cc.total_cubic_meters || 0 }}</td>
                <td class="p-2 border border-gray-300 text-center">
                  <span class="badge badge-info">{{ cc.details_count || 0 }}</span>
                </td>
                <td class="p-2 border border-gray-300 text-end">
                  <div class="flex gap-2 justify-end">
                    <button 
                      @click="viewCustodyChainDetail(cc.id)"
                      class="btn btn-xs border-blue-500 text-teal-500 bg-white"
                      title="Ver detalle"
                    >
                      <i class="las la-eye"></i>
                      VER
                    </button>
                    <button 
                      @click="viewCustodyChainPDF(cc.id)"
                      class="btn btn-xs border-red-500 text-red-500 bg-white"
                      title="Generar PDF"
                    >
                      <i class="las la-file-pdf"></i>
                      PDF
                    </button>
                    <button 
                      v-if="cc.status === 'DRAFT'"
                      @click="router.push({ name: 'custody-chain-form', params: { id: cc.id } })"
                      class="btn btn-xs border-orange-500 text-orange-500 bg-white"
                      title="Editar cadena"
                    >
                      <i class="las la-edit"></i>
                      EDITAR
                    </button>
                    <span 
                      v-else
                      class="btn btn-xs btn-disabled"
                      title="No se puede editar una cadena cerrada"
                    >
                      <i class="las la-lock"></i>
                      CERRADA
                    </span>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
          <tfoot v-if="custodyChains.length > 0">
            <tr class="bg-gray-500 font-bold text-white">
              <td colspan="6" class="p-2 border border-gray-300 text-right">TOTALES:</td>
              <td class="p-2 border border-gray-300 text-center">{{ totalHours }} Mins</td>
              <td colspan="3" class="p-2 border border-gray-300"></td>
              <td class="p-2 border border-gray-300 text-right font-mono">{{ totalGallons }}</td>
              <td class="p-2 border border-gray-300 text-right font-mono">{{ totalBarrels }}</td>
              <td class="p-2 border border-gray-300 text-right font-mono">{{ totalCubicMeters }}</td>
              <td colspan="2" class="p-2 border border-gray-300"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Estadísticas Resumen -->
    <div class="stats shadow w-full mt-6">
      <div class="stat">
        <div class="stat-title">Total Cadenas</div>
        <div class="stat-value text-primary">{{ custodyChains.length }}</div>
        <div class="stat-desc">Registradas</div>
      </div>
      
      <div class="stat">
        <div class="stat-title">Horas Totales</div>
        <div class="stat-value text-info">{{ totalHours }}</div>
        <div class="stat-desc">Horas trabajadas</div>
      </div>

      <div class="stat">
        <div class="stat-title">Total Galones</div>
        <div class="stat-value text-info">{{ totalGallons.toLocaleString() }}</div>
        <div class="stat-desc">Acumulados</div>
      </div>

      <div class="stat">
        <div class="stat-title">Total Barriles</div>
        <div class="stat-value text-info">{{ totalBarrels }}</div>
        <div class="stat-desc">Acumulados</div>
      </div>

      <div class="stat">
        <div class="stat-title">Total M³</div>
        <div class="stat-value text-info">{{ totalCubicMeters }}</div>
        <div class="stat-desc">Acumulados</div>
      </div>
    </div>
  </div>
</template>
