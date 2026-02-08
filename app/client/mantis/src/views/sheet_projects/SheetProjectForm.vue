<script setup>
import { RouterLink, useRouter } from 'vue-router';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';
import { UseProjectStore } from '@/stores/ProjectStore';
import { onMounted, computed, ref } from 'vue';

const router = useRouter();
const sheetProjectStore = UseSheetProjectsStore();
const projectStore = UseProjectStore();
const isSubmitting = ref(false);

const project = computed(() => projectStore.project);

// Formulario con todos los campos
const formData = ref({
  period_start: '',
  period_end: '',
  issue_date: new Date().toISOString().split('T')[0],
  service_type: 'ALQUILER Y MANTENIMIENTO',
  status: 'IN_PROGRESS',
  contact_reference: '',
  contact_phone_reference: '',
  client_po_reference: '',
  final_disposition_reference: '',
  invoice_reference: ''
});

const errorMessage = ref('');
const successMessage = ref('');

const serviceTypeOptions = [
  { value: 'ALQUILER', label: 'Alquiler' },
  { value: 'MANTENIMIENTO', label: 'Mantenimiento' },
  { value: 'ALQUILER Y MANTENIMIENTO', label: 'Alquiler y Mantenimiento' }
];

const statusOptions = [
  { value: 'IN_PROGRESS', label: 'En Progreso' },
  { value: 'INVOICED', label: 'Facturado' },
  { value: 'CANCELLED', label: 'Cancelado' }
];

onMounted(async () => {
  await projectStore.fetchProjectData();
  sheetProjectStore.initializeNewSheetProject(project.value);
  
  // Inicializar contactos del proyecto
  formData.value.contact_reference = project.value.contact_name || '';
  formData.value.contact_phone_reference = project.value.contact_phone || '';
});

