<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router';
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore';
import { UseProjectStore } from '@/stores/ProjectStore';
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore';
import { appConfig } from '@/AppConfig';
import { onMounted, computed, ref, watch } from 'vue';


const router = useRouter();
const route = useRoute();
const sheetProjectStore = UseSheetProjectsStore();
const projectStore = UseProjectStore();
const projectResourceStore = UseProjectResourceStore();
const isSubmitting = ref(false);

const project = computed(() => projectStore.project);
const resources = computed(() => projectResourceStore.resourcesProject || []);

// Detectar si es modo edición o creación
const sheetId = ref(route.params.id ? parseInt(route.params.id) : null);
const isEditMode = computed(() => sheetId.value !== null);

// Verificar si la planilla está cerrada (is_closed)
const isSheetClosed = computed(() => {
  if (!isEditMode.value) return false;
  const existingSheet = sheetProjectStore.getSheetProjectById(sheetId.value);
  return existingSheet?.is_closed === true;
});

// Verificar si el proyecto está cerrado
const isProjectClosed = computed(() => project.value?.is_closed === true);

// Usar el store como fuente de datos
const formData = computed(() => sheetProjectStore.newSheetProject);

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
const resourcesChanged = ref(false);

// Estado de archivos PDF
const sheetFileInput = ref(null);
const certificateFileInput = ref(null);
const invoiceFileInput = ref(null);
const sheetFileInfo = ref(null);
const certificateFileInfo = ref(null);
const invoiceFileInfo = ref(null);
const isUploadingSheet = ref(false);
const isUploadingCertificate = ref(false);
const isUploadingInvoice = ref(false);
const showInvoiceModal = ref(false);
const invoiceReference = ref('');

// Validaciones de fechas
const periodDatesError = computed(() => {
  if (!formData.value.period_start || !formData.value.period_end) {
    return '';
  }
  
  const startDate = new Date(formData.value.period_start);
  const endDate = new Date(formData.value.period_end);
  
  // Comparar solo las fechas (ignorar horas)
  startDate.setHours(0, 0, 0, 0);
  endDate.setHours(0, 0, 0, 0);
  
  if (startDate.getTime() === endDate.getTime()) {
    return 'Las fechas no pueden ser iguales';
  }
  
  if (startDate > endDate) {
    return 'La fecha de inicio debe ser menor que la fecha de fin';
  }
  
  return '';
});

// Calcular días de ejecución (incluyendo primer y último día)
const executionDays = computed(() => {
  if (!formData.value.period_start || !formData.value.period_end) {
    return 0;
  }
  
  const startDate = new Date(formData.value.period_start);
  const endDate = new Date(formData.value.period_end);
  
  // Calcular diferencia en milisegundos
  const diffTime = Math.abs(endDate - startDate);
  
  // Convertir a días y sumar 1 para incluir ambos días (inicio y fin)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  
  return diffDays;
});

const serviceTypeOptions = [
  { value: 'ALQUILER', label: 'Alquiler' },
  { value: 'MANTENIMIENTO', label: 'Mantenimiento' },
  { value: 'ALQUILER Y MANTENIMIENTO', label: 'Alquiler y Mantenimiento' }
];

const statusOptions = [
  { value: 'IN_PROGRESS', label: 'En Progreso' },
  { value: 'LIQUIDATED', label: 'Liquidado' },
  { value: 'INVOICED', label: 'Facturado' },
  { value: 'CANCELLED', label: 'Cancelado' }
];

// Verificar si la planilla está en estado que bloquea todo (INVOICED o CANCELLED)
const isFullyLocked = computed(() => {
  if (!isEditMode.value) return false;
  const existingSheet = sheetProjectStore.getSheetProjectById(sheetId.value);
  return ['INVOICED', 'CANCELLED'].includes(existingSheet?.status);
});

// Verificar si la planilla está LIQUIDATED (solo cabeceras editables)
const isLiquidated = computed(() => {
  if (!isEditMode.value) return false;
  const existingSheet = sheetProjectStore.getSheetProjectById(sheetId.value);
  return existingSheet?.status === 'LIQUIDATED';
});

// Cualquier estado que no sea IN_PROGRESS bloquea los detalles/recursos
const isDetailsLocked = computed(() => {
  return isProjectClosed.value || isSheetClosed.value || isLiquidated.value || isFullyLocked.value;
});

// Verificar si se puede editar cabeceras
const isHeadersLocked = computed(() => {
  return isProjectClosed.value || isSheetClosed.value || isFullyLocked.value;
});

// Solo mostrar recursos activos
const activeResources = computed(() => resources.value.filter(r => r.is_active));

// IDs de project_resource_item que tienen cadena de custodia en esta planilla
const resourceIdsWithCustody = computed(() => {
  if (!isEditMode.value) return new Set();
  const existingSheet = sheetProjectStore.getSheetProjectById(sheetId.value);
  if (!existingSheet || !existingSheet.custody_chains) return new Set();
  const ids = new Set();
  for (const chain of existingSheet.custody_chains) {
    for (const detail of (chain.details || [])) {
      if (detail.project_resource_id) ids.add(detail.project_resource_id);
    }
  }
  return ids;
});

// Verificar si un recurso tiene cadena de custodia
const hasCustodyChain = (resource) => resourceIdsWithCustody.value.has(resource.id);

// Recursos seleccionados (is_selected === true)
const selectedResources = computed(() => activeResources.value.filter(r => r.is_selected));

const allSelected = computed(() => {
  return activeResources.value.length > 0 && 
         activeResources.value.every(r => r.is_selected);
});

