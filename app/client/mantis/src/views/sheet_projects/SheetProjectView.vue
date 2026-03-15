<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { UseProjectStore } from '@/stores/ProjectStore';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';
import { UseMaintenanceSheetStore } from '@/stores/MaintenanceSheetStore';
import { appConfig } from '@/AppConfig';
import { formatDate } from '@/utils/formatters';
import { useTableFilter } from '@/composables/useTableFilter';
import TableControls from '@/components/common/TableControls.vue';

const route = useRoute();
const router = useRouter();
const projectStore = UseProjectStore();
const sheetProjectsStore = UseSheetProjectsStore();
const maintenanceStore = UseMaintenanceSheetStore();
const activeTab = ref('custody');

// Obtener el ID de la planilla desde la ruta
const sheetId = computed(() => parseInt(route.params.id));

// Obtener datos del proyecto desde el store
const project = computed(() => projectStore.project);

// Obtener la planilla específica
const sheetProject = computed(() => {
  return sheetProjectsStore.getSheetProjectById(sheetId.value);
});

// Obtener cadenas de custodia de la planilla
const custodyChains = computed(() => {
  return sheetProjectsStore.getCustodyChainsForSheet(sheetId.value);
});

// Hojas de mantenimiento de la planilla
const maintenanceSheets = computed(() => maintenanceStore.sheets || []);

// Tabla con filtrado para cadenas de custodia
const custodyTableFilter = useTableFilter(custodyChains, {
  searchFields: ['consecutive', 'status', 'location', 'activity_date'],
  searchTransform: (cc) => [
    cc.consecutive, cc.status, cc.location, cc.activity_date,
    cc.technical?.first_name, cc.technical?.last_name,
    cc.vehicle?.no_plate, cc.vehicle?.brand
  ].filter(Boolean).join(' '),
  pageSize: 10
});

// Tabla con filtrado para hojas de mantenimiento
const maintenanceTableFilter = useTableFilter(maintenanceSheets, {
  searchFields: ['sheet_number', 'status', 'maintenance_type', 'resource_item_name', 'responsible_technical_name'],
  pageSize: 10
});

// Verificar si la planilla está cerrada
const isSheetClosed = computed(() => {
  return sheetProject.value?.is_closed === true;
});

// Verificar si las cadenas de custodia están bloqueadas (LIQUIDATED, INVOICED, CANCELLED o is_closed)
const isCustodyLocked = computed(() => {
  if (project.value?.is_closed) return true;
  if (isSheetClosed.value) return true;
  const status = sheetProject.value?.status;
  return ['LIQUIDATED', 'INVOICED', 'CANCELLED'].includes(status);
});

// Mensaje descriptivo del bloqueo
const lockMessage = computed(() => {
  if (project.value?.is_closed) return 'PROYECTO CERRADO - SOLO LECTURA';
  if (isSheetClosed.value) return 'PLANILLA CERRADA - SOLO LECTURA';
  const status = sheetProject.value?.status;
  if (status === 'LIQUIDATED') return 'PLANILLA LIQUIDADA - CADENAS BLOQUEADAS';
  if (status === 'INVOICED') return 'PLANILLA FACTURADA - SOLO LECTURA';
  if (status === 'CANCELLED') return 'PLANILLA CANCELADA - SOLO LECTURA';
  return '';
});

const formatTime = (time) => {
  if (!time) return '--:--';
  return time;
};

const getStatusBadge = (status) => {
  const statusConfig = {
    'IN_PROGRESS': { text: 'EN EJECUCIÓN', class: 'badge-success' },
    'LIQUIDATED': { text: 'LIQUIDADO', class: 'badge-warning' },
    'INVOICED': { text: 'FACTURADO', class: 'badge-info' },
    'CANCELLED': { text: 'CANCELADO', class: 'badge-error' }
  };
  return statusConfig[status] || { text: status, class: 'badge-ghost' };
};

const getCustodyChainStatusBadge = (status) => {
  const statusConfig = {
    'DRAFT': { text: 'BORRADOR', class: 'badge-warning' },
    'CLOSE': { text: 'CERRADO', class: 'badge-success' }
  };
  return statusConfig[status] || { text: status, class: 'badge-ghost' };
};

const totalGallons = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + parseFloat(cc.total_gallons || 0), 0);
});

const totalBarrels = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + parseFloat(cc.total_barrels || 0), 0);
});

const totalCubicMeters = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + parseFloat(cc.total_cubic_meters || 0), 0);
});

const totalHours = computed(() => {
  return custodyChains.value.reduce((sum, cc) => sum + parseFloat(cc.time_duration || 0), 0).toFixed(2);
});

const goBack = () => {
  router.push({ name: 'projects-detail', query: { tab: 'planillas' } });
};

const reopenSheet = async () => {
  if (!confirm('¿Está seguro de reabrir esta planilla? Volverá a estado EN EJECUCIÓN.')) return;
  try {
    await sheetProjectsStore.reopenSheetProject(sheetId.value);
    alert('Planilla reabierta exitosamente');
  } catch (error) {
    alert('Error al reabrir la planilla: ' + error.message);
  }
};

