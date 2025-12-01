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

  const getFrequencyDisplay = (resource) => {
    if (!resource.include_maintenance) return '-'
    
    if (resource.frequency_type === 'DAY') {
      return `Cada ${resource.interval_days} día(s)`
    } else if (resource.frequency_type === 'WEEK') {
      if (!resource.weekdays || resource.weekdays.length === 0) return 'No configurado'
      const days = resource.weekdays.map(d => weekdayOptions[d].label).join(', ')
      return days
    } else if (resource.frequency_type === 'MONTH') {
      if (!resource.monthdays || resource.monthdays.length === 0) return 'No configurado'
      return `Día(s): ${resource.monthdays.sort((a, b) => a - b).join(', ')}`
    }
    return '-'
  }

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
    
    const newProjectResource = {
      resource: resource,
      resource_id: resource.id,
      resource_display_name: resource.display_name,
      detailed_description: resource.display_name,
      frequency_type: 'DAY',
      interval_days: isService ? 3 : 0,
      weekdays: [],
      monthdays: [],
      cost: 0,
      maintenance_cost: 0,
      operation_start_date: projectStore.project?.start_date || null,
      include_maintenance: isService
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

  const handleMaintenanceChange = (resource, event) => {
    if (!resource.include_maintenance) {
      resource.frequency_type = 'DAY'
      resource.interval_days = 0
      resource.weekdays = []
      resource.monthdays = []
      resource.maintenance_cost = 0
    } else {
      const checkbox = event.target
      const row = checkbox.closest('tr')
      const intervalInput = row.querySelector('input[data-input="interval"]')
      if (intervalInput) {
        setTimeout(() => {
          intervalInput.focus()
          intervalInput.select()
        }, 50)
      }
    }
  }

  const handleFrequencyTypeChange = (resource) => {
    if (resource.frequency_type === 'DAY') {
      resource.interval_days = resource.interval_days || 2
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

  const handleMaintenanceCostFocus = (resource) => {
    if (resource.maintenance_cost === 0) {
      resource.maintenance_cost = null
    }
  }
</script>
<template>
  <div class="container mx-auto p-4">
    <span class="font-bold text-lg bg-gray-100 rounded-md px-2 py-1 mb-4 inline-block w-full text-center">
      Recurso del Proyecto
    </span>
    
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
        <AutocompleteResource 
          label="Seleccionar Recurso *"
          placeholder="Buscar recurso disponible..."
          :excludeIds="selectedResourceIds"
          @resource-selected="handleResourceSelected"
        />
        </div>

        <div class="mt-2 mb-2">
            <table class="table table-zebra w-full">
              <thead>
                <tr class="bg-lime-800 text-white border border-green-500 text-center uppercase">
                  <th class="border">#</th>
                  <th class="border">Detalle</th>
                  <th class="border">Tipo</th>
                  <th class="border">Fecha Inicio</th>
                  <th class="border">Costo Alq</th>
                  <th class="border">Mant</th>
                  <th class="border">Frecuencia</th>
                  <th class="border">Costo Mnt</th>
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
                    <input 
                      type="date" 
                      class="input input-sm input-bordered w-full" 
                      v-model="resource.operation_start_date"
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
                      :disabled="resource.resource?.type_equipment_display === 'SERVICIO'"
                    />
                  </td>
                  <td class="border border-gray-300 text-center">
                    <input 
                      type="checkbox" 
                      class="checkbox checkbox-sm" 
                      v-model="resource.include_maintenance"
                      :disabled="resource.resource?.type_equipment_display === 'SERVICIO'"
                      @change="handleMaintenanceChange(resource, $event)"
                    />
                  </td>
                  <td class="border border-gray-300">
                    <div v-if="resource.include_maintenance" class="space-y-2">
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
                    <span v-else class="text-gray-400 text-sm">-</span>
                  </td>
                  <td class="border border-gray-300">
                    <input 
                      type="number" 
                      step="0.01" 
                      min="0"
                      class="input input-sm input-bordered w-full text-end" 
                      v-model="resource.maintenance_cost"
                      @focus="handleMaintenanceCostFocus(resource)"
                      placeholder="0.00"
                      :disabled="!resource.include_maintenance"
                    />
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
                  <td colspan="9" class="text-center py-4 text-gray-500">
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