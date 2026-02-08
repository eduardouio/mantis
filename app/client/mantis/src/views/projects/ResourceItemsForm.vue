<script setup>
  import { RouterLink, useRouter } from 'vue-router'
  import AutocompleteResource from '@/components/resources/AutocompleteResource.vue'
  import { onMounted, ref, computed } from 'vue'
  import { UseResourcesStore } from '@/stores/ResourcesStore'
  import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
  import { UseProjectStore } from '@/stores/ProjectStore'

  const resourcesStore = UseResourcesStore()
  const projectResourceStore = UseProjectResourceStore()
  const projectStore = UseProjectStore()
  const router = useRouter()
  const list_resources = ref([])
  const isSubmitting = ref(false)
  const errorMessage = ref('')
  const successMessage = ref('')

  // Obtener equipos no disponibles para servicios
  const physicalEquipments = computed(() => {
    return resourcesStore.physicalEquipmentsNotAvailable || []
  })

  const selectedResourceIds = computed(() => {
    return list_resources.value
      .filter(r => r.resource?.type_equipment_display !== 'SERVICIO')
      .map(r => r.resource_id)
  })

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

  const handleResourceSelected = async () => {
    const resource = resourcesStore.selectedResource
    const isService = resource.type_equipment === 'SERVIC'

    if (!isService) {
      if (resourcesStore.resources && Array.isArray(resourcesStore.resources)) {
        const originalResource = resourcesStore.resources.find(r => r.id === resource.id)
        if (originalResource) {
          originalResource.is_selected = true
        }
      }
    }
    
    // Calcular días del mes automáticamente para equipos
    let calculatedMonthdays = []
    const startDate = projectStore.project?.start_date
    if (!isService && startDate) {
      const start = new Date(startDate)
      const startDay = start.getDate()
      const lastDayOfMonth = new Date(start.getFullYear(), start.getMonth() + 1, 0).getDate()
      
      for (let day = startDay; day <= lastDayOfMonth; day++) {
        calculatedMonthdays.push(day)
      }
    }
    
    const newProjectResource = {
      resource: resource,
      resource_id: resource.id,
      resource_display_name: resource.display_name,
      detailed_description: resource.display_name,
      frequency_type: isService ? 'DAY' : 'MONTH',
      interval_days: isService ? 3 : 0,
      weekdays: [],
      monthdays: isService ? [] : calculatedMonthdays,
      cost: 0,
      operation_start_date: projectStore.project?.start_date || null,
      physical_equipment_code: null
    }
    
    list_resources.value.push(newProjectResource)
    resourcesStore.selectedResource = null
  }

  const removeResource = (index) => {
    const resource = list_resources.value[index]
    
    if (resource.resource?.type_equipment_display !== 'SERVICIO') {
      if (resourcesStore.resources && Array.isArray(resourcesStore.resources)) {
        const originalResource = resourcesStore.resources.find(
          r => r.id === resource.resource_id
        )
        if (originalResource) {
          originalResource.is_selected = false
        }
      }
    }
    
    list_resources.value.splice(index, 1)
  }

  const submitForm = async () => {
    errorMessage.value = ''
    successMessage.value = ''
    isSubmitting.value = true
    
    try {
      // Validar que todos los recursos tengan fecha de inicio
      const resourcesWithoutDate = list_resources.value.filter(r => !r.operation_start_date)
      if (resourcesWithoutDate.length > 0) {
        errorMessage.value = 'Todos los recursos deben tener una fecha de inicio de operaciones'
        isSubmitting.value = false
        return
      }

      const result = await projectResourceStore.addResourcesToProject(
        list_resources.value,
      )
      successMessage.value = `Se agregaron ${result.added} recurso(s) exitosamente`
      router.push('/project')

    } catch (error) {
      console.error('Error submitting form:', error)
      errorMessage.value = error.message || 'Error al guardar los recursos. Por favor intente nuevamente.'
    } finally {
      isSubmitting.value = false
    }
  }

  const handleFrequencyTypeChange = (resource) => {
    if (resource.frequency_type === 'DAY') {
      // Si no hay intervalo o es 0, usar 3 como valor por defecto
      if (!resource.interval_days || resource.interval_days === 0) {
        resource.interval_days = 3
      }
      resource.weekdays = []
      resource.monthdays = []
    } else if (resource.frequency_type === 'WEEK') {
      resource.interval_days = 0
      resource.weekdays = resource.weekdays || []
      resource.monthdays = []
    } else if (resource.frequency_type === 'MONTH') {
      resource.interval_days = 0
      resource.weekdays = []
      resource.monthdays = resource.monthdays || []
    }
  }

  const toggleWeekday = (resource, dayValue) => {
    if (!resource.weekdays) {
      resource.weekdays = []
    }
    const index = resource.weekdays.indexOf(dayValue)
    if (index === -1) {
      resource.weekdays.push(dayValue)
    } else {
      resource.weekdays.splice(index, 1)
    }
  }

  const toggleMonthday = (resource, day) => {
    if (!resource.monthdays) {
      resource.monthdays = []
    }
    const index = resource.monthdays.indexOf(day)
    if (index === -1) {
      resource.monthdays.push(day)
    } else {
      resource.monthdays.splice(index, 1)
    }
  }

  const handleCostFocus = (resource) => {
    if (resource.cost === 0) {
      resource.cost = null
    }
  }

  onMounted(async () => {
    await resourcesStore.fetchResourcesAvailable()
  })