const viewCustodyChainDetail = (id) => {
  router.push({ 
    name: 'custody-chain-form', 
    params: { id } 
  });
};

const createNewCustodyChain = () => {
  router.push({ 
    name: 'custody-chain-form',
    query: { sheet_id: sheetProject.value?.id }
  });
};

const viewCustodyChainPDF = (id) => {
  const pdfUrl = appConfig.PDFCustodyChainReport.replace('${id}', id);
  window.open(pdfUrl, '_blank');
};

// ── Mantenimiento ──
const createNewMaintenanceSheet = () => {
  router.push({
    name: 'maintenance-sheet-form',
    query: { sheet_id: sheetProject.value?.id }
  });
};

const viewMaintenanceSheetDetail = (id) => {
  router.push({
    name: 'maintenance-sheet-form',
    params: { id }
  });
};

const viewMaintenanceSheetPDF = (id) => {
  const pdfUrl = appConfig.URLMaintenanceSheetDownload.replace('${id}', id);
  window.open(pdfUrl, '_blank');
};

const getMaintenanceStatusBadge = (status) => {
  const statusConfig = {
    'DRAFT': { text: 'BORRADOR', class: 'badge-warning' },
    'CLOSED': { text: 'CERRADO', class: 'badge-success' },
    'VOID': { text: 'ANULADO', class: 'badge-error' }
  };
  return statusConfig[status] || { text: status, class: 'badge-ghost' };
};

// ── Archivos adjuntos ──
const sheetFileInput = ref(null);
const certificateFileInput = ref(null);
const invoiceFileInput = ref(null);
const labAnalysisFileInput = ref(null);
const sheetFileInfo = ref(null);
const certificateFileInfo = ref(null);
const invoiceFileInfo = ref(null);
const labAnalysisFileInfo = ref(null);
const isUploadingSheet = ref(false);
const isUploadingCertificate = ref(false);
const isUploadingInvoice = ref(false);
const isUploadingLabAnalysis = ref(false);
const showInvoiceModal = ref(false);
const invoiceReference = ref('');
const fileMessage = ref('');
const fileMessageType = ref('');

const isHeadersLocked = computed(() => {
  if (project.value?.is_closed) return true;
  if (isSheetClosed.value) return true;
  const status = sheetProject.value?.status;
  return ['INVOICED', 'CANCELLED'].includes(status);
});

const handleAttachSheetFile = () => {
  if (isHeadersLocked.value && sheetFileInfo.value?.has_file) return;
  sheetFileInput.value?.click();
};

const onSheetFileSelected = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.type !== 'application/pdf') {
    fileMessage.value = 'Solo se permiten archivos PDF';
    fileMessageType.value = 'error';
    setTimeout(() => { fileMessage.value = ''; }, 4000);
    return;
  }
  isUploadingSheet.value = true;
  try {
    const result = await sheetProjectsStore.uploadSheetFile(sheetId.value, 'sheet_project_file', file);
    sheetFileInfo.value = result;
    fileMessage.value = 'Archivo de planilla subido correctamente';
    fileMessageType.value = 'success';
    setTimeout(() => { fileMessage.value = ''; }, 3000);
  } catch (error) {
    fileMessage.value = error.message || 'Error al subir el archivo';
    fileMessageType.value = 'error';
    setTimeout(() => { fileMessage.value = ''; }, 4000);
  } finally {
    isUploadingSheet.value = false;
    event.target.value = '';
  }
};

const handleAttachCertificateFile = () => {
  if (isHeadersLocked.value && certificateFileInfo.value?.has_file) return;
  certificateFileInput.value?.click();
};

const onCertificateFileSelected = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.type !== 'application/pdf') {
    fileMessage.value = 'Solo se permiten archivos PDF';
    fileMessageType.value = 'error';
    setTimeout(() => { fileMessage.value = ''; }, 4000);
    return;
  }
  isUploadingCertificate.value = true;
  try {
    const result = await sheetProjectsStore.uploadSheetFile(sheetId.value, 'certificate_final_disposition_file', file);
    certificateFileInfo.value = result;
    fileMessage.value = 'Certificado subido correctamente';
    fileMessageType.value = 'success';
    setTimeout(() => { fileMessage.value = ''; }, 3000);
  } catch (error) {
    fileMessage.value = error.message || 'Error al subir el certificado';
    fileMessageType.value = 'error';
    setTimeout(() => { fileMessage.value = ''; }, 4000);
  } finally {
    isUploadingCertificate.value = false;
    event.target.value = '';
  }
};

const handleAttachLabAnalysisFile = () => {
  if (isHeadersLocked.value && labAnalysisFileInfo.value?.has_file) return;
  labAnalysisFileInput.value?.click();
};

