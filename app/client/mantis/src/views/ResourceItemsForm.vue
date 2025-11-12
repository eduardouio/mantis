<script setup>
  import { RouterLink, useRouter } from 'vue-router'
  import AutocompleteResource from '@/components/resoruces/AutocompleteResource.vue'
  import { onMounted, ref, computed } from 'vue'
  import { UseResourcesStore } from '@/stores/ResourcesStore'
  import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
  import { UseProjectStore } from '@/stores/ProjectStore'

  const resourcesStore = UseResourcesStore()
  const projectResourceStore = UseProjectResourceStore()
  const projectStore = UseProjectStore()
  const router = useRouter()
  const list_resources = ref([])

  const selectedResourceIds = computed(() => {
    return list_resources.value
      .filter(r => r.resource?.type_equipment_display !== 'SERVICIO')
      .map(r => r.resource_id)
  })

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
      interval_days: isService ? 3 : 0,
      cost: 0,
      maintenance_cost: 0,
      operation_start_date: projectStore.project?.start_date || null,
      include_maintenance: isService
    }
    
    list_resources.value.push(newProjectResource)
    
    resourcesStore.selectedResource = null
  }

  const handleDateChange = (resource, displayDate) => {
    resource.operation_start_date = formatDateToISO(displayDate)
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

  onMounted(() => {
    console.log('Mounted ResourceItemsForm.vue')  
  })


  const submitForm = async () => {
    console.log('Submitting form in ResourceItemsForm.vue')
    try {
      for (const resource of list_resources.value) {
        // Limpiar el objeto antes de enviar
        const cleanResource = {
          project_id: projectStore.project.id,
          resource_id: resource.resource_id,
          resource_display_name: resource.resource_display_name,
          detailed_description: resource.detailed_description,
          interval_days: resource.interval_days,
          cost: resource.cost || 0,
          maintenance_cost: resource.maintenance_cost || 0,
          operation_start_date: resource.operation_start_date,
          include_maintenance: resource.include_maintenance
        }
        await projectResourceStore.addResourceToProject(cleanResource)
      }
      router.push('/project')
    } catch (error) {
      console.error('Error submitting form:', error)
    }
  }

  const handleMaintenanceChange = (resource, event) => {
    if (!resource.include_maintenance) {
      resource.interval_days = 0
      resource.maintenance_cost = 0
    } else {
      // Enfocar el input de frecuencia cuando se activa el mantenimiento
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
                  <th class="border">Mantenimiento</th>
                  <th class="border">Frec Dias</th>
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
                    <input 
                      type="number" 
                      min="1"
                      class="input input-sm input-bordered w-full" 
                      v-model="resource.interval_days"
                      :disabled="!resource.include_maintenance"
                      data-input="interval"
                    />
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
          <RouterLink to="/project" class="btn btn-ghost">
            Cancelar
          </RouterLink>
          <button type="submit" class="btn btn-primary" :disabled="list_resources.length === 0">
            Guardar Recursos ({{ list_resources.length }})
          </button>
        </div>
      </div>
    </form>
  </div>
</template>