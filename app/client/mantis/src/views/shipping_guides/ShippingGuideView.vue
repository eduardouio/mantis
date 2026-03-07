<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UseProjectStore } from '@/stores/ProjectStore'
import { UseShippingGuideStore } from '@/stores/ShippingGuideStore'
import { appConfig } from '@/AppConfig'
import { formatDate } from '@/utils/formatters'

const projectStore = UseProjectStore()
const shippingGuideStore = UseShippingGuideStore()
const router = useRouter()

onMounted(async () => {
  await projectStore.fetchProjectData()
  await shippingGuideStore.fetchGuidesByProject()
})

const guides = computed(() => shippingGuideStore.shippingGuides || [])
const isProjectClosed = computed(() => projectStore.project?.is_closed === true)

const goBack = () => {
  router.push({ name: 'projects-detail', query: { tab: 'planillas' } })
}

const createGuide = () => {
  router.push({ name: 'shipping-guide-form' })
}

const editGuide = (guide) => {
  router.push({ name: 'shipping-guide-form', params: { id: guide.id } })
}

const confirmDelete = ref(null)
const confirmStatusChange = ref(null)

const askDelete = (guide) => {
  confirmDelete.value = guide
}

const cancelDelete = () => {
  confirmDelete.value = null
}

const executeDelete = async () => {
  if (!confirmDelete.value) return
  try {
    await shippingGuideStore.deleteGuide(confirmDelete.value.id)
    confirmDelete.value = null
  } catch (error) {
    alert('Error al eliminar la guía: ' + error.message)
  }
}

// Cambio de estado
const askStatusChange = (guide, newStatus) => {
  confirmStatusChange.value = { guide, newStatus }
}

const cancelStatusChange = () => {
  confirmStatusChange.value = null
}

const executeStatusChange = async () => {
  if (!confirmStatusChange.value) return
  try {
    await shippingGuideStore.changeStatus(
      confirmStatusChange.value.guide.id,
      confirmStatusChange.value.newStatus
    )
    confirmStatusChange.value = null
  } catch (error) {
    alert('Error al cambiar estado: ' + error.message)
  }
}

const statusLabel = (status) => {
  const labels = { DRAFT: 'BORRADOR', CLOSED: 'CERRADA', VOID: 'ANULADA' }
  return labels[status] || status
}

const statusClass = (status) => {
  const classes = {
    DRAFT: 'badge-warning',
    CLOSED: 'badge-success',
    VOID: 'badge-error'
  }
  return classes[status] || 'badge-ghost'
}
</script>