// Métodos de selección usando is_selected del recurso
const toggleSelectAll = () => {
  const newValue = !allSelected.value;
  activeResources.value.forEach(r => {
    // No desmarcar recursos con cadena de custodia
    if (!newValue && hasCustodyChain(r)) return;
    r.is_selected = newValue;
  });
  resourcesChanged.value = true;
};

const toggleResourceSelection = (resource) => {
  // Impedir desmarcar si tiene cadena de custodia
  if (resource.is_selected && hasCustodyChain(resource)) {
    errorMessage.value = `No se puede desmarcar "${resource.resource_item_code || resource.resource_item_name}" porque tiene cadenas de custodia registradas en esta planilla.`;
    setTimeout(() => { errorMessage.value = ''; }, 4000);
    return;
  }
  resource.is_selected = !resource.is_selected;
  resourcesChanged.value = true;
};

// Subir archivo de planilla PDF
const handleAttachSheetFile = () => {
  if (isHeadersLocked.value && sheetFileInfo.value?.has_file) return;
  sheetFileInput.value?.click();
};

const onSheetFileSelected = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.type !== 'application/pdf') {
    errorMessage.value = 'Solo se permiten archivos PDF para la planilla';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
    return;
  }
  if (!isEditMode.value || !sheetId.value) {
    errorMessage.value = 'Primero debe guardar la planilla antes de adjuntar archivos';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
    return;
  }
  isUploadingSheet.value = true;
  try {
    const result = await sheetProjectStore.uploadSheetFile(sheetId.value, 'sheet_project_file', file);
    sheetFileInfo.value = result;
    successMessage.value = 'Archivo de planilla subido correctamente';
    setTimeout(() => { successMessage.value = ''; }, 3000);
  } catch (error) {
    errorMessage.value = error.message || 'Error al subir el archivo de planilla';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
  } finally {
    isUploadingSheet.value = false;
    event.target.value = '';
  }
};

// Subir certificado de disposición final
const handleAttachCertificateFile = () => {
  if (isHeadersLocked.value && certificateFileInfo.value?.has_file) return;
  certificateFileInput.value?.click();
};

const onCertificateFileSelected = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.type !== 'application/pdf') {
    errorMessage.value = 'Solo se permiten archivos PDF para el certificado';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
    return;
  }
  if (!isEditMode.value || !sheetId.value) {
    errorMessage.value = 'Primero debe guardar la planilla antes de adjuntar archivos';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
    return;
  }
  isUploadingCertificate.value = true;
  try {
    const result = await sheetProjectStore.uploadSheetFile(sheetId.value, 'certificate_final_disposition_file', file);
    certificateFileInfo.value = result;
    successMessage.value = 'Certificado de disposición final subido correctamente';
    setTimeout(() => { successMessage.value = ''; }, 3000);
  } catch (error) {
    errorMessage.value = error.message || 'Error al subir el certificado';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
  } finally {
    isUploadingCertificate.value = false;
    event.target.value = '';
  }
};

// Subir factura PDF
const handleAttachInvoiceFile = () => {
  if (isHeadersLocked.value && invoiceFileInfo.value?.has_file) return;
  if (!isEditMode.value || !sheetId.value) {
    errorMessage.value = 'Primero debe guardar la planilla antes de adjuntar archivos';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
    return;
  }
  invoiceReference.value = formData.value.invoice_reference || '';
  showInvoiceModal.value = true;
};

const onInvoiceFileSelected = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.type !== 'application/pdf') {
    errorMessage.value = 'Solo se permiten archivos PDF para la factura';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
    return;
  }
  if (!invoiceReference.value.trim()) {
    errorMessage.value = 'Debe ingresar la referencia de factura';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
    return;
  }
  isUploadingInvoice.value = true;
  try {
    const result = await sheetProjectStore.uploadSheetFile(
      sheetId.value, 'invoice_file', file, { invoice_reference: invoiceReference.value.trim() }
    );
    invoiceFileInfo.value = result;
    formData.value.invoice_reference = invoiceReference.value.trim();
    formData.value.status = 'INVOICED';
    successMessage.value = 'Factura subida correctamente. Estado cambiado a FACTURADO.';
    showInvoiceModal.value = false;
    setTimeout(() => { successMessage.value = ''; }, 4000);
  } catch (error) {
    errorMessage.value = error.message || 'Error al subir la factura';
    setTimeout(() => { errorMessage.value = ''; }, 4000);
  } finally {
    isUploadingInvoice.value = false;
    event.target.value = '';
  }
};

// Consultar archivos existentes
const loadFileInfo = async () => {
  if (!isEditMode.value || !sheetId.value) return;
  try {
    const [sheetInfo, certInfo, invoiceInfo] = await Promise.all([
      sheetProjectStore.getSheetFileInfo(sheetId.value, 'sheet_project_file'),
      sheetProjectStore.getSheetFileInfo(sheetId.value, 'certificate_final_disposition_file'),
      sheetProjectStore.getSheetFileInfo(sheetId.value, 'invoice_file')
    ]);
    sheetFileInfo.value = sheetInfo;
    certificateFileInfo.value = certInfo;
    invoiceFileInfo.value = invoiceInfo;
  } catch (error) {
    console.error('Error consultando archivos:', error);
  }
};

// Abrir archivo en nueva pestaña
const openFile = (fileInfo) => {
  if (fileInfo?.file_url) {
    window.open(appConfig.apiBaseUrl + fileInfo.file_url, '_blank');
  }
};

