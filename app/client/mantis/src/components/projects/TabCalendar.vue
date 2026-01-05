<script setup>
import { computed, ref, onMounted } from 'vue';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { generateMaintenanceSchedule, groupMaintenanceByMonth, getMaintenanceSummary } from '@/utils/scheduler';

const projectResourceStore = UseProjectResourceStore();
const resources = computed(() => projectResourceStore.resources || []);

// Estado para navegación de meses
const currentMonthOffset = ref(0); // 0 = mes actual, -1 = mes anterior, +1 = mes siguiente

// Calcular el rango de fechas basado en el offset de meses
const dateRange = computed(() => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  // Calcular el primer día del mes con offset
  const startDate = new Date(today.getFullYear(), today.getMonth() + currentMonthOffset.value, 1);
  
  // Calcular 90 días desde el inicio del mes
  const endDate = new Date(startDate);
  endDate.setDate(startDate.getDate() + 89); // 90 días incluyendo el día de inicio
  
  return { startDate, endDate };
});

// Generar calendario basado en el rango de fechas actual
const maintenanceSchedule = computed(() => {
  if (!resources.value || resources.value.length === 0) return [];
  
  const { startDate, endDate } = dateRange.value;
  const daysAhead = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;
  
  // Generar mantenimientos y filtrar por el rango
  const allMaintenances = generateMaintenanceSchedule(resources.value, daysAhead + Math.abs(currentMonthOffset.value) * 30, startDate);
  
  return allMaintenances.filter(m => {
    const mDate = new Date(m.scheduled_date);
    return mDate >= startDate && mDate <= endDate;
  });
});

const maintenanceByMonth = computed(() => {
  return groupMaintenanceByMonth(maintenanceSchedule.value);
});

const summary = computed(() => {
  return getMaintenanceSummary(maintenanceSchedule.value);
});

// Información del período actual
const periodInfo = computed(() => {
  const { startDate, endDate } = dateRange.value;
  return {
    start: startDate.toLocaleDateString('es-GT', { day: '2-digit', month: 'long', year: 'numeric' }),
    end: endDate.toLocaleDateString('es-GT', { day: '2-digit', month: 'long', year: 'numeric' }),
    monthYear: startDate.toLocaleDateString('es-GT', { month: 'long', year: 'numeric' })
  };
});

// Navegación
const goToPreviousPeriod = () => {
  currentMonthOffset.value -= 1;
};

const goToNextPeriod = () => {
  currentMonthOffset.value += 1;
};

const goToCurrentPeriod = () => {
  currentMonthOffset.value = 0;
};

// Formatear moneda
const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ'
  }).format(value);
};

// Formatear fecha
const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('es-GT', { 
    weekday: 'short',
    day: '2-digit', 
    month: 'short'
  });
};

// Obtener color por tipo de frecuencia
const getFrequencyColor = (frequencyType) => {
  const colors = {
    'DAY': 'badge-primary',
    'WEEK': 'badge-secondary',
    'MONTH': 'badge-accent'
  };
  return colors[frequencyType] || 'badge-ghost';
};

onMounted(async () => {
  if (!resources.value || resources.value.length === 0) {
    await projectResourceStore.fetchResourcesProject();
  }
});
</script>