const handleSubmit = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  isSubmitting.value = true;
  
  try {
    // Validaciones básicas
    if (!formData.value.period_start) {
      throw new Error('La fecha de inicio del período es requerida');
    }
    
    if (!formData.value.service_type) {
      throw new Error('El tipo de servicio es requerido');
    }
    
    const sheetProject = {
      project: project.value.id,
      period_start: formData.value.period_start,
      period_end: formData.value.period_end || null,
      issue_date: formData.value.issue_date || null,
      service_type: formData.value.service_type,
      status: formData.value.status,
      contact_reference: formData.value.contact_reference || null,
      contact_phone_reference: formData.value.contact_phone_reference || null,
      client_po_reference: formData.value.client_po_reference || null,
      final_disposition_reference: formData.value.final_disposition_reference || null,
      invoice_reference: formData.value.invoice_reference || null
    };
    
    const sheetId = await sheetProjectStore.addSheetProject(sheetProject);
    successMessage.value = 'Planilla creada exitosamente';
    
    // Redirigir después de un momento
    setTimeout(() => {
      router.push({ name: 'projects-detail' });
    }, 1500);
  } catch (error) {
    console.error('Error al crear planilla:', error);
    errorMessage.value = error.message || 'Error al crear la planilla';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="container mx-auto p-4 max-w-5xl">
    <div class="mb-4">
      <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
        <i class="las la-file-invoice text-blue-600"></i>
        Nueva Planilla del Proyecto #{{ project?.id }}
      </h1>
      <p class="text-gray-600 text-sm mt-1">Complete todos los campos requeridos para crear una nueva planilla de servicio</p>
    </div>
    
    <form @submit.prevent="handleSubmit" class="card bg-base-100 shadow-xl border border-gray-200 rounded-lg">
      <div class="card-body space-y-6">
        
        <!-- Mensaje de Error -->
        <div v-if="errorMessage" class="alert alert-error shadow-lg">
          <div>
            <i class="las la-exclamation-circle text-2xl"></i>
            <span>{{ errorMessage }}</span>
          </div>
        </div>

        <!-- Mensaje de Éxito -->
        <div v-if="successMessage" class="alert alert-success shadow-lg">
          <div>
            <i class="las la-check-circle text-2xl"></i>
            <span>{{ successMessage }}</span>
          </div>
        </div>

        <!-- Información del Proyecto (solo lectura) -->
        <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 class="font-semibold text-blue-700 mb-3 flex items-center gap-2">
            <i class="las la-building"></i>
            Información del Proyecto
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
            <div class="bg-white p-2 rounded">
              <span class="text-gray-600 text-xs">Cliente:</span>
              <p class="font-semibold">{{ project?.partner_name || 'N/A' }}</p>
            </div>
            <div class="bg-white p-2 rounded">
              <span class="text-gray-600 text-xs">Ubicación:</span>
              <p class="font-semibold">{{ project?.location || 'N/A' }}</p>
            </div>
            <div class="bg-white p-2 rounded">
              <span class="text-gray-600 text-xs">Fecha Inicio:</span>
              <p class="font-semibold">{{ project?.start_date || 'N/A' }}</p>
            </div>
          </div>
        </div>

        <div class="divider">Datos Principales</div>

        <!-- Fila 1: Fechas y Tipo de Servicio -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Fecha Emisión -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Fecha de Emisión</span>
            </label>
            <input
              v-model="formData.issue_date"
              type="date"
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt text-gray-500">Fecha de emisión de la planilla</span>
            </label>
          </div>

          <!-- Fecha Inicio Período -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Fecha Inicio Período *</span>
            </label>
            <input
              v-model="formData.period_start"
              type="date"
              class="input input-bordered w-full"
              :class="{ 'input-error': !formData.period_start }"
              required
            />
            <label class="label">
              <span class="label-text-alt text-gray-500">Inicio del período a facturar</span>
            </label>
          </div>

          <!-- Fecha Fin Período -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Fecha Fin Período</span>
            </label>
            <input
              v-model="formData.period_end"
              type="date"
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt text-gray-500">Fin del período (opcional al crear)</span>
            </label>
          </div>
        </div>

        <!-- Fila 2: Tipo de Servicio y Estado -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              <option v-for="option in serviceTypeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <label class="label">
              <span class="label-text-alt text-gray-500">Tipo de servicio a facturar</span>
            </label>
          </div>

          <!-- Estado -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Estado</span>
            </label>
            <select 
              v-model="formData.status"
              class="select select-bordered w-full"
            >
              <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <label class="label">
              <span class="label-text-alt text-gray-500">Estado actual de la planilla</span>
            </label>
          </div>
        </div>

        <div class="divider">Información de Contacto</div>

        <!-- Fila 3: Contactos -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Nombre Contacto -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Nombre de Contacto</span>
            </label>
            <input
              v-model="formData.contact_reference"
              type="text"
              class="input input-bordered w-full"
              placeholder="Ej: Juan Pérez"
            />
            <label class="label">
              <span class="label-text-alt text-gray-500">Persona de contacto en el proyecto</span>
            </label>
          </div>

          <!-- Teléfono Contacto -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Teléfono de Contacto</span>
            </label>
            <input
              v-model="formData.contact_phone_reference"
              type="text"
              class="input input-bordered w-full"
              placeholder="Ej: +593999999999"
            />
            <label class="label">
              <span class="label-text-alt text-gray-500">Teléfono del contacto</span>
            </label>
          </div>
        </div>

        <div class="divider">Referencias Adicionales</div>

        <!-- Fila 4: Referencias -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- PO Cliente -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">PO Cliente</span>
            </label>
            <input
              v-model="formData.client_po_reference"
              type="text"
              class="input input-bordered w-full"
              placeholder="Ej: PO-2026-001"
            />
            <label class="label">
              <span class="label-text-alt text-gray-500">Número de orden de compra del cliente</span>
            </label>
          </div>

          <!-- Disposición Final -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Disposición Final</span>
            </label>
            <input
              v-model="formData.final_disposition_reference"
              type="text"
              class="input input-bordered w-full"
              placeholder="Ej: Planta de Tratamiento"
            />
            <label class="label">
              <span class="label-text-alt text-gray-500">Lugar de disposición final</span>
            </label>
          </div>

          <!-- Referencia Factura -->
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Referencia Factura</span>
            </label>
            <input
              v-model="formData.invoice_reference"
              type="text"
              class="input input-bordered w-full"
              placeholder="Ej: FAC-2026-001"
            />
            <label class="label">
              <span class="label-text-alt text-gray-500">Número de factura asociada</span>
            </label>
          </div>
        </div>

        <!-- Nota Informativa -->
        <div class="alert alert-info">
          <i class="las la-info-circle text-xl"></i>
          <div>
            <h3 class="font-bold">Información</h3>
            <p class="text-sm">Los campos marcados con (*) son obligatorios. El código de serie se generará automáticamente al crear la planilla.</p>
          </div>
        </div>

        <div class="divider"></div>

        <!-- Botones de Acción -->
        <div class="flex flex-col-reverse sm:flex-row gap-3 sm:justify-end">
          <RouterLink to="/project" class="btn btn-ghost" :class="{ 'btn-disabled': isSubmitting }">
            <i class="las la-times text-lg"></i>
            Cancelar
          </RouterLink>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
            <i v-else class="las la-save text-lg"></i>
            {{ isSubmitting ? 'Creando...' : 'Crear Planilla' }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>
