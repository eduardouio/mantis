<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center">
      <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-calendar text-red-600 text-xl"></i>
        Calendario de Mantenimientos
      </h2>
      <div class="badge badge-info gap-2">
        <i class="las la-wrench"></i>
        {{ scheduleSummary.total_maintenances }} mantenimientos programados
      </div>
    </div>

    <!-- Vista de grilla semanal -->
    <div class="card bg-base-100 shadow border">
      <div class="card-body p-3">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold text-base">Semana del {{ getWeekRange() }}</h3>
        </div>

        <div v-if="uniqueResources.length === 0" class="text-center py-8 text-gray-500">
          <i class="las la-calendar-times text-4xl"></i>
          <p>No hay mantenimientos programados para esta semana</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="table table-zebra w-full">
            <thead>
              <tr class="bg-gray-500 text-white">
                <th class="p-2 border border-gray-100 text-center w-48">Detalle</th>
                <th 
                  v-for="(date, index) in weekDates" 
                  :key="index"
                  class="p-2 border border-gray-100 text-center min-w-[120px]"
                  :class="{
                    'bg-lime-400 text-gray-800': isToday(date)
                  }"
                >
                  <div class="font-bold">{{ getDayName(index) }}</div>
                  <div class="text-xs font-normal">{{ formatWeekDate(date) }}</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="resource in uniqueResources" :key="resource.id">
                <td class="p-2 border border-gray-300 font-medium">
                  <div class="flex items-center gap-2">
                    <i class="las la-tools text-blue-500"></i>
                    <div>
                      <div class="font-semibold text-xs">{{ resource.description }}</div>
                    </div>
                  </div>
                </td>
                <td 
                  v-for="(date, dayIndex) in weekDates" 
                  :key="dayIndex"
                  class="p-2 border border-gray-300 text-center"
                  :class="{ 'bg-lime-100': isToday(date) }"
                >
                  <template v-for="maintenance in getMaintenanceForResourceAndDay(resource.id, date)" :key="maintenance.resource_id + '-' + maintenance.scheduled_date">
                    <div class="bg-blue-50 p-1 rounded">
                      <div class="badge badge-primary badge-xs">Mantenimiento</div>
                      <div class="text-xs text-gray-600 mt-1">
                        {{ maintenance.interval_days }} días
                      </div>
                    </div>
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { generateWeeklyMaintenanceSchedule, getMaintenanceSummary } from '@/utils/scheduler';

const projectResourceStore = UseProjectResourceStore();

const projectResources = computed(() => projectResourceStore.resourcesProject);

// Filtrar solo recursos de tipo SERVIC
const serviceResources = computed(() => {
  return projectResources.value.filter(resource => resource.type === 'SERVIC');
});

// Generar calendario de mantenimientos para la semana actual
const weeklySchedule = computed(() => {
  return generateWeeklyMaintenanceSchedule(serviceResources.value);
});

const scheduleSummary = computed(() => {
  return getMaintenanceSummary(weeklySchedule.value);
});

const getCurrentWeekDates = () => {
  const today = new Date();
  const day = today.getDay();
  const diff = today.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(today.setDate(diff));
  
  const weekDates = [];
  for (let i = 0; i < 7; i++) {
    const date = new Date(monday);
    date.setDate(monday.getDate() + i);
    weekDates.push(date);
  }
  return weekDates;
};

const weekDates = computed(() => getCurrentWeekDates());

const formatWeekDate = (date) => {
  return date.toLocaleDateString('es-GT', { day: '2-digit', month: 'short' });
};

const getDayName = (index) => {
  const days = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM'];
  return days[index];
};

const getMaintenanceForResourceAndDay = (resourceId, dayDate) => {
  const dateStr = dayDate.toISOString().split('T')[0];
  return weeklySchedule.value.filter(
    m => m.resource_id === resourceId && m.scheduled_date === dateStr
  );
};

const uniqueResources = computed(() => {
  const resourceMap = new Map();
  weeklySchedule.value.forEach(m => {
    if (!resourceMap.has(m.resource_id)) {
      resourceMap.set(m.resource_id, {
        id: m.resource_id,
        code: m.resource_code,
        name: m.resource_name,
        description: m.description
      });
    }
  });
  return Array.from(resourceMap.values());
});

const getWeekRange = () => {
  if (weekDates.value.length === 0) return '';
  const start = weekDates.value[0];
  const end = weekDates.value[6];
  return `${start.getDate()} de ${start.toLocaleDateString('es-GT', { month: 'long' })} al ${end.getDate()} de ${end.toLocaleDateString('es-GT', { month: 'long' })} ${end.getFullYear()}`;
};

const isToday = (date) => {
  const today = new Date();
  return date.toDateString() === today.toDateString();
};

onMounted(() => {
  projectResourceStore.fetchResourcesProject();
});
</script>
