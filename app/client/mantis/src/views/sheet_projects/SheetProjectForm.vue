<script setup>
import { RouterLink, useRouter } from 'vue-router';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';
import { UseProjectStore } from '@/stores/ProjectStore';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { onMounted, computed, ref } from 'vue';

const router = useRouter();
const sheetProjectStore = UseSheetProjectsStore();
const projectStore = UseProjectStore();
const projectResourceStore = UseProjectResourceStore();
const isSubmitting = ref(false);

const project = computed(() => projectStore.project);
const resources = computed(() => projectResourceStore.resourcesProject || []);

// Formulario con todos los campos
const formData = ref({
  period_start: '',
  period_end: '',
  issue_date: new Date().toISOString().split('T')[0],
  service_type: 'ALQUILER Y MANTENIMIENTO',
  status: 'IN_PROGRESS',
  series_code: 'PSL-PS-0000-0000',
  secuence_prefix: 'PSL-PS',
  secuence_year: new Date().getFullYear(),
  secuence_number: 0,
  contact_reference: '',
  contact_phone_reference: '',
  client_po_reference: '',
  final_disposition_reference: '',
  invoice_reference: ''
});

// Estadísticas (solo lectura, calculadas)
const stats = ref({
  total_gallons: 0,
  total_barrels: 0,
  total_cubic_meters: 0,
  subtotal: 0,
  tax_amount: 0,
  total: 0
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

// Placeholder para adjuntar archivos PDF (implementación futura)
const handleAttachSheetFile = () => {
  // TODO: Implementar subida de archivo de planilla
  console.log('Adjuntar archivo de planilla');
};

const handleAttachCertificateFile = () => {
  // TODO: Implementar subida de certificado de disposición final
  console.log('Adjuntar certificado de disposición final');
};

onMounted(async () => {
  await projectStore.fetchProjectData();
  await projectResourceStore.fetchResourcesProject();
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
      series_code: formData.value.series_code,
      secuence_prefix: formData.value.secuence_prefix,
      secuence_year: formData.value.secuence_year,
      secuence_number: formData.value.secuence_number,
      contact_reference: formData.value.contact_reference || null,
      contact_phone_reference: formData.value.contact_phone_reference || null,
      client_po_reference: formData.value.client_po_reference || null,
      final_disposition_reference: formData.value.final_disposition_reference || null,
      invoice_reference: formData.value.invoice_reference || null
    };
    
    const sheetId = await sheetProjectStore.addSheetProject(sheetProject);
    successMessage.value = 'Planilla creada exitosamente';
    
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
  <div class="w-[95%] mx-auto p-3">

    <!-- ===== ENCABEZADO: Título + Botones PDF ===== -->
    <div class="flex items-center justify-between mb-3">
      <div>
        <h1 class="text-xl font-bold text-gray-800 flex items-center gap-2">
          <i class="las la-file-invoice text-blue-600"></i>
          Planilla #{{ formData.id || 'Nueva' }} — Proyecto #{{ project?.id }}
        </h1>
        <p class="text-gray-500 text-xs mt-0.5">{{ project?.partner_name || '' }} · {{ project?.location || '' }}</p>
      </div>
      <div class="flex gap-2">
        <button type="button" @click="handleAttachSheetFile" class="btn btn-sm btn-outline btn-info gap-1">
          <i class="las la-file-pdf text-lg"></i> Planilla PDF
        </button>
        <button type="button" @click="handleAttachCertificateFile" class="btn btn-sm btn-outline btn-warning gap-1">
          <i class="las la-file-pdf text-lg"></i> Cert. Disp. Final
        </button>
      </div>
    </div>

    <!-- ===== ALERTAS ===== -->
    <div v-if="errorMessage" class="alert alert-error shadow-sm mb-2 py-2 text-sm">
      <i class="las la-exclamation-circle text-lg"></i>
      <span>{{ errorMessage }}</span>
    </div>
    <div v-if="successMessage" class="alert alert-success shadow-sm mb-2 py-2 text-sm">
      <i class="las la-check-circle text-lg"></i>
      <span>{{ successMessage }}</span>
    </div>

    <form @submit.prevent="handleSubmit">

      <!-- ===== ESTADÍSTICAS (solo lectura) ===== -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 mb-3">
        <div class="stat bg-base-100 border rounded-lg p-3 text-center shadow-sm">
          <div class="text-xs text-gray-500 uppercase">Galones</div>
          <div class="text-xl font-bold text-blue-700">{{ stats.total_gallons }}</div>
        </div>
        <div class="stat bg-base-100 border rounded-lg p-3 text-center shadow-sm">
          <div class="text-xs text-gray-500 uppercase">Barriles</div>
          <div class="text-xl font-bold text-green-700">{{ stats.total_barrels }}</div>
        </div>
        <div class="stat bg-base-100 border rounded-lg p-3 text-center shadow-sm">
          <div class="text-xs text-gray-500 uppercase">m³</div>
          <div class="text-xl font-bold text-purple-700">{{ stats.total_cubic_meters }}</div>
        </div>
        <div class="stat bg-base-100 border rounded-lg p-3 text-center shadow-sm">
          <div class="text-xs text-gray-500 uppercase">Subtotal</div>
          <div class="text-xl font-bold text-gray-700">${{ Number(stats.subtotal).toFixed(2) }}</div>
        </div>
        <div class="stat bg-base-100 border rounded-lg p-3 text-center shadow-sm">
          <div class="text-xs text-gray-500 uppercase">IVA</div>
          <div class="text-xl font-bold text-orange-600">${{ Number(stats.tax_amount).toFixed(2) }}</div>
        </div>
        <div class="stat bg-base-100 border rounded-lg p-3 text-center shadow-sm">
          <div class="text-xs text-gray-500 uppercase">Total</div>
          <div class="text-xl font-bold text-red-700">${{ Number(stats.total).toFixed(2) }}</div>
        </div>
      </div>

      <!-- ===== FORMULARIO COMPACTO ===== -->
      <div class="card bg-base-100 shadow border border-gray-200 rounded-lg">
        <div class="card-body p-4 space-y-3">

          <!-- Fila 1: Fechas + Estado + Tipo Servicio -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Fecha Emisión</span></label>
              <input v-model="formData.issue_date" type="date" class="input input-bordered input-sm w-full" />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Inicio Período *</span></label>
              <input v-model="formData.period_start" type="date" class="input input-bordered input-sm w-full" :class="{ 'input-error': !formData.period_start }" required />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Fin Período</span></label>
              <input v-model="formData.period_end" type="date" class="input input-bordered input-sm w-full" />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Estado</span></label>
              <select v-model="formData.status" class="select select-bordered select-sm w-full">
                <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
          </div>

          <!-- Fila 2: Secuencia + Tipo Servicio -->
          <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Código Serie</span></label>
              <input v-model="formData.series_code" type="text" class="input input-bordered input-sm w-full" placeholder="PSL-PS-0000-0000" />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Prefijo</span></label>
              <input v-model="formData.secuence_prefix" type="text" class="input input-bordered input-sm w-full" placeholder="PSL-PS" />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Año</span></label>
              <input v-model.number="formData.secuence_year" type="number" class="input input-bordered input-sm w-full" min="2020" />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Nº Secuencia</span></label>
              <input v-model.number="formData.secuence_number" type="number" class="input input-bordered input-sm w-full" min="0" />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Tipo Servicio *</span></label>
              <select v-model="formData.service_type" class="select select-bordered select-sm w-full" required>
                <option v-for="opt in serviceTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
          </div>

          <!-- Fila 3: Contacto + Referencias -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Contacto</span></label>
              <input v-model="formData.contact_reference" type="text" class="input input-bordered input-sm w-full" placeholder="Nombre contacto" />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Teléfono</span></label>
              <input v-model="formData.contact_phone_reference" type="text" class="input input-bordered input-sm w-full" placeholder="+593..." />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">PO Cliente</span></label>
              <input v-model="formData.client_po_reference" type="text" class="input input-bordered input-sm w-full" placeholder="PO-2026-001" />
            </div>
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Ref. Factura</span></label>
              <input v-model="formData.invoice_reference" type="text" class="input input-bordered input-sm w-full" placeholder="FAC-2026-001" />
            </div>
          </div>

          <!-- Fila 4: Disposición final -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="form-control">
              <label class="label py-0.5"><span class="label-text text-xs font-semibold">Disposición Final</span></label>
              <input v-model="formData.final_disposition_reference" type="text" class="input input-bordered input-sm w-full" placeholder="Planta de Tratamiento" />
            </div>
          </div>

        </div>
      </div>

      <!-- ===== RECURSOS ASIGNADOS ===== -->
      <div class="card bg-base-100 shadow border border-gray-200 rounded-lg mt-3">
        <div class="card-body p-4">
          <h3 class="text-sm font-bold text-gray-700 mb-2 flex items-center gap-1">
            <i class="las la-tools text-base"></i> Recursos Asignados ({{ resources.length }})
          </h3>
          <div class="overflow-x-auto">
            <table class="table table-zebra w-full table-xs">
              <thead>
                <tr class="bg-lime-800 text-white text-center text-xs">
                  <th class="border">#</th>
                  <th class="border">Código</th>
                  <th class="border">Nombre</th>
                  <th class="border">Tipo</th>
                  <th class="border">Costo</th>
                  <th class="border">Fecha Inicio</th>
                  <th class="border">Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="resources.length === 0">
                  <td colspan="7" class="text-center py-3 text-gray-500 text-xs">
                    No hay recursos asignados al proyecto
                  </td>
                </tr>
                <tr v-for="(resource, index) in resources" :key="resource.id">
                  <td class="border text-center">{{ index + 1 }}</td>
                  <td class="border">{{ resource.resource_item_code || 'N/A' }}</td>
                  <td class="border">{{ resource.resource_item_name || 'N/A' }}</td>
                  <td class="border text-center">
                    <span class="badge badge-xs" :class="resource.type_resource === 'EQUIPO' ? 'badge-primary' : 'badge-info'">
                      {{ resource.type_resource }}
                    </span>
                  </td>
                  <td class="border text-right">${{ parseFloat(resource.cost || 0).toFixed(2) }}</td>
                  <td class="border text-center">{{ resource.operation_start_date ? new Date(resource.operation_start_date).toLocaleDateString('es-EC') : 'N/A' }}</td>
                  <td class="border text-center">
                    <span class="badge badge-xs" :class="resource.is_active ? 'badge-success' : 'badge-error'">
                      {{ resource.is_active ? 'Activo' : 'Inactivo' }}
                    </span>
                  </td>
                </tr>
              </tbody>
              <tfoot v-if="resources.length > 0">
                <tr class="bg-gray-200 font-semibold text-xs">
                  <td colspan="4" class="border text-right">Total recursos:</td>
                  <td class="border text-right">${{ resources.reduce((s, r) => s + parseFloat(r.cost || 0), 0).toFixed(2) }}</td>
                  <td colspan="2" class="border text-center">{{ resources.length }} recursos</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>

      <!-- ===== PIE: Totales financieros + Botones ===== -->
      <div class="flex items-center justify-between mt-3 bg-base-100 border border-gray-200 rounded-lg shadow p-3">
        <!-- Totales financieros -->
        <div class="flex gap-6 text-sm">
          <div>
            <span class="text-gray-500 text-xs">Subtotal:</span>
            <span class="font-bold ml-1">${{ Number(stats.subtotal).toFixed(2) }}</span>
          </div>
          <div>
            <span class="text-gray-500 text-xs">IVA:</span>
            <span class="font-bold ml-1">${{ Number(stats.tax_amount).toFixed(2) }}</span>
          </div>
          <div>
            <span class="text-gray-500 text-xs">Total:</span>
            <span class="font-bold text-red-700 ml-1">${{ Number(stats.total).toFixed(2) }}</span>
          </div>
        </div>
        <!-- Botones -->
        <div class="flex gap-2">
          <RouterLink to="/project" class="btn btn-ghost btn-sm" :class="{ 'btn-disabled': isSubmitting }">
            <i class="las la-times"></i> Cancelar
          </RouterLink>
          <button type="submit" class="btn btn-primary btn-sm" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="loading loading-spinner loading-xs"></span>
            <i v-else class="las la-save"></i>
            {{ isSubmitting ? 'Creando...' : 'Crear Planilla' }}
          </button>
        </div>
      </div>

    </form>
  </div>
</template>
