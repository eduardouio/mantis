<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UseProjectStore } from '@/stores/ProjectStore'
import { UseTechnicalStore } from '@/stores/TechnicalStore'
import { UseVehicleStore } from '@/stores/VehicleStore'
import { appConfig } from '@/AppConfig.js'
import Modal from '@/components/common/Modal.vue'
import TechnicalPresentation from '@/components/resources/TechnicalPresentation.vue'
import VehiclePresentation from '@/components/resources/VehiclePresentation.vue'

const projectStore = UseProjectStore()
const technicalStore = UseTechnicalStore()
const vehicleStore = UseVehicleStore()

onMounted(async () => {
  await projectStore.fetchProjectData()
  await technicalStore.fetchTechnicalsAvailable()
  await vehicleStore.fetchVehicles()
})

const router = useRouter()
const selectedVehicle = ref(null)
const selectedTechnical = ref(null)
const showTechnicalModal = ref(false)
const showVehicleModal = ref(false)

// Obtener todas las cadenas de custodia de todas las órdenes de trabajo
const custodyChains = computed(() => {
  if (!projectStore.projectData?.work_orders) return []
  
  const chains = []
  projectStore.projectData.work_orders.forEach(workOrder => {
    if (workOrder.custody_chains) {
      workOrder.custody_chains.forEach(chain => {
        chains.push({
          ...chain,
          work_order: workOrder
        })
      })
    }
  })
  return chains
})

const openTechnicalModal = (technical) => {
  selectedTechnical.value = technical
  showTechnicalModal.value = true
}

const openVehicleModal = (vehicle) => {
  selectedVehicle.value = vehicle
  showVehicleModal.value = true
}

const formatTime = (time) => {
  if (!time) return 'N/A'
  return time.substring(0, 5) // HH:MM
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('es-ES')
}
</script>

