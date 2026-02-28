<script setup>
import TabResources from '@/components/projects/TabResources.vue'
import TabSheetProject from '@/components/projects/TabSheetProject.vue'
import TabCalendar from '@/components/projects/TabCalendar.vue'
import TabDocuments from '@/components/projects/TabDocuments.vue'
import Modal from '@/components/common/Modal.vue'
import ResourceForm from '@/components/projects/ResourceForm.vue'
import { UseProjectStore } from '@/stores/ProjectStore';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { onMounted, computed, ref } from 'vue';
import { formatDate } from '@/utils/formatters';

const projectStore = UseProjectStore();
const projectResourceStore = UseProjectResourceStore();
const project = computed(() => projectStore.project);
const isProjectClosed = computed(() => project.value?.is_closed === true);

const isModalOpen = ref(false);
const modalTitle = ref('');
const currentModalComponent = ref(null);
const selectedResourceForEdit = ref(null);

// Estado para el modal de cerrar proyecto
const showCloseProjectModal = ref(false);
const closeProjectAlerts = ref([]);
const canCloseProject = ref(false);
const isValidatingClose = ref(false);
const isClosingProject = ref(false);
const closeResultMessage = ref('');
const closeResultType = ref('');

const openEditResourceModal = (resource) => {
  modalTitle.value = 'Editar Recurso del Proyecto';
  currentModalComponent.value = 'ResourceForm';
  selectedResourceForEdit.value = resource;
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  currentModalComponent.value = null;
  modalTitle.value = '';
  selectedResourceForEdit.value = null;
};

// ── Cerrar proyecto ──────────────────────────────────────────
const openCloseProjectModal = async () => {
  showCloseProjectModal.value = true;
  closeProjectAlerts.value = [];
  canCloseProject.value = false;
  closeResultMessage.value = '';
  closeResultType.value = '';
  isValidatingClose.value = true;

  try {
    const result = await projectStore.validateCloseProject();
    closeProjectAlerts.value = result.alerts || [];
    canCloseProject.value = result.can_close === true;
  } catch (error) {
    closeProjectAlerts.value = [{
      type: 'error',
      message: 'Error al validar el cierre del proyecto: ' + error.message,
    }];
    canCloseProject.value = false;
  } finally {
    isValidatingClose.value = false;
  }
};

const confirmCloseProject = async () => {
  isClosingProject.value = true;
  closeResultMessage.value = '';

  try {
    const result = await projectStore.closeProject();
    if (result.success) {
      closeResultMessage.value = result.message;
      closeResultType.value = 'success';
      // Recargar recursos para reflejar liberaciones
      await projectResourceStore.fetchResourcesProject();
    } else {
      closeResultMessage.value = result.message || result.error || 'Error desconocido';
      closeResultType.value = 'error';
    }
  } catch (error) {
    closeResultMessage.value = 'Error al cerrar el proyecto: ' + error.message;
    closeResultType.value = 'error';
  } finally {
    isClosingProject.value = false;
  }
};

const closeCloseProjectModal = () => {
  showCloseProjectModal.value = false;
};

const getAlertClass = (type) => {
  const classes = {
    error: 'alert-error',
    warning: 'alert-warning',
    info: 'alert-info',
  };
  return classes[type] || 'alert-info';
};

