<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
import { UseProjectStore } from '@/stores/ProjectStore'
import { formatCurrency, formatDate, formatNumber } from '@/utils/formatters'
import { useTableFilter } from '@/composables/useTableFilter'
import TableControls from '@/components/common/TableControls.vue'

const emit = defineEmits(['edit-resource'])

const projectResourceStore = UseProjectResourceStore()
const projectStore = UseProjectStore()

// Computed property que devuelve todos los recursos ordenados (primero equipos, luego servicios)
const projectResources = computed(() => {
  return [...projectResourceStore.resourcesProject].sort((a, b) => {
    // Primero: activos arriba, retirados al final
    if (a.is_retired !== b.is_retired) return a.is_retired ? 1 : -1

    // Primero ordenar por tipo: EQUIPO antes que SERVICIO
    if (a.type_resource === 'EQUIPO' && b.type_resource === 'SERVICIO') return -1
    if (a.type_resource === 'SERVICIO' && b.type_resource === 'EQUIPO') return 1
    // Si son del mismo tipo, ordenar por ID
    return a.id - b.id
  })
})

const selectedResources= []
const confirmDeleteId = ref(null)
const confirmReactivateId = ref(null)
const confirmRetireId = ref(null)
const reactivateError = ref(null)  // { message, projectId }
const retireError = ref(null)

// Tabla con filtrado, búsqueda y paginación
const tableFilter = useTableFilter(projectResources, {
  searchFields: ['type_resource', 'resource_item_code', 'detailed_description', 'frequency_type'],
  pageSize: 10
})

const isResourceInSheet = (resourceId) => {
  return projectStore.isResourceInSheet(resourceId)
}

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
      alert(error.message || 'Error al eliminar el recurso')
      confirmDeleteId.value = null
    }
  } else {
    // Primera vez haciendo clic - pedir confirmación
    confirmDeleteId.value = resource.id
  }
}

const handleReactivateResource = async (resource) => {
  reactivateError.value = null
  if (confirmReactivateId.value === resource.id) {
    try {
      await projectResourceStore.reactivateResourceProject(resource.id)
      confirmReactivateId.value = null
    } catch (error) {
      console.error('Error al reactivar recurso:', error)
      reactivateError.value = {
        message: error.message || 'Error al reactivar el recurso',
        projectId: error.active_project_id || null
      }
      confirmReactivateId.value = null
    }
  } else {
    confirmReactivateId.value = resource.id
    confirmDeleteId.value = null
    confirmRetireId.value = null
  }
}

const handleRetireResource = async (resource) => {
  retireError.value = null
  if (confirmRetireId.value === resource.id) {
    try {
      await projectResourceStore.releaseResourceProject(resource.id, resource.operation_end_date)
      confirmRetireId.value = null
    } catch (error) {
      console.error('Error al retirar recurso:', error)
      retireError.value = error.message || 'Error al retirar el recurso'
      confirmRetireId.value = null
    }
  } else {
    confirmRetireId.value = resource.id
    confirmDeleteId.value = null
    confirmReactivateId.value = null
  }
}
</script>

