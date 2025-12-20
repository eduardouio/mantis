<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
import { formatCurrency, formatDate, formatNumber } from '@/utils/formatters'

const emit = defineEmits(['edit-resource'])

const projectResourceStore = UseProjectResourceStore()

// Computed property to filter equipment and merge with related maintenance services
const projectResources = computed(() => {
  const allResources = projectResourceStore.resourcesProject
  const equipment = allResources.filter(r => r.type_resource === 'EQUIPO')
  const services = allResources.filter(r => r.type_resource === 'SERVICIO')
  const usedServiceIds = new Set()

  const mappedEquipment = equipment.map(eq => {
    // Relación por convención de nombre: "MANTENIMIENTO {nombre_item}"
    // Esto vincula el equipo con su servicio de mantenimiento correspondiente
    const relatedService = services.find(s => 
      s.detailed_description === `MANTENIMIENTO ${eq.resource_item_name}`
    )

    if (relatedService) {
      usedServiceIds.add(relatedService.id)
    }

    return {
      ...eq,
      has_maintenance: !!relatedService,
      maintenance_cost: relatedService ? relatedService.cost : 0,
      related_service_id: relatedService ? relatedService.id : null
    }
  })

  // Servicios que no están vinculados a ningún equipo (servicios independientes)
  const standaloneServices = services
    .filter(s => !usedServiceIds.has(s.id))
    .map(s => ({
      ...s,
      has_maintenance: false,
      maintenance_cost: 0,
      related_service_id: null
    }))

  return [...mappedEquipment, ...standaloneServices]
})

const selectedResources= []
const confirmDeleteId = ref(null)

const isZeroCost = (cost) => {
  return parseFloat(cost) === 0;
};

const handleEditResource = (resource) => {
  emit('edit-resource', resource);
};

const handleDeleteResource = async (resource) => {
  if (confirmDeleteId.value === resource.id) {
    // Segunda vez haciendo clic - ejecutar eliminación
    try {
      await projectResourceStore.deleteResourceProject(resource.id)
      
      // Si tiene servicio asociado, intentar eliminarlo también
      if (resource.related_service_id) {
         try {
           await projectResourceStore.deleteResourceProject(resource.related_service_id)
         } catch (e) {
           console.warn('No se pudo eliminar el servicio asociado', e)
         }
      }
      
      confirmDeleteId.value = null
    } catch (error) {
      console.error('Error al eliminar recurso:', error)
      alert('Error al eliminar el recurso')
    }
  } else {
    // Primera vez haciendo clic - pedir confirmación
    confirmDeleteId.value = resource.id
  }
}
</script>

<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center mb-4">
      <h2 class="font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-tools text-blue-600"></i>
        Equipos Asignados
      </h2>
      <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'resource-form' }">
        <i class="las la-plus"></i>
        Asignar Recursos
      </RouterLink>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-gray-500 text-white">
            <th class="p-2 border border-gray-100 text-center">#</th>
            <th class="p-2 border border-gray-100 text-center">Código</th>
            <th class="p-2 border border-gray-100 text-center">Nombre/Descripción</th>
            <th class="p-2 border border-gray-100 text-center">Alquiler</th>
            <th class="p-2 border border-gray-100 text-center">Mantenimiento</th>
            <th class="p-2 border border-gray-100 text-center">Fecha Inicio</th>
            <th class="p-2 border border-gray-100 text-center text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="projectResources.length === 0">
            <tr>
              <td colspan="7" class="text-center text-gray-500 py-8">
                <i class="las la-inbox text-4xl"></i>
                <p>No hay equipos asignados a este proyecto</p>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="resource in projectResources" :key="resource.id" :class="{ 'text-red-500 font-bold bg-red-100': isZeroCost(resource.cost) }">
              <td class="p-2 border border-gray-300">{{ resource.id }}</td>
              <td class="p-2 border border-gray-300">
                <div class="flex items-center gap-2">
                    <i v-if="resource.has_maintenance" class="las la-tools text-orange-500 text-xl" title="Incluye Mantenimiento"></i>
                    <span v-if="resource.is_retired" class="text-red-500 border rounded p-1 bg-red-100 text-xs mr-1">RETIRADO</span>  
                    {{ resource.resource_item_code }}
                </div>
              </td>
              <td 
                class="p-2 border border-gray-300"
              >
                {{ resource.detailed_description }}
              </td>
              <td 
                class="p-2 border border-gray-300 text-right font-mono"
              >
                {{ formatNumber(resource.cost) }}
              </td>
              <td 
                class="p-2 border border-gray-300 text-right font-mono"
              >
                {{ formatNumber(resource.maintenance_cost) }}
              </td>
              <td class="p-2 border border-gray-300 text-end font-mono">{{ formatDate(resource.operation_start_date) }}</td>
              <td class="p-2 border border-gray-300 text-end">
                <div class="flex gap-2 justify-end">
                <button 
                  class="btn btn-xs border-blue-500 text-teal-500 bg-white" 
                  title="Editar"
                  @click="handleEditResource(resource)"
                >
                  <i class="las la-edit"></i>
                  EDITAR
                </button>
                <button 
                  class="btn btn-xs border-red-500 text-red-500 bg-white" 
                  :title="confirmDeleteId === resource.id ? 'Haz clic nuevamente para confirmar' : 'Eliminar'"
                  :disabled="!resource.is_deleteable"
                  :class="{ 
                    'opacity-50 cursor-not-allowed': !resource.is_deleteable,
                    'bg-red-500 text-black': confirmDeleteId === resource.id
                  }"
                  @click="handleDeleteResource(resource)"
                >
                  <i class="las la-trash"></i>
                  {{ confirmDeleteId === resource.id ? 'CONFIRMAR' : 'ELIMINAR' }}
                </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Resumen de equipos -->
    <div class="stats shadow w-full">
      <div class="stat">
        <div class="stat-title">Total Recursos</div>
        <div class="stat-value text-primary">{{ projectResources.length }}</div>
        <div class="stat-desc">Equipos y Servicios asignados</div>
      </div>
      
      <div class="stat text-end">
        <div class="stat-title">Costo Total (Alq + Mant)</div>
        <div class="stat-value text-info text-end">
          {{ formatCurrency(projectResources.reduce((sum, r) => sum + parseFloat(r.cost) + parseFloat(r.maintenance_cost), 0)) }}
        </div>
        <div class="stat-desc">Suma de alquiler y mantenimiento</div>
      </div>
    </div>
  </div>
</template>
