<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UseProjectStore } from '@/stores/ProjectStore'
import { UseMaintenanceSheetStore } from '@/stores/MaintenanceSheetStore'
import { appConfig } from '@/AppConfig'

const projectStore = UseProjectStore()
const maintenanceStore = UseMaintenanceSheetStore()
const router = useRouter()

onMounted(async () => {
  await projectStore.fetchProjectData()
  await maintenanceStore.fetchSheetsByProject()
})

const sheets = computed(() => maintenanceStore.sheets || [])
const isProjectClosed = computed(() => projectStore.project?.is_closed === true)

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('es-ES')
}

const goBack = () => {
  router.push({ name: 'projects-detail', query: { tab: 'planillas' } })
}

// ── Confirmaciones ──
const confirmDelete = ref(null)
const confirmStatusChange = ref(null)

const askDelete = (sheet) => {
  confirmDelete.value = sheet
}

const cancelDelete = () => {
  confirmDelete.value = null
}

const executeDelete = async () => {
  if (!confirmDelete.value) return
  try {
    await maintenanceStore.deleteSheet(confirmDelete.value.id)
    confirmDelete.value = null
  } catch (error) {
    alert('Error al eliminar la hoja: ' + error.message)
  }
}

const askStatusChange = (sheet, newStatus) => {
  confirmStatusChange.value = { sheet, newStatus }
}

const cancelStatusChange = () => {
  confirmStatusChange.value = null
}

const executeStatusChange = async () => {
  if (!confirmStatusChange.value) return
  try {
    await maintenanceStore.changeStatus(
      confirmStatusChange.value.sheet.id,
      confirmStatusChange.value.newStatus
    )
    confirmStatusChange.value = null
  } catch (error) {
    alert('Error al cambiar estado: ' + error.message)
  }
}

