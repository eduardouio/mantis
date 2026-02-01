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
  frequency_type: 'DAY',
  interval_days: 3,
  weekdays: [],
  monthdays: [],
  maintenance_cost: 0,
  operation_start_date: null,
  operation_end_date: null,
  include_maintenance: true
})

const isEditMode = computed(() => !!props.resource)
const isService = computed(() => formData.value.type_resource === 'SERVICIO')

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
      frequency_type: newResource.frequency_type || 'DAY',
      interval_days: newResource.interval_days || 3,
      weekdays: newResource.weekdays || [],
      monthdays: newResource.monthdays || [],
      maintenance_cost: newResource.maintenance_cost || 0,
      operation_start_date: newResource.operation_start_date,
      operation_end_date: newResource.operation_end_date,
      include_maintenance: newResource.interval_days > 0 || 
                          (newResource.weekdays && newResource.weekdays.length > 0) ||
                          (newResource.monthdays && newResource.monthdays.length > 0)
    }
  }
}, { immediate: true })

const handleResourceSelected = () => {
  const resource = resourcesStore.selectedResource
  if (resource) {
    formData.value.resource_id = resource.id
    formData.value.resource_display_name = resource.display_name
    formData.value.detailed_description = resource.display_name
    formData.value.type_resource = resource.type_equipment === 'SERVIC' ? 'SERVICIO' : 'EQUIPO'
    
    if (formData.value.type_resource === 'SERVICIO') {
      formData.value.include_maintenance = true
      formData.value.frequency_type = 'DAY'
      formData.value.interval_days = 3
    }
  }
}

const handleMaintenanceChange = () => {
  if (!formData.value.include_maintenance) {
    formData.value.frequency_type = 'DAY'
    formData.value.interval_days = 0
    formData.value.weekdays = []
    formData.value.monthdays = []
    formData.value.maintenance_cost = 0
  } else {
    if (formData.value.frequency_type === 'DAY' && formData.value.interval_days === 0) {
      formData.value.interval_days = 3
    }
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

  if (formData.value.include_maintenance) {
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
      interval_days: formData.value.include_maintenance && formData.value.frequency_type === 'DAY' 
        ? formData.value.interval_days 
        : 0,
      weekdays: formData.value.include_maintenance && formData.value.frequency_type === 'WEEK'
        ? formData.value.weekdays
        : null,
      monthdays: formData.value.include_maintenance && formData.value.frequency_type === 'MONTH'
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
            :disabled="!formData.include_maintenance"
          />
        </div>
      </div>

      <!-- Mantenimiento -->
      <div class="divider">Configuración de Mantenimiento</div>

      <div class="grid grid-cols-12 gap-4 items-center">
        <label class="col-span-4 text-right font-semibold">
          Incluir Mantenimiento
        </label>
        <div class="col-span-8">
          <label class="label cursor-pointer justify-start gap-3">
            <input 
              type="checkbox" 
              class="checkbox checkbox-primary" 
              v-model="formData.include_maintenance"
              :disabled="isService"
              @change="handleMaintenanceChange"
            />
            <span class="label-text">{{ formData.include_maintenance ? 'Sí' : 'No' }}</span>
          </label>
        </div>
      </div>

      <!-- Configuración de Frecuencia -->
      <template v-if="formData.include_maintenance">
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
                <option v-for="ft in frequencyTypes" :key="ft.value" :value="ft.value">
                  {{ ft.label }}
                </option>
              </select>
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
      </template>

      <!-- Botones de Acción -->
      <div class="flex justify-end gap-3 pt-4">
        <button 
          type="button" 
          class="btn btn-ghost" 
          @click="emit('close')"
          :disabled="isSubmitting"
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          class="btn btn-primary"
          :disabled="isSubmitting"
        >
          <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
          <span v-else>{{ isEditMode ? 'Actualizar' : 'Guardar' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>