const onLabAnalysisFileSelected = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.type !== 'application/pdf') {
    fileMessage.value = 'Solo se permiten archivos PDF';
    fileMessageType.value = 'error';
    setTimeout(() => { fileMessage.value = ''; }, 4000);
    return;
  }
  isUploadingLabAnalysis.value = true;
  try {
    const result = await sheetProjectsStore.uploadSheetFile(sheetId.value, 'laboratory_analysis_file', file);
    labAnalysisFileInfo.value = result;
    fileMessage.value = 'Análisis de laboratorio subido correctamente';
    fileMessageType.value = 'success';
    setTimeout(() => { fileMessage.value = ''; }, 3000);
  } catch (error) {
    fileMessage.value = error.message || 'Error al subir el análisis de laboratorio';
    fileMessageType.value = 'error';
    setTimeout(() => { fileMessage.value = ''; }, 4000);
  } finally {
    isUploadingLabAnalysis.value = false;
    event.target.value = '';
  }
};

const handleAttachInvoiceFile = () => {
  if (isHeadersLocked.value && invoiceFileInfo.value?.has_file) return;
  invoiceReference.value = '';
  showInvoiceModal.value = true;
};

const onInvoiceFileSelected = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.type !== 'application/pdf') {
    fileMessage.value = 'Solo se permiten archivos PDF';
    fileMessageType.value = 'error';
    setTimeout(() => { fileMessage.value = ''; }, 4000);
    return;
  }
  if (!invoiceReference.value.trim()) {
    fileMessage.value = 'Debe ingresar la referencia de factura';
    fileMessageType.value = 'error';
    setTimeout(() => { fileMessage.value = ''; }, 4000);
    return;
  }
  isUploadingInvoice.value = true;
  try {
    const result = await sheetProjectsStore.uploadSheetFile(
      sheetId.value, 'invoice_file', file, { invoice_reference: invoiceReference.value.trim() }
    );
    invoiceFileInfo.value = result;
    fileMessage.value = 'Factura subida correctamente. Estado cambiado a FACTURADO.';
    fileMessageType.value = 'success';
    showInvoiceModal.value = false;
    setTimeout(() => { fileMessage.value = ''; }, 4000);
  } catch (error) {
    fileMessage.value = error.message || 'Error al subir la factura';
    fileMessageType.value = 'error';
    setTimeout(() => { fileMessage.value = ''; }, 4000);
  } finally {
    isUploadingInvoice.value = false;
    event.target.value = '';
  }
};

const openFile = (fileInfo) => {
  if (fileInfo?.file_url) {
    window.open(appConfig.apiBaseUrl + fileInfo.file_url, '_blank');
  }
};

const loadFileInfo = async () => {
  try {
    const [sheetInfo, certInfo, invoiceInfo, labInfo] = await Promise.all([
      sheetProjectsStore.getSheetFileInfo(sheetId.value, 'sheet_project_file'),
      sheetProjectsStore.getSheetFileInfo(sheetId.value, 'certificate_final_disposition_file'),
      sheetProjectsStore.getSheetFileInfo(sheetId.value, 'invoice_file'),
      sheetProjectsStore.getSheetFileInfo(sheetId.value, 'laboratory_analysis_file')
    ]);
    sheetFileInfo.value = sheetInfo;
    certificateFileInfo.value = certInfo;
    invoiceFileInfo.value = invoiceInfo;
    labAnalysisFileInfo.value = labInfo;
  } catch (error) {
    console.error('Error consultando archivos:', error);
  }
};

onMounted(async () => {
  // Si no hay datos, cargar el proyecto completo
  if (!project.value.id) {
    await projectStore.fetchProjectData();
  }
  // Cargar hojas de mantenimiento de esta planilla
  await maintenanceStore.fetchSheetsBySheetProject(sheetId.value);
  // Cargar información de archivos adjuntos
  await loadFileInfo();
});
</script>