const statusLabel = (status) => {
  const labels = { DRAFT: 'BORRADOR', CLOSED: 'CERRADO', VOID: 'ANULADO' }
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
          <i class="las la-tools text-blue-500"></i>
          Hojas de Mantenimiento - {{ projectStore.projectData?.project?.partner_name }}
        </h1>
        <div class="flex gap-2">
          <button class="btn btn-secondary btn-sm" @click="goBack">
            <i class="las la-arrow-left"></i>
            Volver
          </button>
          <button
            v-if="!isProjectClosed"
            class="btn btn-primary btn-sm"
            @click="createSheet"
          >
            <i class="las la-plus"></i>
            Nueva Hoja
          </button>
        </div>
      </div>
    </div>

    <!-- Lista de Hojas -->
    <div class="grid grid-cols-1 gap-4">
      <div
        v-for="sheet in sheets"
        :key="sheet.id"
        class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
      >
        <!-- Cabecera -->
        <div class="bg-gradient-to-r from-sky-600 to-blue-700 text-white p-4 rounded-t-lg">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h2 class="text-xl font-bold">
                  #{{ projectStore.projectData?.project?.id }} {{ projectStore.projectData?.project?.partner_name }} - {{ projectStore.projectData?.project?.location }}
                </h2>
                <span class="badge text-sky-600 font-semibold bg-white px-3 py-1">
                  {{ sheet.maintenance_type_display || sheet.maintenance_type }}
                </span>
                <span class="badge font-semibold px-3 py-1" :class="statusClass(sheet.status)">
                  {{ statusLabel(sheet.status) }}
                </span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-2xl p-1 rounded text-error bg-gray-100 font-mono border border-sky-300 border-2">
                <span class="text-gray-700 ms-5">Hoja Nro.</span>
                <span class="me-2">{{ sheet.sheet_number }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Información General -->
        <div class="p-2">
          <div class="grid grid-cols-4 gap-4">
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Técnico:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ sheet.responsible_technical_name || 'N/A' }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">RIG:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ sheet.rig || 'N/A' }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Equipo:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ sheet.resource_item_name || 'N/A' }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Código:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ sheet.code || 'N/A' }}
              </span>
            </div>
          </div>
        </div>

        <div class="p-2 border-b bg-gray-50 border-b-gray-200">
          <div class="grid grid-cols-4 gap-4">
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Ubicación:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ sheet.location || 'N/A' }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Inicio:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ formatDate(sheet.start_date) }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Fin:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ formatDate(sheet.end_date) }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Días / Costo:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ sheet.total_days || 0 }} días
              </span>
            </div>
          </div>
        </div>

        <div class="p-2 border-b bg-gray-50 border-b-gray-200">
          <div class="grid grid-cols-4 gap-4">
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Costo Día:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                ${{ sheet.cost_day || 0 }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Costo Total:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                ${{ sheet.cost_total || 0 }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Costo Logístico:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                ${{ sheet.cost_logistics || 0 }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="sheet.sheet_project_maintenance_concept || sheet.sheet_project_logistics_concept" class="p-2 border-b bg-gray-50 border-b-gray-200">
          <div class="grid grid-cols-2 gap-4">
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-40">Concepto Mant.:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ sheet.sheet_project_maintenance_concept || 'N/A' }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-40">Concepto Logístico:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ sheet.sheet_project_logistics_concept || 'N/A' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Descripción del mantenimiento -->
        <div v-if="sheet.maintenance_description" class="p-3 border-b border-b-gray-200">
          <div class="border rounded p-3 border-gray-200">
            <span class="font-semibold text-sm text-gray-600">Descripción:</span>
            <p class="text-sm text-gray-800 mt-1 whitespace-pre-wrap">{{ sheet.maintenance_description }}</p>
          </div>
        </div>

        <!-- Archivo PDF -->
        <div v-if="sheet.maintenance_file" class="p-4 border-b border-b-gray-200">
          <div class="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
            <i class="las la-file-pdf text-red-500 text-2xl"></i>
            <span class="flex-1 font-medium text-sm text-gray-700">Archivo PDF de la Hoja</span>
            <a
              :href="sheet.maintenance_file"
              target="_blank"
              class="btn btn-sm btn-primary"
            >
              <i class="las la-eye"></i>
              Ver PDF
            </a>
          </div>
        </div>

        <!-- Notas -->
        <div v-if="sheet.notes" class="p-3 border-b border-b-gray-200">
          <div class="border rounded p-3 border-gray-200">
            <span class="font-semibold text-sm">Notas:</span>
            <span class="text-primary ml-5">{{ sheet.notes }}</span>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 p-4 rounded-b-lg flex justify-between gap-2">
          <button class="btn btn-sm btn-primary" @click="goBack">
            <i class="las la-arrow-left"></i>
            Volver
          </button>
          <div class="flex gap-2">
            <a
              :href="appConfig.URLMaintenanceSheetDownload.replace('${id}', sheet.id)"
              target="_blank"
              class="btn btn-sm btn-outline btn-accent"
              title="Descargar PDF de Hoja de Mantenimiento"
            >
              <i class="las la-file-pdf"></i>
              Descargar PDF
            </a>
            <button
              v-if="sheet.status === 'DRAFT'"
              class="btn btn-sm btn-success"
              @click="askStatusChange(sheet, 'CLOSED')"
            >
              <i class="las la-check-circle"></i>
              Cerrar
            </button>
            <button
              v-if="sheet.status === 'DRAFT'"
              class="btn btn-sm btn-primary"
              @click="editSheet(sheet)"
            >
              <i class="las la-edit"></i>
              Editar
            </button>
            <button
              v-if="sheet.status === 'DRAFT' || sheet.status === 'CLOSED'"
              class="btn btn-sm bg-red-600 text-white"
              @click="askStatusChange(sheet, 'VOID')"
            >
              <i class="las la-ban"></i>
              Anular
            </button>
            <button
              v-if="sheet.status === 'DRAFT' && !isProjectClosed"
              class="btn btn-sm btn-outline btn-error"
              @click="askDelete(sheet)"
            >
              <i class="las la-trash"></i>
              Eliminar
            </button>
          </div>
        </div>
      </div>

      <!-- Vacío -->
      <div v-if="sheets.length === 0 && !maintenanceStore.loading" class="bg-white rounded-lg shadow-md p-8 text-center">
        <i class="las la-inbox text-6xl text-gray-300"></i>
        <p class="text-gray-500 mt-4">No hay hojas de mantenimiento registradas para este proyecto</p>
        <button
          v-if="!isProjectClosed"
          class="btn btn-primary btn-sm mt-4"
          @click="createSheet"
        >
          <i class="las la-plus"></i>
          Crear Primera Hoja
        </button>
      </div>

      <!-- Loading -->
      <div v-if="maintenanceStore.loading" class="bg-white rounded-lg shadow-md p-8 text-center">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <p class="text-gray-500 mt-4">Cargando hojas de mantenimiento...</p>
      </div>
    </div>

    <!-- Modal Confirmar Eliminación -->
    <div v-if="confirmDelete" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg">Confirmar Eliminación</h3>
        <p class="py-4">
          ¿Está seguro de eliminar la Hoja de Mantenimiento
          <strong>#{{ confirmDelete.sheet_number }}</strong>?
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
          {{ confirmStatusChange.newStatus === 'CLOSED' ? 'Cerrar Hoja de Mantenimiento' : 'Anular Hoja de Mantenimiento' }}
        </h3>
        <p class="py-4">
          <template v-if="confirmStatusChange.newStatus === 'CLOSED'">
            ¿Está seguro de <strong>cerrar</strong> la Hoja de Mantenimiento
            <strong>#{{ confirmStatusChange.sheet.sheet_number }}</strong>?
            <br/>
            <span class="text-warning font-semibold">Una vez cerrada, solo podrá ser anulada.</span>
          </template>
          <template v-else>
            ¿Está seguro de <strong>anular</strong> la Hoja de Mantenimiento
            <strong>#{{ confirmStatusChange.sheet.sheet_number }}</strong>?
            <br/>
            <span class="text-error font-semibold">Esta acción es irreversible.</span>
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
