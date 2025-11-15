<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

// Datos de ejemplo del proyecto
const project = ref({
  id: 4,
  partner_name: "ABARCA QUEZADA CONSTRUCCIONES Y SERVICIOS AQSERVIC CIA. LTDA.",
  location: "PAMBIL",
  cardinal_point: "NORTE",
  contact_name: "Edison Guano",
  contact_phone: "0992936569",
  start_date: "2025-11-01",
  end_date: null,
  is_closed: false
});

// Datos de ejemplo de la planilla
const sheetProject = ref({
  id: 1,
  series_code: "PSL-PS-2025-1000",
  status: "IN_PROGRESS",
  issue_date: null,
  period_start: "2025-11-01",
  period_end: null,
  service_type: "ALQUILER Y MANTENIMIENTO",
  total_gallons: 0,
  total_barrels: 0,
  total_cubic_meters: 0,
  subtotal: 0,
  tax_amount: 0,
  total: 0,
  contact_reference: "Edison Guano",
  contact_phone_reference: "0992936569"
});

// Datos de ejemplo de cadenas de custodia
const custodyChains = ref([
  {
    id: 1,
    series_code: "CC-2025-001",
    issue_date: "2025-11-05",
    start_time: "08:00",
    end_time: "16:00",
    time_duration: 8.00,
    contact_name: "Juan Pérez",
    dni_contact: "1234567890",
    contact_position: "Supervisor de Campo",
    date_contact: "2025-11-05",
    driver_name: "Carlos López",
    dni_driver: "0987654321",
    driver_position: "Conductor",
    driver_date: "2025-11-05",
    total_gallons: 450,
    total_barrels: 12,
    total_cubic_meters: 15
  },
  {
    id: 2,
    series_code: "CC-2025-002",
    issue_date: "2025-11-06",
    start_time: "07:30",
    end_time: "15:30",
    time_duration: 8.00,
    contact_name: "María García",
    dni_contact: "1122334455",
    contact_position: "Jefe de Proyecto",
    date_contact: "2025-11-06",
    driver_name: "Pedro Ramírez",
    dni_driver: "5544332211",
    driver_position: "Conductor",
    driver_date: "2025-11-06",
    total_gallons: 380,
    total_barrels: 10,
    total_cubic_meters: 12
  },
  {
    id: 3,
    series_code: "CC-2025-003",
    issue_date: "2025-11-07",
    start_time: "08:00",
    end_time: "17:00",
    time_duration: 9.00,
    contact_name: "Luis Morales",
    dni_contact: "9988776655",
    contact_position: "Coordinador",
    date_contact: "2025-11-07",
    driver_name: "Jorge Vásquez",
    dni_driver: "6677889900",
    driver_position: "Conductor",
    driver_date: "2025-11-07",
    total_gallons: 520,
    total_barrels: 14,
    total_cubic_meters: 18
  }
]);

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

const totalGallons = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + cc.total_gallons, 0);
});

const totalBarrels = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + cc.total_barrels, 0);
});

const totalCubicMeters = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + cc.total_cubic_meters, 0);
});

const totalHours = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + parseFloat(cc.time_duration), 0).toFixed(2);
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
    query: { sheet_id: sheetProject.value.id }
  });
};

onMounted(() => {
  // Aquí se cargarían los datos reales
  console.log('Sheet ID:', route.query.sheet_id);
});
</script>