<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center mb-4">
      <div class="flex items-center gap-3 flex-wrap">
        <h2 class="font-semibold text-gray-800 flex items-center gap-2">
          <i class="las la-tools text-blue-600"></i>
          Recursos Asignados
        </h2>
        <div v-if="reactivateError" class="flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-300 rounded px-3 py-1">
          <i class="las la-exclamation-triangle"></i>
          <span>{{ reactivateError.message }}</span>
          <a
            v-if="reactivateError.projectId"
            :href="`/projects/${reactivateError.projectId}/`"
            class="underline font-semibold text-red-700 hover:text-red-900 whitespace-nowrap"
            target="_blank"
          >
            Ver proyecto #{{ reactivateError.projectId }}
          </a>
          <button class="ml-1 text-red-400 hover:text-red-700" @click="reactivateError = null" title="Cerrar">
            <i class="las la-times"></i>
          </button>
        </div>
        <div v-if="retireError" class="flex items-center gap-2 text-sm text-orange-600 bg-orange-50 border border-orange-300 rounded px-3 py-1">
          <i class="las la-exclamation-triangle"></i>
          <span>{{ retireError }}</span>
          <button class="ml-1 text-orange-400 hover:text-orange-700" @click="retireError = null" title="Cerrar">
            <i class="las la-times"></i>
          </button>
        </div>
      </div>
      <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'resource-form' }">
        <i class="las la-plus"></i>
        Asignar Recursos
      </RouterLink>
    </div>
    
    <TableControls :tableFilter="tableFilter" position="top" searchPlaceholder="Buscar recurso..." />

    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-gray-500 text-white">
            <th class="p-2 border border-gray-100 text-center">#</th>
            <th class="p-2 border border-gray-100 text-center">Tipo</th>
            <th class="p-2 border border-gray-100 text-center">Código</th>
            <th class="p-2 border border-gray-100 text-center">Descripción</th>
            <th class="p-2 border border-gray-100 text-center">Costo</th>
            <th class="p-2 border border-gray-100 text-center">Frecuencia</th>
            <th class="p-2 border border-gray-100 text-center">Fecha Inicio</th>
            <th class="p-2 border border-gray-100 text-center">Fecha Fin</th>
            <th class="p-2 border border-gray-100 text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="projectResources.length === 0">
            <tr>
              <td colspan="9" class="text-center text-gray-500 py-8">
                <i class="las la-inbox text-4xl"></i>
                <p>No hay recursos asignados a este proyecto</p>
              </td>
            </tr>
          </template>
          <template v-else-if="tableFilter.paginatedData.value.length === 0">
            <tr>
              <td colspan="9" class="text-center text-gray-500 py-8">
                <i class="las la-search text-4xl"></i>
                <p>No se encontraron resultados para "{{ tableFilter.searchQuery.value }}"</p>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="resource in tableFilter.paginatedData.value" :key="resource.id">
              <td class="p-2 border border-gray-300">
                <span class="font-mono">{{ resource.id }}</span>
              </td>
              <td class="p-2 border border-gray-300 text-center">
                {{ resource.type_resource }}
              </td>
              <td class="p-2 border border-gray-300">
                <div class="flex items-center gap-2">
                    <span v-if="!resource.is_retired" class="badge badge-success badge-sm w-24 justify-center">ACTIVO</span>
                    <span v-else class="badge badge-error badge-sm w-24 justify-center">RETIRADO</span>
                    <span v-if="isResourceInSheet(resource.id)" class="badge badge-info badge-sm" title="Este recurso está asignado a una planilla de trabajo">EN USO</span>
                    {{ resource.resource_item_code }}
                </div>
              </td>
              <td class="p-2 border border-gray-300">
                {{ resource.detailed_description }}
              </td>
              <td class="p-2 border border-gray-300 text-right font-mono">
                {{ formatNumber(resource.cost) }}
              </td>
              <td class="p-2 border border-gray-300 text-center">
                <span class="text-xs">
                  {{ resource.frequency_type === 'DAY' ? 'Diario' : resource.frequency_type === 'WEEK' ? 'Semanal' : resource.frequency_type === 'MONTH' ? 'Mensual' : resource.frequency_type }}
                </span>
              </td>
              <td class="p-2 border border-gray-300 text-end font-mono">{{ formatDate(resource.operation_start_date) }}</td>
              <td class="p-2 border border-gray-300 text-end font-mono">
                {{ resource.operation_end_date ? formatDate(resource.operation_end_date) : 'Indefinido' }}
              </td>
              <td class="p-2 border border-gray-300 text-end">
                <div class="flex gap-2 justify-end">
                <button
                  class="btn btn-xs btn-ghost border border-base-300"
                  :title="resource.is_retired ? 'No se puede editar: el recurso está retirado' : 'Editar'"
                  :disabled="resource.is_retired"
                  :class="{
                    'opacity-50 cursor-not-allowed': resource.is_retired
                  }"
                  @click="handleEditResource(resource)"
                >
                  <i class="las la-edit"></i>
                  EDITAR
                </button>
                <button
                  v-if="resource.is_retired"
                  class="btn btn-xs btn-ghost border border-green-400 text-green-600"
                  :class="{ 'bg-green-100': confirmReactivateId === resource.id }"
                  :title="confirmReactivateId === resource.id ? 'Haz clic nuevamente para confirmar' : 'Reactivar recurso en el proyecto'"
                  @click="handleReactivateResource(resource)"
                >
                  <i class="las la-redo-alt"></i>
                  {{ confirmReactivateId === resource.id ? 'CONFIRMAR' : 'REACTIVAR' }}
                </button>
                <button
                  v-if="!resource.is_retired && resource.operation_end_date"
                  class="btn btn-xs btn-ghost border border-orange-400 text-orange-600"
                  :class="{ 'bg-orange-100': confirmRetireId === resource.id }"
                  :title="confirmRetireId === resource.id ? 'Haz clic nuevamente para confirmar el retiro' : `Retirar recurso (fecha fin: ${resource.operation_end_date})`"
                  @click="handleRetireResource(resource)"
                >
                  <i class="las la-hand-paper"></i>
                  {{ confirmRetireId === resource.id ? 'CONFIRMAR' : 'RETIRAR' }}
                </button>
                <button
                  class="btn btn-xs btn-ghost border border-base-300 text-red-500"
                  :title="resource.is_retired ? 'No se puede eliminar: el recurso está retirado' : (isResourceInSheet(resource.id) ? 'No se puede eliminar: el recurso está asignado a una planilla de trabajo' : (confirmDeleteId === resource.id ? 'Haz clic nuevamente para confirmar' : 'Eliminar recurso'))"
                  :disabled="isResourceInSheet(resource.id) || resource.is_retired"
                  :class="{
                    'opacity-50 cursor-not-allowed': isResourceInSheet(resource.id) || resource.is_retired,
                    'bg-base-300': confirmDeleteId === resource.id
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

    <TableControls :tableFilter="tableFilter" position="bottom" />

    <!-- Resumen de recursos -->
    <div class="stats shadow w-full">
      <div class="stat">
        <div class="stat-title">Total Recursos</div>
        <div class="stat-value text-primary">{{ projectResources.length }}</div>
        <div class="stat-desc">{{ projectResources.filter(r => r.type_resource === 'EQUIPO').length }} Equipos y {{ projectResources.filter(r => r.type_resource === 'SERVICIO').length }} Servicios</div>
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