<template>
  <div class="w-[95%] mx-auto p-6">
    <!-- Header -->
    <div class="bg-white rounded-lg shadow-md p-2 mb-2 border border-gray-200">
      <div class="flex justify-between items-center">
        <h1 class="text-gray-800 flex items-center gap-2 font-semibold">
          <i class="las la-file-invoice text-blue-500"></i>
          Cadenas de Custodia - {{ projectStore.projectData?.project?.partner_name }}
        </h1>
        <div class="flex gap-2">
          <button class="btn btn-secondary btn-sm" @click="router.push({ name: 'project-detail' })">
            <i class="las la-arrow-left"></i>
            Volver
          </button>
          <button class="btn btn-primary btn-sm" @click="router.push({ name: 'custody-chain-form' })">
            <i class="las la-plus"></i>
            Nueva Cadena de Custodia
          </button>
        </div>
      </div>  
    </div>

    <!-- Lista de Cadenas de Custodia -->
    <div class="grid grid-cols-1 gap-4">
      <div 
        v-for="chain in custodyChains" 
        :key="chain.id"
        class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
      >
        <!-- Cabecera de la Cadena -->
        <div class="bg-gradient-to-r from-blue-500 to-sky-600 text-white p-4 rounded-t-lg backdrop-blur-sm">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h2 class="text-xl font-bold"> 
                  #{{ projectStore.projectData?.project?.id }} {{ projectStore.projectData?.project?.partner_name }} - {{ projectStore.projectData?.project?.location }}
                </h2>
                <span class="badge text-blue-500 font-semibold bg-white px-3 py-1">
                  {{ projectStore.projectData?.project?.cardinal_point || 'N/A' }}
                </span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-2xl p1 rounded text-error bg-gray-100 w-100% font-mono border border-sky-600 border-2">
                <span class="text-gray-700 ms-5">Nro.</span>
                <span class="me-2">{{ chain.consecutive }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Información General -->
        <div class="p-2">
          <div class="grid grid-cols-4 gap-4">
            <!-- Fecha -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Fecha:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ formatDate(chain.activity_date) }}
              </span>
            </div>
            <!-- Inicio - Fin -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Inicio - Fin:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ formatTime(chain.start_time) }} - {{ formatTime(chain.end_time) }} 
                <span class="ml-2 me-2 text-gray-200">|</span>
                {{ chain.time_duration?.toFixed(2) || '0.00' }} HRS
              </span>
            </div>
            <!-- Ubicación -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Ubicación:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">{{ chain.location }}</span>
            </div>
            <!-- Placa Vehículo -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Placa Vehiculo:</span>
              <div class="flex gap-1 flex-1">
                <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                  {{ chain.vehicle?.no_plate }}
                  <span class="ml-2 me-2 text-gray-200">|</span>
                  {{ chain.vehicle?.brand }} {{ chain.vehicle?.model }}
                </span>
                <button 
                  type="button"
                  class="btn btn-sm btn-outline"
                  @click="openVehicleModal(chain.vehicle)"
                  title="Ver detalles del vehículo"
                >
                  <i class="las la-eye"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="p-2 border-b bg-gray-50 border-b-gray-200">
          <div class="grid grid-cols-4 gap-4">
            <!-- Técnico -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Técnico:</span>
              <div class="flex gap-1 flex-1">
                <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                  {{ chain.technical?.first_name }} {{ chain.technical?.last_name }} 
                  <span class="ml-2 me-2 text-gray-200">|</span>
                  <span class="">CI: {{ chain.dni_driver }}</span>
                </span>
                <button 
                  type="button"
                  class="btn btn-sm btn-outline"
                  @click="openTechnicalModal(chain.technical)"
                  title="Ver detalles del técnico"
                >
                  <i class="las la-eye"></i>
                </button>
              </div>
            </div>
            <!-- Cargo -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Cargo:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">{{ chain.driver_position }}</span>
            </div>
            <!-- Contacto -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Contacto:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ chain.contact_name }}
                <span class="ml-2 me-2 text-gray-200">|</span> 
                <span>{{ projectStore.projectData?.project?.contact_phone }}</span>
              </span>
            </div>
            <!-- Cargo Contacto -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Empresa:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ projectStore.projectData?.project?.partner_name }}
              </span>
            </div>
          </div>
        </div>

        <div class="p-4 border-b border-b-gray-200">
          <h3 class="font-semibold text-gray-700 mb-3">Detalle de Cadena de Custodia ({{ chain.details_count }} equipos)</h3>
          <div class="overflow-x-auto">
            <table class="table table-sm w-full table-zebra">
              <thead>
                <tr class="bg-gray-500 text-white text-center">
                  <th class="border border-gray-300 w-10">#</th>
                  <th class="border border-gray-300">Equipo</th>
                  <th class="border border-gray-300 w-30">ID Recurso</th>
                  <th class="border border-gray-300 w-30">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr class="hover:bg-yellow-100" v-for="(detail, index) in chain.details" :key="detail.id">
                  <td class="border border-gray-300 p-2">{{ index + 1 }}</td>
                  <td class="border border-gray-300 p-2">{{ detail.project_resource?.resource_item_name }}</td>
                  <td class="border border-gray-300 p-2 text-center">{{ detail.project_resource_id }}</td>
                  <td class="border border-gray-300 p-2 text-center">
                    <span class="border rounded p-1 cursor-pointer bg-red-400 text-white hover:bg-red-600 font-semibold">
                      Eliminar
                    </span>
                  </td>
                </tr>
                <tr v-if="!chain.details || chain.details.length === 0">
                  <td colspan="4" class="text-center py-4 text-gray-500">
                    No hay detalles en esta cadena de custodia
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pt-2 pb-2">
            <div class="flex gap-4">
              <div class="flex gap-4">
                <div class="p-3 border rounded border-gray-200">
                  Galones:
                  <span class="text-xl text-primary ml-5">{{ chain.total_gallons }}</span>
                </div>
                <div class="p-3 border rounded border-gray-200">
                  Metro Cubicos:
                  <span class="text-xl text-primary ml-5">{{ chain.total_cubic_meters }}</span>
                </div>
                <div class="p-3 border rounded border-gray-200">
                  Barriles:
                  <span class="text-xl text-primary ml-5">{{ chain.total_barrels }}</span>
                </div>
              </div>
              <div class="flex-1 border rounded p-3 border-gray-200">
                <span class="font-semibold">Notas:</span>
                <span class="text-primary ml-5">{{ chain.metadata?.notes || 'Sin notas' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 p-4 rounded-b-lg flex justify-between gap-2">
          <button class="btn btn-sm btn-primary" @click="router.push({ name: 'project-detail' })">
            <i class="las la-arrow-left"></i>
            Volver
          </button>
          <div class="flex gap-2">
            <button 
              class="btn btn-sm btn-primary"
              @click="router.push({ name: 'custody-chain-form', params: { id: chain.id } })"
            >
              <i class="las la-edit"></i>
              Editar
            </button>
            <button class="btn btn-sm btn-primary">
              <i class="las la-print"></i>
              Imprimir
            </button>
            <button class="btn btn-sm bg-red-600 text-white">
              <i class="las la-times-circle"></i>
              Anular
            </button>
          </div>
        </div>
      </div>

      <!-- Mensaje cuando no hay cadenas de custodia -->
      <div v-if="custodyChains.length === 0" class="bg-white rounded-lg shadow-md p-8 text-center">
        <i class="las la-inbox text-6xl text-gray-300"></i>
        <p class="text-gray-500 mt-4">No hay cadenas de custodia registradas para este proyecto</p>
        <button class="btn btn-primary btn-sm mt-4" @click="router.push({ name: 'custody-chain-form' })">
          <i class="las la-plus"></i>
          Crear Primera Cadena
        </button>
      </div>
    </div>

    <!-- Modal de Técnico -->
    <Modal 
      :is-open="showTechnicalModal" 
      :title="`Detalles del Técnico - ${selectedTechnical?.first_name} ${selectedTechnical?.last_name}`"
      size="xl"
      @close="showTechnicalModal = false"
    >
      <TechnicalPresentation v-if="selectedTechnical" :technical="selectedTechnical" />
    </Modal>

    <!-- Modal de Vehículo -->
    <Modal 
      :is-open="showVehicleModal" 
      :title="`Detalles del Vehículo - ${selectedVehicle?.no_plate}`"
      size="xl"
      @close="showVehicleModal = false"
    >
      <VehiclePresentation v-if="selectedVehicle" :vehicle="selectedVehicle" />
    </Modal>
  </div>
</template>