onMounted(async () => {
  await projectStore.fetchProjectData();
  await projectResourceStore.fetchResourcesProject();
  
  if (isEditMode.value) {
    // Modo edición: cargar datos de la planilla existente
    const existingSheet = sheetProjectStore.getSheetProjectById(sheetId.value);
    if (existingSheet) {
      // Cargar datos en el store
      Object.assign(sheetProjectStore.newSheetProject, {
        id: existingSheet.id,
        project: existingSheet.project?.id || project.value.id,
        period_start: existingSheet.period_start || '',
        period_end: existingSheet.period_end || '',
        issue_date: existingSheet.issue_date || '',
        service_type: existingSheet.service_type || 'ALQUILER Y MANTENIMIENTO',
        status: existingSheet.status || 'IN_PROGRESS',
        series_code: existingSheet.series_code || 'PSL-PS-0000-0000',
        contact_reference: existingSheet.contact_reference || '',
        contact_phone_reference: existingSheet.contact_phone_reference || '',
        client_po_reference: existingSheet.client_po_reference || '',
        final_disposition_reference: existingSheet.final_disposition_reference || '',
        invoice_reference: existingSheet.invoice_reference || '',
        notes: existingSheet.notes || ''
      });
      // Cargar estadísticas de la planilla existente
      stats.value = {
        total_gallons: existingSheet.total_gallons || 0,
        total_barrels: existingSheet.total_barrels || 0,
        total_cubic_meters: existingSheet.total_cubic_meters || 0,
        subtotal: existingSheet.subtotal || 0,
        tax_amount: existingSheet.tax_amount || 0,
        total: existingSheet.total || 0
      };
    } else {
      errorMessage.value = 'Planilla no encontrada';
    }
  } else {
    // Modo creación: inicializar con datos del proyecto
    sheetProjectStore.initializeNewSheetProject(project.value);
  }
  
  if (isEditMode.value) {
    // Modo edición: pre-seleccionar los recursos que ya están en la planilla
    const existingSheet = sheetProjectStore.getSheetProjectById(sheetId.value);
    if (existingSheet && existingSheet.details) {
      // Construir mapa: project_resource_item.id -> detail.id (para saber el id del detalle)
      // Usamos un array porque puede haber varios detalles con el mismo project_resource_item.id
      const detailMap = {};
      for (const detail of existingSheet.details) {
        const prId = detail.project_resource_item?.id;
        if (prId) {
          if (!detailMap[prId]) detailMap[prId] = [];
          detailMap[prId].push(detail.id);
        }
      }
      
      // Marcar como seleccionados y asignar detail_id
      for (const resource of resources.value.filter(r => r.is_active)) {
        if (detailMap[resource.id] && detailMap[resource.id].length > 0) {
          resource.is_selected = true;
          resource.detail_id = detailMap[resource.id].shift(); // tomar el primer id disponible
        } else {
          resource.is_selected = false;
          resource.detail_id = 0; // nuevo si se selecciona después
        }
      }
    }
  } else {
    // Seleccionar automáticamente todos los recursos activos (solo en modo creación)
    resources.value
      .filter(r => r.is_active)
      .forEach(r => { r.is_selected = true; r.detail_id = 0; });
  }

  // Cargar información de archivos existentes (solo en modo edición)
  await loadFileInfo();
});

const handleSubmit = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  isSubmitting.value = true;
  
  try {
    if (!formData.value.period_start) {
      throw new Error('La fecha de inicio del período es requerida');
    }
    
    if (!formData.value.period_end) {
      throw new Error('La fecha de fin del período es requerida');
    }
    
    if (!formData.value.service_type) {
      throw new Error('El tipo de servicio es requerido');
    }
    
    if (selectedResources.value.length === 0) {
      throw new Error('Debes seleccionar al menos un recurso para la planilla');
    }
    
    // Validar que las fechas no excedan la fecha de fin del proyecto
    if (project.value.end_date) {
      const projectEndDate = new Date(project.value.end_date);
      const periodStart = new Date(formData.value.period_start);
      const periodEnd = new Date(formData.value.period_end);
      
      if (periodStart > projectEndDate) {
        throw new Error(`La fecha de inicio del período no puede ser posterior a la fecha de fin del proyecto (${new Date(project.value.end_date).toLocaleDateString('es-EC')})`);
      }
      
      if (periodEnd > projectEndDate) {
        throw new Error(`La fecha de fin del período no puede ser posterior a la fecha de fin del proyecto (${new Date(project.value.end_date).toLocaleDateString('es-EC')})`);
      }
    }
    
    // Validar que las fechas no sean iguales y que la fecha de inicio sea menor que la de fin
    const periodStart = new Date(formData.value.period_start);
    const periodEnd = new Date(formData.value.period_end);
    
    // Comparar solo las fechas (ignorar horas)
    periodStart.setHours(0, 0, 0, 0);
    periodEnd.setHours(0, 0, 0, 0);
    
    if (periodStart.getTime() === periodEnd.getTime()) {
      throw new Error('Las fechas de inicio y fin del período no pueden ser iguales');
    }
    
    if (periodStart > periodEnd) {
      throw new Error('La fecha de inicio del período debe ser menor que la fecha de fin');
    }
    
    // Construir payload desde el store
    const payload = {
      project: formData.value.project,
      period_start: formData.value.period_start,
      period_end: formData.value.period_end,
      service_type: formData.value.service_type,
      status: formData.value.status || "IN_PROGRESS",
      series_code: formData.value.series_code || "PSL-PS-00000-00",
      contact_reference: formData.value.contact_reference || null,
      contact_phone_reference: formData.value.contact_phone_reference || null,
      client_po_reference: formData.value.client_po_reference || null,
      invoice_reference: formData.value.invoice_reference || null,
      final_disposition_reference: formData.value.final_disposition_reference || null
    };
    
    // Si es actualización, agregar ID
    if (isEditMode.value) {
      payload.id = formData.value.id;
    }
    
    let resultId;
    if (isEditMode.value) {
      // Actualizar planilla existente, solo enviar recursos si cambiaron
      const resourcesToSend = resourcesChanged.value ? selectedResources.value : [];
      await sheetProjectStore.updateSheetProject(payload, resourcesToSend);
      resultId = payload.id;
      successMessage.value = 'Planilla actualizada exitosamente';
    } else {
      // Crear nueva planilla con los recursos seleccionados
      resultId = await sheetProjectStore.addSheetProject(payload, selectedResources.value);
      successMessage.value = `Planilla creada exitosamente con ID: ${resultId}`;
    }
    
    setTimeout(() => {
      router.push({ name: 'projects-detail', query: { tab: 'planillas' } });
    }, 1500);
  } catch (error) {
    console.error('Error al guardar planilla:', error);
    errorMessage.value = error.message || 'Error al guardar la planilla';
  } finally {
    isSubmitting.value = false;
  }
};

