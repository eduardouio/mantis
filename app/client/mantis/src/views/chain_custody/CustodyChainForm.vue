<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { appConfig } from '@/AppConfig.js'
import { UseProjectStore } from '@/stores/ProjectStore'
import { UseTechnicalStore } from '@/stores/TechnicalStore'
import { UseVehicleStore } from '@/stores/VehicleStore'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
import { UseCustodyChainStore } from '@/stores/CustodyChainStore'
import Modal from '@/components/common/Modal.vue'
import TechnicalPresentation from '@/components/resources/TechnicalPresentation.vue'
import VehiclePresentation from '@/components/resources/VehiclePresentation.vue'
import { validateTechnical, validateVehicle } from '@/utils/validates.js'
import { fromGallons, fromBarrels, fromCubicMeters } from '@/utils/volumenConverter.js'

const projectStore = UseProjectStore()
const technicalStore = UseTechnicalStore()
const vehicleStore = UseVehicleStore()
const projectResourceStore = UseProjectResourceStore()
const custodyChainStore = UseCustodyChainStore()

const router = useRouter()
const route = useRoute()
const isLoading = ref(false)
const showTechnicalModal = ref(false)
const showVehicleModal = ref(false)

// Obtener el ID de la cadena de custodia desde la ruta (0 o undefined = crear, >0 = editar)
const custodyChainId = computed(() => {
  const id = parseInt(route.params.id)
  return isNaN(id) ? 0 : id
})

// Modo edición o creación
const isEditMode = computed(() => custodyChainId.value > 0)

const custodyChain = ref({
  technical: null,
  vehicle: null,
  sheet_project: null,
  consecutive: '',
  activity_date: new Date().toISOString().split('T')[0],
  location: '',
  issue_date: new Date().toISOString().split('T')[0],
  status: 'DRAFT',
  start_time: '',
  end_time: '',
  time_duration: 0,
  contact_name: '',
  dni_contact: '',
  contact_position: '',
  date_contact: new Date().toISOString().split('T')[0],
  driver_name: '',
  dni_driver: '',
  driver_position: '',
  driver_date: new Date().toISOString().split('T')[0],
  total_gallons: 0,
  total_barrels: 0,
  total_cubic_meters: 0,
  notes: '',
  technical_name: '',
  technical_dni: '',
  technical_position: '',
  vehicle_plate: '',
  vehicle_brand: '',
  vehicle_model: '',
  have_logistic: 'NA'
})

const selectedResourceIds = ref([])

// Estado original al cargar (para detectar si ya estaba cerrado)
const originalStatus = ref('DRAFT')

// Computed para verificar si la cadena está cerrada
const isChainClosed = computed(() => {
  return originalStatus.value === 'CLOSE'
})

// Computed para verificar si se puede editar
const canEdit = computed(() => {
  return !isChainClosed.value
})

const loadCustodyChainData = async () => {
  if (!isEditMode.value) return

  try {
    isLoading.value = true
    
    // Obtener los datos completos de la cadena desde la API
    const chainData = await custodyChainStore.fetchCustodyCapphainDetail(custodyChainId.value)
    
    if (chainData) {
      // Cargar datos de la cadena desde la respuesta de la API
      const chain = chainData.custody_chain
      const technical = chainData.technical
      const vehicle = chainData.vehicle
      const details = chainData.details || []
      
      // Guardar el estado original
      originalStatus.value = chain.status || 'DRAFT'
      
      custodyChain.value = {
        technical: technical?.id || null,
        vehicle: vehicle?.id || null,
        sheet_project: chain.sheet_project_id,
        consecutive: chain.consecutive,
        activity_date: chain.activity_date,
        location: chain.location,
        issue_date: chain.issue_date || new Date().toISOString().split('T')[0],
        status: chain.status || 'DRAFT',
        start_time: chain.start_time || '',
        end_time: chain.end_time || '',
        time_duration: chain.time_duration || 0,
        contact_name: chain.contact_name || '',
        dni_contact: chain.dni_contact || '',
        contact_position: chain.contact_position || '',
        date_contact: chain.date_contact || new Date().toISOString().split('T')[0],
        driver_name: chain.driver_name || '',
        dni_driver: chain.dni_driver || '',
        driver_position: chain.driver_position || '',
        driver_date: chain.driver_date || new Date().toISOString().split('T')[0],
        total_gallons: chain.total_gallons || 0,
        total_barrels: chain.total_barrels || 0,
        total_cubic_meters: chain.total_cubic_meters || 0,
        notes: chain.meta?.notes || '',
        technical_name: technical ? `${technical.first_name} ${technical.last_name}` : '',
        technical_dni: technical?.dni || '',
        technical_position: technical?.work_area_display || technical?.work_area || '',
        vehicle_plate: vehicle?.no_plate || '',
        vehicle_brand: vehicle?.brand || '',
        vehicle_model: vehicle?.model || '',
        have_logistic: chain.have_logistic || 'NA'
      }
      
      // Cargar IDs de recursos seleccionados
      if (details.length > 0) {
        selectedResourceIds.value = details.map(d => d.project_resource.id)
      }
    } else {
      console.warn('Cadena de custodia no encontrada')
      router.push({ name: 'projects-detail' })
    }
  } catch (error) {
    console.error('Error al cargar cadena de custodia:', error)
    alert('Error al cargar los datos de la cadena de custodia: ' + error.message)
    router.push({ name: 'projects-detail' })
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await projectStore.fetchProjectData()
  await technicalStore.fetchTechnicalsAvailable()
  await vehicleStore.fetchVehicles()
  await projectResourceStore.fetchResourcesProject()
  
  if (isEditMode.value) {
    await loadCustodyChainData()
  } else {
    // Modo creación: inicializar con datos del proyecto
    custodyChain.value.location = projectStore.project?.location || ''
    custodyChain.value.contact_name = projectStore.project?.contact_name || ''
  }
})

