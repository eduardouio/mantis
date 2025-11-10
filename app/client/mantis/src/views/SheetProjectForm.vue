<script setup>
import { RouterLink, useRouter } from 'vue-router';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';
import { UseProjectStore } from '@/stores/ProjectStore';
import { onMounted, computed, ref } from 'vue';

const router = useRouter();
const sheetProjectStore = UseSheetProjectsStore();
const projectStore = UseProjectStore();

const project = computed(() => projectStore.project);
const formData = ref({
  period_start: '',
  service_type: 'ALQUILER Y MANTENIMIENTO'
});
const errorMessage = ref('');

onMounted(async () => {
  await projectStore.fetchProjectData();
  sheetProjectStore.initializeNewSheetProject(project.value);
});

const handleSubmit = async (e) => {
  e.preventDefault();
  errorMessage.value = '';
  
  try {
    const sheetProject = {
      ...sheetProjectStore.newSheetProject,
      period_start: formData.value.period_start,
      service_type: formData.value.service_type
    };
    
    const sheetId = await sheetProjectStore.addSheetProject(sheetProject);
    console.log('Sheet creado con ID:', sheetId);
    router.push({ name: 'project' });
  } catch (error) {
    console.error('Error al crear planilla:', error);
    errorMessage.value = error.message || 'Error al crear la planilla';
  }
};
</script>

<template>
  <div class="container mx-auto p-4 max-w-2xl">
    <span class="font-bold text-lg bg-gray-100 rounded-md px-2 py-1 mb-4 inline-block w-full text-center">
      Nueva Planilla del Proyecto #{{ project?.id }}
    </span>
    
    <form @submit="handleSubmit" class="card bg-base-100 shadow-xl border border-gray-200 rounded-lg">
      <div class="card-body space-y-4">
        
        <!-- Mensaje de Error -->
        <div v-if="errorMessage" class="alert alert-error shadow-lg">
          <div>
            <i class="las la-exclamation-circle text-2xl"></i>
            <span>{{ errorMessage }}</span>
          </div>
        </div>

        <!-- Información del Proyecto (solo lectura) -->
        <div class="bg-blue-50 p-4 rounded-lg space-y-2">
          <h3 class="font-semibold text-blue-700 text-sm mb-2">Información del Proyecto</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
            <div>
              <span class="text-gray-600">Cliente:</span>
              <span class="font-semibold ml-2">{{ project?.partner_name }}</span>
            </div>
            <div>
              <span class="text-gray-600">Ubicación:</span>
              <span class="font-semibold ml-2">{{ project?.location }}</span>
            </div>
            <div>
              <span class="text-gray-600">Contacto:</span>
              <span class="font-semibold ml-2">{{ project?.contact_name }}</span>
            </div>
            <div>
              <span class="text-gray-600">Teléfono:</span>
              <span class="font-semibold ml-2">{{ project?.contact_phone }}</span>
            </div>
          </div>
        </div>

        <div class="divider">Datos de la Planilla</div>

        <!-- Fecha Inicio Período -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text font-semibold">Fecha Inicio Período *</span>
          </label>
          <input
            v-model="formData.period_start"
            type="date"
            class="input input-bordered w-full"
            required
          />
          <label class="label">
            <span class="label-text-alt">Fecha de inicio del período a facturar</span>
          </label>
        </div>

        <!-- Tipo de Servicio -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text font-semibold">Tipo de Servicio *</span>
          </label>
          <select 
            v-model="formData.service_type"
            class="select select-bordered w-full"
            required
          >
            <option value="ALQUILER">ALQUILER</option>
            <option value="MANTENIMIENTO">MANTENIMIENTO</option>
            <option value="ALQUILER Y MANTENIMIENTO" selected>ALQUILER Y MANTENIMIENTO</option>
          </select>
        </div>

        <div class="divider"></div>

        <!-- Botones de Acción -->
        <div class="flex flex-col-reverse sm:flex-row gap-3 sm:justify-end">
          <RouterLink to="/project" class="btn btn-ghost">
            <i class="las la-times text-lg"></i>
            Cancelar
          </RouterLink>
          <button type="submit" class="btn btn-primary">
            <i class="las la-save text-lg"></i>
            Crear Planilla
          </button>
        </div>
      </div>
    </form>
  </div>
</template>