<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { UseCalendarEventStore } from '@/stores/CalendarEventStore';
import { generateMaintenanceSchedule, getMaintenanceSummary } from '@/utils/scheduler';
import { appConfig } from '@/AppConfig';
import { storeToRefs } from 'pinia';
import Modal from '@/components/common/Modal.vue';
import CalendarEventForm from '@/components/projects/CalendarEventForm.vue';

const projectResourceStore = UseProjectResourceStore();
const calendarEventStore = UseCalendarEventStore();
const { resourcesProject } = storeToRefs(projectResourceStore);
const { events: calendarEvents } = storeToRefs(calendarEventStore);

// Estado de carga
const isLoading = ref(true);

// Nombres de los días de la semana (Lunes a Domingo)
const weekDays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

// Estado para navegación de meses
const currentMonthOffset = ref(0);

// Modal de detalles del día
const showDayModal = ref(false);
const selectedDay = ref(null);

// Modal de evento
const showEventModal = ref(false);
const editingEvent = ref(null);
const defaultEventDate = ref(null);

// Drag and drop
const draggedEvent = ref(null);
const dropTargetDate = ref(null);

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

// Generar calendario del mes (planificación automática)
const maintenanceSchedule = computed(() => {
  if (!resourcesProject.value || resourcesProject.value.length === 0) return [];

  const { firstDay, lastDay } = currentMonth.value;
  const daysAhead = Math.ceil((lastDay - firstDay) / (1000 * 60 * 60 * 24)) + 1;

  return generateMaintenanceSchedule(resourcesProject.value, daysAhead, firstDay);
});

// Agrupar mantenimientos por fecha
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

// Agrupar eventos confirmados por fecha
const eventsByDate = computed(() => {
  return calendarEventStore.eventsByDate;
});

// Generar la estructura del calendario
const calendarWeeks = computed(() => {
  const { firstDay, daysInMonth, year, month } = currentMonth.value;
  const weeks = [];

  let startDayOfWeek = (firstDay.getDay() + 6) % 7;
  let currentWeek = [];

  for (let i = 0; i < startDayOfWeek; i++) {
    currentWeek.push(null);
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const maintenances = maintenanceByDate.value[dateStr] || [];
    const events = eventsByDate.value[dateStr] || [];

    currentWeek.push({
      day,
      dateStr,
      maintenances,
      events,
      isToday: isToday(year, month, day),
      hasMaintenances: maintenances.length > 0,
      hasEvents: events.length > 0,
      hasContent: maintenances.length > 0 || events.length > 0
    });

    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  }

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

const periodInfo = computed(() => {
  const { firstDay } = currentMonth.value;
  return {
    monthYear: firstDay.toLocaleDateString('es-GT', { month: 'long', year: 'numeric' })
  };
});

// ── Navegación ──────────────────────────────────────────────
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

// Seleccionar un día para ver detalles en modal
const selectDay = (dayInfo) => {
  if (dayInfo && dayInfo.hasContent) {
    selectedDay.value = dayInfo;
    showDayModal.value = true;
  }
};

const closeDayModal = () => {
  showDayModal.value = false;
  selectedDay.value = null;
};

// Fecha formateada del día seleccionado
const selectedDayFormatted = computed(() => {
  if (!selectedDay.value) return '';
  return new Date(selectedDay.value.dateStr + 'T00:00:00').toLocaleDateString('es-GT', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
});

// ── Modal de Eventos ──────────────────────────────────────────
const openCreateEvent = (dateStr) => {
  editingEvent.value = null;
  defaultEventDate.value = dateStr;
  showEventModal.value = true;
};

const openEditEvent = (event) => {
  editingEvent.value = event;
  defaultEventDate.value = null;
  showEventModal.value = true;
};

const closeEventModal = () => {
  showEventModal.value = false;
  editingEvent.value = null;
  defaultEventDate.value = null;
};

const onEventSaved = () => {
  closeEventModal();
  loadCalendarEvents();
};

const confirmDeleteEvent = async (event) => {
  if (!confirm(`¿Eliminar el evento "${event.title}"?`)) return;
  try {
    await calendarEventStore.deleteEvent(event.id);
  } catch (error) {
    alert('Error al eliminar: ' + error.message);
  }
};

// ── Drag and Drop ──────────────────────────────────────────
const onDragStart = (event, calEvent) => {
  draggedEvent.value = calEvent;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', calEvent.id.toString());
  event.target.classList.add('opacity-50');
};

const onDragEnd = (event) => {
  event.target.classList.remove('opacity-50');
  draggedEvent.value = null;
  dropTargetDate.value = null;
};

const onDragOver = (event, dateStr) => {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'move';
  dropTargetDate.value = dateStr;
};

const onDragLeave = () => {
  dropTargetDate.value = null;
};

const onDrop = async (event, dateStr) => {
  event.preventDefault();
  dropTargetDate.value = null;

  if (!draggedEvent.value) return;
  if (draggedEvent.value.start_date === dateStr) return;

  try {
    await calendarEventStore.moveEvent(draggedEvent.value.id, dateStr);
  } catch (error) {
    alert('Error al mover evento: ' + error.message);
  }

  draggedEvent.value = null;
};

// ── Utilidades ──────────────────────────────────────────────
const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ'
  }).format(value);
};

