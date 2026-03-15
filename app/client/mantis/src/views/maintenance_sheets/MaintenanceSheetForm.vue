<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { appConfig } from '@/AppConfig.js'
import { UseProjectStore } from '@/stores/ProjectStore'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
import { UseMaintenanceSheetStore } from '@/stores/MaintenanceSheetStore'
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore'
import { UseTechnicalStore } from '@/stores/TechnicalStore'
import { getLocalDateString } from '@/utils/formatters'

const projectStore = UseProjectStore()
const projectResourceStore = UseProjectResourceStore()
const maintenanceStore = UseMaintenanceSheetStore()
const sheetProjectsStore = UseSheetProjectsStore()
const technicalStore = UseTechnicalStore()

const router = useRouter()
const route = useRoute()
const isLoading = ref(false)

// Tab activo
const activeTab = ref('general')

// ID de la hoja desde la ruta
const sheetId = computed(() => {
  const id = parseInt(route.params.id)
  return isNaN(id) ? 0 : id
})

// ID de la planilla padre (desde query en modo creación, o desde datos cargados en edición)
const sheetProjectId = computed(() => {
  return parseInt(route.query.sheet_id) || sheet.value.id_sheet_project || 0
})

const isEditMode = computed(() => sheetId.value > 0)
const isProjectClosed = computed(() => projectStore.project?.is_closed === true)

// Estado de la hoja
const sheetStatus = ref('DRAFT')
const canEdit = computed(() => sheetStatus.value === 'DRAFT')

// Datos del formulario
const sheet = ref({
  id_sheet_project: parseInt(route.query.sheet_id) || null,
  responsible_technical_id: null,
  requested_by: '',
  rig: '',
  resource_item_id: null,
  code: '',
  location: '',
  maintenance_type: 'PREVENTIVO',
  start_date: getLocalDateString(),
  end_date: '',
  total_days: 0,
  cost_day: 0,
  cost_total: 0,
  sheet_project_maintenance_concept: 'SERVICIO TÉCNICO ESPECIALIZADO',
  sheet_project_logistics_concept: '',
  cost_logistics: 0,
  maintenance_description: '',
  fault_description: '',
  possible_causes: '',
  replaced_parts: '',
  observations: '',
  performed_by: appConfig.userData.siganture_name || '',
  performed_by_position: appConfig.userData.siganture_role || '',
  approved_by: '',
  approved_by_position: '',
  notes: '',
})

// Flag para evitar cálculos automáticos al cargar datos en edición
const isLoadingData = ref(false)

// Calcular total_days automáticamente cuando cambian las fechas
watch(
  [() => sheet.value.start_date, () => sheet.value.end_date],
  ([startDate, endDate]) => {
    if (isLoadingData.value) return
    if (startDate && endDate && endDate >= startDate) {
      const start = new Date(startDate + 'T00:00:00')
      const end = new Date(endDate + 'T00:00:00')
      const diffMs = end.getTime() - start.getTime()
      const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24)) + 1
      sheet.value.total_days = diffDays
    }
  }
)

// Calcular cost_total automáticamente cuando cambia cost_day o total_days
watch(
  [() => sheet.value.cost_day, () => sheet.value.total_days],
  ([costDay, totalDays]) => {
    if (isLoadingData.value) return
    if (costDay > 0 && totalDays > 0) {
      sheet.value.cost_total = parseFloat((totalDays * costDay).toFixed(2))
    }
  }
)

// Obtener la planilla padre para restricción de fechas
const parentSheet = computed(() => {
  const spId = sheetProjectId.value
  if (!spId) return null
  return sheetProjectsStore.getSheetProjectById(spId)
})

// Rango de fechas permitido (período de la planilla)
const minDate = computed(() => parentSheet.value?.period_start || '')
const maxDate = computed(() => parentSheet.value?.period_end || '')

