<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { appConfig } from '@/AppConfig.js'
import { UseProjectStore } from '@/stores/ProjectStore'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
import { UseShippingGuideStore } from '@/stores/ShippingGuideStore'
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore'
import { UseVehicleStore } from '@/stores/VehicleStore'
import { UseTechnicalStore } from '@/stores/TechnicalStore'
import { getLocalDateString } from '@/utils/formatters'

const projectStore = UseProjectStore()
const projectResourceStore = UseProjectResourceStore()
const shippingGuideStore = UseShippingGuideStore()
const sheetProjectsStore = UseSheetProjectsStore()
const vehicleStore = UseVehicleStore()
const technicalStore = UseTechnicalStore()

const router = useRouter()
const route = useRoute()
const isLoading = ref(false)
const BASE_PLACE = 'BASE PEISOL'

// Tab activo
const activeTab = ref('general')

// ID de la guía desde la ruta
const guideId = computed(() => {
  const id = parseInt(route.params.id)
  return isNaN(id) ? 0 : id
})

const isEditMode = computed(() => guideId.value > 0)
const isProjectClosed = computed(() => projectStore.project?.is_closed === true)

// Estado de la guía
const guideStatus = ref('DRAFT')

// Determina si la guía es editable (solo en BORRADOR)
const canEdit = computed(() => guideStatus.value === 'DRAFT')
const projectLocation = computed(() => projectStore.project?.location || '')

// Obtener la planilla activa (IN_PROGRESS) para restricción de fechas
const activeSheet = computed(() => {
  const sheets = sheetProjectsStore.sheetProjects || []
  return sheets.find(s => s.status === 'IN_PROGRESS') || null
})

// Rango de fechas permitido (período de la planilla activa)
const minDate = computed(() => activeSheet.value?.period_start || '')
const maxDate = computed(() => activeSheet.value?.period_end || '')

// Validación de fechas fuera del rango de la planilla
const dateRangeError = computed(() => {
  if (!minDate.value || !maxDate.value) return ''
  const errors = []
  if (guide.value.issue_date && (guide.value.issue_date < minDate.value || guide.value.issue_date > maxDate.value)) {
    errors.push('La fecha de emisión está fuera del período de la planilla activa')
  }
  if (guide.value.start_date && (guide.value.start_date < minDate.value || guide.value.start_date > maxDate.value)) {
    errors.push('La fecha de inicio está fuera del período de la planilla activa')
  }
  if (guide.value.end_date && (guide.value.end_date < minDate.value || guide.value.end_date > maxDate.value)) {
    errors.push('La fecha fin está fuera del período de la planilla activa')
  }
  return errors.join('. ')
})

// Datos del formulario
const guide = ref({
  project_id: appConfig.idProject,
  type_shipping_guide: 'EXIT',
  guide_number: null,
  issue_date: getLocalDateString(),
  start_date: '',
  end_date: '',
  origin_place: '',
  destination_place: '',
  carrier_name: '',
  carrier_ci: '',
  vehicle_plate: '',
  dispatcher_name: appConfig.userData.siganture_name || '',
  dispatcher_ci: appConfig.userData.siganture_dni || '',
  contact_name: '',
  contact_phone: '',
  recibed_by: '',
  recibed_ci: '',
  reason_transport: '',
  cost_transport: 0,
  sheet_project_logistics_concept: '',
  cost_stowage: 0,
  sheet_project_stowage_concept: '',
  notes: '',
})

const derivedGuidePlaces = computed(() => {
  switch (guide.value.type_shipping_guide) {
    case 'EXIT':
      return {
        origin_place: BASE_PLACE,
        destination_place: projectLocation.value,
      }
    case 'IN':
      return {
        origin_place: projectLocation.value,
        destination_place: BASE_PLACE,
      }
    case 'TRANSFER':
      return {
        origin_place: projectLocation.value,
        destination_place: '',
      }
    default:
      return {
        origin_place: guide.value.origin_place || '',
        destination_place: guide.value.destination_place || '',
      }
  }
})

