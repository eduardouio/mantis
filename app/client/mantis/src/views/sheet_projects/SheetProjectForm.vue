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
  invoice_reference: '',
  notes: ''
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

// Solo mostrar recursos activos
const activeResources = computed(() => resources.value.filter(r => r.is_active));

// Recursos seleccionados (is_selected === true)
const selectedResources = computed(() => activeResources.value.filter(r => r.is_selected));

const allSelected = computed(() => {
  return activeResources.value.length > 0 && 
         activeResources.value.every(r => r.is_selected);
});

// Métodos de selección usando is_selected del recurso
const toggleSelectAll = () => {
  const newValue = !allSelected.value;
  activeResources.value.forEach(r => { r.is_selected = newValue; });
};

const toggleResourceSelection = (resource) => {
  resource.is_selected = !resource.is_selected;
};

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
  
  // Seleccionar automáticamente todos los recursos activos
  resources.value
    .filter(r => r.is_active)
    .forEach(r => { r.is_selected = true; });
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
    
    if (selectedResources.value.length === 0) {
      throw new Error('Debes seleccionar al menos un recurso para la planilla');
    }
    
    // Construir payload con recursos seleccionados
    const resourcesPayload = selectedResources.value.map(r => ({
      id: r.id,
      resource_item_code: r.resource_item_code,
      resource_item_name: r.resource_item_name,
      type_resource: r.type_resource,
      cost: r.cost,
      maintenance_cost: r.maintenance_cost,
      operation_start_date: r.operation_start_date,
      is_active: r.is_active,
      is_selected: r.is_selected
    }));

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
      invoice_reference: formData.value.invoice_reference || null,
      notes: formData.value.notes || null,
      total_gallons: stats.value.total_gallons,
      total_barrels: stats.value.total_barrels,
      total_cubic_meters: stats.value.total_cubic_meters,
      subtotal: stats.value.subtotal,
      tax_amount: stats.value.tax_amount,
      total: stats.value.total,
      selected_resources: resourcesPayload
    };
    
    // Mostrar JSON para validación antes de enviar
    console.log('=== PAYLOAD PLANILLA ===');
    console.log(JSON.stringify(sheetProject, null, 2));
    
    // TODO: Descomentar cuando el backend esté listo
    // const sheetId = await sheetProjectStore.addSheetProject(sheetProject);
    successMessage.value = 'JSON generado — revisa la consola del navegador para validar el payload.';
    
    // setTimeout(() => {
    //   router.push({ name: 'projects-detail' });
    // }, 1500);
  } catch (error) {
    console.error('Error al crear planilla:', error);
    errorMessage.value = error.message || 'Error al crear la planilla';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="container mx-auto p-4">

    <!-- Mensaje de Error -->
    <div v-if="errorMessage" class="alert alert-error shadow-lg mb-4">
      <div>
        <i class="las la-exclamation-circle text-2xl"></i>
        <span>{{ errorMessage }}</span>
      </div>
    </div>

    <!-- Mensaje de Éxito -->
    <div v-if="successMessage" class="alert alert-success shadow-lg mb-4">
      <div>
        <i class="las la-check-circle text-2xl"></i>
        <span>{{ successMessage }}</span>
      </div>
    </div>
    
    <form @submit.prevent="handleSubmit" class="card bg-base-100 shadow-xl border border-gray-200 rounded-lg">
      <div class="card-body">

        <!-- ===== ENCABEZADO: Título + Botones PDF ===== -->
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
          <div>
            <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
              <i class="las la-file-invoice text-blue-600"></i>
              Planilla #{{ formData.id || 'Nueva' }} — Proyecto #{{ project?.id }}
            </h1>
            <p class="text-gray-600 text-sm mt-1">{{ project?.partner_name || '' }} · {{ project?.location || '' }}</p>
          </div>
          <div class="flex gap-2">
            <button type="button" @click="handleAttachSheetFile" class="btn btn-outline btn-info gap-2">
              <i class="las la-file-pdf text-xl"></i> Adjuntar Planilla PDF
            </button>
            <button type="button" @click="handleAttachCertificateFile" class="btn btn-outline btn-warning gap-2">
              <i class="las la-file-pdf text-xl"></i> Adjuntar Cert. Disp. Final
            </button>
          </div>
        </div>

        <!-- ===== ESTADÍSTICAS (solo lectura) ===== -->
        <div class="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg mb-4">
          <h3 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <i class="las la-chart-bar text-blue-600"></i>
            Estadísticas de la Planilla
          </h3>
          <div class="grid grid-cols-2 md:grid-cols-6 gap-3">
            <div class="bg-white p-3 rounded-lg shadow-sm text-center">
              <div class="text-xs text-gray-500 font-medium uppercase">Galones</div>
              <div class="text-2xl font-bold text-blue-700 mt-1">{{ stats.total_gallons }}</div>
            </div>
            <div class="bg-white p-3 rounded-lg shadow-sm text-center">
              <div class="text-xs text-gray-500 font-medium uppercase">Barriles</div>
              <div class="text-2xl font-bold text-green-700 mt-1">{{ stats.total_barrels }}</div>
            </div>
            <div class="bg-white p-3 rounded-lg shadow-sm text-center">
              <div class="text-xs text-gray-500 font-medium uppercase">m³</div>
              <div class="text-2xl font-bold text-purple-700 mt-1">{{ stats.total_cubic_meters }}</div>
            </div>
            <div class="bg-white p-3 rounded-lg shadow-sm text-center">
              <div class="text-xs text-gray-500 font-medium uppercase">Subtotal</div>
              <div class="text-2xl font-bold text-gray-700 mt-1">${{ Number(stats.subtotal).toFixed(2) }}</div>
            </div>
            <div class="bg-white p-3 rounded-lg shadow-sm text-center">
              <div class="text-xs text-gray-500 font-medium uppercase">IVA</div>
              <div class="text-2xl font-bold text-orange-600 mt-1">${{ Number(stats.tax_amount).toFixed(2) }}</div>
            </div>
            <div class="bg-white p-3 rounded-lg shadow-sm text-center">
              <div class="text-xs text-gray-500 font-medium uppercase">Total</div>
              <div class="text-2xl font-bold text-red-700 mt-1">${{ Number(stats.total).toFixed(2) }}</div>
            </div>
          </div>
        </div>

        <div class="divider">Información de la Planilla</div>

        <!-- Fila 1: Fechas + Estado + Tipo Servicio (4 columnas) -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Fecha Emisión</span>
            </label>
            <input v-model="formData.issue_date" type="date" class="input input-bordered w-full" />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Inicio Período *</span>
            </label>
            <input 
              v-model="formData.period_start" 
              type="date" 
              class="input input-bordered w-full" 
              :class="{ 'input-error': !formData.period_start }" 
              required 
            />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Fin Período</span>
            </label>
            <input v-model="formData.period_end" type="date" class="input input-bordered w-full" />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Estado</span>
            </label>
            <select v-model="formData.status" class="select select-bordered w-full">
              <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </div>

        <div class="divider">Código de Serie y Secuencia</div>

        <!-- Fila 2: Código Serie + Prefijo + Año + Número (4 columnas) -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Código Serie</span>
            </label>
            <input v-model="formData.series_code" type="text" class="input input-bordered w-full" placeholder="PSL-PS-0000-0000" />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Prefijo</span>
            </label>
            <input v-model="formData.secuence_prefix" type="text" class="input input-bordered w-full" placeholder="PSL-PS" />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Año</span>
            </label>
            <input v-model.number="formData.secuence_year" type="number" class="input input-bordered w-full" min="2020" />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Nº Secuencia</span>
            </label>
            <input v-model.number="formData.secuence_number" type="number" class="input input-bordered w-full" min="0" />
          </div>
        </div>

        <div class="divider">Tipo de Servicio y Contacto</div>

        <!-- Fila 3: Tipo Servicio + Contacto + Teléfono + PO (4 columnas) -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Tipo Servicio *</span>
            </label>
            <select v-model="formData.service_type" class="select select-bordered w-full" required>
              <option v-for="opt in serviceTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Contacto</span>
            </label>
            <input v-model="formData.contact_reference" type="text" class="input input-bordered w-full" placeholder="Nombre contacto" />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Teléfono</span>
            </label>
            <input v-model="formData.contact_phone_reference" type="text" class="input input-bordered w-full" placeholder="+593..." />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">PO Cliente</span>
            </label>
            <input v-model="formData.client_po_reference" type="text" class="input input-bordered w-full" placeholder="PO-2026-001" />
          </div>
        </div>

        <div class="divider">Referencias Adicionales</div>

        <!-- Fila 4: Ref. Factura + Disposición Final (4 columnas, dejando 2 vacías) -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Ref. Factura</span>
            </label>
            <input v-model="formData.invoice_reference" type="text" class="input input-bordered w-full" placeholder="FAC-2026-001" />
          </div>
          <div class="form-control w-full md:col-span-3">
            <label class="label">
              <span class="label-text font-semibold">Disposición Final</span>
            </label>
            <input v-model="formData.final_disposition_reference" type="text" class="input input-bordered w-full" placeholder="Planta de Tratamiento" />
          </div>
        </div>

        <div class="divider">Recursos Asignados al Proyecto</div>

        <!-- Badge informativo -->
        <div class="alert" :class="selectedResources.length > 0 ? 'alert-info' : 'alert-warning'">
          <i class="las text-xl" :class="selectedResources.length > 0 ? 'la-info-circle' : 'la-exclamation-triangle'"></i>
          <div>
            <h3 class="font-bold">Recursos Seleccionados</h3>
            <p class="text-sm">
              {{ selectedResources.length > 0 
                ? `Has seleccionado ${selectedResources.length} de ${activeResources.length} recurso(s) activos para esta planilla.` 
                : 'Selecciona al menos un recurso activo para incluir en la planilla.' 
              }}
            </p>
          </div>
        </div>

        <!-- Tabla de Recursos -->
        <div class="overflow-x-auto">
          <table class="table table-zebra w-full">
            <thead>
              <tr class="bg-lime-800 text-white text-center">
                <th class="border">
                  <input 
                    type="checkbox" 
                    class="checkbox checkbox-sm" 
                    :checked="allSelected"
                    @change="toggleSelectAll"
                  />
                </th>
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
              <tr v-if="activeResources.length === 0">
                <td colspan="8" class="text-center py-4 text-gray-500">
                  No hay recursos activos asignados al proyecto
                </td>
              </tr>
              <tr v-for="(resource, index) in activeResources" :key="resource.id">
                <td class="border text-center">
                  <input 
                    type="checkbox" 
                    class="checkbox checkbox-sm" 
                    :checked="resource.is_selected"
                    @change="toggleResourceSelection(resource)"
                  />
                </td>
                <td class="border text-center">{{ index + 1 }}</td>
                <td class="border">{{ resource.resource_item_code || 'N/A' }}</td>
                <td class="border">{{ resource.resource_item_name || 'N/A' }}</td>
                <td class="border text-center">
                  <span 
                    class="badge badge-sm" 
                    :class="resource.type_resource === 'EQUIPO' ? 'badge-primary' : 'badge-info'"
                  >
                    {{ resource.type_resource }}
                  </span>
                </td>
                <td class="border text-right">${{ parseFloat(resource.cost || 0).toFixed(2) }}</td>
                <td class="border text-center">
                  {{ resource.operation_start_date ? new Date(resource.operation_start_date).toLocaleDateString('es-EC') : 'N/A' }}
                </td>
                <td class="border text-center">
                  <span 
                    class="badge badge-sm" 
                    :class="resource.is_active ? 'badge-success' : 'badge-error'"
                  >
                    {{ resource.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
              </tr>
            </tbody>
            <tfoot v-if="activeResources.length > 0">
              <tr class="bg-gray-200 font-semibold">
                <td class="border text-center">
                  <span class="badge badge-sm badge-primary">{{ selectedResources.length }}</span>
                </td>
                <td colspan="4" class="border text-right">Total recursos seleccionados:</td>
                <td class="border text-right">${{ selectedResources.reduce((s, r) => s + parseFloat(r.cost || 0), 0).toFixed(2) }}</td>
                <td colspan="2" class="border text-center">{{ activeResources.length }} activos</td>
              </tr>
            </tfoot>
          </table>
        </div>

        <div class="divider">Notas Adicionales</div>

        <!-- Campo de Notas -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text font-semibold">Notas</span>
            <span class="label-text-alt text-gray-500">{{ formData.notes.length }}/500</span>
          </label>
          <textarea 
            v-model="formData.notes" 
            class="textarea textarea-bordered w-full h-24" 
            placeholder="Ingrese notas adicionales sobre la planilla..."
            maxlength="500"
          ></textarea>
        </div>

        <div class="divider"></div>

        <!-- ===== PIE: Totales financieros + Botones ===== -->
        <div class="bg-gray-50 p-4 rounded-lg flex items-center justify-between">
          <!-- Totales financieros -->
          <div class="flex gap-6 text-sm">
            <div>
              <span class="text-gray-600 font-medium">Subtotal:</span>
              <span class="font-bold text-lg ml-2">${{ Number(stats.subtotal).toFixed(2) }}</span>
            </div>
            <div>
              <span class="text-gray-600 font-medium">IVA:</span>
              <span class="font-bold text-lg ml-2">${{ Number(stats.tax_amount).toFixed(2) }}</span>
            </div>
            <div>
              <span class="text-gray-600 font-medium">Total:</span>
              <span class="font-bold text-xl text-red-700 ml-2">${{ Number(stats.total).toFixed(2) }}</span>
            </div>
          </div>
          <!-- Botones -->
          <div class="flex gap-3">
            <RouterLink to="/project" class="btn btn-ghost" :class="{ 'btn-disabled': isSubmitting }">
              <i class="las la-times text-lg"></i> Cancelar
            </RouterLink>
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
              <i v-else class="las la-save text-lg"></i>
              {{ isSubmitting ? 'Creando...' : 'Crear Planilla' }}
            </button>
          </div>
        </div>

      </div>
    </form>
  </div>
</template>
