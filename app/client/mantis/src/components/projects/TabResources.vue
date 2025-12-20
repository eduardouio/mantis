<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
import { formatCurrency, formatDate, formatNumber } from '@/utils/formatters'

const emit = defineEmits(['edit-resource'])

const projectResourceStore = UseProjectResourceStore()
const projectResources = computed(() => projectResourceStore.resourcesProject)
const selectedResources= []
const confirmDeleteId = ref(null)

const weekdayOptions = {
  0: 'Lun', 1: 'Mar', 2: 'Mié', 3: 'Jue', 4: 'Vie', 5: 'Sáb', 6: 'Dom'
}

const getFrequencyDisplay = (resource) => {
  if (resource.frequency_type === 'WEEK') {
    if (Array.isArray(resource.weekdays) && resource.weekdays.length > 0) {
       const sortedDays = [...resource.weekdays].sort((a, b) => a - b)
       return sortedDays.map(d => weekdayOptions[d]).join(', ')
    }
    return 'Semanal'
  }
  if (resource.frequency_type === 'MONTH') {
    if (Array.isArray(resource.monthdays) && resource.monthdays.length > 0) {
       return 'Días: ' + resource.monthdays.sort((a, b) => a - b).join(', ')
    }
    return 'Mensual'
  }
  return `${resource.interval_days} día(s)`
}

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
        Asignar Recusros
      </RouterLink>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-gray-500 text-white">
            <th class="p-2 border border-gray-100 text-center">#</th>
            <th class="p-2 border border-gray-100 text-center">Código</th>
            <th class="p-2 border border-gray-100 text-center">Nombre/Descripción</th>
            <th class="p-2 border border-gray-100 text-center">Tipo Recurso</th>
            <th class="p-2 border border-gray-100 text-center">Costo</th>
            <th class="p-2 border border-gray-100 text-center">Frecuencia</th>
            <th class="p-2 border border-gray-100 text-center">Fecha Inicio</th>
            <th class="p-2 border border-gray-100 text-center text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="projectResources.length === 0">
            <tr>
              <td colspan="8" class="text-center text-gray-500 py-8">
                <i class="las la-inbox text-4xl"></i>
                <p>No hay equipos asignados a este proyecto</p>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="resource in projectResources" :key="resource.id" :class="{ 'text-red-500 font-bold bg-red-100': isZeroCost(resource.cost) }">
              <td class="p-2 border border-gray-300">{{ resource.id }}</td>
              <td class="p-2 border border-gray-300">
                <span v-if="resource.is_retired" class="text-red-500 border rounded p-1 bg-red-100">RETIRADO</span>  
                {{ resource.resource_item_code }}
              </td>
              <td 
                class="p-2 border border-gray-300"
              >
                {{ resource.detailed_description }}
              </td>
              <td 
                class="p-2 border border-gray-300 text-center"
              >
                {{ resource.type_resource }}
              </td>
              <td 
                class="p-2 border border-gray-300 text-right font-mono"
              >
                {{ formatNumber(resource.cost) }}
              </td>
              <td class="p-2 border border-gray-300 text-center text-xs">
                {{ getFrequencyDisplay(resource) }}
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
        <div class="stat-desc">Asignados al proyecto</div>
      </div>
      
      <div class="stat text-end">
        <div class="stat-title">Costo Total</div>
        <div class="stat-value text-info text-end">
          {{ formatCurrency(projectResources.reduce((sum, r) => sum + parseFloat(r.cost), 0)) }}
        </div>
        <div class="stat-desc">Suma de todos los recursos</div>
      </div>
    </div>
  </div>
</template>