const placeHelpText = computed(() => {
  switch (guide.value.type_shipping_guide) {
    case 'EXIT':
      return 'Sugerido: origen BASE PEISOL y destino en la ubicación del proyecto.'
    case 'IN':
      return 'Sugerido: origen en la ubicación del proyecto y destino BASE PEISOL.'
    case 'TRANSFER':
      return 'Sugerido: origen en la ubicación del proyecto y destino en blanco.'
    default:
      return ''
  }
})

const applyDerivedPlaces = () => {
  guide.value.origin_place = derivedGuidePlaces.value.origin_place
  guide.value.destination_place = derivedGuidePlaces.value.destination_place
}

// Detalles (ítems de la guía)
const details = ref([])

// Nuevo ítem manual
const newDetail = ref({
  description: '',
  quantity: 1,
  unit: '',
})

// Recursos del proyecto disponibles para agregar (solo equipos físicos, sin importar si están activos)
const availableResources = computed(() => {
  return projectResourceStore.resourcesProject.filter(r => 
    !r.is_deleted && r.type_resource === 'EQUIPO'
  )
})

// Vehículos disponibles
const vehicles = computed(() => {
  return vehicleStore.vehicles.map(v => ({
    id: v.id,
    display: `${v.no_plate} - ${v.brand} ${v.model}`,
    plate: v.no_plate,
  }))
})

const selectedVehicleId = ref(null)

// Al seleccionar un vehículo, rellenar la placa
watch(selectedVehicleId, (newId) => {
  if (newId) {
    const vehicle = vehicleStore.vehicles.find(v => v.id === newId)
    if (vehicle) {
      guide.value.vehicle_plate = vehicle.no_plate
    }
  }
})

// Lista de técnicos para autocompletar nombre del transportista
const technicalOptions = computed(() => {
  return (technicalStore.technicals || []).map(t => ({
    id: t.id,
    fullName: `${t.first_name} ${t.last_name}`.trim(),
    dni: t.dni || '',
  }))
})

// Cuando cambia el nombre del transportista, verificar si coincide con un técnico
watch(() => guide.value.carrier_name, (newName) => {
  if (!newName) return
  const match = technicalOptions.value.find(t => t.fullName === newName)
  if (match) {
    guide.value.carrier_ci = match.dni
  }
})

// Cargar datos en modo edición
const loadGuideData = async () => {
  if (!isEditMode.value) return

  try {
    isLoading.value = true
    const data = await shippingGuideStore.fetchGuideDetail(guideId.value)

    if (data) {
      guide.value = {
        id: data.id,
        project_id: data.project_id,
        type_shipping_guide: data.type_shipping_guide || 'EXIT',
        guide_number: data.guide_number || null,
        issue_date: data.issue_date || '',
        start_date: data.start_date || '',
        end_date: data.end_date || '',
        origin_place: data.origin_place || '',
        destination_place: data.destination_place || '',
        carrier_name: data.carrier_name || '',
        carrier_ci: data.carrier_ci || '',
        vehicle_plate: data.vehicle_plate || '',
        dispatcher_name: data.dispatcher_name || '',
        dispatcher_ci: data.dispatcher_ci || '',
        contact_name: data.contact_name || '',
        contact_phone: data.contact_phone || '',
        recibed_by: data.recibed_by || '',
        recibed_ci: data.recibed_ci || '',
        reason_transport: data.reason_transport || '',
        cost_transport: data.cost_transport || 0,
        sheet_project_logistics_concept: data.sheet_project_logistics_concept || '',
        cost_stowage: data.cost_stowage || 0,
        sheet_project_stowage_concept: data.sheet_project_stowage_concept || '',
        notes: data.notes || '',
      }

      // Cargar estado
      guideStatus.value = data.status || 'DRAFT'

      // Cargar archivo PDF si existe
      if (data.shipping_guide_file) {
        shippingGuideFileUrl.value = data.shipping_guide_file
        shippingGuideFileName.value = data.shipping_guide_file.split('/').pop()
      }

      // Cargar detalles
      details.value = (data.details || []).map(d => ({
        id_resource_item: d.id_resource_item || null,
        description: d.description,
        quantity: d.quantity,
        unit: d.unit || '',
      }))

      // Buscar vehículo por placa
      if (data.vehicle_plate) {
        const vehicle = vehicleStore.vehicles.find(v => v.no_plate === data.vehicle_plate)
        if (vehicle) selectedVehicleId.value = vehicle.id
      }
    } else {
      alert('Guía de remisión no encontrada')
      router.push({ name: 'shipping-guide-list' })
    }
  } catch (error) {
    console.error('Error al cargar guía:', error)
    alert('Error al cargar los datos: ' + error.message)
    router.push({ name: 'shipping-guide-list' })
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await projectStore.fetchProjectData()
  await projectResourceStore.fetchResourcesProject()
  await vehicleStore.fetchVehicles()
  await technicalStore.fetchTechnicalsAvailable()

  // Inicializar con datos del proyecto
  if (!isEditMode.value) {
    guide.value.contact_name = projectStore.project?.contact_name || ''
    guide.value.contact_phone = projectStore.project?.contact_phone || ''
    applyDerivedPlaces()
  }

  if (isEditMode.value) {
    await loadGuideData()
  }
})

