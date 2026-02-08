<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
import { UseResourcesStore } from '@/stores/ResourcesStore'
import { UseProjectStore } from '@/stores/ProjectStore'
import AutocompleteResource from '@/components/resources/AutocompleteResource.vue'

const props = defineProps({
  resource: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const projectResourceStore = UseProjectResourceStore()
const resourcesStore = UseResourcesStore()
const projectStore = UseProjectStore()

const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showReleaseConfirm = ref(false)
const releaseReason = ref('')
const isReleasing = ref(false)

const frequencyTypes = [
  { value: 'DAY', label: 'Por intervalo de días' },
  { value: 'WEEK', label: 'Días de la semana' },
  { value: 'MONTH', label: 'Días del mes' }
]

const weekdayOptions = [
  { value: 0, label: 'Lunes' },
  { value: 1, label: 'Martes' },
  { value: 2, label: 'Miércoles' },
  { value: 3, label: 'Jueves' },
  { value: 4, label: 'Viernes' },
  { value: 5, label: 'Sábado' },
  { value: 6, label: 'Domingo' }
]

const formData = ref({
  id: null,
  resource_id: null,
  resource_display_name: '',
  detailed_description: '',
  type_resource: 'SERVICIO',
  cost: 0,
  frequency_type: 'MONTH',
  interval_days: 3,
  weekdays: [],
  monthdays: [],
  maintenance_cost: 0,
  operation_start_date: null,
  operation_end_date: null,
  is_retired: false
})

const isEditMode = computed(() => !!props.resource)
const isService = computed(() => formData.value.type_resource === 'SERVICIO')
const isRental = computed(() => formData.value.type_resource === 'EQUIPO' && parseFloat(formData.value.cost) > 0)

// Opciones de frecuencia disponibles según el tipo de recurso
const availableFrequencyTypes = computed(() => {
  // Si es un recurso de alquiler (EQUIPO con costo > 0), solo mostrar "Días del mes"
  if (isRental.value) {
    return frequencyTypes.filter(ft => ft.value === 'MONTH')
  }
  // Para servicios y equipos sin costo, mostrar todas las opciones
  return frequencyTypes
})

const selectedResourceIds = computed(() => {
  if (isEditMode.value) {
    return projectResourceStore.resources
      .filter(r => r.id !== props.resource?.id && r.type_resource === 'EQUIPO')
      .map(r => r.resource_id)
  }
  return projectResourceStore.resources
    .filter(r => r.type_resource === 'EQUIPO')
    .map(r => r.resource_id)
})

watch(() => props.resource, (newResource) => {
  if (newResource) {
    formData.value = {
      id: newResource.id,
      resource_id: newResource.resource_id,
      resource_display_name: newResource.resource_display_name || newResource.detailed_description,
      detailed_description: newResource.detailed_description,
      type_resource: newResource.type_resource,
      cost: newResource.cost || 0,
      frequency_type: newResource.frequency_type || 'MONTH',
      interval_days: newResource.interval_days || 3,
      weekdays: newResource.weekdays || [],
      monthdays: newResource.monthdays || [],
      maintenance_cost: newResource.maintenance_cost || 0,
      operation_start_date: newResource.operation_start_date,
      operation_end_date: newResource.operation_end_date,
      is_retired: newResource.is_retired || false
    }
  }
}, { immediate: true })

// Watch para cambiar automáticamente a MONTH si es recurso de alquiler
watch(() => formData.value.cost, (newCost) => {
  const cost = parseFloat(newCost)
  // Si es un equipo y tiene costo (es alquiler), cambiar a MONTH automáticamente
  if (formData.value.type_resource === 'EQUIPO' && cost > 0) {
    if (formData.value.frequency_type !== 'MONTH') {
      formData.value.frequency_type = 'MONTH'
      formData.value.interval_days = 0
      formData.value.weekdays = []
    }
  }
})

const handleResourceSelected = () => {
  const resource = resourcesStore.selectedResource
  if (resource) {
    formData.value.resource_id = resource.id
    formData.value.resource_display_name = resource.display_name
    formData.value.detailed_description = resource.display_name
    formData.value.type_resource = resource.type_equipment === 'SERVIC' ? 'SERVICIO' : 'EQUIPO'
    
    // Configurar valores por defecto de intervalos
    formData.value.frequency_type = 'MONTH'
    formData.value.interval_days = 3
    formData.value.weekdays = []
    formData.value.monthdays = []
  }
}

const handleFrequencyTypeChange = () => {
  if (formData.value.frequency_type === 'DAY') {
    formData.value.interval_days = formData.value.interval_days || 3
    formData.value.weekdays = []
    formData.value.monthdays = []
  } else if (formData.value.frequency_type === 'WEEK') {
    formData.value.interval_days = 0
    formData.value.weekdays = formData.value.weekdays || []
    formData.value.monthdays = []
  } else if (formData.value.frequency_type === 'MONTH') {
    formData.value.interval_days = 0
    formData.value.weekdays = []
    formData.value.monthdays = formData.value.monthdays || []
  }
}

const toggleWeekday = (dayValue) => {
  const index = formData.value.weekdays.indexOf(dayValue)
  if (index === -1) {
    formData.value.weekdays.push(dayValue)
  } else {
    formData.value.weekdays.splice(index, 1)
  }
}

const toggleMonthday = (day) => {
  const index = formData.value.monthdays.indexOf(day)
  if (index === -1) {
    formData.value.monthdays.push(day)
  } else {
    formData.value.monthdays.splice(index, 1)
  }
}



const validateForm = () => {
  if (!isEditMode.value && !formData.value.resource_id) {
    errorMessage.value = 'Debe seleccionar un recurso'
    return false
  }
  
  if (!formData.value.operation_start_date) {
    errorMessage.value = 'Debe ingresar la fecha de inicio de operaciones'
    return false
  }

  // Validar configuración de intervalos (siempre requerido)
  if (formData.value.frequency_type === 'DAY' && (!formData.value.interval_days || formData.value.interval_days < 1)) {
    errorMessage.value = 'El intervalo de días debe ser mayor a 0'
    return false
  }
  if (formData.value.frequency_type === 'WEEK' && (!formData.value.weekdays || formData.value.weekdays.length === 0)) {
    errorMessage.value = 'Debe seleccionar al menos un día de la semana'
    return false
  }
  if (formData.value.frequency_type === 'MONTH' && (!formData.value.monthdays || formData.value.monthdays.length === 0)) {
    errorMessage.value = 'Debe seleccionar al menos un día del mes'
    return false
  }

  return true
}

const submitForm = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    const payload = {
      ...formData.value,
      interval_days: formData.value.frequency_type === 'DAY' 
        ? formData.value.interval_days 
        : 0,
      weekdays: formData.value.frequency_type === 'WEEK'
        ? formData.value.weekdays
        : null,
      monthdays: formData.value.frequency_type === 'MONTH'
        ? formData.value.monthdays
        : null
    }

    if (isEditMode.value) {
      await projectResourceStore.updateResourceProject(payload)
      successMessage.value = 'Recurso actualizado exitosamente'
    } else {
      await projectResourceStore.addResourcesToProject([payload])
      successMessage.value = 'Recurso agregado exitosamente'
    }

    setTimeout(() => {
      emit('close')
    }, 1500)
  } catch (error) {
    console.error('Error al guardar recurso:', error)
    errorMessage.value = error.message || 'Error al guardar el recurso'
  } finally {
    isSubmitting.value = false
  }
}