<template>
  <div class="space-y-4">
    <!-- Controles de Navegación -->
    <div class="bg-gradient-to-r from-lime-500 to-lime-600 rounded-lg p-4 shadow-lg">
      <div class="flex items-center justify-between">
        <!-- Botón Anterior -->
        <button 
          @click="goToPreviousPeriod"
          class="btn btn-circle btn-sm bg-white text-lime-600 hover:bg-lime-50 border-none"
        >
          <i class="las la-chevron-left text-xl"></i>
        </button>

        <!-- Información del Período -->
        <div class="text-center flex-1">
          <h2 class="text-white font-bold text-lg capitalize">
            {{ periodInfo.monthYear }}
          </h2>
          <p class="text-lime-100 text-sm">
            Del {{ periodInfo.start }} al {{ periodInfo.end }}
          </p>
          
          <!-- Botón Hoy (solo si no estamos en el mes actual) -->
          <button 
            v-if="currentMonthOffset !== 0"
            @click="goToCurrentPeriod"
            class="btn btn-xs bg-white text-lime-600 hover:bg-lime-50 border-none mt-2"
          >
            <i class="las la-calendar-day"></i>
            Período Actual
          </button>
        </div>

        <!-- Botón Siguiente -->
        <button 
          @click="goToNextPeriod"
          class="btn btn-circle btn-sm bg-white text-lime-600 hover:bg-lime-50 border-none"
        >
          <i class="las la-chevron-right text-xl"></i>
        </button>
      </div>

      <!-- Resumen Rápido -->
      <div class="grid grid-cols-3 gap-4 mt-4">
        <div class="bg-white bg-opacity-20 rounded-lg p-3 text-center">
          <p class="text-lime-100 text-xs">Mantenimientos</p>
          <p class="text-white font-bold text-2xl">{{ summary.total_maintenances }}</p>
        </div>
        <div class="bg-white bg-opacity-20 rounded-lg p-3 text-center">
          <p class="text-lime-100 text-xs">Recursos</p>
          <p class="text-white font-bold text-2xl">{{ summary.resources_count }}</p>
        </div>
        <div class="bg-white bg-opacity-20 rounded-lg p-3 text-center">
          <p class="text-lime-100 text-xs">Costo Total</p>
          <p class="text-white font-bold text-lg">{{ formatCurrency(summary.total_cost) }}</p>
        </div>
      </div>
    </div>

    <!-- Mensaje de carga -->
    <div v-if="!resources || resources.length === 0" class="alert alert-warning">
      <i class="las la-spinner la-spin text-2xl"></i>
      <span>Cargando recursos del proyecto...</span>
    </div>

    <!-- Mensaje si no hay mantenimientos -->
    <div v-else-if="maintenanceSchedule.length === 0" class="alert alert-info">
      <i class="las la-info-circle text-2xl"></i>
      <span>No hay mantenimientos programados para este período.</span>
    </div>

    <!-- Calendario Agrupado por Mes -->
    <div v-else v-for="(maintenances, monthKey) in maintenanceByMonth" :key="monthKey" class="space-y-3">
      <h3 class="text-lg font-semibold text-gray-700 capitalize border-b-2 border-lime-500 pb-2">
        <i class="las la-calendar text-lime-600"></i>
        {{ monthKey }}
        <span class="badge badge-lime ml-2">{{ maintenances.length }} mantenimientos</span>
      </h3>

      <div class="overflow-x-auto">
        <table class="table table-zebra table-sm">
          <thead>
            <tr class="bg-lime-100">
              <th class="text-xs">Fecha</th>
              <th class="text-xs">Día</th>
              <th class="text-xs">Código</th>
              <th class="text-xs">Recurso</th>
              <th class="text-xs">Descripción</th>
              <th class="text-xs">Frecuencia</th>
              <th class="text-xs text-right">Costo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="maintenance in maintenances" :key="`${maintenance.resource_id}-${maintenance.scheduled_date}`">
              <td class="text-xs font-semibold">{{ formatDate(maintenance.scheduled_date) }}</td>
              <td class="text-xs">
                <span class="capitalize">{{ maintenance.day_of_week }}</span>
              </td>
              <td class="text-xs">
                <span class="badge badge-outline badge-sm">{{ maintenance.resource_code }}</span>
              </td>
              <td class="text-xs font-medium">{{ maintenance.resource_name }}</td>
              <td class="text-xs text-gray-600">{{ maintenance.description }}</td>
              <td class="text-xs">
                <span class="badge badge-sm" :class="getFrequencyColor(maintenance.frequency_type)">
                  {{ maintenance.frequency_type }}
                </span>
              </td>
              <td class="text-xs text-right font-semibold">{{ formatCurrency(maintenance.cost) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="bg-lime-50 font-semibold">
              <td colspan="6" class="text-right text-xs">Subtotal {{ monthKey }}:</td>
              <td class="text-right text-xs">
                {{ formatCurrency(maintenances.reduce((sum, m) => sum + m.cost, 0)) }}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>