// Agregar recurso del proyecto como ítem de la guía
const addResourceAsDetail = (resource) => {
  // Descripción: CÓDIGO / TIPO DE EQUIPO (ej: PSL-BT-185 / BATERIA SANITARIA HOMBRE)
  const equipType = resource.type_equipment_display || resource.resource_item_name || ''
  const description = `${resource.resource_item_code} / ${equipType}`
  details.value.push({
    id_resource_item: resource.resource_item_id,
    description,
    quantity: 1,
    unit: '',
  })
}

// Agregar ítem manual
const addManualDetail = () => {
  if (!newDetail.value.description.trim()) return
  details.value.push({
    description: newDetail.value.description,
    quantity: newDetail.value.quantity || 1,
    unit: newDetail.value.unit || '',
  })
  newDetail.value = { description: '', quantity: 1, unit: '' }
}

// Remover ítem
const removeDetail = (index) => {
  details.value.splice(index, 1)
}

// Enviar formulario
const submitForm = async () => {
  try {
    isLoading.value = true

    if (!guide.value.issue_date) {
      alert('La fecha de emisión es requerida')
      return
    }

    if (dateRangeError.value) {
      alert(dateRangeError.value)
      return
    }

    const payload = {
      ...guide.value,
      project_id: appConfig.idProject,
      guide_number: guide.value.guide_number || null,
      origin_place: derivedGuidePlaces.value.origin_place,
      destination_place: derivedGuidePlaces.value.destination_place,
      details: details.value.map(d => ({
        id_resource_item: d.id_resource_item || null,
        description: d.description,
        quantity: d.quantity,
        unit: d.unit,
      })),
    }

    if (isEditMode.value) {
      payload.id = guideId.value
      await shippingGuideStore.updateGuide(payload)
    } else {
      await shippingGuideStore.createGuide(payload)
    }

    router.push({ name: 'shipping-guide-list' })
  } catch (error) {
    console.error('Error al guardar:', error)
    alert('Error al ' + (isEditMode.value ? 'actualizar' : 'crear') + ' la guía: ' + error.message)
  } finally {
    isLoading.value = false
  }
}

const cancelForm = () => {
  router.push({ name: 'shipping-guide-list' })
}

