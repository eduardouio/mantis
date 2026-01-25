<script setup>
import { computed, ref, onMounted } from 'vue';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { generateMaintenanceSchedule, getMaintenanceSummary } from '@/utils/scheduler';

const projectResourceStore = UseProjectResourceStore();
const resources = computed(() => projectResourceStore.resources || []);

// Estado para navegación de meses
const currentMonthOffset = ref(0); // 0 = mes actual, -1 = mes anterior, +1 = mes siguiente

// Día seleccionado para ver detalles
const selectedDay = ref(null);

// Nombres de los días de la semana (Lunes a Domingo)
const weekDays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

// Calcular el primer y último día del mes actual
const currentMonth = computed(() => {
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth() + currentMonthOffset.value;
  
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  
  return {
    year: firstDay.getFullYear(),
    month: firstDay.getMonth(),
    firstDay,
    lastDay,
    daysInMonth: lastDay.getDate()
  };
});

// Generar calendario del mes
const maintenanceSchedule = computed(() => {
  if (!resources.value || resources.value.length === 0) return [];
  
  const { firstDay, lastDay } = currentMonth.value;
  const daysAhead = Math.ceil((lastDay - firstDay) / (1000 * 60 * 60 * 24)) + 1;
  
  return generateMaintenanceSchedule(resources.value, daysAhead, firstDay);
});

// Agrupar mantenimientos por fecha (clave: YYYY-MM-DD)
const maintenanceByDate = computed(() => {
  const byDate = {};
  maintenanceSchedule.value.forEach(m => {
    if (!byDate[m.scheduled_date]) {
      byDate[m.scheduled_date] = [];
    }
    byDate[m.scheduled_date].push(m);
  });
  return byDate;
});

// Generar la estructura del calendario (semanas y días)
const calendarWeeks = computed(() => {
  const { firstDay, daysInMonth, year, month } = currentMonth.value;
  const weeks = [];
  
  // Obtener el día de la semana del primer día (0=Domingo en JS, convertir a 0=Lunes)
  let startDayOfWeek = (firstDay.getDay() + 6) % 7;
  
  let currentWeek = [];
  
  // Agregar días vacíos al inicio
  for (let i = 0; i < startDayOfWeek; i++) {
    currentWeek.push(null);
  }
  
  // Agregar los días del mes
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const maintenances = maintenanceByDate.value[dateStr] || [];
    
    currentWeek.push({
      day,
      dateStr,
      maintenances,
      isToday: isToday(year, month, day),
      hasMaintenances: maintenances.length > 0
    });
    
    // Si es domingo (posición 6), empezar nueva semana
    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  }
  
  // Agregar días vacíos al final si es necesario
  if (currentWeek.length > 0) {
    while (currentWeek.length < 7) {
      currentWeek.push(null);
    }
    weeks.push(currentWeek);
  }
  
  return weeks;
});

// Verificar si una fecha es hoy
const isToday = (year, month, day) => {
  const today = new Date();
  return today.getFullYear() === year && 
         today.getMonth() === month && 
         today.getDate() === day;
};

const summary = computed(() => {
  return getMaintenanceSummary(maintenanceSchedule.value);
});

// Información del período actual
const periodInfo = computed(() => {
  const { firstDay } = currentMonth.value;
  return {
    monthYear: firstDay.toLocaleDateString('es-GT', { month: 'long', year: 'numeric' })
  };
});

// Navegación
const goToPreviousPeriod = () => {
  currentMonthOffset.value -= 1;
  selectedDay.value = null;
};

const goToNextPeriod = () => {
  currentMonthOffset.value += 1;
  selectedDay.value = null;
};

const goToCurrentPeriod = () => {
  currentMonthOffset.value = 0;
  selectedDay.value = null;
};

// Seleccionar un día para ver detalles
const selectDay = (dayInfo) => {
  if (dayInfo && dayInfo.hasMaintenances) {
    selectedDay.value = selectedDay.value?.dateStr === dayInfo.dateStr ? null : dayInfo;
  }
};

// Formatear moneda
const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ'
  }).format(value);
};

// Obtener color por tipo de frecuencia
const getFrequencyColor = (frequencyType) => {
  const colors = {
    'DAY': 'bg-blue-500',
    'WEEK': 'bg-purple-500',
    'MONTH': 'bg-orange-500'
  };
  return colors[frequencyType] || 'bg-gray-500';
};

// Obtener badge color por tipo de frecuencia
const getFrequencyBadgeColor = (frequencyType) => {
  const colors = {
    'DAY': 'badge-primary',
    'WEEK': 'badge-secondary',
    'MONTH': 'badge-accent'
  };
  return colors[frequencyType] || 'badge-ghost';
};

