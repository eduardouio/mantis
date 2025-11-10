<script setup>
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { formatCurrency, formatDate, formatNumber } from '@/utils/formatters';

const projectResourceStore = UseProjectResourceStore();

const projectResources = computed(() => projectResourceStore.resourcesProject);
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
        Asignar Equipo
      </RouterLink>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-gray-500 text-white">
            <th class="p-2 border border-gray-100 text-center">#</th>
            <th class="p-2 border border-gray-100 text-center">Código</th>
            <th class="p-2 border border-gray-100 text-center">Nombre/Descripción</th>
            <th class="p-2 border border-gray-100 text-center">Costo</th>
            <th class="p-2 border border-gray-100 text-center">Frecuencia (días)</th>
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
            <tr v-for="resource in projectResources" :key="resource.id">
              <td class="p-2 border border-gray-300">{{ resource.id }}</td>
              <td class="p-2 border border-gray-300 font-mono">
                <span v-if="!resource.is_active" class="text-red-500 border rounded p-1 bg-red-100">INACTIVO</span>  
                {{ resource.resource_item_code }}
              </td>
              <td class="p-2 border border-gray-300">{{ resource.detailed_description }}</td>
              <td class="p-2 border border-gray-300 text-right">{{ formatNumber(resource.cost) }}</td>
              <td class="p-2 border border-gray-300 text-end">
                {{ resource.interval_days }} días
              </td>
              <td class="p-2 border border-gray-300 text-end">{{ formatDate(resource.operation_start_date) }}</td>
              <td class="p-2 border border-gray-300 text-center">
                <div class="flex gap-1 justify-center">
                  <button class="btn btn-ghost btn-xs" title="Ver detalles">
                    <i class="las la-eye"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs" title="Editar">
                    <i class="las la-edit"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs text-error" title="Eliminar">
                    <i class="las la-trash"></i>
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