const getAlertIcon = (type) => {
  const icons = {
    error: 'la-times-circle',
    warning: 'la-exclamation-triangle',
    info: 'la-info-circle',
  };
  return icons[type] || 'la-info-circle';
};

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
        <div class="flex items-center gap-3">
          <!-- Estado del proyecto -->
          <div class="text-gray-500">
            <span class="badge" :class="!project?.is_closed ? 'badge-success' : 'badge-error'">
              {{ !project?.is_closed ? 'Abierto' : 'Cerrado' }}
            </span>
          </div>
          <!-- Botón cerrar proyecto -->
          <button
            v-if="!isProjectClosed"
            @click="openCloseProjectModal"
            class="btn btn-error btn-sm"
            title="Cerrar proyecto"
          >
            <i class="las la-lock"></i>
            Cerrar Proyecto
          </button>
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
            <span class="font-semibold text-xs">
              {{ project?.location || 'N/A' }}
              <span class="badge badge-info ml-1" v-if="project?.location && project?.cardinal_point">
                {{ project?.cardinal_point ? ` ${project.cardinal_point}` : '' }}
              </span>
            </span>
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
      <div role="tablist" class="tabs tabs-lifted bg-base-100 p-1">
        <input type="radio" name="project_tabs" role="tab" class="tab bg-amber-500 text-white font-semibold border-s-gray-50 border-s-2" aria-label="Recursos Asignados" checked />
        <div role="tabpanel" class="tab-content bg-base-100 rounded-box p-4">
          <TabResources @edit-resource="openEditResourceModal" />
        </div>

        <input type="radio" name="project_tabs" role="tab" class="tab bg-cyan-500 text-white font-semibold border-s-gray-50 border-s-2" aria-label="Planillas de Trabajo" />
        <div role="tabpanel" class="tab-content bg-base-100 rounded-box p-4">
          <TabSheetProject />
        </div>

        <input type="radio" name="project_tabs" role="tab" class="tab bg-lime-500 text-white font-semibold border-s-gray-50 border-s-2" aria-label="Calendario Mantenimientos" />
        <div role="tabpanel" class="tab-content bg-base-100 rounded-box p-4">
          <TabCalendar />
        </div>

        <input type="radio" name="project_tabs" role="tab" class="tab bg-violet-500 text-white font-semibold border-s-gray-50 border-s-2" aria-label="Documentos" />
        <div role="tabpanel" class="tab-content bg-base-100 rounded-box p-4">
          <TabDocuments />
        </div>
      </div>
      <!-- Botones con sombra (estilo cadena de custodia) -->
      <div class="mt-8 bg-white border-t border-gray-200 shadow-md rounded-b-xl flex justify-end gap-3 px-4 py-3">
        <a href="/projects/" class="btn btn-primary btn-sm">
          <i class="las la-times"></i>
          Volver A Proyectos
        </a>
    </div>
    </div>

    <!-- Modal -->
    <Modal 
      :is-open="isModalOpen" 
      :title="modalTitle" 
      size="lg"
      @close="closeModal"
    >
      <!-- Renderizar componente dinámicamente -->
      <ResourceForm 
        v-if="currentModalComponent === 'ResourceForm'" 
        :resource="selectedResourceForEdit"
        @close="closeModal"
      />
    </Modal>

    <!-- Modal Cerrar Proyecto -->
    <Modal
      :is-open="showCloseProjectModal"
      title="Cerrar Proyecto"
      size="lg"
      @close="closeCloseProjectModal"
    >
      <div class="space-y-4">
        <!-- Cargando validación -->
        <div v-if="isValidatingClose" class="flex items-center justify-center py-8">
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <span class="ml-3 text-gray-500">Validando proyecto...</span>
        </div>

        <!-- Alertas de validación -->
        <template v-else>
          <div v-for="(alert, index) in closeProjectAlerts" :key="index"
            class="alert shadow-sm"
            :class="getAlertClass(alert.type)"
          >
            <div class="flex items-start gap-2 w-full">
              <i class="las text-xl mt-0.5" :class="getAlertIcon(alert.type)"></i>
              <div class="flex-1">
                <p class="text-sm">{{ alert.message }}</p>
                <a v-if="alert.link" :href="alert.link"
                  class="text-xs underline font-semibold mt-1 inline-block"
                >
                  {{ alert.link_text || 'Ver detalle' }}
                </a>
              </div>
            </div>
          </div>

          <!-- Resultado del cierre -->
          <div v-if="closeResultMessage"
            class="alert shadow-sm"
            :class="closeResultType === 'success' ? 'alert-success' : 'alert-error'"
          >
            <div class="flex items-center gap-2">
              <i class="las text-xl" :class="closeResultType === 'success' ? 'la-check-circle' : 'la-times-circle'"></i>
              <p class="text-sm font-semibold">{{ closeResultMessage }}</p>
            </div>
          </div>

          <!-- Botones -->
          <div class="flex justify-end gap-3 pt-2 border-t">
            <button @click="closeCloseProjectModal" class="btn btn-ghost btn-sm">
              {{ closeResultType === 'success' ? 'Cerrar' : 'Cancelar' }}
            </button>
            <button
              v-if="canCloseProject && closeResultType !== 'success'"
              @click="confirmCloseProject"
              class="btn btn-error btn-sm"
              :disabled="isClosingProject"
            >
              <span v-if="isClosingProject" class="loading loading-spinner loading-sm"></span>
              <i v-else class="las la-lock"></i>
              {{ isClosingProject ? 'Cerrando...' : 'Confirmar Cierre' }}
            </button>
          </div>
        </template>
      </div>
    </Modal>
  </div>
</template>