<template>
  <div class="w-[95%] mx-auto p-4">
    <!-- Header con información del proyecto y planilla -->
    <div class="bg-white rounded-2xl shadow-md border border-blue-300 border-t-[15px] border-t-blue-300 p-6 mb-6">
      <div class="flex justify-between items-center border-b-blue-500 border-b pb-3 mb-4">
        <h1 class="text-xl font-semibold text-blue-500">
          <i class="las la-file-invoice text-2xl"></i>
          Planilla {{ sheetProject?.series_code || 'N/A' }}
        </h1>
        <div class="flex gap-3">
          <div 
            v-if="isCustodyLocked"
            class="text-orange-700 badge bg-orange-100 px-4 py-3"
          >
            <i class="las la-lock"></i>
            {{ lockMessage }}
          </div>
          <button
            v-if="sheetProject?.status === 'LIQUIDATED' && !isSheetClosed"
            @click="reopenSheet"
            class="btn btn-warning btn-sm"
          >
            <i class="las la-lock-open"></i>
            Abrir Planilla
          </button>
          <a
            :href="appConfig.URLWorkSheetReport.replace('${id}', sheetId)"
            target="_blank"
            class="btn btn-success btn-sm"
            title="Descargar reporte PDF de la planilla"
          >
            <i class="las la-file-pdf"></i>
            Descargar PDF
          </a>
          <button
            v-if="sheetProject?.status === 'IN_PROGRESS' && !isSheetClosed"
            @click="router.push({ name: 'sheet-project-form', params: { id: sheetId } })"
            class="btn btn-primary btn-sm"
          >
            <i class="las la-edit"></i>
            Editar Planilla
          </button>
          <button @click="goBack" class="btn btn-outline btn-sm">
            <i class="las la-arrow-left"></i>
            Volver
          </button>
        </div>
      </div>

      <!-- Botones de Archivos Adjuntos + Serie -->
      <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div class="flex flex-wrap items-center gap-2">
          <!-- Input oculto para planilla PDF -->
          <input type="file" ref="sheetFileInput" accept=".pdf" class="hidden" @change="onSheetFileSelected" />
          <!-- Input oculto para certificado PDF -->
          <input type="file" ref="certificateFileInput" accept=".pdf" class="hidden" @change="onCertificateFileSelected" />
          <!-- Input oculto para análisis de laboratorio PDF -->
          <input type="file" ref="labAnalysisFileInput" accept=".pdf" class="hidden" @change="onLabAnalysisFileSelected" />

          <!-- Botón Planilla PDF -->
          <div class="flex items-center gap-1">
            <button 
              type="button" 
              @click="handleAttachSheetFile" 
              class="btn btn-info btn-sm gap-1"
              :class="{ 'btn-disabled': isUploadingSheet || (isHeadersLocked && sheetFileInfo?.has_file) }"
              :disabled="isUploadingSheet || (isHeadersLocked && sheetFileInfo?.has_file)"
            >
              <span v-if="isUploadingSheet" class="loading loading-spinner loading-xs"></span>
              <i v-else class="las la-file-pdf text-lg"></i>
              {{ sheetFileInfo?.has_file ? (isHeadersLocked ? 'Planilla (Bloqueado)' : 'Actualizar Planilla') : 'Adjuntar Planilla' }}
            </button>
            <button 
              v-if="sheetFileInfo?.has_file" 
              type="button" 
              @click="openFile(sheetFileInfo)" 
              class="btn btn-ghost btn-sm btn-circle"
              title="Ver planilla PDF"
            >
              <i class="las la-eye text-lg text-info"></i>
            </button>
            <span v-if="sheetFileInfo?.has_file" class="badge badge-success badge-sm gap-1">
              <i class="las la-check-circle"></i> PDF
            </span>
          </div>

          <!-- Botón Certificado Disposición Final -->
          <div class="flex items-center gap-1">
            <button 
              type="button" 
              @click="handleAttachCertificateFile" 
              class="btn btn-warning btn-sm gap-1"
              :class="{ 'btn-disabled': isUploadingCertificate || (isHeadersLocked && certificateFileInfo?.has_file) }"
              :disabled="isUploadingCertificate || (isHeadersLocked && certificateFileInfo?.has_file)"
            >
              <span v-if="isUploadingCertificate" class="loading loading-spinner loading-xs"></span>
              <i v-else class="las la-file-pdf text-lg"></i>
              {{ certificateFileInfo?.has_file ? (isHeadersLocked ? 'Cert. (Bloqueado)' : 'Actualizar Cert.') : 'Adjuntar Cert.' }}
            </button>
            <button 
              v-if="certificateFileInfo?.has_file" 
              type="button" 
              @click="openFile(certificateFileInfo)" 
              class="btn btn-ghost btn-sm btn-circle"
              title="Ver certificado de disposición final"
            >
              <i class="las la-eye text-lg text-warning"></i>
            </button>
            <span v-if="certificateFileInfo?.has_file" class="badge badge-success badge-sm gap-1">
              <i class="las la-check-circle"></i> PDF
            </span>
          </div>

          <!-- Botón Análisis de Laboratorio -->
          <div class="flex items-center gap-1">
            <button 
              type="button" 
              @click="handleAttachLabAnalysisFile" 
              class="btn btn-secondary btn-sm gap-1"
              :class="{ 'btn-disabled': isUploadingLabAnalysis || (isHeadersLocked && labAnalysisFileInfo?.has_file) }"
              :disabled="isUploadingLabAnalysis || (isHeadersLocked && labAnalysisFileInfo?.has_file)"
            >
              <span v-if="isUploadingLabAnalysis" class="loading loading-spinner loading-xs"></span>
              <i v-else class="las la-flask text-lg"></i>
              {{ labAnalysisFileInfo?.has_file ? (isHeadersLocked ? 'Lab. (Bloqueado)' : 'Actualizar Lab.') : 'Adjuntar Lab.' }}
            </button>
            <button 
              v-if="labAnalysisFileInfo?.has_file" 
              type="button" 
              @click="openFile(labAnalysisFileInfo)" 
              class="btn btn-ghost btn-sm btn-circle"
              title="Ver análisis de laboratorio"
            >
              <i class="las la-eye text-lg text-secondary"></i>
            </button>
            <span v-if="labAnalysisFileInfo?.has_file" class="badge badge-success badge-sm gap-1">
              <i class="las la-check-circle"></i> PDF
            </span>
          </div>

          <!-- Botón Factura PDF -->
          <div class="flex items-center gap-1">
            <button 
              type="button" 
              @click="handleAttachInvoiceFile" 
              class="btn btn-accent btn-sm gap-1"
              :class="{ 'btn-disabled': isUploadingInvoice || (isHeadersLocked && invoiceFileInfo?.has_file) }"
              :disabled="isUploadingInvoice || (isHeadersLocked && invoiceFileInfo?.has_file)"
            >
              <span v-if="isUploadingInvoice" class="loading loading-spinner loading-xs"></span>
              <i v-else class="las la-file-invoice text-lg"></i>
              {{ invoiceFileInfo?.has_file ? (isHeadersLocked ? 'Factura (Bloqueado)' : 'Actualizar Factura') : 'Adjuntar Factura' }}
            </button>
            <button 
              v-if="invoiceFileInfo?.has_file" 
              type="button" 
              @click="openFile(invoiceFileInfo)" 
              class="btn btn-ghost btn-sm btn-circle"
              title="Ver factura PDF"
            >
              <i class="las la-eye text-lg text-accent"></i>
            </button>
            <span v-if="invoiceFileInfo?.has_file" class="badge badge-success badge-sm gap-1">
              <i class="las la-check-circle"></i> PDF
            </span>
          </div>
        </div>

        <!-- Serie Code -->
        <div class="font-bold text-red-800 font-mono text-lg border border-gray-300 rounded px-4 py-1">
          {{ sheetProject?.series_code || 'N/A' }}
        </div>
      </div>

      <!-- Mensaje de archivo -->
      <div v-if="fileMessage" class="alert shadow-sm mb-4" :class="fileMessageType === 'success' ? 'alert-success' : 'alert-error'">
        <i class="las" :class="fileMessageType === 'success' ? 'la-check-circle' : 'la-exclamation-triangle'"></i>
        <span>{{ fileMessage }}</span>
      </div>

      <!-- Información de Proyecto y Planilla en Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Información del Proyecto -->
        <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <h3 class="font-semibold text-blue-700 mb-3 flex items-center gap-2">
            <i class="las la-building"></i>
            Información del Proyecto #{{ project?.id || 'N/A' }}
          </h3>
          <div class="space-y-2 text-sm">
            <div>
              <span class="font-medium">Cliente:</span>
              <span class="ml-2">{{ project?.partner_name || 'N/A' }}</span>
            </div>
            <div>
              <span class="font-medium">Ubicación:</span>
              <span class="ml-2">{{ project?.location || 'N/A' }}{{ project?.cardinal_point ? ' - ' + project.cardinal_point : '' }}</span>
            </div>
            <div>
              <span class="font-medium">Contacto:</span>
              <span class="ml-2">{{ project?.contact_name || 'N/A' }} ({{ project?.contact_phone || 'N/A' }})</span>
            </div>
            <div>
              <span class="font-medium">Fecha Inicio:</span>
              <span class="ml-2">{{ formatDate(project?.start_date) }}</span>
            </div>
          </div>
        </div>

        <!-- Información de la Planilla -->
        <div class="bg-sky-50 rounded-lg p-4 border border-sky-200">
          <h3 class="font-semibold text-sky-700 mb-3 flex items-center gap-2">
            <i class="las la-file-invoice"></i>
            Información de la Planilla
          </h3>
          <div class="space-y-2 text-sm">
            <div>
              <span class="font-medium">Serie:</span>
              <span class="ml-2 font-mono">{{ sheetProject?.series_code || 'N/A' }}</span>
            </div>
            <div>
              <span class="font-medium">Estado:</span>
              <span class="ml-2 badge" :class="getStatusBadge(sheetProject?.status).class">
                {{ getStatusBadge(sheetProject?.status).text }}
              </span>
            </div>
            <div>
              <span class="font-medium">Tipo Servicio:</span>
              <span class="ml-2">{{ sheetProject?.service_type || 'N/A' }}</span>
            </div>
            <div>
              <span class="font-medium">Período:</span>
              <span class="ml-2">
                {{ formatDate(sheetProject?.period_start) }} - 
                {{ sheetProject?.period_end ? formatDate(sheetProject.period_end) : 'En curso' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs con colores -->
    <div class="bg-white rounded-xl shadow-md border border-gray-200 p-6">
      <div class="flex gap-1 mb-4 border-b border-gray-200">
        <button type="button"
          class="px-5 py-2.5 rounded-t-lg font-semibold text-sm transition-all flex items-center gap-2"
          :class="activeTab === 'custody'
            ? 'bg-blue-600 text-white shadow-sm'
            : 'bg-gray-100 text-gray-600 hover:bg-blue-50 hover:text-blue-600'"
          @click="activeTab = 'custody'">
          <i class="las la-link"></i> Cadenas de Custodia
          <span class="badge badge-xs ml-1" :class="activeTab === 'custody' ? 'badge-ghost text-white' : 'badge-primary'">{{ custodyChains.length }}</span>
        </button>
        <button type="button"
          class="px-5 py-2.5 rounded-t-lg font-semibold text-sm transition-all flex items-center gap-2"
          :class="activeTab === 'maintenance'
            ? 'bg-emerald-600 text-white shadow-sm'
            : 'bg-gray-100 text-gray-600 hover:bg-emerald-50 hover:text-emerald-600'"
          @click="activeTab = 'maintenance'">
          <i class="las la-tools"></i> Hojas de Mantenimiento
          <span class="badge badge-xs ml-1" :class="activeTab === 'maintenance' ? 'badge-ghost text-white' : 'badge-primary'">{{ maintenanceSheets.length }}</span>
        </button>
      </div>

      <!-- ═══ Tab: Cadenas de Custodia ═══ -->
      <div v-show="activeTab === 'custody'">
        <div class="flex justify-between items-center mb-4">
          <h2 class="font-semibold text-lg flex items-center gap-2 text-gray-800">
            <i class="las la-list text-blue-600"></i>
            Listado de Cadenas de Custodia ({{ custodyChains.length }})
          </h2>
          <button 
            v-if="sheetProject?.status === 'IN_PROGRESS' && !isSheetClosed"
            @click="createNewCustodyChain" 
            class="btn btn-primary btn-sm"
          >
            <i class="las la-plus"></i>
            Nueva Cadena de Custodia
          </button>
        </div>

      <TableControls :tableFilter="custodyTableFilter" position="top" searchPlaceholder="Buscar cadena de custodia..." />

      <div class="overflow-x-auto">
        <table class="table table-zebra w-full">
          <thead>
            <tr class="bg-gray-500 text-white">
              <th class="p-2 border border-gray-100 text-center">#</th>
              <th class="p-2 border border-gray-100 text-center">Consecutivo</th>
              <th class="p-2 border border-gray-100 text-center">Estado</th>
              <th class="p-2 border border-gray-100 text-center">Fecha Actividad</th>
              <th class="p-2 border border-gray-100 text-center">Ubicación</th>
              <th class="p-2 border border-gray-100 text-center">Técnico</th>
              <th class="p-2 border border-gray-100 text-center">Vehículo</th>
              <th class="p-2 border border-gray-100 text-center">Galones</th>
              <th class="p-2 border border-gray-100 text-center">Barriles</th>
              <th class="p-2 border border-gray-100 text-center">M³</th>
              <th class="p-2 border border-gray-100 text-center">Recursos</th>
              <th class="p-2 border border-gray-100 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="custodyChains.length === 0">
              <tr>
                <td colspan="12" class="text-center text-gray-500 py-8">
                  <i class="las la-inbox text-4xl"></i>
                  <p>No hay cadenas de custodia registradas para esta planilla</p>
                </td>
              </tr>
            </template>
            <template v-else-if="custodyTableFilter.paginatedData.value.length === 0">
              <tr>
                <td colspan="12" class="text-center text-gray-500 py-8">
                  <i class="las la-search text-4xl"></i>
                  <p>No se encontraron resultados para "{{ custodyTableFilter.searchQuery.value }}"</p>
                </td>
              </tr>
            </template>
            <template v-else>
              <tr v-for="cc in custodyTableFilter.paginatedData.value" :key="cc.id">
                <td class="p-2 border border-gray-300 text-center">{{ cc.id }}</td>
                <td class="p-2 border border-gray-300 font-mono">{{ cc.consecutive }}</td>
                <td class="p-2 border border-gray-300 text-center">
                  <span class="badge" :class="getCustodyChainStatusBadge(cc.status).class">
                    {{ getCustodyChainStatusBadge(cc.status).text }}
                  </span>
                </td>
                <td class="p-2 border border-gray-300 text-center">{{ formatDate(cc.activity_date) }}</td>
                <td class="p-2 border border-gray-300">{{ cc.location || 'N/A' }}</td>
                <td class="p-2 border border-gray-300">
                  <div class="text-xs" v-if="cc.technical">
                    <div class="font-semibold">{{ cc.technical.first_name }} {{ cc.technical.last_name }}</div>
                  </div>
                  <span v-else class="text-gray-400">N/A</span>
                </td>
                <td class="p-2 border border-gray-300">
                  <div class="text-xs" v-if="cc.vehicle">
                    <div class="font-semibold">{{ cc.vehicle.no_plate }}</div>
                    <div class="text-gray-500">{{ cc.vehicle.brand }}</div>
                  </div>
                  <span v-else class="text-gray-400">N/A</span>
                </td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ cc.total_gallons || 0 }}</td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ cc.total_barrels || 0 }}</td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ cc.total_cubic_meters || 0 }}</td>
                <td class="p-2 border border-gray-300 text-center">
                  <span class="badge badge-info">{{ cc.details_count || 0 }}</span>
                </td>
                <td class="p-2 border border-gray-300 text-end">
                  <div class="flex gap-2 justify-end">
                    <button 
                      @click="viewCustodyChainDetail(cc.id)"
                      class="btn btn-xs border-blue-500 text-teal-500 bg-white"
                      title="Ver detalle"
                    >
                      <i class="las la-eye"></i>
                      VER
                    </button>
                    <button 
                      @click="viewCustodyChainPDF(cc.id)"
                      class="btn btn-xs border-red-500 text-red-500 bg-white"
                      title="Generar PDF"
                    >
                      <i class="las la-file-pdf"></i>
                      PDF
                    </button>
                    <button 
                      @click="router.push({ name: 'custody-chain-form', params: { id: cc.id } })"
                      class="btn btn-xs border-orange-500 text-orange-500 bg-white"
                      title="Ver/Editar cadena"
                    >
                      <i class="las la-edit"></i>
                      {{ cc.status === 'CLOSE' ? 'VER/EDITAR' : 'EDITAR' }}
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
          <tfoot v-if="custodyChains.length > 0">
            <tr class="bg-gray-500 font-bold text-white">
              <td colspan="7" class="p-2 border border-gray-300 text-right">TOTALES:</td>
              <td class="p-2 border border-gray-300 text-right font-mono">{{ totalGallons.toFixed(2) }}</td>
              <td class="p-2 border border-gray-300 text-right font-mono">{{ totalBarrels.toFixed(2) }}</td>
              <td class="p-2 border border-gray-300 text-right font-mono">{{ totalCubicMeters.toFixed(2) }}</td>
              <td colspan="2" class="p-2 border border-gray-300"></td>
            </tr>
          </tfoot>
        </table>
      </div>

        <TableControls :tableFilter="custodyTableFilter" position="bottom" />
      </div>

      <!-- ═══ Tab: Hojas de Mantenimiento ═══ -->
      <div v-show="activeTab === 'maintenance'">
        <div class="flex justify-between items-center mb-4">
          <h2 class="font-semibold text-lg flex items-center gap-2 text-gray-800">
            <i class="las la-tools text-emerald-600"></i>
            Hojas de Mantenimiento ({{ maintenanceSheets.length }})
          </h2>
          <button
            v-if="sheetProject?.status === 'IN_PROGRESS' && !isSheetClosed"
            @click="createNewMaintenanceSheet"
            class="btn btn-primary btn-sm"
          >
            <i class="las la-plus"></i>
            Nueva Hoja de Mantenimiento
          </button>
        </div>

        <TableControls :tableFilter="maintenanceTableFilter" position="top" searchPlaceholder="Buscar hoja de mantenimiento..." />

      <div class="overflow-x-auto">
        <table class="table table-zebra w-full">
          <thead>
            <tr class="bg-sky-600 text-white">
              <th class="p-2 border border-sky-400 text-center">#</th>
              <th class="p-2 border border-sky-400 text-center">Nro. Hoja</th>
              <th class="p-2 border border-sky-400 text-center">Estado</th>
              <th class="p-2 border border-sky-400 text-center">Tipo</th>
              <th class="p-2 border border-sky-400 text-center">Fecha Inicio</th>
              <th class="p-2 border border-sky-400 text-center">Fecha Fin</th>
              <th class="p-2 border border-sky-400 text-center">Días</th>
              <th class="p-2 border border-sky-400 text-center">Horas</th>
              <th class="p-2 border border-sky-400 text-center">C/Hora</th>
              <th class="p-2 border border-sky-400 text-center">Costo Total</th>
              <th class="p-2 border border-sky-400 text-center">Equipo</th>
              <th class="p-2 border border-sky-400 text-center">Técnico</th>
              <th class="p-2 border border-sky-400 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="maintenanceSheets.length === 0">
              <tr>
                <td colspan="13" class="text-center text-gray-500 py-8">
                  <i class="las la-inbox text-4xl"></i>
                  <p>No hay hojas de mantenimiento registradas para esta planilla</p>
                </td>
              </tr>
            </template>
            <template v-else-if="maintenanceTableFilter.paginatedData.value.length === 0">
              <tr>
                <td colspan="13" class="text-center text-gray-500 py-8">
                  <i class="las la-search text-4xl"></i>
                  <p>No se encontraron resultados para "{{ maintenanceTableFilter.searchQuery.value }}"</p>
                </td>
              </tr>
            </template>
            <template v-else>
              <tr v-for="ms in maintenanceTableFilter.paginatedData.value" :key="ms.id">
                <td class="p-2 border border-gray-300 text-center">{{ ms.id }}</td>
                <td class="p-2 border border-gray-300 font-mono font-bold text-center">{{ ms.sheet_number }}</td>
                <td class="p-2 border border-gray-300 text-center">
                  <span class="badge" :class="getMaintenanceStatusBadge(ms.status).class">
                    {{ getMaintenanceStatusBadge(ms.status).text }}
                  </span>
                </td>
                <td class="p-2 border border-gray-300 text-center">
                  <span class="badge badge-outline badge-sm">{{ ms.maintenance_type }}</span>
                </td>
                <td class="p-2 border border-gray-300 text-center">{{ formatDate(ms.start_date) }}</td>
                <td class="p-2 border border-gray-300 text-center">{{ formatDate(ms.end_date) }}</td>
                <td class="p-2 border border-gray-300 text-center font-semibold">{{ ms.total_days || 0 }}</td>
                <td class="p-2 border border-gray-300 text-center font-semibold">{{ ms.total_hours || 0 }}</td>
                <td class="p-2 border border-gray-300 text-right font-mono">{{ ms.cost_hour || 0 }}</td>
                <td class="p-2 border border-gray-300 text-right font-mono font-semibold">{{ ms.total_cost || 0 }}</td>
                <td class="p-2 border border-gray-300">{{ ms.resource_item_name || 'N/A' }}</td>
                <td class="p-2 border border-gray-300">{{ ms.responsible_technical_name || 'N/A' }}</td>
                <td class="p-2 border border-gray-300 text-end">
                  <div class="flex gap-2 justify-end">
                    <button
                      @click="viewMaintenanceSheetDetail(ms.id)"
                      class="btn btn-xs border-blue-500 text-teal-500 bg-white"
                      title="Ver detalle"
                    >
                      <i class="las la-eye"></i>
                      VER
                    </button>
                    <button
                      @click="viewMaintenanceSheetPDF(ms.id)"
                      class="btn btn-xs border-red-500 text-red-500 bg-white"
                      title="Generar PDF"
                    >
                      <i class="las la-file-pdf"></i>
                      PDF
                    </button>
                    <button
                      @click="ms.status === 'DRAFT' && !isCustodyLocked ? viewMaintenanceSheetDetail(ms.id) : null"
                      class="btn btn-xs border-orange-500 text-orange-500 bg-white"
                      :class="{ 'btn-disabled opacity-50 cursor-not-allowed': ms.status !== 'DRAFT' || isCustodyLocked }"
                      :title="isCustodyLocked ? 'No se puede editar - ' + lockMessage : (ms.status === 'DRAFT' ? 'Editar hoja' : 'No se puede editar una hoja cerrada/anulada')"
                      :disabled="ms.status !== 'DRAFT' || isCustodyLocked"
                    >
                      <i class="las la-edit"></i>
                      EDITAR
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

        <TableControls :tableFilter="maintenanceTableFilter" position="bottom" />
      </div>

    </div>

    <!-- Estadísticas Resumen -->
    <div class="stats shadow w-full mt-6">
      <div class="stat">
        <div class="stat-title">Total Cadenas</div>
        <div class="stat-value text-primary">{{ custodyChains.length }}</div>
        <div class="stat-desc">Registradas</div>
      </div>
      
      <div class="stat">
        <div class="stat-title">Horas Totales</div>
        <div class="stat-value text-info">{{ totalHours }}</div>
        <div class="stat-desc">Horas trabajadas</div>
      </div>

      <div class="stat">
        <div class="stat-title">Total Galones</div>
        <div class="stat-value text-info">{{ totalGallons.toFixed(2) }}</div>
        <div class="stat-desc">Acumulados</div>
      </div>

      <div class="stat">
        <div class="stat-title">Total Barriles</div>
        <div class="stat-value text-info">{{ totalBarrels.toFixed(2) }}</div>
        <div class="stat-desc">Acumulados</div>
      </div>

      <div class="stat">
        <div class="stat-title">Total M³</div>
        <div class="stat-value text-info">{{ totalCubicMeters.toFixed(2) }}</div>
        <div class="stat-desc">Acumulados</div>
      </div>

      <div class="stat">
        <div class="stat-title">Hojas Mantenimiento</div>
        <div class="stat-value text-sky-600">{{ maintenanceSheets.length }}</div>
        <div class="stat-desc">Registradas</div>
      </div>
    </div>

    <!-- Modal Factura -->
    <div v-if="showInvoiceModal" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">
          <i class="las la-file-invoice text-accent"></i>
          Adjuntar Factura
        </h3>
        <div class="form-control mb-4">
          <label class="label"><span class="label-text">Referencia de Factura *</span></label>
          <input 
            v-model="invoiceReference" 
            type="text" 
            class="input input-bordered w-full" 
            placeholder="Ej: FAC-001-2026"
          />
        </div>
        <div class="form-control mb-4">
          <label class="label"><span class="label-text">Archivo PDF *</span></label>
          <input 
            type="file" 
            accept=".pdf" 
            class="file-input file-input-bordered w-full" 
            @change="onInvoiceFileSelected"
            :disabled="isUploadingInvoice"
          />
        </div>
        <div v-if="isUploadingInvoice" class="flex justify-center py-2">
          <span class="loading loading-spinner loading-md"></span>
        </div>
        <div class="modal-action">
          <button class="btn" @click="showInvoiceModal = false" :disabled="isUploadingInvoice">Cancelar</button>
        </div>
      </div>
      <div class="modal-backdrop" @click="showInvoiceModal = false"></div>
    </div>
  </div>
</template>
