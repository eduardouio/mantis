<script setup>
import { ref, onMounted, computed } from 'vue';
import { formatDate } from '@/utils/formatters';

// Datos de ejemplo - aquí conectarías con tu store
const sheetProjects = ref([]);
const selectedSheet = ref(null);
const isLoading = ref(false);

const fetchSheetProjects = async () => {
  isLoading.value = true;
  // Aquí harías la llamada al API
  // const response = await sheetProjectsStore.fetchAllSheetProjects();
  // sheetProjects.value = response.data;
  isLoading.value = false;
};

const selectSheet = (sheet) => {
  selectedSheet.value = sheet;
};

const getStatusBadgeClass = (status) => {
  const statusClasses = {
    'IN_PROGRESS': 'badge-warning',
    'INVOICED': 'badge-success',
    'CANCELLED': 'badge-error'
  };
  return statusClasses[status] || 'badge-ghost';
};

const getStatusLabel = (status) => {
  const statusLabels = {
    'IN_PROGRESS': 'En Ejecución',
    'INVOICED': 'Facturado',
    'CANCELLED': 'Cancelado'
  };
  return statusLabels[status] || status;
};

onMounted(() => {
  fetchSheetProjects();
});
</script>

<template>
  <div class="w-[95%] mx-auto p-6">
    <!-- Header -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <i class="las la-file-invoice text-blue-500"></i>
          Planillas de Proyecto
        </h1>
        <button class="btn btn-primary btn-sm">
          <i class="las la-plus"></i>
          Nueva Planilla
        </button>
      </div>
    </div>

    <!-- Lista de Planillas -->
    <div class="grid grid-cols-1 gap-4">
      <!-- Planilla Card -->
      <div 
        v-for="sheet in sheetProjects" 
        :key="sheet.sheet_id"
        class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
      >
        <!-- Cabecera de la Planilla -->
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-t-lg">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h2 class="text-xl font-bold">{{ sheet.series_code }}</h2>
                <span class="badge badge-sm" :class="getStatusBadgeClass(sheet.status)">
                  {{ getStatusLabel(sheet.status) }}
                </span>
              </div>
              <div class="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <i class="las la-calendar-alt mr-1"></i>
                  <span class="opacity-90">Emisión:</span>
                  <span class="font-semibold ml-1">{{ formatDate(sheet.issue_date) }}</span>
                </div>
                <div>
                  <i class="las la-calendar-check mr-1"></i>
                  <span class="opacity-90">Inicio:</span>
                  <span class="font-semibold ml-1">{{ formatDate(sheet.period_start) }}</span>
                </div>
                <div>
                  <i class="las la-calendar-times mr-1"></i>
                  <span class="opacity-90">Fin:</span>
                  <span class="font-semibold ml-1">{{ formatDate(sheet.period_end) }}</span>
                </div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-xs opacity-80">Total</div>
              <div class="text-2xl font-bold">${{ sheet.total.toLocaleString('es-CO', { minimumFractionDigits: 2 }) }}</div>
              <div class="text-xs opacity-80">
                Subtotal: ${{ sheet.subtotal.toLocaleString('es-CO', { minimumFractionDigits: 2 }) }} + 
                IVA: ${{ sheet.tax_amount.toLocaleString('es-CO', { minimumFractionDigits: 2 }) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Información del Servicio -->
        <div class="p-4 border-b">
          <div class="flex items-center gap-2 text-sm text-gray-600">
            <i class="las la-cog text-blue-500 text-lg"></i>
            <span class="font-semibold">Tipo de Servicio:</span>
            <span class="badge badge-outline">{{ sheet.service_type }}</span>
          </div>
        </div>

        <!-- Cadenas de Custodia -->
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-700 flex items-center gap-2">
              <i class="las la-link text-green-500"></i>
              Cadenas de Custodia
              <span class="badge badge-sm badge-neutral">{{ sheet.custody_chains?.length || 0 }}</span>
            </h3>
          </div>

          <!-- Sin Cadenas de Custodia -->
          <div v-if="!sheet.custody_chains || sheet.custody_chains.length === 0" 
               class="text-center py-8 text-gray-400">
            <i class="las la-inbox text-4xl"></i>
            <p class="mt-2">No hay cadenas de custodia registradas</p>
          </div>

          <!-- Lista de Cadenas de Custodia -->
          <div v-else class="space-y-3">
            <div 
              v-for="chain in sheet.custody_chains" 
              :key="chain.custody_chain_id"
              class="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <!-- Header de Cadena -->
              <div class="flex justify-between items-start mb-3">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="badge badge-primary badge-sm">{{ chain.consecutive }}</span>
                    <span class="font-semibold text-gray-700">{{ chain.technical_name }}</span>
                  </div>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-600">
                    <div class="flex items-center gap-1">
                      <i class="las la-calendar text-blue-500"></i>
                      {{ formatDate(chain.activity_date) }}
                    </div>
                    <div class="flex items-center gap-1">
                      <i class="las la-clock text-green-500"></i>
                      {{ chain.start_time }} - {{ chain.end_time }}
                    </div>
                    <div class="flex items-center gap-1">
                      <i class="las la-hourglass-half text-orange-500"></i>
                      {{ chain.time_duration }}h
                    </div>
                    <div class="flex items-center gap-1">
                      <i class="las la-map-marker text-red-500"></i>
                      {{ chain.location }}
                    </div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-xs text-gray-500">Total Línea</div>
                  <div class="text-lg font-bold text-green-600">
                    ${{ chain.total_price.toLocaleString('es-CO', { minimumFractionDigits: 2 }) }}
                  </div>
                </div>
              </div>

              <!-- Información de Contacto -->
              <div v-if="chain.contact_name" class="bg-blue-50 rounded p-2 mb-3 text-xs">
                <div class="flex items-center gap-2">
                  <i class="las la-user text-blue-600"></i>
                  <span class="font-semibold">{{ chain.contact_name }}</span>
                  <span class="text-gray-500">-</span>
                  <span class="text-gray-600">{{ chain.contact_position }}</span>
                </div>
              </div>

              <!-- Volúmenes -->
              <div class="grid grid-cols-3 gap-2 mb-3">
                <div class="bg-amber-50 rounded p-2 text-center">
                  <i class="las la-flask text-amber-600 text-lg"></i>
                  <div class="text-xs text-gray-600">Galones</div>
                  <div class="font-bold text-amber-700">{{ chain.total_gallons }}</div>
                </div>
                <div class="bg-purple-50 rounded p-2 text-center">
                  <i class="las la-drumstick-bite text-purple-600 text-lg"></i>
                  <div class="text-xs text-gray-600">Barriles</div>
                  <div class="font-bold text-purple-700">{{ chain.total_barrels }}</div>
                </div>
                <div class="bg-cyan-50 rounded p-2 text-center">
                  <i class="las la-cube text-cyan-600 text-lg"></i>
                  <div class="text-xs text-gray-600">M³</div>
                  <div class="font-bold text-cyan-700">{{ chain.total_cubic_meters }}</div>
                </div>
              </div>

              <!-- Detalles de Facturación -->
              <div class="bg-gray-50 rounded p-3 mb-3">
                <div class="grid grid-cols-4 gap-2 text-xs">
                  <div>
                    <span class="text-gray-500">Unidad:</span>
                    <span class="font-semibold ml-1">{{ chain.item_unity }}</span>
                  </div>
                  <div>
                    <span class="text-gray-500">Cantidad:</span>
                    <span class="font-semibold ml-1">{{ chain.quantity }}</span>
                  </div>
                  <div>
                    <span class="text-gray-500">Precio Unit:</span>
                    <span class="font-semibold ml-1">${{ chain.unit_price.toLocaleString('es-CO') }}</span>
                  </div>
                  <div>
                    <span class="text-gray-500">Total:</span>
                    <span class="font-semibold ml-1">${{ chain.total_line.toLocaleString('es-CO') }}</span>
                  </div>
                </div>
                <div v-if="chain.detail" class="mt-2 pt-2 border-t text-xs text-gray-600">
                  <i class="las la-comment-alt"></i>
                  {{ chain.detail }}
                </div>
              </div>

              <!-- Items/Recursos Utilizados -->
              <div v-if="chain.items && chain.items.length > 0">
                <div class="text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1">
                  <i class="las la-tools"></i>
                  Recursos Utilizados:
                </div>
                <div class="flex flex-wrap gap-2">
                  <div 
                    v-for="item in chain.items" 
                    :key="item.detail_id"
                    class="badge badge-outline badge-sm gap-1"
                  >
                    <i class="las la-wrench text-xs"></i>
                    {{ item.resource_code }} - {{ item.resource_name }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer de la Planilla -->
        <div class="bg-gray-50 p-3 rounded-b-lg flex justify-end gap-2">
          <button class="btn btn-sm btn-ghost">
            <i class="las la-eye"></i>
            Ver Detalles
          </button>
          <button class="btn btn-sm btn-ghost">
            <i class="las la-print"></i>
            Imprimir
          </button>
          <button class="btn btn-sm btn-ghost">
            <i class="las la-download"></i>
            Exportar
          </button>
        </div>
      </div>
    </div>

    <!-- Estado de carga -->
    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <!-- Sin resultados -->
    <div v-if="!isLoading && sheetProjects.length === 0" 
         class="bg-white rounded-lg shadow-md p-12 text-center">
      <i class="las la-folder-open text-6xl text-gray-300"></i>
      <p class="text-gray-500 mt-4">No hay planillas de proyecto registradas</p>
      <button class="btn btn-primary btn-sm mt-4">
        <i class="las la-plus"></i>
        Crear Primera Planilla
      </button>
    </div>
  </div>
</template>

<style scoped>
.badge-warning {
  @apply bg-yellow-400 text-yellow-900 border-yellow-500;
}

.badge-success {
  @apply bg-green-400 text-green-900 border-green-500;
}

.badge-error {
  @apply bg-red-400 text-red-900 border-red-500;
}
</style>