// Obtener etiqueta de frecuencia
const getFrequencyLabel = (maintenance) => {
  switch (maintenance.frequency_type) {
    case 'DAY':
      return maintenance.interval_days === 0 ? 'Diario' : `Cada ${maintenance.interval_days} días`;
    case 'WEEK':
      return 'Semanal';
    case 'MONTH':
      return 'Mensual';
    default:
      return maintenance.frequency_type;
  }
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
          <h2 class="text-white font-bold text-xl capitalize">
            {{ periodInfo.monthYear }}
          </h2>
          
          <!-- Botón Hoy (solo si no estamos en el mes actual) -->
          <button 
            v-if="currentMonthOffset !== 0"
            @click="goToCurrentPeriod"
            class="btn btn-xs bg-white text-lime-600 hover:bg-lime-50 border-none mt-2"
          >
            <i class="las la-calendar-day"></i>
            Mes Actual
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

      <!-- Leyenda de Frecuencias -->
      <div class="flex justify-center gap-4 mt-4">
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-blue-500"></span>
          <span class="text-white text-xs">Intervalo días</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-purple-500"></span>
          <span class="text-white text-xs">Días semana</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-orange-500"></span>
          <span class="text-white text-xs">Días mes</span>
        </div>
      </div>
    </div>

    <!-- Mensaje de carga -->
    <div v-if="!resources || resources.length === 0" class="alert alert-warning">
      <i class="las la-spinner la-spin text-2xl"></i>
      <span>Cargando recursos del proyecto...</span>
    </div>

    <!-- Calendario Visual del Mes -->
    <div v-else class="bg-white rounded-lg shadow-lg overflow-hidden">
      <!-- Encabezado de días de la semana -->
      <div class="grid grid-cols-7 bg-lime-100">
        <div 
          v-for="day in weekDays" 
          :key="day" 
          class="p-2 text-center text-sm font-semibold text-lime-700 border-r border-lime-200 last:border-r-0"
        >
          {{ day }}
        </div>
      </div>

      <!-- Semanas del mes -->
      <div v-for="(week, weekIndex) in calendarWeeks" :key="weekIndex" class="grid grid-cols-7 border-t border-gray-200">
        <div 
          v-for="(dayInfo, dayIndex) in week" 
          :key="dayIndex"
          class="min-h-24 p-1 border-r border-gray-200 last:border-r-0 transition-colors"
          :class="{
            'bg-gray-50': !dayInfo,
            'bg-lime-50 hover:bg-lime-100 cursor-pointer': dayInfo?.hasMaintenances,
            'bg-white': dayInfo && !dayInfo.hasMaintenances,
            'ring-2 ring-lime-500 ring-inset': dayInfo?.isToday,
            'bg-lime-200': selectedDay?.dateStr === dayInfo?.dateStr
          }"
          @click="selectDay(dayInfo)"
        >
          <template v-if="dayInfo">
            <!-- Número del día -->
            <div class="flex items-center justify-between mb-1">
              <span 
                class="text-sm font-medium"
                :class="{
                  'text-lime-700': dayInfo.isToday,
                  'text-gray-700': !dayInfo.isToday && dayInfo.hasMaintenances,
                  'text-gray-400': !dayInfo.hasMaintenances
                }"
              >
                {{ dayInfo.day }}
              </span>
              <span 
                v-if="dayInfo.hasMaintenances" 
                class="badge badge-xs badge-success"
              >
                {{ dayInfo.maintenances.length }}
              </span>
            </div>

            <!-- Indicadores de mantenimientos (máximo 3 visibles) -->
            <div v-if="dayInfo.hasMaintenances" class="space-y-0.5">
              <div 
                v-for="(m, idx) in dayInfo.maintenances.slice(0, 3)" 
                :key="m.resource_id"
                class="flex items-center gap-1"
              >
                <span 
                  class="w-2 h-2 rounded-full flex-shrink-0"
                  :class="getFrequencyColor(m.frequency_type)"
                ></span>
                <span class="text-xs truncate text-gray-600">
                  {{ m.resource_code }}
                </span>
              </div>
              <div 
                v-if="dayInfo.maintenances.length > 3" 
                class="text-xs text-gray-500 pl-3"
              >
                +{{ dayInfo.maintenances.length - 3 }} más
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Panel de Detalles del Día Seleccionado -->
    <div 
      v-if="selectedDay" 
      class="bg-white rounded-lg shadow-lg p-4 border-l-4 border-lime-500"
    >
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-700">
          <i class="las la-calendar-check text-lime-600"></i>
          Mantenimientos del {{ new Date(selectedDay.dateStr).toLocaleDateString('es-GT', { 
            weekday: 'long', 
            day: 'numeric', 
            month: 'long', 
            year: 'numeric' 
          }) }}
        </h3>
        <button 
          @click="selectedDay = null" 
          class="btn btn-circle btn-sm btn-ghost"
        >
          <i class="las la-times"></i>
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="table table-sm">
          <thead>
            <tr class="bg-lime-50">
              <th class="text-xs">Código</th>
              <th class="text-xs">Recurso</th>
              <th class="text-xs">Descripción</th>
              <th class="text-xs">Frecuencia</th>
              <th class="text-xs text-right">Costo</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="m in selectedDay.maintenances" 
              :key="m.resource_id"
              class="hover:bg-lime-50"
            >
              <td class="text-xs">
                <span class="badge badge-outline badge-sm">{{ m.resource_code }}</span>
              </td>
              <td class="text-xs font-medium">{{ m.resource_name }}</td>
              <td class="text-xs text-gray-600">{{ m.description || '-' }}</td>
              <td class="text-xs">
                <span 
                  class="badge badge-sm" 
                  :class="getFrequencyBadgeColor(m.frequency_type)"
                >
                  {{ getFrequencyLabel(m) }}
                </span>
              </td>
              <td class="text-xs text-right font-semibold">{{ formatCurrency(m.cost) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="bg-lime-100 font-semibold">
              <td colspan="4" class="text-right text-xs">Total del día:</td>
              <td class="text-right text-xs">
                {{ formatCurrency(selectedDay.maintenances.reduce((sum, m) => sum + m.cost, 0)) }}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Mensaje si no hay mantenimientos en el mes -->
    <div 
      v-if="resources && resources.length > 0 && maintenanceSchedule.length === 0" 
      class="alert alert-info"
    >
      <i class="las la-info-circle text-2xl"></i>
      <span>No hay mantenimientos programados para este mes.</span>
    </div>
  </div>
</template>