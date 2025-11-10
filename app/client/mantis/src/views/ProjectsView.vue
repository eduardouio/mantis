<script setup>
import TabResources from '@/components/projects/TabResources.vue'
import TabSheetProject from '@/components/projects/TabSheetProject.vue'
import TabCalendar from '@/components/projects/TabCalendar.vue'
import { UseProjectStore } from '@/stores/ProjectStore';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { onMounted, computed } from 'vue';
import { formatDate } from '@/utils/formatters';

const projectStore = UseProjectStore();
const projectResourceStore = UseProjectResourceStore();

const project = computed(() => projectStore.project);

onMounted(() => {
  projectStore.fetchProjectData();
  projectResourceStore.fetchResourcesProject();
});
</script>

<template>
  <div>
    <div id="project-app" class="w-[90%] mx-auto p-4 bg-white rounded-2xl shadow-md border border-blue-300 border-t-[15px] border-t-blue-300">
      <div class="flex justify-between items-center border-b-blue-500 border-b pb-1 mb-3">
        <h1 class="text-xl font-semibold text-blue-500">
          Ficha de Proyecto #{{ project?.id || 'N/A' }}
        </h1>
        <div class="text-gray-500">
          <span class="badge" :class="!project?.is_closed ? 'badge-success' : 'badge-error'">
            {{ !project?.is_closed ? 'Abierto' : 'Cerrado' }}
          </span>
        </div>
      </div>

      <!-- Información del Proyecto en 3 Columnas -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <!-- Columna 1: Datos del Proyecto -->
        <div class="space-y-1">
          <div class="flex items-center gap-2 py-0.5">
            <i class="las la-building text-blue-500 text-sm"></i>
            <span class="text-xs text-gray-500">Cliente:</span>
            <span class="font-semibold text-xs">{{ project?.partner_name || 'N/A' }}</span>
          </div>
          <div class="flex items-center gap-2 py-0.5">
            <i class="las la-map-marker text-blue-500 text-sm"></i>
            <span class="text-xs text-gray-500">Campamento:</span>
            <span class="font-semibold text-xs">{{ project?.location || 'N/A' }}</span>
          </div>  
        </div>

        <!-- Columna 2: Fechas -->
        <div class="space-y-1">
          <div class="flex items-center gap-2 py-0.5">
            <i class="las la-calendar-check text-blue-500 text-sm"></i>
            <span class="text-xs text-gray-500">Inicio:</span>
            <span class="font-semibold text-xs">{{ formatDate(project?.start_date) }}</span>
          </div>
          <div class="flex items-center gap-2 py-0.5">
            <i class="las la-calendar-times text-blue-500 text-sm"></i>
            <span class="text-xs text-gray-500">Fin:</span>
            <span v-if="project?.end_date" class="font-semibold text-xs">{{ formatDate(project?.end_date) }}</span>
            <span v-else class="text-success font-bold text-xs">EN CURSO</span>
          </div>
        </div>

        <!-- Columna 3: Datos del Cliente -->
        <div class="space-y-1">
          <div class="flex items-center gap-2 py-0.5">
            <i class="las la-user text-blue-500 text-sm"></i>
            <span class="text-xs text-gray-500">Contacto:</span>
            <span class="font-semibold text-xs">{{ project?.contact_name || 'N/A' }}</span>
          </div>
          <div class="flex items-center gap-2 py-0.5">
            <i class="las la-phone text-blue-500 text-sm"></i>
            <span class="text-xs text-gray-500">Teléfono:</span>
            <span class="font-semibold text-xs">{{ project?.contact_phone || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <!-- Tabs para organizar el contenido -->
      <div role="tablist" class="tabs tabs-lifted bg-gray-100 border border-blue-100 p-1">
        <input type="radio" name="project_tabs" role="tab" class="tab bg-red-300" aria-label="Equipos Asignados" checked />
        <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-4">
          <TabResources />
        </div>

        <input type="radio" name="project_tabs" role="tab" class="tab bg-blue-300" aria-label="Órdenes de Trabajo" />
        <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-4">
          <TabSheetProject />
        </div>

        <input type="radio" name="project_tabs" role="tab" class="tab bg-orange-300" aria-label="Calendario Mantenimientos" />
        <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-4">
          <TabCalendar />
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="mt-6 pt-4 border-t">
        <div class="flex flex-wrap justify-center gap-3">
          <button class="btn btn-primary btn-sm">
            <i class="las la-plus text-xl"></i>
            Nuevo Proyecto
          </button>
          <button class="btn btn-primary btn-sm">
            <i class="las la-edit text-xl"></i>
            Editar Proyecto
          </button>
          <button class="btn btn-primary btn-sm">
            <i class="las la-trash text-xl"></i>
            Eliminar Proyecto
          </button>
          <button class="btn btn-primary btn-sm">
            <i class="las la-arrow-left text-xl"></i>
            Volver al Listado
          </button>
        </div>
      </div>
    </div>
  </div>
</template>