const handleReleaseResource = () => {
  showReleaseConfirm.value = true
}

const cancelRelease = () => {
  showReleaseConfirm.value = false
  releaseReason.value = ''
}

const confirmRelease = async () => {
  if (!releaseReason.value.trim()) {
    errorMessage.value = 'Debe ingresar un motivo de liberación'
    return
  }

  isReleasing.value = true
  errorMessage.value = ''

  try {
    const payload = {
      id: formData.value.id,
      is_retired: true,
      retirement_date: new Date().toISOString().split('T')[0],
      retirement_reason: releaseReason.value
    }

    await projectResourceStore.updateResourceProject(payload)
    successMessage.value = 'Equipo liberado exitosamente'
    
    setTimeout(() => {
      emit('close')
    }, 1500)
  } catch (error) {
    console.error('Error al liberar equipo:', error)
    errorMessage.value = error.message || 'Error al liberar el equipo'
  } finally {
    isReleasing.value = false
    showReleaseConfirm.value = false
    releaseReason.value = ''
  }
}

onMounted(() => {
  if (!isEditMode.value) {
    formData.value.operation_start_date = projectStore.project?.start_date || null
  }
})
</script>

<template>
  <div class="space-y-4">
    <!-- Mensajes -->
    <div v-if="errorMessage" class="alert alert-error shadow-lg">
      <div>
        <i class="las la-exclamation-circle text-2xl"></i>
        <span>{{ errorMessage }}</span>
      </div>
      <button @click="errorMessage = ''" class="btn btn-sm btn-ghost">
        <i class="las la-times"></i>
      </button>
    </div>

    <div v-if="successMessage" class="alert alert-success shadow-lg">
      <div>
        <i class="las la-check-circle text-2xl"></i>
        <span>{{ successMessage }}</span>
      </div>
    </div>

    <form @submit.prevent="submitForm" class="space-y-3">
      <!-- Selección de Recurso (solo en modo creación) -->
      <div v-if="!isEditMode" class="grid grid-cols-12 gap-4 items-center">
        <label class="col-span-4 text-right font-semibold">
          Seleccionar Recurso <span class="text-error">*</span>
        </label>
        <div class="col-span-8">
          <AutocompleteResource 
            placeholder="Buscar recurso disponible..."
            :excludeIds="selectedResourceIds"
            @resource-selected="handleResourceSelected"
          />
        </div>
      </div>

      <!-- Nombre del Recurso (en modo edición) -->
      <div v-else class="grid grid-cols-12 gap-4 items-center">
        <label class="col-span-4 text-right font-semibold">
          Recurso
        </label>
        <div class="col-span-8">
          <input 
            type="text" 
            class="input input-bordered bg-gray-100 w-full" 
            :value="formData.resource_display_name"
            disabled
          />
        </div>
      </div>

      <!-- Descripción Detallada -->
      <div class="grid grid-cols-12 gap-4 items-start">
        <label class="col-span-4 text-right font-semibold pt-3">
          Descripción Detallada
        </label>
        <div class="col-span-8">
          <textarea 
            class="textarea textarea-bordered h-20 w-full" 
            v-model="formData.detailed_description"
            placeholder="Ingrese detalles adicionales del recurso..."
          ></textarea>
        </div>
      </div>

      <!-- Fecha Inicio Operaciones -->
      <div class="grid grid-cols-12 gap-4 items-center">
        <label class="col-span-4 text-right font-semibold">
          Fecha Inicio Operaciones <span class="text-error">*</span>
        </label>
        <div class="col-span-8">
          <input 
            type="date" 
            class="input input-bordered w-full" 
            v-model="formData.operation_start_date"
            required
          />
        </div>
      </div>

      <!-- Fecha Fin Operaciones -->
      <div class="grid grid-cols-12 gap-4 items-center">
        <label class="col-span-4 text-right font-semibold">
          Fecha Fin Operaciones
        </label>
        <div class="col-span-8">
          <input 
            type="date" 
            class="input input-bordered w-full" 
            v-model="formData.operation_end_date"
          />
        </div>
      </div>

      <!-- Costo Alquiler -->
      <div class="grid grid-cols-12 gap-4 items-center">
        <label class="col-span-4 text-right font-semibold">
          Costo Alquiler (Bs)
        </label>
        <div class="col-span-8">
          <input 
            type="number" 
            step="0.01" 
            min="0"
            class="input input-bordered text-right w-full" 
            v-model="formData.cost"
            placeholder="0.00"
            :disabled="isService"
          />
        </div>
      </div>

      <!-- Costo Mantenimiento -->
      <div class="grid grid-cols-12 gap-4 items-center">
        <label class="col-span-4 text-right font-semibold">
          Costo Mantenimiento (Bs)
        </label>
        <div class="col-span-8">
          <input 
            type="number" 
            step="0.01" 
            min="0"
            class="input input-bordered text-right w-full" 
            v-model="formData.maintenance_cost"
            placeholder="0.00"
          />
        </div>
      </div>

      <!-- Configuración de Intervalos -->
      <div class="divider">Configuración de Intervalos</div>

      <!-- Configuración de Frecuencia -->
        <div class="bg-gray-50 rounded-lg p-4 space-y-3">
          <!-- Tipo de Frecuencia -->
          <div class="grid grid-cols-12 gap-4 items-center">
            <label class="col-span-4 text-right font-semibold">
              Tipo de Frecuencia <span class="text-error">*</span>
            </label>
            <div class="col-span-8">
              <select 
                class="select select-bordered w-full"
                v-model="formData.frequency_type"
                @change="handleFrequencyTypeChange"
              >
                <option v-for="ft in availableFrequencyTypes" :key="ft.value" :value="ft.value">
                  {{ ft.label }}
                </option>
              </select>
              <div v-if="isRental" class="label">
                <span class="label-text-alt text-info">
                  <i class="las la-info-circle"></i>
                  Para recursos de alquiler solo está disponible "Días del mes"
                </span>
              </div>
            </div>
          </div>

          <!-- Intervalo de días -->
          <div v-if="formData.frequency_type === 'DAY'" class="grid grid-cols-12 gap-4 items-center">
            <label class="col-span-4 text-right font-semibold">
              Intervalo en días <span class="text-error">*</span>
            </label>
            <div class="col-span-8">
              <input 
                type="number" 
                min="1"
                class="input input-bordered w-full" 
                v-model="formData.interval_days"
                placeholder="Ej: 3"
                required
              />
              <div class="label">
                <span class="label-text-alt text-info">
                  <i class="las la-info-circle"></i>
                  Mantenimiento cada {{ formData.interval_days || 0 }} día(s)
                </span>
              </div>
            </div>
          </div>

          <!-- Días de la semana -->
          <div v-else-if="formData.frequency_type === 'WEEK'" class="grid grid-cols-12 gap-4 items-start">
            <label class="col-span-4 text-right font-semibold pt-2">
              Días de la semana <span class="text-error">*</span>
            </label>
            <div class="col-span-8">
              <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2">
                <button
                  v-for="day in weekdayOptions"
                  :key="day.value"
                  type="button"
                  class="btn btn-sm"
                  :class="formData.weekdays.includes(day.value) ? 'btn-primary' : 'btn-outline'"
                  @click="toggleWeekday(day.value)"
                >
                  <span class="hidden sm:inline">{{ day.label }}</span>
                  <span class="sm:hidden">{{ day.label.substring(0, 3) }}</span>
                </button>
              </div>
              <div class="label">
                <span class="label-text-alt text-info">
                  <i class="las la-info-circle"></i>
                  {{ formData.weekdays.length }} día(s) seleccionado(s)
                </span>
              </div>
            </div>
          </div>

          <!-- Días del mes -->
          <div v-else-if="formData.frequency_type === 'MONTH'" class="grid grid-cols-12 gap-4 items-start">
            <label class="col-span-4 text-right font-semibold pt-2">
              Días del mes <span class="text-error">*</span>
            </label>
            <div class="col-span-8">
              <div class="grid grid-cols-7 sm:grid-cols-10 gap-2">
                <button
                  v-for="day in 31"
                  :key="day"
                  type="button"
                  class="btn btn-sm"
                  :class="formData.monthdays.includes(day) ? 'btn-primary' : 'btn-outline'"
                  @click="toggleMonthday(day)"
                >
                  {{ day }}
                </button>
              </div>
              <div class="label">
                <span class="label-text-alt text-info">
                  <i class="las la-info-circle"></i>
                  {{ formData.monthdays.length }} día(s) seleccionado(s)
                </span>
              </div>
            </div>
          </div>
        </div>

      <!-- Botones de Acción -->
      <div class="flex justify-between items-center pt-4">
        <div>
          <button 
            v-if="isEditMode && formData.type_resource === 'EQUIPO' && !formData.is_retired"
            type="button" 
            class="btn btn-warning btn-sm"
            @click="handleReleaseResource"
            :disabled="isSubmitting || isReleasing"
          >
            <i class="las la-hand-paper"></i>
            Liberar Equipo
          </button>
        </div>
        <div class="flex gap-3">
          <button 
            type="button" 
            class="btn btn-ghost" 
            @click="emit('close')"
            :disabled="isSubmitting || isReleasing"
          >
            Cancelar
          </button>
          <button 
            type="submit" 
            class="btn btn-primary"
            :disabled="isSubmitting || isReleasing"
          >
            <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
            <span v-else>{{ isEditMode ? 'Actualizar' : 'Guardar' }}</span>
          </button>
        </div>
      </div>
    </form>

    <!-- Modal de Confirmación de Liberación -->
    <div v-if="showReleaseConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold mb-4 text-warning">
          <i class="las la-exclamation-triangle"></i>
          Confirmar Liberación de Equipo
        </h3>
        
        <div class="space-y-4">
          <p class="text-sm text-gray-600">
            ¿Está seguro que desea liberar este equipo del proyecto?
          </p>
          
          <div>
            <label class="block text-sm font-semibold mb-2">
              Motivo de liberación <span class="text-error">*</span>
            </label>
            <textarea 
              class="textarea textarea-bordered w-full h-24" 
              v-model="releaseReason"
              placeholder="Ingrese el motivo por el cual se libera el equipo..."
              :disabled="isReleasing"
            ></textarea>
          </div>

          <div class="flex justify-end gap-3">
            <button 
              type="button" 
              class="btn btn-ghost btn-sm"
              @click="cancelRelease"
              :disabled="isReleasing"
            >
              Cancelar
            </button>
            <button 
              type="button" 
              class="btn btn-warning btn-sm"
              @click="confirmRelease"
              :disabled="isReleasing"
            >
              <span v-if="isReleasing" class="loading loading-spinner loading-sm"></span>
              <span v-else>
                <i class="las la-check"></i>
                Confirmar Liberación
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>