// ── Upload de archivo PDF de guía ────────────────────────────
const shippingGuideFileUrl = ref(null)
const shippingGuideFileName = ref(null)
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
  fd.append('model_type', 'shipping_guide')
  fd.append('object_id', guideId.value)
  fd.append('field_name', 'shipping_guide_file')

  try {
    const res = await fetch(appConfig.URLLoadFiles, {
      method: 'POST',
      body: fd,
    })
    const data = await res.json()
    if (data.success) {
      shippingGuideFileUrl.value = data.data.file_url
      shippingGuideFileName.value = data.data.file_name
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

const deleteGuideFile = async () => {
  if (!confirm('¿Eliminar el archivo PDF de esta guía?')) return
  try {
    const params = new URLSearchParams({
      model_type: 'shipping_guide',
      object_id: guideId.value,
      field_name: 'shipping_guide_file',
    })
    const res = await fetch(`${appConfig.URLLoadFiles}?${params}`, {
      method: 'DELETE',
    })
    const data = await res.json()
    if (data.success) {
      shippingGuideFileUrl.value = null
      shippingGuideFileName.value = null
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
            <i class="las la-shipping-fast text-teal-600"></i>
            {{ isEditMode ? `Editar Guía de Remisión #${guideId}` : 'Nueva Guía de Remisión' }}
          </h2>
          <p class="text-xs text-gray-600 mt-0.5">
            {{ isEditMode ? 'Modifique los datos de la guía de remisión' : 'Complete los datos para generar una nueva guía de remisión' }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <span class="badge badge-primary">
            Proyecto #{{ appConfig.idProject }}
          </span>
          <span v-if="isEditMode" class="badge" :class="{
            'badge-warning': guideStatus === 'DRAFT',
            'badge-success': guideStatus === 'CLOSED',
            'badge-error': guideStatus === 'VOID'
          }">
            {{ guideStatus === 'DRAFT' ? 'BORRADOR' : guideStatus === 'CLOSED' ? 'CERRADA' : 'ANULADA' }}
          </span>
          <div class="form-control">
            <div class="flex items-center gap-1">
              <span class="text-xs text-gray-500 font-medium">Guía Nro.</span>
              <input
                v-model.number="guide.guide_number"
                type="number"
                min="1"
                :disabled="!canEdit"
                class="input input-bordered input-sm w-32 font-bold text-red-800 font-mono text-[16px] text-center"
                placeholder="Auto"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerta de solo lectura -->
    <div v-if="isEditMode && !canEdit" class="alert alert-warning shadow-sm mb-2 py-2">
      <i class="las la-lock text-lg"></i>
      <span class="text-sm">
        Esta guía está en estado <strong>{{ guideStatus === 'CLOSED' ? 'CERRADA' : 'ANULADA' }}</strong> y no permite modificaciones.
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
          <i class="las la-info-circle"></i> General y Transporte
        </button>
        <button type="button"
          class="px-4 py-2.5 rounded-t-lg font-semibold text-sm transition-all flex items-center gap-1"
          :class="activeTab === 'contacts'
            ? 'bg-emerald-600 text-white shadow-sm'
            : 'bg-gray-100 text-gray-600 hover:bg-emerald-50 hover:text-emerald-600'"
          @click="activeTab = 'contacts'">
          <i class="las la-users"></i> Contacto y Costos
        </button>
        <button type="button"
          class="px-4 py-2.5 rounded-t-lg font-semibold text-sm transition-all flex items-center gap-1"
          :class="activeTab === 'items'
            ? 'bg-amber-600 text-white shadow-sm'
            : 'bg-gray-100 text-gray-600 hover:bg-amber-50 hover:text-amber-600'"
          @click="activeTab = 'items'">
          <i class="las la-boxes"></i> Ítems y Notas
          <span class="badge badge-xs badge-primary ml-1">{{ details.length }}</span>
        </button>
      </div>

      <!-- ═══ Tab 1: General y Transporte ═══ -->
      <div v-show="activeTab === 'general'" class="space-y-3">
        <!-- Información General -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Información General</h6>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <!-- Tipo de Guía -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Tipo de Guía *</span>
              </label>
              <select
                id="type_shipping_guide"
                v-model="guide.type_shipping_guide"
                @change="applyDerivedPlaces"
                :disabled="!canEdit"
                class="select select-bordered w-full"
              >
                <option value="EXIT">SALIDA A PROYECTO</option>
                <option value="IN">ENTRADA A BASE</option>
                <option value="TRANSFER">TRANSFERENCIA ENTRE PROYECTOS</option>
              </select>
            </div>

            <!-- Fecha de Emisión -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Fecha de Emisión *</span>
              </label>
              <input
                type="date"
                id="issue_date"
                v-model="guide.issue_date"
                required
                :min="minDate"
                :max="maxDate"
                :disabled="!canEdit"
                class="input input-bordered w-full"
                :class="{ 'input-error': guide.issue_date && minDate && maxDate && (guide.issue_date < minDate || guide.issue_date > maxDate) }"
              />
              <label v-if="guide.issue_date && minDate && maxDate && (guide.issue_date < minDate || guide.issue_date > maxDate)" class="label py-0">
                <span class="label-text-alt text-error">Debe estar entre {{ minDate }} y {{ maxDate }}</span>
              </label>
            </div>

            <!-- Fecha Inicio Transporte -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Fecha Inicio Transporte</span>
              </label>
              <input
                type="date"
                id="start_date"
                v-model="guide.start_date"
                :min="minDate"
                :max="maxDate"
                :disabled="!canEdit"
                class="input input-bordered w-full"
                :class="{ 'input-error': guide.start_date && minDate && maxDate && (guide.start_date < minDate || guide.start_date > maxDate) }"
              />
              <label v-if="guide.start_date && minDate && maxDate && (guide.start_date < minDate || guide.start_date > maxDate)" class="label py-0">
                <span class="label-text-alt text-error">Debe estar entre {{ minDate }} y {{ maxDate }}</span>
              </label>
            </div>

            <!-- Fecha Fin Transporte -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Fecha Fin Transporte</span>
              </label>
              <input
                type="date"
                id="end_date"
                v-model="guide.end_date"
                :min="minDate"
                :max="maxDate"
                :disabled="!canEdit"
                class="input input-bordered w-full"
                :class="{ 'input-error': guide.end_date && minDate && maxDate && (guide.end_date < minDate || guide.end_date > maxDate) }"
              />
              <label v-if="guide.end_date && minDate && maxDate && (guide.end_date < minDate || guide.end_date > maxDate)" class="label py-0">
                <span class="label-text-alt text-error">Debe estar entre {{ minDate }} y {{ maxDate }}</span>
              </label>
            </div>

            <!-- Lugar de Origen -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Lugar de Origen</span>
              </label>
              <input
                type="text"
                id="origin_place"
                v-model="guide.origin_place"
                placeholder="Ej: Quito, Bodega Central"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
              <label class="label py-0">
                <span class="label-text-alt text-gray-500">{{ placeHelpText }}</span>
              </label>
            </div>

            <!-- Lugar de Destino -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Lugar de Destino</span>
              </label>
              <input
                type="text"
                id="destination_place"
                v-model="guide.destination_place"
                placeholder="Ej: Campamento Norte"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
              <label class="label py-0">
                <span class="label-text-alt text-gray-500">Se autocompleta al cambiar el tipo, pero puedes modificarlo.</span>
              </label>
            </div>

            <!-- Motivo del Transporte -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Motivo del Transporte</span>
              </label>
              <select
                id="reason_transport"
                v-model="guide.reason_transport"
                :disabled="!canEdit"
                class="select select-bordered w-full"
              >
                <option value="">Seleccione un motivo (opcional)</option>
                <option value="USE_IN_PROJECT">UTILIZACIÓN EN PROYECTO</option>
                <option value="RENT">ALQUILER</option>
                <option value="DEVOLUTION">DEVOLUCIÓN</option>
                <option value="SALE">VENTA</option>
              </select>
            </div>

            <!-- Vehículo -->
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Vehículo</span>
              </label>
              <select
                id="vehicle_select"
                v-model.number="selectedVehicleId"
                :disabled="!canEdit"
                class="select select-bordered w-full"
              >
                <option :value="null">Seleccione un vehículo (opcional)</option>
                <option v-for="v in vehicles" :key="v.id" :value="v.id">
                  {{ v.display }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Información del Transportista -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Información del Transportista</h6>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Nombre del Transportista</span>
              </label>
              <input
                type="text"
                id="carrier_name"
                v-model="guide.carrier_name"
                list="carrier-technicals-list"
                placeholder="Seleccione o escriba un nombre"
                autocomplete="off"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
              <datalist id="carrier-technicals-list">
                <option v-for="t in technicalOptions" :key="t.id" :value="t.fullName" />
              </datalist>
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Cédula del Transportista</span>
              </label>
              <input
                type="text"
                id="carrier_ci"
                v-model="guide.carrier_ci"
                placeholder="Número de identificación"
                maxlength="20"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Placa del Vehículo</span>
              </label>
              <input
                type="text"
                id="vehicle_plate"
                v-model="guide.vehicle_plate"
                placeholder="Ej: ABC-1234"
                maxlength="20"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>
          </div>
        </div>

        <!-- Despachador -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Despachador</h6>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Nombre del Despachador</span>
              </label>
              <input
                type="text"
                id="dispatcher_name"
                v-model="guide.dispatcher_name"
                placeholder="Nombre completo"
                disabled
                class="input input-bordered w-full bg-gray-100"
              />
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Cédula del Despachador</span>
              </label>
              <input
                type="text"
                id="dispatcher_ci"
                v-model="guide.dispatcher_ci"
                placeholder="Número de identificación"
                maxlength="20"
                disabled
                class="input input-bordered w-full bg-gray-100"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ Tab 2: Contacto y Costos ═══ -->
      <div v-show="activeTab === 'contacts'" class="space-y-3">
        <!-- Contacto en el Proyecto -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Contacto en el Proyecto</h6>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Nombre de Contacto</span>
              </label>
              <input
                type="text"
                id="contact_name"
                v-model="guide.contact_name"
                placeholder="Nombre completo"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Teléfono de Contacto</span>
              </label>
              <input
                type="text"
                id="contact_phone"
                v-model="guide.contact_phone"
                placeholder="Teléfono"
                maxlength="15"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>
          </div>
        </div>

        <!-- Recepción -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Recepción</h6>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Recibido Por</span>
              </label>
              <input
                type="text"
                id="recibed_by"
                v-model="guide.recibed_by"
                placeholder="Nombre de quien recibe"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Cédula de Quien Recibe</span>
              </label>
              <input
                type="text"
                id="recibed_ci"
                v-model="guide.recibed_ci"
                placeholder="Número de identificación"
                maxlength="20"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>
          </div>
        </div>

        <!-- Costos y Conceptos -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Costos y Conceptos</h6>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Costo del Transporte</span>
              </label>
              <input
                type="number"
                id="cost_transport"
                v-model.number="guide.cost_transport"
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
                id="sheet_project_logistics_concept"
                v-model="guide.sheet_project_logistics_concept"
                placeholder="Concepto logístico (opcional)"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Costo de Estiba</span>
              </label>
              <input
                type="number"
                id="cost_stowage"
                v-model.number="guide.cost_stowage"
                min="0"
                step="0.01"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control w-full">
              <label class="label py-1">
                <span class="label-text font-medium">Concepto de Estiba</span>
              </label>
              <input
                type="text"
                id="sheet_project_stowage_concept"
                v-model="guide.sheet_project_stowage_concept"
                placeholder="Concepto de estiba (opcional)"
                :disabled="!canEdit"
                class="input input-bordered w-full"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ Tab 3: Ítems y Notas ═══ -->
      <div v-show="activeTab === 'items'" class="space-y-3">
        <!-- Detalle de Ítems -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">
            Detalle de Ítems
            <span class="badge badge-sm badge-primary ml-2">{{ details.length }} ítems</span>
          </h6>

          <!-- Agregar desde recursos del proyecto -->
          <div v-if="canEdit" class="mb-3">
            <h6 class="text-sm font-semibold text-gray-600 mb-2">
              <i class="las la-toolbox text-teal-500"></i>
              Agregar desde Equipos del Proyecto
            </h6>
            <div class="overflow-x-auto max-h-48 border rounded border-gray-200">
              <table class="table table-sm table-zebra w-full">
                <thead class="sticky top-0">
                  <tr class="bg-gray-500 text-white">
                    <th class="border border-gray-300">#</th>
                    <th class="border border-gray-300">Equipo / Recurso</th>
                    <th class="border border-gray-300">Tipo</th>
                    <th class="border border-gray-300 text-right">Costo</th>
                    <th class="border border-gray-300 w-24 text-center">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(resource, idx) in availableResources" :key="resource.id" class="hover:bg-teal-50">
                    <td class="border border-gray-300">{{ idx + 1 }}</td>
                    <td class="border border-gray-300">{{ resource.resource_item_code }} / {{ resource.type_equipment_display || resource.resource_item_name }}</td>
                    <td class="border border-gray-300">
                      <span class="badge badge-sm badge-info">
                        {{ resource.type_equipment_display || resource.type_resource }}
                      </span>
                    </td>
                    <td class="border border-gray-300 text-right font-mono">${{ parseFloat(resource.cost || 0).toFixed(2) }}</td>
                    <td class="border border-gray-300 text-center">
                      <button
                        type="button"
                        class="btn btn-xs btn-primary"
                        @click="addResourceAsDetail(resource)"
                        title="Agregar a la guía"
                      >
                        <i class="las la-plus"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="availableResources.length === 0">
                    <td colspan="5" class="text-center py-4 text-gray-500">
                      No hay recursos asignados al proyecto
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Agregar ítem manual -->
          <div v-if="canEdit" class="mb-3 p-3 bg-gray-50 rounded border border-gray-200">
            <h6 class="text-sm font-semibold text-gray-600 mb-2">
              <i class="las la-pen text-teal-500"></i>
              Agregar Ítem Manual
            </h6>
            <div class="flex gap-2 items-end">
              <div class="form-control flex-1">
                <label class="label py-0">
                  <span class="label-text text-xs">Descripción</span>
                </label>
                <input
                  type="text"
                  v-model="newDetail.description"
                  placeholder="Descripción del ítem"
                  class="input input-bordered input-sm w-full"
                  @keyup.enter="addManualDetail"
                />
              </div>
              <div class="form-control w-24">
                <label class="label py-0">
                  <span class="label-text text-xs">Cantidad</span>
                </label>
                <input
                  type="number"
                  v-model.number="newDetail.quantity"
                  min="1"
                  class="input input-bordered input-sm w-full"
                />
              </div>
              <div class="form-control w-28">
                <label class="label py-0">
                  <span class="label-text text-xs">Unidad</span>
                </label>
                <input
                  type="text"
                  v-model="newDetail.unit"
                  placeholder="Ej: UND, KG, M3"
                  class="input input-bordered input-sm w-full"
                />
              </div>
              <button
                type="button"
                class="btn btn-sm btn-primary"
                @click="addManualDetail"
                :disabled="!newDetail.description.trim()"
              >
                <i class="las la-plus"></i>
                Agregar
              </button>
            </div>
          </div>

          <!-- Tabla de ítems agregados -->
          <div class="overflow-x-auto">
            <table class="table table-sm table-zebra w-full">
              <thead>
                <tr class="bg-teal-600 text-white">
                  <th class="border border-gray-300 w-10 text-center">#</th>
                  <th class="border border-gray-300">Descripción</th>
                  <th class="border border-gray-300 w-24 text-center">Cantidad</th>
                  <th class="border border-gray-300 w-28 text-right">Unidad</th>
                  <th v-if="canEdit" class="border border-gray-300 w-20 text-center">Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(detail, index) in details" :key="index" class="hover:bg-yellow-50">
                  <td class="border border-gray-300 text-center">{{ index + 1 }}</td>
                  <td class="border border-gray-300">
                    <input
                      type="text"
                      v-model="detail.description"
                      :disabled="!canEdit"
                      class="input input-bordered input-sm w-full"
                    />
                  </td>
                  <td class="border border-gray-300">
                    <input
                      type="number"
                      v-model.number="detail.quantity"
                      min="1"
                      :disabled="!canEdit"
                      class="input input-bordered input-sm w-full text-center"
                    />
                  </td>
                  <td class="border border-gray-300">
                    <input
                      type="text"
                      v-model="detail.unit"
                      placeholder="Ej: UND, KG, M3"
                      :disabled="!canEdit"
                      class="input input-bordered input-sm w-full"
                    />
                  </td>
                  <td v-if="canEdit" class="border border-gray-300 text-center">
                    <button
                      type="button"
                      class="btn btn-xs btn-error"
                      @click="removeDetail(index)"
                      title="Eliminar ítem"
                    >
                      <i class="las la-trash"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="details.length === 0">
                  <td colspan="5" class="text-center py-8 text-gray-500">
                    <i class="las la-inbox text-4xl"></i>
                    <p class="mt-2">No hay ítems agregados. Use los equipos del proyecto o agregue manualmente.</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Archivo PDF de la Guía -->
        <div v-if="isEditMode" class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">
            <i class="las la-file-pdf text-red-500"></i>
            Archivo PDF de la Guía
          </h6>

          <div v-if="shippingGuideFileUrl" class="flex items-center gap-3 mb-3 p-3 bg-green-50 border border-green-200 rounded-lg">
            <i class="las la-check-circle text-success text-2xl"></i>
            <span class="flex-1 text-sm">
              <strong>Archivo cargado:</strong> {{ shippingGuideFileName }}
            </span>
            <a :href="shippingGuideFileUrl" target="_blank" class="btn btn-sm btn-ghost text-blue-500" title="Ver PDF">
              <i class="las la-eye text-lg"></i> Ver
            </a>
            <button
              v-if="canEdit"
              type="button"
              class="btn btn-sm btn-ghost text-error"
              @click="deleteGuideFile"
              title="Eliminar archivo"
            >
              <i class="las la-trash text-lg"></i> Eliminar
            </button>
          </div>

          <div v-else class="flex items-center gap-3 mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <i class="las la-exclamation-circle text-warning text-2xl"></i>
            <span class="text-sm text-gray-600">No se ha cargado un archivo PDF para esta guía.</span>
          </div>

          <div v-if="canEdit" class="flex items-center gap-3">
            <input
              type="file"
              accept=".pdf,application/pdf"
              class="file-input file-input-bordered file-input-sm flex-1"
              @change="onFileChange"
              :disabled="uploadingFile"
            />
            <span v-if="uploadingFile" class="loading loading-spinner loading-sm text-primary"></span>
          </div>

          <div v-if="uploadFileMsg" class="mt-2 text-sm" :class="uploadFileMsgType === 'success' ? 'text-success' : 'text-error'">
            {{ uploadFileMsg }}
          </div>
        </div>

        <!-- Notas -->
        <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <h6 class="font-semibold text-sm mb-3 text-gray-700 border-b pb-1">Observaciones</h6>

          <div class="form-control w-full">
            <textarea
              id="notes"
              v-model="guide.notes"
              rows="3"
              placeholder="Observaciones o notas adicionales..."
              :disabled="!canEdit"
              class="textarea textarea-bordered w-full"
            ></textarea>
          </div>
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
          {{ isLoading ? 'Guardando...' : (isEditMode ? 'Actualizar Guía' : 'Guardar Guía') }}
        </button>
      </div>
    </form>
  </div>
</template>
