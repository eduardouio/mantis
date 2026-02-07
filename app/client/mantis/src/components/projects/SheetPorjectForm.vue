<script setup>
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';
import { UseProjectStore } from '@/stores/ProjectStore';
import { onMounted, computed, ref, defineEmits, defineProps, watch } from 'vue';

const props = defineProps({
  sheet: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close']);

const sheetProjectStore = UseSheetProjectsStore();
const projectStore = UseProjectStore();

const project = computed(() => projectStore.project);
const isEditMode = computed(() => props.sheet !== null);

const formData = ref({
  issue_date: '',
  period_start: '',
  period_end: '',
  service_type: 'ALQUILER Y MANTENIMIENTO',
  contact_reference: '',
  contact_phone_reference: ''
});
const errorMessage = ref('');
const closeSheetAction = ref('');

onMounted(async () => {
  await projectStore.fetchProjectData();
  if (!isEditMode.value) {
    sheetProjectStore.initializeNewSheetProject(project.value);
  }
});

// Observar cambios en la prop sheet para cargar datos en modo edición
watch(() => props.sheet, (newSheet) => {
  if (newSheet) {
    formData.value = {
      issue_date: newSheet.issue_date || '',
      period_start: newSheet.period_start || '',
      period_end: newSheet.period_end || '',
      service_type: newSheet.service_type || 'ALQUILER Y MANTENIMIENTO',
      contact_reference: newSheet.contact_reference || '',
      contact_phone_reference: newSheet.contact_phone_reference || ''
    };
  }
}, { immediate: true });

const handleSubmit = async (e) => {
  e.preventDefault();
  errorMessage.value = '';
  
  // Validar campos requeridos si se va a cerrar la planilla
  if (closeSheetAction.value === 'close') {
    if (!formData.value.issue_date) {
      errorMessage.value = 'La fecha de emisión es requerida para cerrar la planilla';
      return;
    }
    if (!formData.value.period_end) {
      errorMessage.value = 'La fecha de fin de período es requerida para cerrar la planilla';
      return;
    }
  }
  
  try {
    if (isEditMode.value) {
      // Modo edición
      const updatedSheet = {
        id: props.sheet.id,
        issue_date: formData.value.issue_date || null,
        period_start: formData.value.period_start,
        period_end: formData.value.period_end || null,
        service_type: formData.value.service_type,
        contact_reference: formData.value.contact_reference,
        contact_phone_reference: formData.value.contact_phone_reference,
        status: closeSheetAction.value === 'close' ? 'INVOICED' : props.sheet.status
      };
      
      await sheetProjectStore.updateSheetProject(updatedSheet);
      console.log('Planilla actualizada:', props.sheet.id);
    } else {
      // Modo creación
      const sheetProject = {
        ...sheetProjectStore.newSheetProject,
        period_start: formData.value.period_start,
        service_type: formData.value.service_type
      };
      
      const sheetId = await sheetProjectStore.addSheetProject(sheetProject);
      console.log('Planilla creada con ID:', sheetId);
    }
    emit('close');
  } catch (error) {
    console.error('Error al guardar planilla:', error);
    errorMessage.value = error.message || 'Error al guardar la planilla';
  }
};

const handleCancel = () => {
  emit('close');
};

const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Intl.DateTimeFormat('es-GT').format(new Date(date));
};

const getStatusBadge = (status) => {
  const statusConfig = {
    'IN_PROGRESS': { text: 'EN EJECUCIÓN', class: 'badge-success' },
    'INVOICED': { text: 'FACTURADO', class: 'badge-info' },
    'CANCELLED': { text: 'CANCELADO', class: 'badge-warning' }
  };
  return statusConfig[status] || { text: status, class: 'badge-ghost' };
};
</script>

<template>
  <div class="max-w-2xl mx-auto p-1">
    <h5 class="text-xl font-bold mb-6">
      {{ isEditMode ? `Planilla #${sheet.id} - ${sheet.series_code}` : 'Nueva Planilla de Proyecto' }}
    </h5>
    
    <!-- Detalles del Proyecto -->
    <div class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Información del Proyecto</h6>
      
      <div class="grid grid-cols-2 gap-3 text-sm border p-2 rounded border-gray-300 bg-base-100">
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Proyecto ID:</span>
          <span class="ml-2">{{ project?.id }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Cliente:</span>
          <span class="ml-2">{{ project?.partner_name }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Ubicación:</span>
          <span class="ml-2">{{ project?.location }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Contacto:</span>
          <span class="ml-2">{{ project?.contact_name }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Teléfono:</span>
          <span class="ml-2">{{ project?.contact_phone }}</span>
        </div>
        <div v-if="isEditMode" class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Estado:</span>
          <span class="ml-2 badge" :class="getStatusBadge(sheet.status).class">
            {{ getStatusBadge(sheet.status).text }}
          </span>
        </div>
        <div v-if="isEditMode" class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Fecha Emisión:</span>
          <span class="ml-2">{{ formatDate(sheet.issue_date) }}</span>
        </div>
        <div v-if="isEditMode" class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Total Galones:</span>
          <span class="ml-2">{{ sheet.total_gallons?.toLocaleString() || 0 }}</span>
        </div>
        <div v-if="isEditMode" class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Total Barriles:</span>
          <span class="ml-2">{{ sheet.total_barrels?.toLocaleString() || 0 }}</span>
        </div>
        <div v-if="isEditMode" class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Total M³:</span>
          <span class="ml-2">{{ sheet.total_cubic_meters?.toFixed(1) || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- Mensaje de Error -->
    <div v-if="errorMessage" class="alert alert-error shadow-lg mb-4">
      <div>
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>
    </div>
    <!-- Formulario -->
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Fecha de Emisión (solo en edición) -->
      <div v-if="isEditMode" class="form-control w-full">
        <label class="label" for="issue_date">
          <span class="label-text font-medium">Fecha de Emisión
            <span v-if="closeSheetAction === 'close'" class="text-error">*</span>
          </span>
        </label>
        <input
          type="date"
          id="issue_date"
          v-model="formData.issue_date"
          :class="['input input-bordered w-full', closeSheetAction === 'close' && !formData.issue_date ? 'input-error' : '']"
          :required="closeSheetAction === 'close'"
        />
        <label class="label">
          <span class="label-text-alt" :class="closeSheetAction === 'close' ? 'text-error font-semibold' : ''">
            {{ closeSheetAction === 'close' ? 'Requerida para cerrar la planilla' : 'Fecha de emisión de la planilla' }}
          </span>
        </label>
      </div>

      <!-- Fecha Inicio Período -->
      <div class="form-control w-full">
        <label class="label" for="period_start">
          <span class="label-text font-medium">Fecha Inicio Período *</span>
        </label>
        <input
          type="date"
          id="period_start"
          v-model="formData.period_start"
          required
          class="input input-bordered w-full"
        />
        <label class="label">
          <span class="label-text-alt">Fecha de inicio del período a facturar</span>
        </label>
      </div>

      <!-- Fecha Fin Período (solo en edición) -->
      <div v-if="isEditMode" class="form-control w-full">
        <label class="label" for="period_end">
          <span class="label-text font-medium">Fecha Fin Período
            <span v-if="closeSheetAction === 'close'" class="text-error">*</span>
          </span>
        </label>
        <input
          type="date"
          id="period_end"
          v-model="formData.period_end"
          :class="['input input-bordered w-full', closeSheetAction === 'close' && !formData.period_end ? 'input-error' : '']"
          :required="closeSheetAction === 'close'"
        />
        <label class="label">
          <span class="label-text-alt" :class="closeSheetAction === 'close' ? 'text-error font-semibold' : ''">
            {{ closeSheetAction === 'close' ? 'Requerida para cerrar la planilla' : 'Fecha de fin del período (opcional)' }}
          </span>
        </label>
      </div>

      <!-- Tipo de Servicio -->
      <div class="form-control w-full">
        <label class="label" for="service_type">
          <span class="label-text font-medium">Tipo de Servicio *</span>
        </label>
        <select
          id="service_type"
          v-model="formData.service_type"
          required
          class="select select-bordered w-full"
        >
          <option value="ALQUILER">ALQUILER</option>
          <option value="MANTENIMIENTO">MANTENIMIENTO</option>
          <option value="ALQUILER Y MANTENIMIENTO">ALQUILER Y MANTENIMIENTO</option>
        </select>
      </div>

      <!-- Contacto de Referencia (solo en edición) -->
      <div v-if="isEditMode" class="form-control w-full">
        <label class="label" for="contact_reference">
          <span class="label-text font-medium">Contacto de Referencia</span>
        </label>
        <input
          type="text"
          id="contact_reference"
          v-model="formData.contact_reference"
          placeholder="Nombre del contacto"
          class="input input-bordered w-full"
        />
      </div>

      <!-- Teléfono de Referencia (solo en edición) -->
      <div v-if="isEditMode" class="form-control w-full">
        <label class="label" for="contact_phone_reference">
          <span class="label-text font-medium">Teléfono de Referencia</span>
        </label>
        <input
          type="text"
          id="contact_phone_reference"
          v-model="formData.contact_phone_reference"
          placeholder="Teléfono del contacto"
          class="input input-bordered w-full"
        />
      </div>

      <!-- Cerrar Planilla (solo en edición) -->
      <div v-if="isEditMode" class="form-control w-full">
        <label class="label" for="close_sheet">
          <span class="label-text font-medium">Cerrar Planilla</span>
        </label>
        <select
          id="close_sheet"
          v-model="closeSheetAction"
          class="select select-bordered w-full"
        >
          <option value="">Seleccionar acción</option>
          <option value="close">Cerrar Planilla</option>
        </select>
        <label class="label">
          <span class="label-text-alt" :class="closeSheetAction === 'close' ? 'text-warning font-semibold' : ''">
            {{ closeSheetAction === 'close' ? '⚠️ Se requerirán la fecha de emisión y fecha fin de período' : 'Selecciona esta opción para cerrar la planilla' }}
          </span>
        </label>
      </div>

      <!-- Botones -->
      <div class="flex gap-3 justify-end mt-6">
        <button type="button" class="btn btn-outline" @click="handleCancel">
          Cancelar
        </button>
        <button type="submit" class="btn btn-primary">
          {{ isEditMode ? 'Actualizar' : 'Crear' }} Planilla
        </button>
      </div>
    </form>
  </div>
</template>