const availableResources = computed(() => {
  return projectResourceStore.resourcesProject
    .filter(resource => resource.type_resource === 'SERVICIO')
    .map(resource => ({
      ...resource,
      selected: selectedResourceIds.value.includes(resource.id)
    }))
})

const selectedResources = computed(() => {
  return availableResources.value.filter(r => r.selected)
})

const technicals = computed(() => {
  return technicalStore.technicals.map(tech => ({
    id: tech.id,
    display: `${tech.first_name} ${tech.last_name}`,
    fullData: tech
  }))
})

const vehicles = computed(() => {
  return vehicleStore.vehicles.map(vehicle => ({
    id: vehicle.id,
    display: `${vehicle.no_plate} - ${vehicle.brand} ${vehicle.model}`,
    fullData: vehicle
  }))
})

const toggleResourceSelection = (resourceId) => {
  const index = selectedResourceIds.value.indexOf(resourceId)
  if (index > -1) {
    selectedResourceIds.value.splice(index, 1)
  } else {
    selectedResourceIds.value.push(resourceId)
  }
}

const calculateDuration = () => {
  if (custodyChain.value.start_time && custodyChain.value.end_time) {
    const start = custodyChain.value.start_time.split(':')
    const end = custodyChain.value.end_time.split(':')
    
    const startMinutes = parseInt(start[0]) * 60 + parseInt(start[1])
    const endMinutes = parseInt(end[0]) * 60 + parseInt(end[1])
    
    const duration = endMinutes - startMinutes
    custodyChain.value.time_duration = duration > 0 ? duration : 0
  }
}