<template>
  <div class="w-[95%] mx-auto p-6">
    <!-- Header -->
    <div class="bg-white rounded-lg shadow-md p-2 mb-2 border border-gray-200">
      <div class="flex justify-between items-center">
        <h1 class="text-gray-800 flex items-center gap-2 font-semibold">
          <i class="las la-shipping-fast text-blue-500"></i>
          Guías de Remisión - {{ projectStore.projectData?.project?.partner_name }}
        </h1>
        <div class="flex gap-2">
          <button class="btn btn-secondary btn-sm" @click="goBack">
            <i class="las la-arrow-left"></i>
            Volver
          </button>
          <button
            v-if="!isProjectClosed"
            class="btn btn-primary btn-sm"
            @click="createGuide"
          >
            <i class="las la-plus"></i>
            Generar Guía
          </button>
        </div>
      </div>
    </div>

    <!-- Lista de Guías -->
    <div class="grid grid-cols-1 gap-4">
      <div
        v-for="guide in guides"
        :key="guide.id"
        class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
      >
        <!-- Cabecera -->
        <div class="bg-gradient-to-r from-teal-500 to-emerald-600 text-white p-4 rounded-t-lg">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h2 class="text-xl font-bold">
                  #{{ projectStore.projectData?.project?.id }} {{ projectStore.projectData?.project?.partner_name }} - {{ projectStore.projectData?.project?.location }}
                </h2>
                <span class="badge text-teal-500 font-semibold bg-white px-3 py-1">
                  {{ projectStore.projectData?.project?.cardinal_point || 'N/A' }}
                </span>
                <span class="badge font-semibold px-3 py-1" :class="statusClass(guide.status)">
                  {{ statusLabel(guide.status) }}
                </span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-2xl p-1 rounded text-error bg-gray-100 font-mono border border-teal-600 border-2">
                <span class="text-gray-700 ms-5">Guía Nro.</span>
                <span class="me-2">{{ guide.guide_number }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Información General -->
        <div class="p-2">
          <div class="grid grid-cols-4 gap-4">
            <!-- Tipo de Guía -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Tipo:</span>
              <span class="text-sm font-semibold border rounded p-1 border-gray-300 flex-1" :class="{
                'text-blue-700 bg-blue-50': guide.type_shipping_guide === 'EXIT',
                'text-green-700 bg-green-50': guide.type_shipping_guide === 'IN',
                'text-orange-700 bg-orange-50': guide.type_shipping_guide === 'TRANSFER'
              }">
                {{ guide.type_shipping_guide_display || guide.type_shipping_guide || 'N/A' }}
              </span>
            </div>
            <!-- Fecha de Emisión -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Emisión:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ formatDate(guide.issue_date) }}
              </span>
            </div>
            <!-- Motivo del Transporte -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Motivo:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ guide.reason_transport_display || 'N/A' }}
              </span>
            </div>
            <!-- Transporte -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Transporte:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ formatDate(guide.start_date) }} - {{ formatDate(guide.end_date) }}
              </span>
            </div>
            <!-- Origen -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Origen:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ guide.origin_place || 'N/A' }}
              </span>
            </div>
            <!-- Destino -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Destino:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ guide.destination_place || 'N/A' }}
              </span>
            </div>
          </div>
        </div>

        <div class="p-2 border-b bg-gray-50 border-b-gray-200">
          <div class="grid grid-cols-4 gap-4">
            <!-- Transportista -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Transportista:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ guide.carrier_name || 'N/A' }}
                <span v-if="guide.carrier_ci" class="ml-2 me-2 text-gray-200">|</span>
                <span v-if="guide.carrier_ci">CI: {{ guide.carrier_ci }}</span>
              </span>
            </div>
            <!-- Placa -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Placa:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ guide.vehicle_plate || 'N/A' }}
              </span>
            </div>
            <!-- Despachador -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Despachador:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ guide.dispatcher_name || 'N/A' }}
                <span v-if="guide.dispatcher_ci" class="ml-2 me-2 text-gray-200">|</span>
                <span v-if="guide.dispatcher_ci">CI: {{ guide.dispatcher_ci }}</span>
              </span>
            </div>
            <!-- Recibido por -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Recibido por:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ guide.recibed_by || 'N/A' }}
                <span v-if="guide.recibed_ci" class="ml-2 me-2 text-gray-200">|</span>
                <span v-if="guide.recibed_ci">CI: {{ guide.recibed_ci }}</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Costos y Conceptos -->
        <div class="p-2 border-b bg-gray-50 border-b-gray-200">
          <div class="grid grid-cols-4 gap-4">
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-32">Costo Transporte:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                ${{ guide.cost_transport || 0 }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-32">Concepto Logístico:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ guide.sheet_project_logistics_concept || 'N/A' }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-32">Costo Estiba:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                ${{ guide.cost_stowage || 0 }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-32">Concepto Estiba:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ guide.sheet_project_stowage_concept || 'N/A' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Archivo PDF -->
        <div v-if="guide.shipping_guide_file" class="p-4 border-b border-b-gray-200">
          <div class="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
            <i class="las la-file-pdf text-red-500 text-2xl"></i>
            <span class="flex-1 font-medium text-sm text-gray-700">Archivo PDF de la Guía</span>
            <a
              :href="guide.shipping_guide_file"
              target="_blank"
              class="btn btn-sm btn-primary"
              title="Ver PDF"
            >
              <i class="las la-eye"></i>
              Ver PDF
            </a>
            <a
              :href="guide.shipping_guide_file"
              download
              class="btn btn-sm btn-outline btn-primary"
              title="Descargar PDF"
            >
              <i class="las la-download"></i>
              Descargar
            </a>
          </div>
        </div>

        <!-- Detalle de ítems -->
        <div class="p-4 border-b border-b-gray-200">
          <h3 class="font-semibold text-gray-700 mb-3">Detalle de Ítems ({{ guide.details?.length || 0 }} ítems)</h3>
          <div class="overflow-x-auto">
            <table class="table table-sm w-full table-zebra">
              <thead>
                <tr class="bg-gray-500 text-white text-center">
                  <th class="border border-gray-300 w-10">#</th>
                  <th class="border border-gray-300">Descripción</th>
                  <th class="border border-gray-300 w-24">Cantidad</th>
                  <th class="border border-gray-300 w-24">Unidad</th>
                </tr>
              </thead>
              <tbody>
                <tr class="hover:bg-yellow-100" v-for="(detail, index) in guide.details" :key="detail.id">
                  <td class="border border-gray-300 p-2 text-center">{{ index + 1 }}</td>
                  <td class="border border-gray-300 p-2">{{ detail.description }}</td>
                  <td class="border border-gray-300 p-2 text-center">{{ detail.quantity }}</td>
                  <td class="border border-gray-300 p-2 text-center">{{ detail.unit || '' }}</td>
                </tr>
                <tr v-if="!guide.details || guide.details.length === 0">
                  <td colspan="4" class="text-center py-4 text-gray-500">
                    No hay ítems en esta guía de remisión
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="guide.notes" class="pt-2 pb-2">
            <div class="border rounded p-3 border-gray-200">
              <span class="font-semibold">Notas:</span>
              <span class="text-primary ml-5">{{ guide.notes }}</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 p-4 rounded-b-lg flex justify-between gap-2">
          <button class="btn btn-sm btn-primary" @click="goBack">
            <i class="las la-arrow-left"></i>
            Volver
          </button>
          <div class="flex gap-2">
            <!-- Descargar PDF -->
            <a
              :href="appConfig.URLShippingGuideDownload.replace('${id}', guide.id)"
              target="_blank"
              class="btn btn-sm btn-outline btn-accent"
              title="Descargar PDF de Guía de Remisión"
            >
              <i class="las la-file-pdf"></i>
              Descargar PDF
            </a>
            <!-- Cerrar guía (solo desde BORRADOR) -->
            <button
              v-if="guide.status === 'DRAFT'"
              class="btn btn-sm btn-success"
              @click="askStatusChange(guide, 'CLOSED')"
            >
              <i class="las la-check-circle"></i>
              Cerrar Guía
            </button>
            <!-- Editar (solo en BORRADOR) -->
            <button
              v-if="guide.status === 'DRAFT'"
              class="btn btn-sm btn-primary"
              @click="editGuide(guide)"
            >
              <i class="las la-edit"></i>
              Editar
            </button>
            <!-- Anular (desde BORRADOR o CERRADA) -->
            <button
              v-if="guide.status === 'DRAFT' || guide.status === 'CLOSED'"
              class="btn btn-sm bg-red-600 text-white"
              @click="askStatusChange(guide, 'VOID')"
            >
              <i class="las la-ban"></i>
              Anular
            </button>
            <!-- Eliminar (solo en BORRADOR) -->
            <button
              v-if="guide.status === 'DRAFT' && !isProjectClosed"
              class="btn btn-sm btn-outline btn-error"
              @click="askDelete(guide)"
            >
              <i class="las la-trash"></i>
              Eliminar
            </button>
          </div>
        </div>
      </div>

      <!-- Mensaje vacío -->
      <div v-if="guides.length === 0 && !shippingGuideStore.loading" class="bg-white rounded-lg shadow-md p-8 text-center">
        <i class="las la-inbox text-6xl text-gray-300"></i>
        <p class="text-gray-500 mt-4">No hay guías de remisión registradas para este proyecto</p>
        <button
          v-if="!isProjectClosed"
          class="btn btn-primary btn-sm mt-4"
          @click="createGuide"
        >
          <i class="las la-plus"></i>
          Crear Primera Guía
        </button>
      </div>

      <!-- Loading -->
      <div v-if="shippingGuideStore.loading" class="bg-white rounded-lg shadow-md p-8 text-center">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <p class="text-gray-500 mt-4">Cargando guías de remisión...</p>
      </div>
    </div>

    <!-- Modal Confirmar Eliminación -->
    <div v-if="confirmDelete" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg">Confirmar Eliminación</h3>
        <p class="py-4">
          ¿Está seguro de eliminar la Guía de Remisión
          <strong>#{{ confirmDelete.guide_number }}</strong>?
          Esta acción no se puede deshacer.
        </p>
        <div class="modal-action">
          <button class="btn btn-ghost" @click="cancelDelete">Cancelar</button>
          <button class="btn btn-error" @click="executeDelete">Eliminar</button>
        </div>
      </div>
      <div class="modal-backdrop" @click="cancelDelete"></div>
    </div>

    <!-- Modal Confirmar Cambio de Estado -->
    <div v-if="confirmStatusChange" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg">
          {{ confirmStatusChange.newStatus === 'CLOSED' ? 'Cerrar Guía de Remisión' : 'Anular Guía de Remisión' }}
        </h3>
        <p class="py-4">
          <template v-if="confirmStatusChange.newStatus === 'CLOSED'">
            ¿Está seguro de <strong>cerrar</strong> la Guía de Remisión
            <strong>#{{ confirmStatusChange.guide.guide_number }}</strong>?
            <br/>
            <span class="text-warning font-semibold">Una vez cerrada, solo podrá ser anulada.</span>
          </template>
          <template v-else>
            ¿Está seguro de <strong>anular</strong> la Guía de Remisión
            <strong>#{{ confirmStatusChange.guide.guide_number }}</strong>?
            <br/>
            <span class="text-error font-semibold">Esta acción es irreversible. La guía no podrá ser editada ni revertida.</span>
          </template>
        </p>
        <div class="modal-action">
          <button class="btn btn-ghost" @click="cancelStatusChange">Cancelar</button>
          <button
            class="btn"
            :class="confirmStatusChange.newStatus === 'CLOSED' ? 'btn-success' : 'btn-error'"
            @click="executeStatusChange"
          >
            {{ confirmStatusChange.newStatus === 'CLOSED' ? 'Cerrar' : 'Anular' }}
          </button>
        </div>
      </div>
      <div class="modal-backdrop" @click="cancelStatusChange"></div>
    </div>
  </div>
</template>
