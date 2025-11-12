<script setup>
import { computed, onMounted } from 'vue';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { generateWeeklyMaintenanceSchedule, getMaintenanceSummary } from '@/utils/scheduler';

const projectResourceStore = UseProjectResourceStore();

const projectResources = computed(() => projectResourceStore.resourcesProject);

const serviceResources = computed(() => {
  return projectResources.value.filter(resource => 
    resource.type === 'SERVIC' && !resource.is_retired
  );
});

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
  
  const fourWeeksDates = [];
  for (let i = 0; i < 28; i++) { // 4 semanas = 28 días
    const date = new Date(monday);
    date.setDate(monday.getDate() + i);
    fourWeeksDates.push(date);
  }
  return fourWeeksDates;
};

const weekDates = computed(() => getCurrentWeekDates());

const formatWeekDate = (date) => {
  return date.getDate();
};

const getDayName = (index) => {
  const days = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
  return days[index % 7];
};

const getMaintenanceForResourceAndDay = (resourceId, dayDate) => {
  const year = dayDate.getFullYear();
  const month = String(dayDate.getMonth() + 1).padStart(2, '0');
  const day = String(dayDate.getDate()).padStart(2, '0');
  const dateStr = `${year}-${month}-${day}`;
  
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
  const end = weekDates.value[27]; // Último día de las 4 semanas
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

<template>
  <div class="space-y-3">
    <div class="text-end">
      <div class="badge badge-info gap-2">
        <i class="las la-wrench"></i>
        <span class="font-semibold">{{ scheduleSummary.total_maintenances }} Servicios Programados</span>
      </div>
    </div>

    <!-- Vista de grilla de 4 semanas -->
    <div class="card bg-base-100 shadow border">
      <div class="card-body p-3">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold text-base">Planificación de 4 semanas: {{ getWeekRange() }}</h3>
        </div>

        <div v-if="uniqueResources.length === 0" class="text-center py-8 text-gray-500">
          <i class="las la-calendar-times text-4xl"></i>
          <p>No hay mantenimientos programados para las próximas 4 semanas</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="table table-zebra w-full">
            <thead>
              <tr class="bg-gray-500 text-white">
                <th class="p-2 border border-gray-100 text-center" style="width: 20%">Detalle</th>
                <th 
                  v-for="(date, index) in weekDates" 
                  :key="index"
                  class="p-2 border text-center text-xs"
                  style="width: 2.86%"
                  :class="{
                    'bg-lime-400 text-gray-800': isToday(date),
                    'border-r-4 border-r-sky-200': index % 7 === 6,
                    'border-gray-100': index % 7 !== 6
                  }"
                >
                  <div class="font-bold">{{ getDayName(index) }}-{{ formatWeekDate(date) }}</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="resource in uniqueResources" :key="resource.id">
                <td class="p-2 border border-gray-300 font-medium" style="width: 20%">
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
                  class="p-1 border text-center"
                  style="width: 2.86%"
                  :class="{ 
                    'bg-lime-100': isToday(date),
                    ' border-r-4 border-r-sky-200 border-b-gray-300': dayIndex % 7 === 6,
                    'border-gray-300': dayIndex % 7 !== 6
                  }"
                >
                  <template v-for="maintenance in getMaintenanceForResourceAndDay(resource.id, date)" :key="maintenance.resource_id + '-' + maintenance.scheduled_date">
                    <div class="bg-amber-200 p-1 rounded border-amber-400 border text-xs">
                      <div class="text-gray-600">
                        S
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