const submitForm = async () => {
  try {
    isLoading.value = true
    
    if (!custodyChain.value.technical || !custodyChain.value.vehicle || selectedResources.value.length === 0) {
      alert('Por favor complete los campos requeridos y seleccione al menos un recurso')
      return
    }

    const payload = {
      custody_chain: {
        technical_id: custodyChain.value.technical,
        vehicle_id: custodyChain.value.vehicle,
        activity_date: custodyChain.value.activity_date,
        issue_date: custodyChain.value.issue_date,
        consecutive: custodyChain.value.consecutive,
        status: custodyChain.value.status,
        location: custodyChain.value.location,
        start_time: custodyChain.value.start_time,
        end_time: custodyChain.value.end_time,
        time_duration: custodyChain.value.time_duration,
        contact_name: custodyChain.value.contact_name,
        dni_contact: custodyChain.value.dni_contact,
        contact_position: custodyChain.value.contact_position,
        date_contact: custodyChain.value.date_contact,
        driver_name: custodyChain.value.driver_name,
        dni_driver: custodyChain.value.dni_driver,
        driver_position: custodyChain.value.driver_position,
        driver_date: custodyChain.value.driver_date,
        total_gallons: parseFloat(custodyChain.value.total_gallons) || 0,
        total_barrels: parseFloat(custodyChain.value.total_barrels) || 0,
        total_cubic_meters: parseFloat(custodyChain.value.total_cubic_meters) || 0,
        have_logistic: custodyChain.value.have_logistic,
        meta: {
          notes: custodyChain.value.notes,
          id_user_updated: appConfig.userId || 1
        }
      },
      details: selectedResourceIds.value.map(resourceId => ({
        project_resource_id: resourceId
      }))
    }

    if (isEditMode.value) {
      const result = await custodyChainStore.updateCustodyChain(custodyChainId.value, payload)
      
      if (result) {
        await projectStore.fetchProjectData()
        
        const workOrder = projectStore.workOrders.find(wo => wo.status === 'IN_PROGRESS')
        if (workOrder) {
          router.push({ name: 'sheet-project-view', params: { id: workOrder.id } })
        } else {
          router.push({ name: 'projects-detail' })
        }
      }
    } else {
      const createPayload = {
        technical_id: custodyChain.value.technical,
        vehicle_id: custodyChain.value.vehicle,
        project_id: appConfig.idProject,
        activity_date: custodyChain.value.activity_date,
        issue_date: custodyChain.value.issue_date,
        consecutive: custodyChain.value.consecutive,
        location: custodyChain.value.location,
        start_time: custodyChain.value.start_time,
        end_time: custodyChain.value.end_time,
        duration_hours: custodyChain.value.time_duration,
        contact_name: custodyChain.value.contact_name,
        dni_contact: custodyChain.value.dni_contact,
        contact_position: custodyChain.value.contact_position,
        date_contact: custodyChain.value.date_contact,
        driver_name: custodyChain.value.driver_name,
        dni_driver: custodyChain.value.dni_driver,
        driver_position: custodyChain.value.driver_position,
        driver_date: custodyChain.value.driver_date,
        technical_name: custodyChain.value.technical_name,
        technical_dni: custodyChain.value.technical_dni,
        technical_position: custodyChain.value.technical_position,
        vehicle_plate: custodyChain.value.vehicle_plate,
        vehicle_brand: custodyChain.value.vehicle_brand,
        vehicle_model: custodyChain.value.vehicle_model,
        total_gallons: parseFloat(custodyChain.value.total_gallons) || 0,
        total_barrels: parseFloat(custodyChain.value.total_barrels) || 0,
        total_cubic_meters: parseFloat(custodyChain.value.total_cubic_meters) || 0,
        have_logistic: custodyChain.value.have_logistic,
        notes: custodyChain.value.notes,
        resources: selectedResourceIds.value
      }
      
      const result = await custodyChainStore.addCustodyChain(createPayload)
      
      if (result) {
        await projectStore.fetchProjectData()
        
        const workOrder = projectStore.workOrders.find(wo => wo.status === 'IN_PROGRESS')
        if (workOrder) {
          router.push({ name: 'sheet-project-view', params: { id: workOrder.id } })
        } else {
          router.push({ name: 'projects-detail' })
        }
      }
    }
  } catch (error) {
    console.error('Error al guardar:', error)
    alert('Error al ' + (isEditMode.value ? 'actualizar' : 'guardar') + ' la cadena de custodia: ' + error.message)
  } finally {
    isLoading.value = false
  }
}

const openTechnicalModal = () => {
  if (selectedTechnicalData.value) {
    showTechnicalModal.value = true
  }
}

const openVehicleModal = () => {
  if (selectedVehicleData.value) {
    showVehicleModal.value = true
  }
}

const cancelForm = () => {
  // Volver a la vista de la planilla
  const workOrder = projectStore.workOrders.find(wo => wo.status === 'IN_PROGRESS')
  if (workOrder) {
    router.push({ name: 'sheet-project-view', params: { id: workOrder.id } })
  } else {
    router.push({ name: 'projects-detail' })
  }
}

watch(() => projectStore.project?.location, (newLocation) => {
  if (newLocation && !custodyChain.value.location && !isEditMode.value) {
    custodyChain.value.location = newLocation
  }
})

watch(() => projectStore.project?.contact_name, (newContact) => {
  if (newContact && !custodyChain.value.contact_name && !isEditMode.value) {
    custodyChain.value.contact_name = newContact
  }
})

const selectedTechnicalData = computed(() => {
  if (!custodyChain.value.technical) return null
  return technicalStore.technicals.find(t => t.id === custodyChain.value.technical)
})

const selectedVehicleData = computed(() => {
  if (!custodyChain.value.vehicle) return null
  return vehicleStore.vehicles.find(v => v.id === custodyChain.value.vehicle)
})

const technicalValidation = computed(() => {
  return validateTechnical(selectedTechnicalData.value)
})

const vehicleValidation = computed(() => {
  return validateVehicle(selectedVehicleData.value)
})

const hasValidationIssues = computed(() => {
  return technicalValidation.value.hasErrors || 
         technicalValidation.value.hasWarnings ||
         vehicleValidation.value.hasErrors || 
         vehicleValidation.value.hasWarnings
})

