<script setup>
import { ref } from 'vue';
import { RouterLink } from 'vue-router';

// Datos ficticios basados en ProjectResourceItem y ResourceItem
const projectResources = ref([
  {
    id: 1,
    resource_item: {
      id: 101,
      type_equipment: 'BTSNHM',
      code: 'BSH-001',
      name: 'Batería Sanitaria Hombre Premium',
      brand: 'SaniPro',
      model: 'SP-2024'
    },
    detailed_description: 'Batería sanitaria para área de trabajadores',
    cost: 850.00,
    maintenance_cost: 150.00,
    interval_days: 15,
    operation_start_date: '2024-01-15',
    operation_end_date: '2024-12-31',
    is_retired: false,
    stst_status_equipment: 'FUNCIONANDO',
    stst_status_disponibility: 'RENTADO'
  },
  {
    id: 2,
    resource_item: {
      id: 102,
      type_equipment: 'PTRTAP',
      code: 'PTAP-005',
      name: 'Planta Tratamiento Agua Potable 500gal',
      brand: 'AquaPure',
      model: 'AP-500'
    },
    detailed_description: 'Planta de tratamiento para campamento principal',
    cost: 2500.00,
    maintenance_cost: 450.00,
    interval_days: 30,
    operation_start_date: '2024-01-10',
    operation_end_date: '2024-12-31',
    is_retired: false,
    stst_status_equipment: 'FUNCIONANDO',
    stst_status_disponibility: 'RENTADO'
  },
  {
    id: 3,
    resource_item: {
      id: 103,
      type_equipment: 'LVMNOS',
      code: 'LVM-012',
      name: 'Lavamanos Portátil Doble',
      brand: 'CleanTech',
      model: 'CT-D200'
    },
    detailed_description: 'Lavamanos para área de comedor',
    cost: 350.00,
    maintenance_cost: 75.00,
    interval_days: 7,
    operation_start_date: '2024-02-01',
    operation_end_date: '2024-12-31',
    is_retired: false,
    stst_status_equipment: 'FUNCIONANDO',
    stst_status_disponibility: 'RENTADO'
  },
  {
    id: 4,
    resource_item: {
      id: 104,
      type_equipment: 'BTSNMJ',
      code: 'BSM-003',
      name: 'Batería Sanitaria Mujer Estándar',
      brand: 'SaniPro',
      model: 'SP-W2024'
    },
    detailed_description: 'Batería sanitaria para área administrativa',
    cost: 850.00,
    maintenance_cost: 150.00,
    interval_days: 15,
    operation_start_date: '2024-01-20',
    operation_end_date: '2024-06-30',
    is_retired: true,
    retirement_date: '2024-06-30',
    retirement_reason: 'Fin de contrato de proyecto',
    stst_status_equipment: 'FUNCIONANDO',
    stst_status_disponibility: 'DISPONIBLE'
  },
  {
    id: 5,
    resource_item: {
      id: 105,
      type_equipment: 'PTRTAR',
      code: 'PTAR-008',
      name: 'Planta Tratamiento Aguas Residuales',
      brand: 'EcoWater',
      model: 'EW-1000'
    },
    detailed_description: 'Tratamiento de aguas residuales del campamento',
    cost: 3200.00,
    maintenance_cost: 600.00,
    interval_days: 30,
    operation_start_date: '2024-01-05',
    operation_end_date: '2024-12-31',
    is_retired: false,
    stst_status_equipment: 'FUNCIONANDO',
    stst_status_disponibility: 'RENTADO'
  }
]);

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
      <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'resource-form', params: { projectId: 1 } }">
        <i class="las la-plus text-lg"></i>
        Asignar Equipo
      </RouterLink>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-base-200">
            <th>#</th>
            <th>Tipo</th>
            <th>Código</th>
            <th>Nombre</th>
            <th>Estado</th>
            <th>Disponibilidad</th>
            <th class="text-right">Costo Renta</th>
            <th class="text-right">Costo Mant.</th>
            <th>Frecuencia (días)</th>
            <th>Fecha Inicio</th>
            <th>Fecha Fin</th>
            <th class="text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="projectResources.length === 0">
            <tr>
              <td colspan="12" class="text-center text-gray-500 py-8">
                <i class="las la-inbox text-4xl"></i>
                <p>No hay equipos asignados a este proyecto</p>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="resource in projectResources" :key="resource.id" :class="{ 'opacity-60': resource.is_retired }">
              <td>{{ resource.id }}</td>
              <td>
                <span class="badge badge-sm badge-outline">
                  {{ getEquipmentTypeLabel(resource.resource_item.type_equipment) }}
                </span>
              </td>
              <td class="font-mono text-sm">{{ resource.resource_item.code }}</td>
              <td>
                <div class="flex flex-col">
                  <span class="font-medium">{{ resource.resource_item.name }}</span>
                  <span class="text-xs text-gray-500">{{ resource.resource_item.brand }} - {{ resource.resource_item.model }}</span>
                </div>
              </td>
              <td>
                <span 
                  class="badge badge-sm" 
                  :class="getStatusBadgeClass(resource.stst_status_equipment)"
                >
                  {{ resource.stst_status_equipment }}
                </span>
              </td>
              <td>
                <span 
                  class="badge badge-sm" 
                  :class="getAvailabilityBadgeClass(resource.stst_status_disponibility)"
                >
                  {{ resource.stst_status_disponibility }}
                </span>
              </td>
              <td class="text-right font-semibold">{{ formatCurrency(resource.cost) }}</td>
              <td class="text-right">{{ formatCurrency(resource.maintenance_cost) }}</td>
              <td class="text-center">
                <span class="badge badge-neutral badge-sm">{{ resource.interval_days }} días</span>
              </td>
              <td>{{ formatDate(resource.operation_start_date) }}</td>
              <td>
                <div class="flex flex-col">
                  <span>{{ formatDate(resource.operation_end_date) }}</span>
                  <span v-if="resource.is_retired" class="text-xs text-warning">
                    <i class="las la-exclamation-triangle"></i> Retirado
                  </span>
                </div>
              </td>
              <td class="text-center">
                <div class="flex gap-1 justify-center">
                  <button class="btn btn-ghost btn-xs" title="Ver detalles">
                    <i class="las la-eye text-lg"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs" title="Editar" :disabled="resource.is_retired">
                    <i class="las la-edit text-lg"></i>
                  </button>
                  <button class="btn btn-ghost btn-xs text-error" title="Retirar" :disabled="resource.is_retired">
                    <i class="las la-sign-out-alt text-lg"></i>
                  </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
        <tfoot v-if="projectResources.length > 0">
          <tr class="bg-base-200 font-bold">
            <td colspan="6" class="text-right">TOTALES:</td>
            <td class="text-right text-primary">
              {{ formatCurrency(projectResources.filter(r => !r.is_retired).reduce((sum, r) => sum + parseFloat(r.cost), 0)) }}
            </td>
            <td class="text-right text-primary">
              {{ formatCurrency(projectResources.filter(r => !r.is_retired).reduce((sum, r) => sum + parseFloat(r.maintenance_cost), 0)) }}
            </td>
            <td colspan="4"></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- Resumen de equipos -->
    <div class="stats shadow w-full">
      <div class="stat">
        <div class="stat-title">Total Equipos</div>
        <div class="stat-value text-primary">{{ projectResources.length }}</div>
        <div class="stat-desc">Asignados al proyecto</div>
      </div>
      
      <div class="stat">
        <div class="stat-title">Equipos Activos</div>
        <div class="stat-value text-success">{{ projectResources.filter(r => !r.is_retired).length }}</div>
        <div class="stat-desc">En operación</div>
      </div>
      
      <div class="stat">
        <div class="stat-title">Equipos Retirados</div>
        <div class="stat-value text-warning">{{ projectResources.filter(r => r.is_retired).length }}</div>
        <div class="stat-desc">Fuera de operación</div>
      </div>

      <div class="stat">
        <div class="stat-title">Costo Mensual</div>
        <div class="stat-value text-info">
          {{ formatCurrency(projectResources.filter(r => !r.is_retired).reduce((sum, r) => sum + parseFloat(r.cost) + parseFloat(r.maintenance_cost), 0)) }}
        </div>
        <div class="stat-desc">Renta + Mantenimiento</div>
      </div>
    </div>
  </div>
</template>