<template>
  <div class="w-[95%] mx-auto p-4">
    <!-- Header con información del proyecto y planilla -->
    <div class="bg-white rounded-2xl shadow-md border border-blue-300 border-t-[15px] border-t-blue-300 p-6 mb-6">
      <div class="flex justify-between items-center border-b-blue-500 border-b pb-3 mb-4">
        <h1 class="text-xl font-semibold text-blue-500">
          <i class="las la-link text-2xl"></i>
          Cadenas de Custodia - Planilla {{ sheetProject.series_code }}
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
            Información del Proyecto #{{ project.id }}
          </h3>
          <div class="space-y-2 text-sm">
            <div>
              <span class="font-medium">Cliente:</span>
              <span class="ml-2">{{ project.partner_name }}</span>
            </div>
            <div>
              <span class="font-medium">Ubicación:</span>
              <span class="ml-2">{{ project.location }} - {{ project.cardinal_point }}</span>
            </div>
            <div>
              <span class="font-medium">Contacto:</span>
              <span class="ml-2">{{ project.contact_name }} ({{ project.contact_phone }})</span>
            </div>
            <div>
              <span class="font-medium">Fecha Inicio:</span>
              <span class="ml-2">{{ formatDate(project.start_date) }}</span>
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
              <span class="ml-2 font-mono">{{ sheetProject.series_code }}</span>
            </div>
            <div>
              <span class="font-medium">Estado:</span>
              <span class="ml-2 badge" :class="getStatusBadge(sheetProject.status).class">
                {{ getStatusBadge(sheetProject.status).text }}
              </span>
            </div>
            <div>
              <span class="font-medium">Tipo Servicio:</span>
              <span class="ml-2">{{ sheetProject.service_type }}</span>
            </div>
            <div>
              <span class="font-medium">Período:</span>
              <span class="ml-2">
                {{ formatDate(sheetProject.period_start) }} - 
                {{ sheetProject.period_end ? formatDate(sheetProject.period_end) : 'En curso' }}
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
        Listado de Cadenas de Custodia
      </h2>

      <div class="overflow-x-auto">
        <table class="table table-zebra w-full">
          <thead>
            <tr class="bg-gray-500 text-white">
              <th class="p-2 border border-gray-100 text-center">#</th>
              <th class="p-2 border border-gray-100 text-center">Serie</th>
              <th class="p-2 border border-gray-100 text-center">Fecha Emisión</th>
              <th class="p-2 border border-gray-100 text-center">Hora Inicio</th>
              <th class="p-2 border border-gray-100 text-center">Hora Fin</th>
              <th class="p-2 border border-gray-100 text-center">Horas</th>
              <th class="p-2 border border-gray-100 text-center">Contacto</th>
              <th class="p-2 border border-gray-100 text-center">Conductor</th>
              <th class="p-2 border border-gray-100 text-center">Galones</th>
              <th class="p-2 border border-gray-100 text-center">Barriles</th>
              <th class="p-2 border border-gray-100 text-center">M³</th>
              <th class="p-2 border border-gray-100 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="custodyChains.length === 0">
              <tr>
                <td colspan="12" class="text-center text-gray-500 py-8">
                  <i class="las la-inbox text-4xl"></i>
                  <p>No hay cadenas de custodia registradas para esta planilla</p>
                </td>
              </tr>
            </template>
            <template v-else>
              <tr v-for="cc in custodyChains" :key="cc.id">
                <td class="p-2 border border-gray-300 text-center">{{ cc.id }}</td>
                <td class="p-2 border border-gray-300 font-mono">{{ cc.series_code }}</td>
                <td class="p-2 border border-gray-300 text-center">{{ formatDate(cc.issue_date) }}</td>
                <td class="p-2 border border-gray-300 text-center font-mono">{{ formatTime(cc.start_time) }}</td>
                <td class="p-2 border border-gray-300 text-center font-mono">{{ formatTime(cc.end_time) }}</td>
                <td class="p-2 border border-gray-300 text-center font-semibold">{{ cc.time_duration }}</td>
                <td class="p-2 border border-gray-300">
                  <div class="text-xs">
                    <div class="font-semibold">{{ cc.contact_name }}</div>
                    <div class="text-gray-500">{{ cc.contact_position }}</div>
                  </div>
                </td>
                <td class="p-2 border border-gray-300">
                  <div class="text-xs">
                    <div class="font-semibold">{{ cc.driver_name }}</div>
                    <div class="text-gray-500">CI: {{ cc.dni_driver }}</div>
                  </div>
                </td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ cc.total_gallons }}</td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ cc.total_barrels }}</td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ cc.total_cubic_meters }}</td>
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
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
          <tfoot v-if="custodyChains.length > 0">
            <tr class="bg-gray-100 font-bold">
              <td colspan="5" class="p-2 border border-gray-300 text-right">TOTALES:</td>
              <td class="p-2 border border-gray-300 text-center">{{ totalHours }} hrs</td>
              <td colspan="2" class="p-2 border border-gray-300"></td>
              <td class="p-2 border border-gray-300 text-right font-mono">{{ totalGallons }}</td>
              <td class="p-2 border border-gray-300 text-right font-mono">{{ totalBarrels }}</td>
              <td class="p-2 border border-gray-300 text-right font-mono">{{ totalCubicMeters }}</td>
              <td class="p-2 border border-gray-300"></td>
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