// ===== CALENDARIO DE DÍAS PARA EQUIPOS =====

// Recurso equipo expandido para mostrar calendario
const expandedEquipmentId = ref(null);

// Estado local de monthdays_apply_cost por detail_id
const equipmentDaysMap = ref({});

// Equipos seleccionados (solo tipo EQUIPO) con su detalle de planilla
const selectedEquipmentResources = computed(() => {
  if (!isEditMode.value) return [];
  const existingSheet = sheetProjectStore.getSheetProjectById(sheetId.value);
  if (!existingSheet || !existingSheet.details) return [];
  
  return existingSheet.details
    .filter(d => d.project_resource_item?.type_resource === 'EQUIPO')
    .map(d => ({
      detail_id: d.id,
      resource_item_code: d.resource_item_code,
      resource_item_name: d.resource_item_name,
      equipment: d.equipment,
      detail: d.detail,
      unit_price: d.unit_price,
      quantity: d.quantity,
      total_line: d.total_line,
      monthdays_apply_cost: d.monthdays_apply_cost || [],
      operation_start_date: d.project_resource_item?.operation_start_date,
      operation_end_date: d.project_resource_item?.operation_end_date,
      is_retired: d.project_resource_item?.is_retired,
      retirement_date: d.project_resource_item?.retirement_date,
    }));
});

// Generar los días del período de la planilla para un equipo considerando entradas/salidas
const getDaysInPeriod = computed(() => {
  if (!formData.value.period_start || !formData.value.period_end) return [];
  
  const start = new Date(formData.value.period_start + 'T00:00:00');
  const end = new Date(formData.value.period_end + 'T00:00:00');
  const days = [];
  
  const current = new Date(start);
  while (current <= end) {
    days.push(current.getDate());
    current.setDate(current.getDate() + 1);
  }
  
  return days;
});

// Verificar si un día está dentro del rango efectivo del equipo
const isDayInEquipmentRange = (equipment, day) => {
  if (!formData.value.period_start || !formData.value.period_end) return false;
  
  const periodStart = new Date(formData.value.period_start + 'T00:00:00');
  const periodEnd = new Date(formData.value.period_end + 'T00:00:00');
  
  // Construir fecha real del día dentro del mes del período
  const dayDate = new Date(periodStart.getFullYear(), periodStart.getMonth(), day);
  
  // Fecha efectiva de inicio del equipo
  let effectiveStart = periodStart;
  if (equipment.operation_start_date) {
    const opStart = new Date(equipment.operation_start_date + 'T00:00:00');
    if (opStart > effectiveStart) effectiveStart = opStart;
  }
  
  // Fecha efectiva de fin del equipo
  let effectiveEnd = periodEnd;
  if (equipment.is_retired && equipment.retirement_date) {
    const retDate = new Date(equipment.retirement_date + 'T00:00:00');
    if (retDate < effectiveEnd) effectiveEnd = retDate;
  } else if (equipment.operation_end_date) {
    const opEnd = new Date(equipment.operation_end_date + 'T00:00:00');
    if (opEnd < effectiveEnd) effectiveEnd = opEnd;
  }
  
  return dayDate >= effectiveStart && dayDate <= effectiveEnd;
};

// Obtener los días seleccionados para un detalle 
const getSelectedDays = (detailId) => {
  return equipmentDaysMap.value[detailId] || [];
};

// Último día clickeado por detalle (para Shift+Click de rango)
const lastClickedDay = ref({});

// Toggle un día para un detalle de equipo (soporta Shift+Click para rango)
const toggleEquipmentDay = (detailId, day, event, equipment) => {
  if (isDetailsLocked.value) return;
  
  if (!equipmentDaysMap.value[detailId]) {
    equipmentDaysMap.value[detailId] = [];
  }
  
  const days = equipmentDaysMap.value[detailId];
  
  // Shift+Click: seleccionar rango desde el último día clickeado
  if (event && event.shiftKey && lastClickedDay.value[detailId] !== undefined) {
    const from = Math.min(lastClickedDay.value[detailId], day);
    const to = Math.max(lastClickedDay.value[detailId], day);
    
    for (let d = from; d <= to; d++) {
      // Solo agregar días válidos que estén en el período y en el rango del equipo
      if (getDaysInPeriod.value.includes(d) && (!equipment || isDayInEquipmentRange(equipment, d))) {
        if (!days.includes(d)) {
          days.push(d);
        }
      }
    }
  } else {
    // Click normal: toggle individual
    const index = days.indexOf(day);
    if (index === -1) {
      days.push(day);
    } else {
      days.splice(index, 1);
    }
  }
  
  // Guardar último día clickeado
  lastClickedDay.value[detailId] = day;
  
  // Ordenar
  equipmentDaysMap.value[detailId] = [...days].sort((a, b) => a - b);
};