// Validación de fechas fuera del rango de la planilla
const dateRangeError = computed(() => {
  if (!minDate.value || !maxDate.value) return ''
  const errors = []
  if (sheet.value.start_date && (sheet.value.start_date < minDate.value || sheet.value.start_date > maxDate.value)) {
    errors.push('La fecha de inicio está fuera del período de la planilla')
  }
  if (sheet.value.end_date && (sheet.value.end_date < minDate.value || sheet.value.end_date > maxDate.value)) {
    errors.push('La fecha de finalización está fuera del período de la planilla')
  }
  return errors.join('. ')
})

// Técnicos disponibles
const technicals = computed(() => technicalStore.technicals || [])

// Equipos del proyecto (solo tipo EQUIPO)
const availableEquipments = computed(() => {
  return projectResourceStore.resourcesProject.filter(r =>
    !r.is_deleted && r.type_resource === 'EQUIPO'
  )
})

// Cargar datos en modo edición
const loadSheetData = async () => {
  if (!isEditMode.value) return

  try {
    isLoading.value = true
    isLoadingData.value = true
    const data = await maintenanceStore.fetchSheetDetail(sheetId.value)

    if (data) {
      sheet.value = {
        id: data.id,
        id_sheet_project: data.id_sheet_project,
        responsible_technical_id: data.responsible_technical_id || null,
        requested_by: data.requested_by || '',
        rig: data.rig || '',
        resource_item_id: data.resource_item_id || null,
        code: data.code || '',
        location: data.location || '',
        maintenance_type: data.maintenance_type || 'PREVENTIVO',
        start_date: data.start_date ? data.start_date.substring(0, 10) : '',
        end_date: data.end_date ? data.end_date.substring(0, 10) : '',
        total_days: data.total_days || 0,
        cost_day: data.cost_day || 0,
        cost_total: data.cost_total || 0,
        sheet_project_maintenance_concept: data.sheet_project_maintenance_concept || 'SERVICIO TÉCNICO ESPECIALIZADO',
        sheet_project_logistics_concept: data.sheet_project_logistics_concept || '',
        cost_logistics: data.cost_logistics || 0,
        maintenance_description: data.maintenance_description || '',
        fault_description: data.fault_description || '',
        possible_causes: data.possible_causes || '',
        replaced_parts: data.replaced_parts || '',
        observations: data.observations || '',
        performed_by: data.performed_by || '',
        performed_by_position: data.performed_by_position || '',
        approved_by: data.approved_by || '',
        approved_by_position: data.approved_by_position || '',
        notes: data.notes || '',
      }

      sheetStatus.value = data.status || 'DRAFT'

      // Archivo PDF
      if (data.maintenance_file) {
        maintenanceFileUrl.value = data.maintenance_file
        maintenanceFileName.value = data.maintenance_file.split('/').pop()
      }
    } else {
      alert('Hoja de mantenimiento no encontrada')
      goBackToSheet()
    }
  } catch (error) {
    console.error('Error al cargar hoja:', error)
    alert('Error al cargar los datos: ' + error.message)
    goBackToSheet()
  } finally {
    isLoading.value = false
    isLoadingData.value = false
  }
}

onMounted(async () => {
  await projectStore.fetchProjectData()
  await projectResourceStore.fetchResourcesProject()
  await technicalStore.fetchTechnicalsAvailable()

  if (!isEditMode.value) {
    sheet.value.location = projectStore.project?.location || ''
  }

  if (isEditMode.value) {
    await loadSheetData()
  }
})

// Enviar formulario
const submitForm = async () => {
  try {
    isLoading.value = true

    if (!sheet.value.start_date) {
      alert('La fecha de inicio es requerida')
      return
    }

    if (dateRangeError.value) {
      alert(dateRangeError.value)
      return
    }

    const payload = {
      ...sheet.value,
      id_sheet_project: sheetProjectId.value,
      responsible_technical_id: sheet.value.responsible_technical_id || null,
      resource_item_id: sheet.value.resource_item_id || null,
    }

    if (isEditMode.value) {
      payload.id = sheetId.value
      await maintenanceStore.updateSheet(payload)
    } else {
      await maintenanceStore.createSheet(payload)
    }

    goBackToSheet()
  } catch (error) {
    console.error('Error al guardar:', error)
    alert('Error al ' + (isEditMode.value ? 'actualizar' : 'crear') + ' la hoja: ' + error.message)
  } finally {
    isLoading.value = false
  }
}