</script>
<template>
  <div class="container mx-auto p-4">
    <!-- Mensaje de Error -->
    <div v-if="errorMessage" class="alert alert-error shadow-lg mb-4">
      <div>
        <i class="las la-exclamation-circle text-2xl"></i>
        <span>{{ errorMessage }}</span>
      </div>
      <button @click="errorMessage = ''" class="btn btn-sm btn-ghost">
        <i class="las la-times"></i>
      </button>
    </div>

    <!-- Mensaje de Éxito -->
    <div v-if="successMessage" class="alert alert-success shadow-lg mb-4">
      <div>
        <i class="las la-check-circle text-2xl"></i>
        <span>{{ successMessage }}</span>
      </div>
    </div>
    
    <form class="card bg-base-100 shadow-xl border border-gray-200 rounded-lg" @submit.prevent="submitForm">
      <div class="card-body space-y-4">
        <div class="flex gap-4">
          <!-- Autocomplete de Recursos -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Seleccionar Recurso *</span>
            </label>
            <AutocompleteResource 
              placeholder="Buscar recurso disponible..."
              :excludeIds="selectedResourceIds"
              @resource-selected="handleResourceSelected"
            />
          </div>
        </div>

        <div class="mt-2 mb-2">
            <table class="table table-zebra w-full">
              <thead>
                <tr class="bg-lime-800 text-white border border-green-500 text-center uppercase text-xs">
                  <th class="border">#</th>
                  <th class="border">Detalle</th>
                  <th class="border">Tipo</th>
                  <th class="border">Equipo Físico</th>
                  <th class="border">Fecha Inicio *</th>
                  <th class="border">Costo</th>
                  <th class="border">Frecuencia</th>
                  <th class="border">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(resource, index) in list_resources" :key="index">
                  <td class="border border-gray-300">{{ index + 1 }}</td>
                  <td class="border border-gray-300">
                    {{ resource.resource_display_name || resource.detailed_description }}
                  </td>
                  <td class="border border-gray-300">{{ resource.resource?.type_equipment_display === 'SERVICIO' ? 'SERVICIO' : 'EQUIPO' }}</td>
                  <td class="border border-gray-300">
                    <select 
                      v-if="resource.resource?.type_equipment === 'SERVIC'"
                      class="select select-sm select-bordered w-full"
                      v-model="resource.physical_equipment_code"
                    >
                      <option :value="null">Sin equipo asignado</option>
                      <option v-for="equipment in physicalEquipments" :key="equipment.id" :value="equipment.id">
                        {{ equipment.code }} - {{ equipment.type_equipment_display }}
                      </option>
                    </select>
                    <span v-else class="text-gray-400 text-sm">-</span>
                  </td>
                  <td class="border border-gray-300">
                    <input 
                      type="date" 
                      class="input input-sm input-bordered w-full" 
                      :class="{ 'input-error': !resource.operation_start_date }"
                      v-model="resource.operation_start_date"
                      required
                    />
                  </td>
                  <td class="border border-gray-300">
                    <input 
                      type="number" 
                      step="0.01" 
                      min="0"
                      class="input input-sm input-bordered w-full text-end" 
                      v-model="resource.cost"
                      @focus="handleCostFocus(resource)"
                      placeholder="0.00"
                    />
                  </td>
                  <!-- Frecuencia -->
                  <td class="border border-gray-300">
                    <div class="space-y-2">
                      <select 
                        class="select select-sm select-bordered w-full"
                        v-model="resource.frequency_type"
                        @change="handleFrequencyTypeChange(resource)"
                      >
                        <option v-for="ft in frequencyTypes" :key="ft.value" :value="ft.value">
                          {{ ft.label }}
                        </option>
                      </select>
                      
                      <!-- Intervalo de días -->
                      <div v-if="resource.frequency_type === 'DAY'">
                        <input 
                          type="number" 
                          min="1"
                          class="input input-sm input-bordered w-full" 
                          v-model="resource.interval_days"
                          data-input="interval"
                          placeholder="Días"
                        />
                      </div>
                      
                      <!-- Días de la semana -->
                      <div v-else-if="resource.frequency_type === 'WEEK'" class="flex flex-wrap gap-1">
                        <button
                          v-for="day in weekdayOptions"
                          :key="day.value"
                          type="button"
                          class="btn btn-xs"
                          :class="resource.weekdays?.includes(day.value) ? 'btn-primary' : 'btn-outline'"
                          @click="toggleWeekday(resource, day.value)"
                        >
                          {{ day.label.substring(0, 3) }}
                        </button>
                      </div>
                      
                      <!-- Días del mes -->
                      <div v-else-if="resource.frequency_type === 'MONTH'" class="grid grid-cols-7 gap-1">
                        <button
                          v-for="day in 31"
                          :key="day"
                          type="button"
                          class="btn btn-xs"
                          :class="resource.monthdays?.includes(day) ? 'btn-primary' : 'btn-outline'"
                          @click="toggleMonthday(resource, day)"
                        >
                          {{ day }}
                        </button>
                      </div>
                    </div>
                  </td>
                  <td class="border border-gray-300 text-center">
                    <button 
                      type="button" 
                      class="btn btn-sm btn-error"
                      @click="removeResource(index)"
                      :disabled="isSubmitting"
                    >
                      <i class="las la-trash text-lg"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="list_resources.length === 0">
                  <td colspan="8" class="text-center py-4 text-gray-500">
                    No hay recursos agregados. Seleccione un recurso del autocomplete.
                  </td>
                </tr>
              </tbody>
            </table>
        </div>

        <!-- Divisor final -->
        <div class="divider"></div>

        <!-- Botones de Acción -->
        <div class="flex flex-col-reverse sm:flex-row gap-3 sm:justify-end">
          <RouterLink to="/project" class="btn btn-ghost" :class="{ 'btn-disabled': isSubmitting }">
            Cancelar
          </RouterLink>
          <button 
            type="submit" 
            class="btn btn-primary" 
            :disabled="list_resources.length === 0 || isSubmitting"
          >
            <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
            <span v-else>Guardar Recursos ({{ list_resources.length }})</span>
          </button>
        </div>
      </div>
    </form>
  </div>
</template>