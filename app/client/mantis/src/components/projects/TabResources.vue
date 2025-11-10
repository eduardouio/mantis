<script setup>
import { computed } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';

const route = useRoute();
const projectResourceStore = UseProjectResourceStore();

const projectResources = computed(() => projectResourceStore.resourcesProject);

const getEquipmentTypeLabel = (type) => {
  const labels = {
    'LVMNOS': 'Lavamanos',
    'BTSNHM': 'Batería Sanitaria Hombre',
    'BTSNMJ': 'Batería Sanitaria Mujer',
    'EST4UR': 'Estación Cuádruple Urinario',
    'CMPRBN': 'Camper Baño',
    'PTRTAP': 'Planta Trat. Agua Potable',
    'PTRTAR': 'Planta Trat. Agua Residual',
    'TNQAAC': 'Tanque Agua Cruda',
    'TNQAAR': 'Tanque Agua Residual'
  };
  return labels[type] || type;
};

const getStatusBadgeClass = (status) => {
  const classes = {
    'FUNCIONANDO': 'badge-success',
    'DAÑADO': 'badge-error',
    'INCOMPLETO': 'badge-warning',
    'EN REPARACION': 'badge-info'
  };
  return classes[status] || 'badge-ghost';
};

const getAvailabilityBadgeClass = (availability) => {
  const classes = {
    'DISPONIBLE': 'badge-success',
    'RENTADO': 'badge-info'
  };
  return classes[availability] || 'badge-ghost';
};

const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ'
  }).format(value);
};

const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Intl.DateTimeFormat('es-GT').format(new Date(date));
};
</script>

<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-tools text-blue-600 text-xl"></i>
        Equipos Asignados
      </h2>
      <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'resource-form', params: { projectId: route.params.id || 1 } }">
        <i class="las la-plus text-lg"></i>
        Asignar Equipo
      </RouterLink>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-base-200">
            <th>#</th>
            <th>Código</th>
            <th>Nombre/Descripción</th>
            <th class="text-right">Costo</th>
            <th>Frecuencia (días)</th>
            <th>Fecha Inicio</th>
            <th class="text-center">Acciones</th>
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
              <td>{{ resource.id }}</td>
              <td class="font-mono text-sm">{{ resource.resource_item_code }}</td>
              <td>
                <div class="flex flex-col">
                  <span class="font-medium">{{ resource.resource_item_name }}</span>
                  <span class="text-xs text-gray-500">{{ resource.detailed_description }}</span>
                </div>
              </td>
              <td class="text-right font-semibold">{{resource.cost }}</td>
              <td class="text-center">
                <span class="badge badge-neutral badge-sm">{{ resource.interval_days }} días</span>
              </td>
              <td>{{ formatDate(resource.operation_start_date) }}</td>
              <td class="text-center">
                <div class="flex gap-1 justify-center">
                  <button class="btn btn-ghost btn-xs" title="Ver detalles">
                    <i class="las la-eye text-lg"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs" title="Editar">
                    <i class="las la-edit text-lg"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs text-error" title="Eliminar">
                    <i class="las la-trash text-lg"></i>
                  </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
        <tfoot v-if="projectResources.length > 0">
          <tr class="bg-base-200 font-bold">
            <td colspan="3" class="text-right">TOTAL:</td>
            <td class="text-right text-primary">
              {{ formatCurrency(projectResources.reduce((sum, r) => sum + parseFloat(r.cost), 0)) }}
            </td>
            <td colspan="3"></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- Resumen de equipos -->
    <div class="stats shadow w-full">
      <div class="stat">
        <div class="stat-title">Total Recursos</div>
        <div class="stat-value text-primary">{{ projectResources.length }}</div>
        <div class="stat-desc">Asignados al proyecto</div>
      </div>
      
      <div class="stat">
        <div class="stat-title">Costo Total</div>
        <div class="stat-value text-info">
          {{ formatCurrency(projectResources.reduce((sum, r) => sum + parseFloat(r.cost), 0)) }}
        </div>
        <div class="stat-desc">Suma de todos los recursos</div>
      </div>
    </div>
  </div>
</template>