const cancelForm = () => {
  goBackToSheet()
}

const goBackToSheet = () => {
  const spId = sheetProjectId.value
  if (spId) {
    router.push({ name: 'sheet-project-view', params: { id: spId } })
  } else {
    router.push({ name: 'projects-detail', query: { tab: 'planillas' } })
  }
}

// ── Upload de archivo PDF ──
const maintenanceFileUrl = ref(null)
const maintenanceFileName = ref(null)
const uploadingFile = ref(false)
const uploadFileMsg = ref('')
const uploadFileMsgType = ref('')

const onFileChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (file.type !== 'application/pdf') {
    uploadFileMsg.value = 'Solo se permiten archivos PDF'
    uploadFileMsgType.value = 'error'
    return
  }

  uploadingFile.value = true
  uploadFileMsg.value = ''

  const fd = new FormData()
  fd.append('file', file)
  fd.append('model_type', 'sheet_maintenance')
  fd.append('object_id', sheetId.value)
  fd.append('field_name', 'maintenance_file')

  try {
    const res = await fetch(appConfig.URLLoadFiles, {
      method: 'POST',
      body: fd,
    })
    const data = await res.json()
    if (data.success) {
      maintenanceFileUrl.value = data.data.file_url
      maintenanceFileName.value = data.data.file_name
      uploadFileMsg.value = 'Archivo subido correctamente'
      uploadFileMsgType.value = 'success'
    } else {
      uploadFileMsg.value = data.error || 'Error al subir el archivo'
      uploadFileMsgType.value = 'error'
    }
  } catch (err) {
    uploadFileMsg.value = 'Error de conexión: ' + err.message
    uploadFileMsgType.value = 'error'
  } finally {
    uploadingFile.value = false
  }
}

const deleteMaintenanceFile = async () => {
  if (!confirm('¿Eliminar el archivo PDF de esta hoja?')) return
  try {
    const params = new URLSearchParams({
      model_type: 'sheet_maintenance',
      object_id: sheetId.value,
      field_name: 'maintenance_file',
    })
    const res = await fetch(`${appConfig.URLLoadFiles}?${params}`, {
      method: 'DELETE',
    })
    const data = await res.json()
    if (data.success) {
      maintenanceFileUrl.value = null
      maintenanceFileName.value = null
      uploadFileMsg.value = 'Archivo eliminado'
      uploadFileMsgType.value = 'success'
    } else {
      uploadFileMsg.value = data.error || 'Error al eliminar'
      uploadFileMsgType.value = 'error'
    }
  } catch (err) {
    uploadFileMsg.value = 'Error: ' + err.message
    uploadFileMsgType.value = 'error'
  }
}
</script>