const getFrequencyColor = (frequencyType) => {
  const colors = {
    'DAY': 'bg-blue-500',
    'WEEK': 'bg-purple-500',
    'MONTH': 'bg-orange-500'
  };
  return colors[frequencyType] || 'bg-gray-500';
};

const getFrequencyBadgeColor = (frequencyType) => {
  const colors = {
    'DAY': 'badge-primary',
    'WEEK': 'badge-secondary',
    'MONTH': 'badge-accent'
  };
  return colors[frequencyType] || 'badge-ghost';
};

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

const getPriorityColor = (priority) => {
  const colors = {
    'LOW': 'badge-info',
    'MEDIUM': 'badge-warning',
    'HIGH': 'badge-error',
    'URGENT': 'badge-error'
  };
  return colors[priority] || 'badge-ghost';
};

const getStatusIcon = (status) => {
  const icons = {
    'SCHEDULED': 'la-clock',
    'IN_PROGRESS': 'la-spinner',
    'COMPLETED': 'la-check-circle',
    'CANCELLED': 'la-times-circle'
  };
  return icons[status] || 'la-calendar';
};

// ── Carga de datos ──────────────────────────────────────────
const loadCalendarEvents = async () => {
  const { year, month } = currentMonth.value;
  try {
    await calendarEventStore.fetchEventsByMonth(appConfig.idProject, year, month + 1);
  } catch (error) {
    console.error('Error loading calendar events:', error);
  }
};

onMounted(async () => {
  if (!resourcesProject.value || resourcesProject.value.length === 0) {
    await projectResourceStore.fetchResourcesProject();
  }
  await loadCalendarEvents();
  isLoading.value = false;
});

watch(resourcesProject, (newVal) => {
  if (newVal && newVal.length > 0) {
    isLoading.value = false;
  }
}, { immediate: true });

// Recargar eventos al cambiar de mes
watch(currentMonthOffset, () => {
  loadCalendarEvents();
});
</script>