const timeValidation = computed(() => {
  if (!custodyChain.value.start_time || !custodyChain.value.end_time) {
    return { isValid: true, message: '' }
  }
  
  const start = custodyChain.value.start_time.split(':')
  const end = custodyChain.value.end_time.split(':')
  
  const startMinutes = parseInt(start[0]) * 60 + parseInt(start[1])
  const endMinutes = parseInt(end[0]) * 60 + parseInt(end[1])
  
  if (endMinutes <= startMinutes) {
    return {
      isValid: false,
      message: 'La hora de fin debe ser mayor que la hora de inicio'
    }
  }
  
  return { isValid: true, message: '' }
})

watch(() => custodyChain.value.start_time, () => {
  calculateDuration()
})

watch(() => custodyChain.value.end_time, () => {
  calculateDuration()
})

watch(() => custodyChain.value.technical, (newTechnicalId) => {
  if (newTechnicalId && !isEditMode.value) {
    const selectedTech = technicalStore.technicals.find(t => t.id === newTechnicalId)
    if (selectedTech) {
      custodyChain.value.technical_name = `${selectedTech.first_name} ${selectedTech.last_name}`
      custodyChain.value.technical_dni = selectedTech.dni
      custodyChain.value.technical_position = selectedTech.work_area_display || selectedTech.work_area
      
      custodyChain.value.driver_name = `${selectedTech.first_name} ${selectedTech.last_name}`
      custodyChain.value.dni_driver = selectedTech.dni
      custodyChain.value.driver_position = selectedTech.work_area_display || selectedTech.work_area
      custodyChain.value.driver_date = new Date().toISOString().split('T')[0]
    }
  }
})

watch(() => custodyChain.value.vehicle, (newVehicleId) => {
  if (newVehicleId && !isEditMode.value) {
    const selectedVehicle = vehicleStore.vehicles.find(v => v.id === newVehicleId)
    if (selectedVehicle) {
      custodyChain.value.vehicle_plate = selectedVehicle.no_plate
      custodyChain.value.vehicle_brand = selectedVehicle.brand
      custodyChain.value.vehicle_model = selectedVehicle.model
    }
  }
})

const lastEditedVolumeField = ref(null)

watch(() => custodyChain.value.total_gallons, (newValue, oldValue) => {
  if (lastEditedVolumeField.value === 'gallons' && newValue !== oldValue) {
    const converted = fromGallons(newValue)
    lastEditedVolumeField.value = null
    custodyChain.value.total_barrels = converted.barrels
    custodyChain.value.total_cubic_meters = converted.cubicMeters
  }
})

watch(() => custodyChain.value.total_barrels, (newValue, oldValue) => {
  if (lastEditedVolumeField.value === 'barrels' && newValue !== oldValue) {
    const converted = fromBarrels(newValue)
    lastEditedVolumeField.value = null
    custodyChain.value.total_gallons = converted.gallons
    custodyChain.value.total_cubic_meters = converted.cubicMeters
  }
})

watch(() => custodyChain.value.total_cubic_meters, (newValue, oldValue) => {
  if (lastEditedVolumeField.value === 'cubicMeters' && newValue !== oldValue) {
    const converted = fromCubicMeters(newValue)
    lastEditedVolumeField.value = null
    custodyChain.value.total_gallons = converted.gallons
    custodyChain.value.total_barrels = converted.barrels
  }
})

const handleGallonsInput = () => {
  lastEditedVolumeField.value = 'gallons'
}

const handleBarrelsInput = () => {
  lastEditedVolumeField.value = 'barrels'
}

const handleCubicMetersInput = () => {
  lastEditedVolumeField.value = 'cubicMeters'
}

const statusOptions = computed(() => [
  { value: 'DRAFT', label: 'BORRADOR', class: 'badge-warning' },
  { value: 'CLOSE', label: 'CERRADO', class: 'badge-success' }
])

const currentStatusBadge = computed(() => {
  return statusOptions.value.find(opt => opt.value === custodyChain.value.status) || statusOptions.value[0]
})
</script>