<template>
  <div class="w-[90%] mx-auto p-3">
    <!-- Título -->
    <div class="bg-white rounded-lg p-3 mb-2 border border-gray-200 shadow-sm">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-lg font-semibold text-gray-800">
            <i class="las la-tools text-sky-600"></i>
            {{ isEditMode ? `Editar Hoja de Mantenimiento #${sheetId}` : 'Nueva Hoja de Mantenimiento' }}
          </h2>
          <p class="text-xs text-gray-600 mt-0.5">
            {{ isEditMode ? 'Modifique los datos de la hoja de mantenimiento' : 'Complete los datos para generar una nueva hoja de mantenimiento' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <span class="badge badge-primary">
            Proyecto #{{ appConfig.idProject }}
          </span>
          <span v-if="isEditMode" class="badge" :class="{
            'badge-warning': sheetStatus === 'DRAFT',
            'badge-success': sheetStatus === 'CLOSED',
            'badge-error': sheetStatus === 'VOID'
          }">
            {{ sheetStatus === 'DRAFT' ? 'BORRADOR' : sheetStatus === 'CLOSED' ? 'CERRADO' : 'ANULADO' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Alerta de solo lectura -->
    <div v-if="isEditMode && !canEdit" class="alert alert-warning shadow-sm mb-2 py-2">
      <i class="las la-lock text-lg"></i>
      <span class="text-sm">
        Esta hoja está en estado <strong>{{ sheetStatus === 'CLOSED' ? 'CERRADO' : 'ANULADO' }}</strong> y no permite modificaciones.
      </span>
    </div>

    <form @submit.prevent="submitForm">
      <!-- Tabs con colores -->
      <div class="flex gap-1 mb-3 border-b border-gray-200">
        <button type="button"
          class="px-4 py-2.5 rounded-t-lg font-semibold text-sm transition-all flex items-center gap-1"
          :class="activeTab === 'general'
            ? 'bg-blue-600 text-white shadow-sm'
            : 'bg-gray-100 text-gray-600 hover:bg-blue-50 hover:text-blue-600'"
          @click="activeTab = 'general'">
          <i class="las la-cog"></i> General y Costos
        </button>
        <button type="button"
          class="px-4 py-2.5 rounded-t-lg font-semibold text-sm transition-all flex items-center gap-1"
          :class="activeTab === 'maintenance'
            ? 'bg-emerald-600 text-white shadow-sm'
            : 'bg-gray-100 text-gray-600 hover:bg-emerald-50 hover:text-emerald-600'"
          @click="activeTab = 'maintenance'">
          <i class="las la-wrench"></i> Mantenimiento
        </button>
        <button type="button"
          class="px-4 py-2.5 rounded-t-lg font-semibold text-sm transition-all flex items-center gap-1"
          :class="activeTab === 'details'
            ? 'bg-amber-600 text-white shadow-sm'
            : 'bg-gray-100 text-gray-600 hover:bg-amber-50 hover:text-amber-600'"
          @click="activeTab = 'details'">
          <i class="las la-clipboard-check"></i> Observaciones y Responsables
        </button>
      </div>

      <!-- Tab: General y Costos -->
      <div v-show="activeTab === 'general'" class="space-y-3">
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Datos Generales del Mantenimiento</h6>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <!-- Técnico Responsable -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Técnico Responsable</span>
              </label>
              <select
                v-model.number="sheet.responsible_technical_id"
                :disabled="!canEdit"
                class="select select-bordered w-full"
              >
                <option :value="null">Seleccione un técnico (opcional)</option>
                <option v-for="tech in technicals" :key="tech.id" :value="tech.id">
                  {{ tech.name }} {{ tech.last_name || '' }}
                </option>
              </select>
            </div>

            <!-- Solicitado Por -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Solicitado Por</span>
              </label>
              <input
                type="text"
                v-model="sheet.requested_by"
                placeholder="Nombre de quien solicita"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <!-- RIG -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">RIG</span>
              </label>
              <input
                type="text"
                v-model="sheet.rig"
                placeholder="Ej: 125"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <!-- Equipo -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Equipo</span>
              </label>
              <select
                v-model.number="sheet.resource_item_id"
                :disabled="!canEdit"
                class="select select-bordered w-full"
              >
                <option :value="null">Seleccione un equipo (opcional)</option>
                <option v-for="equip in availableEquipments" :key="equip.resource_item_id" :value="equip.resource_item_id">
                  {{ equip.resource_item_code }} / {{ equip.type_equipment_display || equip.resource_item_name }}
                </option>
              </select>
            </div>

            <!-- Código -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Código</span>
              </label>
              <input
                type="text"
                v-model="sheet.code"
                placeholder="Código del equipo"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <!-- Ubicación -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Ubicación</span>
              </label>
              <input
                type="text"
                v-model="sheet.location"
                placeholder="Ubicación del equipo"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <!-- Tipo de Mantenimiento -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Tipo de Mantenimiento *</span>
              </label>
              <select
                v-model="sheet.maintenance_type"
                :disabled="!canEdit"
                class="select select-bordered w-full"
                required
              >
                <option value="PREVENTIVO">PREVENTIVO</option>
                <option value="CORRECTIVO">CORRECTIVO</option>
              </select>
            </div>

            <!-- Fecha de Inicio -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Fecha de Inicio *</span>
              </label>
              <input
                type="date"
                v-model="sheet.start_date"
                required
                :min="minDate"
                :max="maxDate"
                :disabled="!canEdit"
                class="input input-bordered w-full"
                :class="{ 'input-error': sheet.start_date && minDate && maxDate && (sheet.start_date < minDate || sheet.start_date > maxDate) }"
              />
              <label v-if="sheet.start_date && minDate && maxDate && (sheet.start_date < minDate || sheet.start_date > maxDate)" class="label py-0">
                <span class="label-text-alt text-error">Debe estar entre {{ minDate }} y {{ maxDate }}</span>
              </label>
            </div>

            <!-- Fecha de Finalización -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Fecha de Finalización</span>
              </label>
              <input
                type="date"
                v-model="sheet.end_date"
                :min="minDate"
                :max="maxDate"
                :disabled="!canEdit"
                class="input input-bordered w-full"
                :class="{ 'input-error': sheet.end_date && minDate && maxDate && (sheet.end_date < minDate || sheet.end_date > maxDate) }"
              />
              <label v-if="sheet.end_date && minDate && maxDate && (sheet.end_date < minDate || sheet.end_date > maxDate)" class="label py-0">
                <span class="label-text-alt text-error">Debe estar entre {{ minDate }} y {{ maxDate }}</span>
              </label>
            </div>

            <!-- Total Días -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Total Días</span>
              </label>
              <input
                type="number"
                v-model.number="sheet.total_days"
                min="0"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <!-- Costo Día -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Costo Día</span>
              </label>
              <input
                type="number"
                v-model.number="sheet.cost_day"
                min="0"
                step="0.01"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>
          </div>
        </div>

        <!-- Costos -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Costos</h6>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Costo Total</span>
              </label>
              <input
                type="number"
                v-model.number="sheet.cost_total"
                min="0"
                step="0.01"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Concepto de Mantenimiento</span>
              </label>
              <input
                type="text"
                v-model="sheet.sheet_project_maintenance_concept"
                placeholder="Ej: SERVICIO TÉCNICO ESPECIALIZADO"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Costo Logístico</span>
              </label>
              <input
                type="number"
                v-model.number="sheet.cost_logistics"
                min="0"
                step="0.01"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Concepto Logístico</span>
              </label>
              <input
                type="text"
                v-model="sheet.sheet_project_logistics_concept"
                placeholder="Concepto logístico (opcional)"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: Mantenimiento -->
      <div v-show="activeTab === 'maintenance'" class="space-y-3">
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Descripción del Mantenimiento</h6>
          <textarea
            v-model="sheet.maintenance_description"
            rows="4"
            placeholder="Describa las actividades realizadas..."
            :disabled="!canEdit"
            class="textarea textarea-bordered w-full"
          ></textarea>
        </div>

        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Falla y Posibles Causas</h6>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Descripción de la Falla</span>
              </label>
              <textarea
                v-model="sheet.fault_description"
                rows="4"
                placeholder="Describa la falla encontrada..."
                :disabled="!canEdit"
                class="textarea textarea-bordered w-full"
              ></textarea>
            </div>
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Posibles Causas</span>
              </label>
              <textarea
                v-model="sheet.possible_causes"
                rows="4"
                placeholder="Posibles causas de la falla..."
                :disabled="!canEdit"
                class="textarea textarea-bordered w-full"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Repuestos y/o Accesorios Reemplazados</h6>
          <textarea
            v-model="sheet.replaced_parts"
            rows="3"
            placeholder="Detalle los repuestos o accesorios reemplazados..."
            :disabled="!canEdit"
            class="textarea textarea-bordered w-full"
          ></textarea>
        </div>
      </div>

      <!-- Tab: Observaciones y Responsables -->
      <div v-show="activeTab === 'details'" class="space-y-3">
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Observaciones y Recomendaciones</h6>
          <textarea
            v-model="sheet.observations"
            rows="3"
            placeholder="Observaciones y recomendaciones..."
            :disabled="!canEdit"
            class="textarea textarea-bordered w-full"
          ></textarea>
        </div>

        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Responsables</h6>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Realizado Por</span>
              </label>
              <input
                type="text"
                v-model="sheet.performed_by"
                placeholder="Nombre de quien realizó"
                disabled
                class="input input-bordered w-full bg-gray-100"
              />
            </div>
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Cargo</span>
              </label>
              <input
                type="text"
                v-model="sheet.performed_by_position"
                placeholder="Cargo de quien realizó"
                disabled
                class="input input-bordered w-full bg-gray-100"
              />
            </div>
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Aprobado Por</span>
              </label>
              <input
                type="text"
                v-model="sheet.approved_by"
                placeholder="Nombre de quien aprobó"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Cargo</span>
              </label>
              <input
                type="text"
                v-model="sheet.approved_by_position"
                placeholder="Cargo de quien aprobó"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>
          </div>
        </div>

        <!-- Archivo PDF -->
        <div v-if="isEditMode" class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">
            <i class="las la-file-pdf text-red-500"></i>
            Archivo PDF de la Hoja
          </h6>

          <div v-if="maintenanceFileUrl" class="flex items-center gap-2 mb-3 p-2 bg-green-50 border border-green-200 rounded">
            <i class="las la-check-circle text-success text-lg"></i>
            <span class="flex-1 text-sm">
              <strong>Archivo cargado:</strong> {{ maintenanceFileName }}
            </span>
            <a :href="maintenanceFileUrl" target="_blank" class="btn btn-xs btn-ghost text-blue-500">
              <i class="las la-eye"></i> Ver
            </a>
            <button
              v-if="canEdit"
              type="button"
              class="btn btn-xs btn-ghost text-error"
              @click="deleteMaintenanceFile"
            >
              <i class="las la-trash"></i> Eliminar
            </button>
          </div>

          <div v-else class="flex items-center gap-2 mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
            <i class="las la-exclamation-circle text-warning text-lg"></i>
            <span class="text-sm text-gray-600">No se ha cargado un archivo PDF para esta hoja.</span>
          </div>

          <div v-if="canEdit" class="flex items-center gap-2">
            <input
              type="file"
              accept=".pdf,application/pdf"
              class="file-input file-input-bordered file-input-sm flex-1"
              @change="onFileChange"
              :disabled="uploadingFile"
            />
            <span v-if="uploadingFile" class="loading loading-spinner loading-sm text-primary"></span>
          </div>

          <div v-if="uploadFileMsg" class="mt-1 text-sm" :class="uploadFileMsgType === 'success' ? 'text-success' : 'text-error'">
            {{ uploadFileMsg }}
          </div>
        </div>

        <!-- Notas -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Notas</h6>
          <textarea
            v-model="sheet.notes"
            rows="3"
            placeholder="Notas adicionales..."
            :disabled="!canEdit"
            class="textarea textarea-bordered w-full"
          ></textarea>
        </div>
      </div>

      <!-- Botones -->
      <div class="flex gap-2 justify-end mt-3">
        <button type="button" class="btn btn-outline btn-sm" @click="cancelForm" :disabled="isLoading">
          <i class="las la-times"></i>
          Volver
        </button>
        <button
          v-if="canEdit"
          type="submit"
          class="btn btn-primary btn-sm"
          :disabled="isLoading || isProjectClosed"
        >
          <i v-if="!isLoading" class="las la-save"></i>
          <i v-else class="las la-spinner animate-spin"></i>
          {{ isLoading ? 'Guardando...' : (isEditMode ? 'Actualizar Hoja' : 'Guardar Hoja') }}
        </button>
      </div>
    </form>
  </div>
</template>