<template>
  <!-- CALENDARIO -->
  <div class="space-y-4">
    <!-- Controles de Navegación -->
    <div class="bg-slate-700 rounded-lg p-3 shadow border border-slate-600">
      <div class="flex items-center justify-between">
        <!-- Botón Anterior -->
        <button
          @click="goToPreviousPeriod"
          class="btn btn-circle btn-sm bg-white text-gray-600 hover:bg-gray-50 border-gray-300"
        >
          <i class="las la-chevron-left text-xl"></i>
        </button>

        <!-- Información del Período -->
        <div class="text-center flex-1">
          <h2 class="text-white font-bold text-xl capitalize">
            {{ periodInfo.monthYear }}
          </h2>

          <button
            v-if="currentMonthOffset !== 0"
            @click="goToCurrentPeriod"
            class="btn btn-xs bg-white text-gray-600 hover:bg-gray-50 border-gray-300 mt-2"
          >
            <i class="las la-calendar-day"></i>
            Mes Actual
          </button>
        </div>

        <!-- Botón Siguiente -->
        <button
          @click="goToNextPeriod"
          class="btn btn-circle btn-sm bg-white text-gray-600 hover:bg-gray-50 border-gray-300"
        >
          <i class="las la-chevron-right text-xl"></i>
        </button>
      </div>

      <!-- Resumen Rápido -->
      <div class="grid grid-cols-4 gap-2 mt-3">
        <div class="bg-white rounded-lg p-3 text-center border border-gray-200">
          <p class="text-gray-500 text-xs">Planificados</p>
          <p class="text-gray-800 font-bold text-2xl">{{ summary.total_maintenances }}</p>
        </div>
        <div class="bg-white rounded-lg p-3 text-center border border-gray-200">
          <p class="text-gray-500 text-xs">Eventos</p>
          <p class="text-blue-600 font-bold text-2xl">{{ calendarEvents.length }}</p>
        </div>
        <div class="bg-white rounded-lg p-3 text-center border border-gray-200">
          <p class="text-gray-500 text-xs">Recursos</p>
          <p class="text-gray-800 font-bold text-2xl">{{ summary.resources_count }}</p>
        </div>
        <div class="bg-white rounded-lg p-3 text-center border border-gray-200">
          <p class="text-gray-500 text-xs">Costo Total</p>
          <p class="text-gray-800 font-bold text-lg">{{ formatCurrency(summary.total_cost) }}</p>
        </div>
      </div>

      <!-- Leyenda -->
      <div class="flex justify-center gap-3 mt-2 bg-slate-800 text-white rounded-lg py-1.5 px-2">
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
        <div class="flex items-center gap-1 border-l border-slate-600 pl-3">
          <span class="w-3 h-3 rounded bg-emerald-500"></span>
          <span class="text-white text-xs">Evento confirmado</span>
        </div>
      </div>
    </div>

    <!-- Mensaje de carga -->
    <div v-if="isLoading" class="alert alert-warning">
      <i class="las la-spinner la-spin text-2xl"></i>
      <span>Cargando recursos del proyecto...</span>
    </div>

    <!-- Mensaje si no hay recursos -->
    <div v-else-if="!resourcesProject || resourcesProject.length === 0" class="alert alert-info">
      <i class="las la-info-circle text-2xl"></i>
      <span>No hay recursos asignados a este proyecto.</span>
    </div>

    <!-- Calendario Visual del Mes -->
    <div v-else class="bg-white rounded-lg shadow-lg overflow-hidden border-2 border-slate-300">
      <!-- Encabezado de días de la semana -->
      <div class="grid grid-cols-7 bg-slate-700">
        <div
          v-for="day in weekDays"
          :key="day"
          class="p-2 text-center text-sm font-semibold text-white border-r border-slate-600 last:border-r-0"
        >
          {{ day }}
        </div>
      </div>

      <!-- Semanas del mes -->
      <div v-for="(week, weekIndex) in calendarWeeks" :key="weekIndex" class="grid grid-cols-7 border-t-2 border-slate-300">
        <div
          v-for="(dayInfo, dayIndex) in week"
          :key="dayIndex"
          class="min-h-28 p-1 border-r-2 border-slate-300 last:border-r-0 transition-colors"
          :class="{
            'bg-gray-50': !dayInfo,
            'bg-lime-50 hover:bg-lime-100 cursor-pointer': dayInfo?.hasContent,
            'bg-white': dayInfo && !dayInfo.hasContent,
            'ring-2 ring-lime-500 ring-inset': dayInfo?.isToday,
            'bg-blue-50 ring-2 ring-blue-300 ring-inset': dropTargetDate === dayInfo?.dateStr
          }"
          @click="selectDay(dayInfo)"
          @dragover="dayInfo && onDragOver($event, dayInfo.dateStr)"
          @dragleave="onDragLeave"
          @drop="dayInfo && onDrop($event, dayInfo.dateStr)"
        >
          <template v-if="dayInfo">
            <!-- Cabecera del día -->
            <div class="flex items-center justify-between mb-1">
              <span
                class="text-sm font-medium"
                :class="{
                  'text-lime-700': dayInfo.isToday,
                  'text-gray-700': !dayInfo.isToday && dayInfo.hasContent,
                  'text-gray-400': !dayInfo.hasContent
                }"
              >
                {{ dayInfo.day }}
              </span>
              <div class="flex items-center gap-1">
                <span
                  v-if="dayInfo.hasMaintenances"
                  class="badge badge-xs badge-success"
                  :title="`${dayInfo.maintenances.length} planificados`"
                >
                  {{ dayInfo.maintenances.length }}
                </span>
                <span
                  v-if="dayInfo.hasEvents"
                  class="badge badge-xs badge-primary"
                  :title="`${dayInfo.events.length} eventos`"
                >
                  {{ dayInfo.events.length }}
                </span>
                <!-- Botón agregar evento -->
                <button
                  @click.stop="openCreateEvent(dayInfo.dateStr)"
                  class="btn btn-circle btn-ghost btn-xs opacity-0 hover:opacity-100 group-hover:opacity-100 transition-opacity"
                  :class="{ 'opacity-40': true }"
                  title="Agregar evento"
                >
                  <i class="las la-plus text-xs"></i>
                </button>
              </div>
            </div>

            <!-- Eventos confirmados (draggables) -->
            <div v-if="dayInfo.hasEvents" class="space-y-0.5 mb-1">
              <div
                v-for="evt in dayInfo.events.slice(0, 2)"
                :key="'evt-' + evt.id"
                class="flex items-center gap-1 rounded px-1 py-0.5 cursor-grab active:cursor-grabbing text-white text-xs truncate"
                :style="{ backgroundColor: evt.color || '#10B981' }"
                draggable="true"
                @dragstart="onDragStart($event, evt)"
                @dragend="onDragEnd"
                @click.stop="openEditEvent(evt)"
                :title="evt.title"
              >
                <i class="las text-xs" :class="getStatusIcon(evt.status)"></i>
                <span class="truncate">{{ evt.title }}</span>
              </div>
              <div
                v-if="dayInfo.events.length > 2"
                class="text-xs text-blue-600 pl-1 font-medium"
              >
                +{{ dayInfo.events.length - 2 }} más
              </div>
            </div>

            <!-- Indicadores de mantenimientos planificados -->
            <div v-if="dayInfo.hasMaintenances" class="space-y-0.5">
              <div
                v-for="m in dayInfo.maintenances.slice(0, 2)"
                :key="'m-' + m.resource_id"
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
                v-if="dayInfo.maintenances.length > 2"
                class="text-xs text-gray-500 pl-3"
              >
                +{{ dayInfo.maintenances.length - 2 }} más
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Mensaje si no hay contenido -->
    <div
      v-if="resourcesProject && resourcesProject.length > 0 && maintenanceSchedule.length === 0 && calendarEvents.length === 0"
      class="alert alert-info"
    >
      <i class="las la-info-circle text-2xl"></i>
      <span>No hay mantenimientos ni eventos programados para este mes.</span>
    </div>
  </div>

  <!-- Modal de Evento -->
  <Modal
    :isOpen="showEventModal"
    :title="editingEvent ? 'Editar Evento' : 'Nuevo Evento'"
    size="xl"
    @close="closeEventModal"
  >
    <CalendarEventForm
      :event="editingEvent"
      :defaultDate="defaultEventDate"
      @saved="onEventSaved"
      @close="closeEventModal"
    />
  </Modal>
  <!-- FIN CALENDARIO -->
</template>