// Contar los días válidos (dentro del rango) para un equipo
const countValidDays = (equipment) => {
  return getDaysInPeriod.value.filter(d => isDayInEquipmentRange(equipment, d)).length;
};

// Seleccionar/deseleccionar todos los días válidos de un equipo
const toggleAllEquipmentDays = (equipment) => {
  if (isDetailsLocked.value) return;
  
  const currentDays = getSelectedDays(equipment.detail_id);
  const validDays = getDaysInPeriod.value.filter(d => isDayInEquipmentRange(equipment, d));
  
  if (currentDays.length === validDays.length) {
    // Deseleccionar todos
    equipmentDaysMap.value[equipment.detail_id] = [];
  } else {
    // Seleccionar todos los válidos
    equipmentDaysMap.value[equipment.detail_id] = [...validDays];
  }
};

// Expandir/contraer calendario de un equipo
const toggleEquipmentCalendar = (detailId) => {
  expandedEquipmentId.value = expandedEquipmentId.value === detailId ? null : detailId;
};

// ===== MODAL DE CALENDARIO =====
const showCalendarModal = ref(false);
const calendarModalEquipment = ref(null);

// Abrir modal de calendario para un equipo
const openCalendarModal = (equipment) => {
  calendarModalEquipment.value = equipment;
  expandedEquipmentId.value = equipment.detail_id;
  showCalendarModal.value = true;
};

// Cerrar modal
const closeCalendarModal = () => {
  showCalendarModal.value = false;
  calendarModalEquipment.value = null;
};

// Buscar el detalle de equipamiento correspondiente a un recurso de la tabla
const getEquipmentDetailForResource = (resource) => {
  return selectedEquipmentResources.value.find(
    eq => eq.resource_item_code === resource.resource_item_code
  ) || null;
};

// Guardar los días de un detalle de equipo
const isSavingDays = ref(false);
const savingDetailId = ref(null);

const saveEquipmentDays = async (detailId) => {
  isSavingDays.value = true;
  savingDetailId.value = detailId;
  errorMessage.value = '';
  
  try {
    const days = getSelectedDays(detailId);
    const result = await sheetProjectStore.updateSheetDetailDays(detailId, days);
    
    // Actualizar estadísticas locales con los nuevos totales
    if (result?.sheet_totals) {
      stats.value.subtotal = result.sheet_totals.subtotal;
      stats.value.tax_amount = result.sheet_totals.tax_amount;
      stats.value.total = result.sheet_totals.total;
    }
    
    successMessage.value = `Días de cobro actualizados (${days.length} días)`;
    setTimeout(() => { successMessage.value = ''; }, 3000);
    
    // Cerrar el modal después de guardar exitosamente
    closeCalendarModal();
  } catch (error) {
    errorMessage.value = error.message || 'Error al actualizar los días de cobro';
    setTimeout(() => { errorMessage.value = ''; }, 5000);
  } finally {
    isSavingDays.value = false;
    savingDetailId.value = null;
  }
};

// Inicializar el mapa de días cuando se cargan los datos de la planilla
const initializeEquipmentDays = () => {
  for (const eq of selectedEquipmentResources.value) {
    equipmentDaysMap.value[eq.detail_id] = [...(eq.monthdays_apply_cost || [])];
  }
};