<template>
  <div class="max-w-7xl mx-auto p-4">
    <!-- Título dinámico según modo -->
    <div class="bg-white rounded-lg p-4 mb-4 border border-gray-200 shadow-sm">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-xl font-semibold text-gray-800">
            <i class="las la-link text-blue-600"></i>
            {{ isEditMode ? `${isChainClosed ? 'Ver' : 'Editar'} Cadena de Custodia #${custodyChainId}` : 'Nueva Cadena de Custodia' }}
          </h2>
          <p class="text-sm text-gray-600 mt-1">
            {{ isChainClosed ? 'Esta cadena de custodia está cerrada y no puede ser modificada' : (isEditMode ? 'Modifique los datos de la cadena de custodia' : 'Complete los datos para crear una nueva cadena de custodia') }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <!-- Selector de Estado -->
          <div class="form-control">
            <label class="label py-0 mb-1">
              <span class="label-text font-semibold text-xs">Estado</span>
            </label>
            <select 
              v-model="custodyChain.status"
              :disabled="isChainClosed"
              class="select select-bordered select-sm"
              :class="{
                'select-warning': custodyChain.status === 'DRAFT',
                'select-success': custodyChain.status === 'CLOSE'
              }"
            >
              <option 
                v-for="option in statusOptions" 
                :key="option.value" 
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <!-- Badge de Estado Visual -->
          <div class="flex flex-col items-center">
            <span class="text-xs text-gray-500 mb-1">Estado Actual</span>
            <span class="badge badge-lg" :class="currentStatusBadge.class">
              <i class="las mr-1" :class="{
                'la-edit': custodyChain.status === 'DRAFT',
                'la-lock': custodyChain.status === 'CLOSE'
              }"></i>
              {{ currentStatusBadge.label }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Mensaje informativo sobre el estado -->
      <div v-if="isEditMode" class="mt-3 pt-3 border-t border-gray-200">
        <div v-if="!isChainClosed && custodyChain.status === 'DRAFT'" class="flex items-center gap-2 text-sm text-amber-600">
          <i class="las la-info-circle text-lg"></i>
          <span>La cadena de custodia está en estado <strong>BORRADOR</strong> y puede ser modificada libremente.</span>
        </div>
        <div v-else-if="isChainClosed" class="flex items-center gap-2 text-sm text-red-600">
          <i class="las la-lock text-lg"></i>
          <span>La cadena de custodia está <strong>CERRADA</strong>. No se pueden realizar modificaciones.</span>
        </div>
        <div v-else class="flex items-center gap-2 text-sm text-green-600">
          <i class="las la-check-circle text-lg"></i>
          <span>Al guardar con estado <strong>CERRADO</strong>, no se podrán realizar más modificaciones.</span>
        </div>
      </div>
    </div>

    <!-- Alertas de Validación -->
    <div v-if="hasValidationIssues" class="mb-6 space-y-3">
      <!-- Alertas del Técnico -->
      <div v-if="technicalValidation.hasErrors" class="alert alert-error shadow-lg">
        <div class="flex items-start w-full">
          <i class="las la-exclamation-circle text-2xl"></i>
          <div class="flex-1">
            <h3 class="font-bold">Problemas críticos con el técnico seleccionado</h3>
            <ul class="text-sm mt-2 space-y-1">
              <li v-for="(issue, idx) in technicalValidation.issues.filter(i => i.type === 'error')" :key="idx">
                <strong>{{ issue.field }}:</strong> {{ issue.message }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="technicalValidation.hasWarnings && !technicalValidation.hasErrors" class="alert alert-warning shadow-lg">
        <div class="flex items-start w-full">
          <i class="las la-exclamation-triangle text-2xl"></i>
          <div class="flex-1">
            <h3 class="font-bold">Advertencias del técnico seleccionado</h3>
            <ul class="text-sm mt-2 space-y-1">
              <li v-for="(issue, idx) in technicalValidation.issues.filter(i => i.type === 'warning')" :key="idx">
                <strong>{{ issue.field }}:</strong> {{ issue.message }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Alertas del Vehículo -->
      <div v-if="vehicleValidation.hasErrors" class="alert alert-error shadow-lg">
        <div class="flex items-start w-full">
          <i class="las la-exclamation-circle text-2xl"></i>
          <div class="flex-1">
            <h3 class="font-bold">Problemas críticos con el vehículo seleccionado</h3>
            <ul class="text-sm mt-2 space-y-1">
              <li v-for="(issue, idx) in vehicleValidation.issues.filter(i => i.type === 'error')" :key="idx">
                <strong>{{ issue.field }}:</strong> {{ issue.message }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="vehicleValidation.hasWarnings && !vehicleValidation.hasErrors" class="alert alert-warning shadow-lg">
        <div class="flex items-start w-full">
          <i class="las la-exclamation-triangle text-2xl"></i>
          <div class="flex-1">
            <h3 class="font-bold">Advertencias del vehículo seleccionado</h3>
            <ul class="text-sm mt-2 space-y-1">
              <li v-for="(issue, idx) in vehicleValidation.issues.filter(i => i.type === 'warning')" :key="idx">
                <strong>{{ issue.field }}:</strong> {{ issue.message }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Información General -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Información General</h6>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Técnico -->
          <div class="form-control w-full">
            <label class="label" for="technical">
              <span class="label-text font-medium">
                Técnico *
                <span v-if="technicalValidation.hasErrors" class="badge badge-error badge-sm ml-1">
                  <i class="las la-exclamation-circle"></i>
                </span>
                <span v-else-if="technicalValidation.hasWarnings" class="badge badge-warning badge-sm ml-1">
                  <i class="las la-exclamation-triangle"></i>
                </span>
              </span>
            </label>
            <div class="flex gap-2">
              <select 
                id="technical"
                v-model.number="custodyChain.technical"
                :disabled="isChainClosed"
                required
                class="select select-bordered w-full flex-1"
                :class="{ 'select-error': technicalValidation.hasErrors, 'select-warning': technicalValidation.hasWarnings && !technicalValidation.hasErrors }"
              >
                <option :value="null" disabled>Seleccione un técnico</option>
                <option v-for="tech in technicals" :key="tech.id" :value="tech.id">
                  {{ tech.display }}
                </option>
              </select>
              <button
                v-if="selectedTechnicalData"
                type="button"
                class="btn btn-outline btn-square"
                @click="openTechnicalModal"
                title="Ver detalles del técnico"
              >
                <i class="las la-eye text-lg"></i>
              </button>
            </div>
          </div>

          <!-- Vehículo -->
          <div class="form-control w-full">
            <label class="label" for="vehicle">
              <span class="label-text font-medium">
                Vehículo *
                <span v-if="vehicleValidation.hasErrors" class="badge badge-error badge-sm ml-1">
                  <i class="las la-exclamation-circle"></i>
                </span>
                <span v-else-if="vehicleValidation.hasWarnings" class="badge badge-warning badge-sm ml-1">
                  <i class="las la-exclamation-triangle"></i>
                </span>
              </span>
            </label>
            <div class="flex gap-2">
              <select 
                id="vehicle"
                v-model.number="custodyChain.vehicle"
                :disabled="isChainClosed"
                required
                class="select select-bordered w-full flex-1"
                :class="{ 'select-error': vehicleValidation.hasErrors, 'select-warning': vehicleValidation.hasWarnings && !vehicleValidation.hasErrors }"
              >
                <option :value="null" disabled>Seleccione un vehículo</option>
                <option v-for="vehicle in vehicles" :key="vehicle.id" :value="vehicle.id">
                  {{ vehicle.display }}
                </option>
              </select>
              <button
                v-if="selectedVehicleData"
                type="button"
                class="btn btn-outline btn-square"
                @click="openVehicleModal"
                title="Ver detalles del vehículo"
              >
                <i class="las la-eye text-lg"></i>
              </button>
            </div>
          </div>

          <!-- Consecutivo -->
          <div class="form-control w-full">
            <label class="label" for="consecutive">
              <span class="label-text font-medium">Consecutivo</span>
            </label>
            <input 
              type="text"
              id="consecutive"
              v-model="custodyChain.consecutive"
              readonly
              placeholder="Se generará automáticamente"
              class="input input-bordered w-full bg-gray-100"
            />
          </div>

          <!-- Fecha de Actividad -->
          <div class="form-control w-full">
            <label class="label" for="activity_date">
              <span class="label-text font-medium">Fecha de Actividad *</span>
            </label>
            <input 
              type="date"
              id="activity_date"
              v-model="custodyChain.activity_date"
              :disabled="isChainClosed"
              required
              class="input input-bordered w-full"
            />
          </div>

          <!-- Ubicación -->
          <div class="form-control w-full">
            <label class="label" for="location">
              <span class="label-text font-medium">Ubicación</span>
            </label>
            <input 
              type="text"
              id="location"
              v-model="custodyChain.location"
              :disabled="isChainClosed"
              placeholder="Ej: Bloque 31"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Fecha de Emisión -->
          <div class="form-control w-full">
            <label class="label" for="issue_date">
              <span class="label-text font-medium">Fecha de Emisión</span>
            </label>
            <input 
              type="date"
              id="issue_date"
              v-model="custodyChain.issue_date"
              :disabled="isChainClosed"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Hora de Inicio -->
          <div class="form-control w-full">
            <label class="label" for="start_time">
              <span class="label-text font-medium">Hora de Inicio</span>
            </label>
            <input 
              type="time"
              id="start_time"
              v-model="custodyChain.start_time"
              :disabled="isChainClosed"
              class="input input-bordered w-full"
              :class="{ 'input-error': !timeValidation.isValid }"
            />
          </div>

          <!-- Hora de Fin -->
          <div class="form-control w-full">
            <label class="label" for="end_time">
              <span class="label-text font-medium">Hora de Fin</span>
            </label>
            <input 
              type="time"
              id="end_time"
              v-model="custodyChain.end_time"
              :disabled="isChainClosed"
              class="input input-bordered w-full"
              :class="{ 'input-error': !timeValidation.isValid }"
            />
            <label v-if="!timeValidation.isValid" class="label">
              <span class="label-text-alt text-error">
                <i class="las la-exclamation-circle"></i>
                {{ timeValidation.message }}
              </span>
            </label>
          </div>

          <!-- Duración -->
          <div class="form-control w-full">
            <label class="label" for="time_duration">
              <span class="label-text font-medium">Duración (Minutos)</span>
            </label>
            <input 
              type="number"
              id="time_duration"
              v-model="custodyChain.time_duration"
              step="0.01"
              readonly
              class="input input-bordered w-full bg-gray-100"
            />
          </div>

          <!-- Logística -->
          <div class="form-control w-full">
            <label class="label" for="have_logistic">
              <span class="label-text font-medium">¿Tiene Logística? *</span>
            </label>
            <select 
              id="have_logistic"
              v-model="custodyChain.have_logistic"
              :disabled="isChainClosed"
              required
              class="select select-bordered w-full"
            >
              <option value="SI">SÍ</option>
              <option value="NO">NO</option>
              <option value="NA">NO APLICA</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Información del Transportista -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Información del Transportista</h6>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label" for="driver_name">
              <span class="label-text font-medium">Nombre de Transportista</span>
            </label>
            <input 
              type="text"
              id="driver_name"
              v-model="custodyChain.driver_name"
              :disabled="isChainClosed"
              placeholder="Nombre completo"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="dni_driver">
              <span class="label-text font-medium">Cédula de Transportista</span>
            </label>
            <input 
              type="text"
              id="dni_driver"
              v-model="custodyChain.dni_driver"
              :disabled="isChainClosed"
              placeholder="Número de identificación"
              maxlength="15"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="driver_position">
              <span class="label-text font-medium">Cargo de Transportista</span>
            </label>
            <input 
              type="text"
              id="driver_position"
              v-model="custodyChain.driver_position"
              :disabled="isChainClosed"
              placeholder="Ej: Conductor"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="driver_date">
              <span class="label-text font-medium">Fecha de Transportista</span>
            </label>
            <input 
              type="date"
              id="driver_date"
              v-model="custodyChain.driver_date"
              :disabled="isChainClosed"
              class="input input-bordered w-full"
            />
          </div>
        </div>
      </div>

      <!-- Información de Contacto -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Información de Contacto</h6>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label" for="contact_name">
              <span class="label-text font-medium">Nombre de Contacto</span>
            </label>
            <input 
              type="text"
              id="contact_name"
              v-model="custodyChain.contact_name"
              :disabled="isChainClosed"
              placeholder="Nombre completo"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="dni_contact">
              <span class="label-text font-medium">Cédula de Contacto</span>
            </label>
            <input 
              type="text"
              id="dni_contact"
              v-model="custodyChain.dni_contact"
              :disabled="isChainClosed"
              placeholder="Número de identificación"
              maxlength="15"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="contact_position">
              <span class="label-text font-medium">Cargo de Contacto</span>
            </label>
            <input 
              type="text"
              id="contact_position"
              v-model="custodyChain.contact_position"
              :disabled="isChainClosed"
              placeholder="Ej: Maquinista"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="date_contact">
              <span class="label-text font-medium">Fecha de Contacto</span>
            </label>
            <input 
              type="date"
              id="date_contact"
              v-model="custodyChain.date_contact"
              :disabled="isChainClosed"
              class="input input-bordered w-full"
            />
          </div>
        </div>
      </div>

      <!-- Recursos del Proyecto -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">
          Recursos del Proyecto
          <span class="badge badge-primary ml-2">{{ selectedResources.length }} seleccionados</span>
        </h6>
        
        <div class="overflow-x-auto">
          <table class="table table-zebra w-full table-sm">
            <thead>
              <tr class="bg-gray-500 text-white">
                <th class="border border-gray-300 w-16 text-center">
                  <input type="checkbox" class="checkbox checkbox-sm" :disabled="isChainClosed" />
                </th>
                <th class="border border-gray-300">#</th>
                <th class="border border-gray-300">Código</th>
                <th class="border border-gray-300">Descripción</th>
                <th class="border border-gray-300 text-right">Costo</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(resource, index) in availableResources" 
                :key="resource.id"
                :class="{ 
                  'bg-blue-100': resource.selected,
                  'cursor-pointer hover:bg-blue-50': !isChainClosed,
                  'opacity-60': isChainClosed
                }"
                @click="!isChainClosed && toggleResourceSelection(resource.id)"
              >
                <td class="border border-gray-300 text-center">
                  <input 
                    type="checkbox" 
                    class="checkbox checkbox-sm checkbox-primary"
                    :checked="resource.selected"
                    :disabled="isChainClosed"
                    @click.stop="!isChainClosed && toggleResourceSelection(resource.id)"
                  />
                </td>
                <td class="border border-gray-300">{{ index + 1 }}</td>
                <td class="border border-gray-300">{{ resource.resource_item_code }}</td>
                <td class="border border-gray-300">{{ resource.detailed_description }}</td>
                <td class="border border-gray-300 text-right font-mono">${{ resource.cost }}</td>
              </tr>
              <tr v-if="availableResources.length === 0">
                <td colspan="5" class="text-center text-gray-500 py-8">
                  <i class="las la-inbox text-4xl"></i>
                  <p>No hay recursos disponibles</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Totales -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">
          Totales
          <span class="text-xs text-gray-500 ml-2">(Los valores se convierten automáticamente)</span>
        </h6>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-control w-full">
            <label class="label" for="total_gallons">
              <span class="label-text font-medium">Total Galones</span>
            </label>
            <input 
              type="number"
              id="total_gallons"
              v-model.number="custodyChain.total_gallons"
              @input="handleGallonsInput"
              :disabled="isChainClosed"
              min="0"
              step="0.0001"
              class="input input-bordered w-full"
              placeholder="0.0000"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="total_barrels">
              <span class="label-text font-medium">Total Barriles</span>
            </label>
            <input 
              type="number"
              id="total_barrels"
              v-model.number="custodyChain.total_barrels"
              @input="handleBarrelsInput"
              :disabled="isChainClosed"
              min="0"
              step="0.0001"
              class="input input-bordered w-full"
              placeholder="0.0000"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="total_cubic_meters">
              <span class="label-text font-medium">Total Metros Cúbicos</span>
            </label>
            <input 
              type="number"
              id="total_cubic_meters"
              v-model.number="custodyChain.total_cubic_meters"
              @input="handleCubicMetersInput"
              :disabled="isChainClosed"
              min="0"
              step="0.0001"
              class="input input-bordered w-full"
              placeholder="0.0000"
            />
          </div>
        </div>
      </div>

      <!-- Notas -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Notas</h6>
        
        <div class="form-control w-full">
          <textarea 
            id="notes"
            v-model="custodyChain.notes"
            :disabled="isChainClosed"
            rows="4"
            placeholder="Observaciones o notas adicionales..."
            class="textarea textarea-bordered w-full"
          ></textarea>
        </div>
      </div>

      <!-- Botones -->
      <div class="flex gap-3 justify-end mt-6">
        <button type="button" class="btn btn-outline" @click="cancelForm" :disabled="isLoading">
          <i class="las la-times"></i>
          {{ isChainClosed ? 'Cerrar' : 'Cancelar' }}
        </button>
        <button 
          v-if="!isChainClosed"
          type="submit" 
          class="btn btn-primary" 
          :disabled="isLoading"
        >
          <i v-if="!isLoading" class="las la-save"></i>
          <i v-else class="las la-spinner animate-spin"></i>
          {{ isLoading ? 'Guardando...' : (isEditMode ? 'Actualizar Cadena de Custodia' : 'Guardar Cadena de Custodia') }}
        </button>
      </div>
    </form>

    <!-- Modal de Técnico -->
    <Modal 
      :is-open="showTechnicalModal" 
      :title="`Detalles del Técnico - ${selectedTechnicalData?.first_name} ${selectedTechnicalData?.last_name}`"
      size="xl"
      @close="showTechnicalModal = false"
    >
      <TechnicalPresentation v-if="selectedTechnicalData" :technical="selectedTechnicalData" />
    </Modal>

    <!-- Modal de Vehículo -->
    <Modal 
      :is-open="showVehicleModal" 
      :title="`Detalles del Vehículo - ${selectedVehicleData?.no_plate}`"
      size="xl"
      @close="showVehicleModal = false"
    >
      <VehiclePresentation v-if="selectedVehicleData" :vehicle="selectedVehicleData" />
    </Modal>
  </div>
</template>