// Watch para re-inicializar cuando cambian los detalles de la planilla
watch(selectedEquipmentResources, () => {
  initializeEquipmentDays();
}, { immediate: true });
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

        <!-- ===== BANNER PROYECTO CERRADO ===== -->
        <div v-if="isProjectClosed" class="alert alert-error shadow-lg mb-4">
          <div class="flex items-center gap-2">
            <i class="las la-lock text-2xl"></i>
            <div>
              <h3 class="font-bold">Proyecto Cerrado</h3>
              <p class="text-sm">El proyecto está cerrado. No se permiten modificaciones en ninguna planilla.</p>
            </div>
          </div>
        </div>

        <!-- ===== BANNER PLANILLA CERRADA ===== -->
        <div v-else-if="isFullyLocked" class="alert alert-error shadow-lg mb-4">
          <div class="flex items-center gap-2">
            <i class="las la-ban text-2xl"></i>
            <div>
              <h3 class="font-bold">Planilla {{ formData.status === 'INVOICED' ? 'Facturada' : 'Cancelada' }}</h3>
              <p class="text-sm">Esta planilla no permite ninguna modificación.</p>
            </div>
          </div>
        </div>

        <div v-else-if="isLiquidated" class="alert alert-warning shadow-lg mb-4">
          <div class="flex items-center gap-2">
            <i class="las la-lock text-2xl"></i>
            <div>
              <h3 class="font-bold">Planilla Liquidada</h3>
              <p class="text-sm">Solo se pueden modificar las cabeceras de la planilla. Los recursos y cadenas de custodia están bloqueados.</p>
            </div>
          </div>
        </div>

        <div v-else-if="isSheetClosed" class="alert alert-warning shadow-lg mb-4">
          <div class="flex items-center gap-2">
            <i class="las la-lock text-2xl"></i>
            <div>
              <h3 class="font-bold">Planilla Cerrada</h3>
              <p class="text-sm">Esta planilla está cerrada y no permite modificaciones. Solo se pueden agregar archivos pendientes.</p>
            </div>
          </div>
        </div>

        <!-- ===== ENCABEZADO: Título + Botones PDF + Código Serie ===== -->
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
          <div>
            <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
              <i class="las la-file-invoice text-blue-600"></i>
              {{ isEditMode ? `Planilla ${formData.series_code}` : 'Nueva Planilla' }} — Proyecto #{{ project?.id }}
            </h1>
            <div class="flex items-center gap-3 mt-1">
              <p class="text-gray-600 text-sm">{{ project?.partner_name || '' }} · {{ project?.location || '' }}</p>
              <div v-if="executionDays > 0" class="badge badge-primary badge-lg gap-2">
                <i class="las la-calendar-check"></i>
                <span class="font-semibold">Días de Ejecución:</span>
                <span class="font-bold">{{ executionDays }}</span>
              </div>
            </div>
          </div>
          <div class="flex gap-2 items-center">
            <!-- Input oculto para planilla PDF -->
            <input type="file" ref="sheetFileInput" accept=".pdf" class="hidden" @change="onSheetFileSelected" />
            <!-- Input oculto para certificado PDF -->
            <input type="file" ref="certificateFileInput" accept=".pdf" class="hidden" @change="onCertificateFileSelected" />

            <!-- Botón Planilla PDF -->
            <div class="flex items-center gap-1">
              <button 
                type="button" 
                @click="handleAttachSheetFile" 
                class="btn btn-info btn-sm gap-1"
                :class="{ 'btn-disabled': !isEditMode || isUploadingSheet || (isHeadersLocked && sheetFileInfo?.has_file) }"
                :disabled="!isEditMode || isUploadingSheet || (isHeadersLocked && sheetFileInfo?.has_file)"
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
                :class="{ 'btn-disabled': !isEditMode || isUploadingCertificate || (isHeadersLocked && certificateFileInfo?.has_file) }"
                :disabled="!isEditMode || isUploadingCertificate || (isHeadersLocked && certificateFileInfo?.has_file)"
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

            <!-- Botón Factura PDF -->
            <div class="flex items-center gap-1">
              <button 
                type="button" 
                @click="handleAttachInvoiceFile" 
                class="btn btn-accent btn-sm gap-1"
                :class="{ 'btn-disabled': !isEditMode || isUploadingInvoice || (isHeadersLocked && invoiceFileInfo?.has_file) }"
                :disabled="!isEditMode || isUploadingInvoice || (isHeadersLocked && invoiceFileInfo?.has_file)"
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

            <div class="form-control w-48">
              <input v-model="formData.series_code" type="text" class="input input-bordered input-sm w-full font-bold text-red-800 font-mono text-[16px]" :disabled="isHeadersLocked" />
            </div>
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
            <input v-model="formData.issue_date" type="date" class="input input-bordered w-full" :disabled="isHeadersLocked" />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Inicio Período *</span>
            </label>
            <input 
              v-model="formData.period_start" 
              type="date" 
              class="input input-bordered w-full" 
              :class="{ 'input-error': !formData.period_start || periodDatesError }" 
              required 
              :disabled="isHeadersLocked"
            />
            <label v-if="periodDatesError && formData.period_start" class="label">
              <span class="label-text-alt text-error">{{ periodDatesError }}</span>
            </label>
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Fin Período *</span>
            </label>
            <input 
              v-model="formData.period_end" 
              type="date" 
              class="input input-bordered w-full" 
              :class="{ 'input-error': !formData.period_end || periodDatesError }" 
              required 
              :disabled="isHeadersLocked"
            />
            <label v-if="periodDatesError && formData.period_end" class="label">
              <span class="label-text-alt text-error">{{ periodDatesError }}</span>
            </label>
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Estado</span>
            </label>
            <select v-model="formData.status" class="select select-bordered w-full" :disabled="isHeadersLocked">
              <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </div>

        <div class="divider">Tipo de Servicio y Contacto</div>

        <!-- Fila 3: Tipo Servicio + Contacto + Teléfono + PO (4 columnas) -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Tipo Servicio *</span>
            </label>
            <select v-model="formData.service_type" class="select select-bordered w-full" required :disabled="isHeadersLocked">
              <option v-for="opt in serviceTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Contacto</span>
            </label>
            <input v-model="formData.contact_reference" type="text" class="input input-bordered w-full" placeholder="Nombre contacto" :disabled="isHeadersLocked" />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Teléfono</span>
            </label>
            <input v-model="formData.contact_phone_reference" type="text" class="input input-bordered w-full" placeholder="+593..." :disabled="isHeadersLocked" />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">PO Cliente</span>
            </label>
            <input v-model="formData.client_po_reference" type="text" class="input input-bordered w-full" placeholder="PO-2026-001" :disabled="isHeadersLocked" />
          </div>
        </div>

        <div class="divider">Referencias Adicionales</div>

        <!-- Fila 4: Ref. Factura + Disposición Final (4 columnas, dejando 2 vacías) -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Ref. Factura</span>
            </label>
            <input v-model="formData.invoice_reference" type="text" class="input input-bordered w-full" placeholder="FAC-2026-001" :disabled="isHeadersLocked" />
          </div>
          <div class="form-control w-full md:col-span-3">
            <label class="label">
              <span class="label-text font-semibold">Disposición Final</span>
            </label>
            <input v-model="formData.final_disposition_reference" type="text" class="input input-bordered w-full" placeholder="Planta de Tratamiento" :disabled="isHeadersLocked" />
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
                <th v-if="isEditMode && selectedEquipmentResources.length > 0" class="border">Días</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="activeResources.length === 0">
                <td :colspan="isEditMode && selectedEquipmentResources.length > 0 ? 9 : 8" class="text-center py-4 text-gray-500">
                  No hay recursos activos asignados al proyecto
                </td>
              </tr>
              <tr v-for="(resource, index) in activeResources" :key="resource.id">
                <td class="border text-center">
                  <div class="tooltip" :data-tip="hasCustodyChain(resource) ? 'Tiene cadena de custodia' : ''">
                    <input 
                      type="checkbox" 
                      class="checkbox checkbox-sm" 
                      :checked="resource.is_selected"
                      :disabled="isDetailsLocked || (hasCustodyChain(resource) && resource.is_selected)"
                      @change="isDetailsLocked ? null : toggleResourceSelection(resource)"
                    />
                  </div>
                </td>
                <td class="border text-center">{{ index + 1 }}</td>
                <td class="border">
                  {{ resource.resource_item_code || 'N/A' }}
                  <i v-if="hasCustodyChain(resource)" class="las la-link text-warning ml-1" title="Tiene cadena de custodia"></i>
                </td>
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
                <td v-if="isEditMode && selectedEquipmentResources.length > 0" class="border text-center">
                  <button
                    v-if="resource.type_resource === 'EQUIPO' && resource.is_selected && getEquipmentDetailForResource(resource)"
                    type="button"
                    class="btn btn-ghost btn-xs text-primary hover:bg-primary/10"
                    @click.stop="openCalendarModal(getEquipmentDetailForResource(resource))"
                    title="Configurar días de cobro"
                  >
                    <i class="las la-calendar-alt text-lg"></i>
                    <span class="text-xs ml-1">{{ getSelectedDays(getEquipmentDetailForResource(resource).detail_id).length }}d</span>
                  </button>
                  <span v-else class="text-gray-300">—</span>
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
                <td :colspan="isEditMode && selectedEquipmentResources.length > 0 ? 3 : 2" class="border text-center">{{ activeResources.length }} activos</td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Calendario inline eliminado - ahora es un modal popup -->

        <div class="divider">Notas Adicionales</div>

        <!-- Campo de Notas -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text font-semibold">Notas</span>
            <span class="label-text-alt text-gray-500">{{ (formData.notes || '').length }}/500</span>
          </label>
          <textarea 
            v-model="formData.notes" 
            class="textarea textarea-bordered w-full h-24" 
            placeholder="Ingrese notas adicionales sobre la planilla..."
            maxlength="500"
            :disabled="isHeadersLocked"
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
            <RouterLink :to="{ name: 'projects-detail', query: { tab: 'planillas' } }" class="btn btn-ghost" :class="{ 'btn-disabled': isSubmitting }">
              <i class="las la-times text-lg"></i> Cancelar
            </RouterLink>
            <button v-if="!isFullyLocked && !isProjectClosed" type="submit" class="btn btn-primary" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
              <i v-else class="las la-save text-lg"></i>
              {{ isSubmitting ? (isEditMode ? 'Actualizando...' : 'Creando...') : (isEditMode ? 'Actualizar Planilla' : 'Crear Planilla') }}
            </button>
          </div>
        </div>

      </div>
    </form>
  </div>

  <!-- Modal para cargar factura -->
  <dialog class="modal" :class="{ 'modal-open': showInvoiceModal }">
    <div class="modal-box max-w-lg">
      <h3 class="font-bold text-xl flex items-center gap-2 mb-4">
        <i class="las la-file-invoice text-accent"></i>
        Cargar Factura PDF
      </h3>
      <div class="form-control w-full mb-3">
        <label class="label">
          <span class="label-text font-semibold">Referencia de Factura <span class="text-error">*</span></span>
        </label>
        <input type="text" v-model="invoiceReference" maxlength="50"
               class="input input-bordered w-full" placeholder="Ej: FAC-2026-001" />
      </div>
      <input type="file" ref="invoiceFileInput" accept=".pdf"
             class="file-input file-input-bordered file-input-md w-full" @change="onInvoiceFileSelected" />
      <div v-if="isUploadingInvoice" class="mt-3">
        <progress class="progress progress-primary w-full"></progress>
        <p class="text-sm text-gray-500 mt-1">Subiendo factura...</p>
      </div>
      <div class="modal-action">
        <button class="btn" @click="showInvoiceModal = false" :disabled="isUploadingInvoice">Cancelar</button>
      </div>
    </div>
    <div class="modal-backdrop" @click="showInvoiceModal = false"></div>
  </dialog>

  <!-- Modal de Calendario de Días de Cobro -->
  <dialog class="modal" :class="{ 'modal-open': showCalendarModal }">
    <div class="modal-box max-w-2xl">
      <template v-if="calendarModalEquipment">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-lg flex items-center gap-2">
            <i class="las la-calendar-alt text-primary text-2xl"></i>
            Días de Cobro
          </h3>
          <button class="btn btn-sm btn-ghost btn-circle" @click="closeCalendarModal">
            <i class="las la-times text-lg"></i>
          </button>
        </div>

        <!-- Info del equipo -->
        <div class="bg-base-200 rounded-lg p-3 mb-4">
          <div class="flex items-center gap-2 mb-1">
            <span class="badge badge-primary badge-sm">EQUIPO</span>
            <span class="font-semibold">{{ calendarModalEquipment.resource_item_code }}</span>
            <span class="text-gray-500 text-sm">{{ calendarModalEquipment.resource_item_name }}</span>
          </div>
          <div class="text-xs text-gray-500">{{ calendarModalEquipment.detail }}</div>
          <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span>
              <i class="las la-sign-in-alt text-green-600"></i>
              Entrada: <strong>{{ calendarModalEquipment.operation_start_date ? new Date(calendarModalEquipment.operation_start_date + 'T00:00:00').toLocaleDateString('es-EC') : 'N/A' }}</strong>
            </span>
            <span v-if="calendarModalEquipment.is_retired && calendarModalEquipment.retirement_date">
              <i class="las la-sign-out-alt text-red-600"></i>
              Retiro: <strong class="text-red-600">{{ new Date(calendarModalEquipment.retirement_date + 'T00:00:00').toLocaleDateString('es-EC') }}</strong>
            </span>
            <span v-else-if="calendarModalEquipment.operation_end_date">
              <i class="las la-sign-out-alt text-orange-600"></i>
              Fin Op.: <strong>{{ new Date(calendarModalEquipment.operation_end_date + 'T00:00:00').toLocaleDateString('es-EC') }}</strong>
            </span>
            <span v-else>
              <i class="las la-infinity text-blue-500"></i>
              Sin fecha de retiro (todo el período)
            </span>
          </div>
        </div>

        <!-- Estadísticas rápidas -->
        <div class="grid grid-cols-3 gap-3 mb-4">
          <div class="bg-white border rounded-lg p-2 text-center">
            <div class="text-xs text-gray-500">Días seleccionados</div>
            <div class="text-xl font-bold text-primary">{{ getSelectedDays(calendarModalEquipment.detail_id).length }}</div>
          </div>
          <div class="bg-white border rounded-lg p-2 text-center">
            <div class="text-xs text-gray-500">Precio/día</div>
            <div class="text-xl font-bold">${{ parseFloat(calendarModalEquipment.unit_price || 0).toFixed(2) }}</div>
          </div>
          <div class="bg-white border rounded-lg p-2 text-center">
            <div class="text-xs text-gray-500">Total</div>
            <div class="text-xl font-bold text-green-700">
              ${{ (getSelectedDays(calendarModalEquipment.detail_id).length * parseFloat(calendarModalEquipment.unit_price || 0)).toFixed(2) }}
            </div>
          </div>
        </div>

        <!-- Instrucciones -->
        <div class="text-xs text-gray-400 mb-2 flex items-center gap-1">
          <i class="las la-info-circle"></i>
          Click para seleccionar/deseleccionar. <strong>Shift+Click</strong> para seleccionar un rango.
        </div>

        <!-- Botones de acción -->
        <div class="flex items-center gap-2 mb-3">
          <button 
            type="button" 
            class="btn btn-outline btn-xs"
            :disabled="isDetailsLocked"
            @click.stop="toggleAllEquipmentDays(calendarModalEquipment)"
          >
            <i class="las la-check-double"></i>
            {{ getSelectedDays(calendarModalEquipment.detail_id).length === countValidDays(calendarModalEquipment) ? 'Deseleccionar todos' : 'Seleccionar todos' }}
          </button>
        </div>

        <!-- Grid de días -->
        <div class="grid grid-cols-7 sm:grid-cols-8 gap-1.5">
          <button
            v-for="day in getDaysInPeriod"
            :key="day"
            type="button"
            class="btn btn-sm w-full h-10 p-0 text-sm font-semibold"
            :class="{
              'btn-primary': getSelectedDays(calendarModalEquipment.detail_id).includes(day) && isDayInEquipmentRange(calendarModalEquipment, day),
              'btn-outline': !getSelectedDays(calendarModalEquipment.detail_id).includes(day) && isDayInEquipmentRange(calendarModalEquipment, day),
              'btn-disabled bg-gray-100 text-gray-300 cursor-not-allowed': !isDayInEquipmentRange(calendarModalEquipment, day)
            }"
            :disabled="isDetailsLocked || !isDayInEquipmentRange(calendarModalEquipment, day)"
            @click.stop="isDayInEquipmentRange(calendarModalEquipment, day) ? toggleEquipmentDay(calendarModalEquipment.detail_id, day, $event, calendarModalEquipment) : null"
          >
            {{ day }}
          </button>
        </div>

        <!-- Footer del modal -->
        <div class="modal-action mt-4">
          <div class="flex items-center justify-between w-full">
            <span class="text-sm text-gray-500">
              <i class="las la-calendar-check text-primary"></i>
              {{ getSelectedDays(calendarModalEquipment.detail_id).length }} día(s) seleccionado(s)
            </span>
            <div class="flex gap-2">
              <button class="btn btn-ghost btn-sm" @click="closeCalendarModal">Cancelar</button>
              <button 
                type="button" 
                class="btn btn-primary btn-sm"
                :disabled="isDetailsLocked || isSavingDays"
                @click.stop="saveEquipmentDays(calendarModalEquipment.detail_id)"
              >
                <span v-if="isSavingDays && savingDetailId === calendarModalEquipment.detail_id" class="loading loading-spinner loading-xs"></span>
                <i v-else class="las la-save"></i>
                Guardar días
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
    <div class="modal-backdrop" @click="closeCalendarModal"></div>
  </dialog>
</template>
