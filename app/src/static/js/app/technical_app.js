// Arrays temporales para almacenar datos antes de guardar
let tempVaccinations = [];
let tempPasses = [];

// Diccionario para traducir tipos de vacunas
const vaccineTypeLabels = {
  'HEPATITIS_A_B': 'Hepatitis A y B',
  'TETANUS': 'Tétanos',
  'TYPHOID': 'Tifoidea',
  'YELLOW_FEVER': 'Fiebre Amarilla',
  'INFLUENZA': 'Influenza',
  'MEASLES': 'Sarampión',
  'COVID': 'Covid-19',
  'OTHER': 'Otra'
};

// Diccionario para traducir bloques
const bloqueLabels = {
  'petroecuador': 'Tarjeta de Petroecuador',
  'shaya': 'Shaya',
  'consorcio_shushufindi': 'Consorcio Shushufindi',
  'enap_sipec': 'ENAP SIPEC',
  'orion': 'Tarjeta Orion',
  'andes_petroleum': 'Andes Petroleum',
  'pardalis_services': 'Pardalis Services',
  'frontera_energy': 'Frontera Energy',
  'gran_tierra': 'Gran Tierra',
  'pcr': 'PCR',
  'halliburton': 'Halliburton',
  'gente_oil': 'Gente Oil',
  'tribiol_gas': 'Tribiol Gas',
  'adico': 'Adico',
  'cuyaveno_petro': 'Cuyaveno Petro',
  'geopark': 'Geopark'
};

// Definición para certificateDurations (faltante en el código original)
const certificateDurations = {
  'license': {
    badgeId: 'licenseExpiryBadge',
    startField: 'id_license_issue_date',
    endField: 'id_license_expiry_date',
    name: 'Licencia'
  },
  'defensiveDriving': {
    badgeId: 'defensiveDrivingExpiryBadge',
    startField: 'id_defensive_driving_certificate_issue_date',
    endField: 'id_defensive_driving_certificate_expiry_date',
    name: 'Manejo Defensivo'
  },
  'mae': {
    badgeId: 'maeExpiryBadge',
    startField: 'id_mae_certificate_issue_date',
    endField: 'id_mae_certificate_expiry_date',
    name: 'MAE'
  },
  'medical': {
    badgeId: 'medicalExpiryBadge',
    startField: 'id_medical_certificate_issue_date',
    endField: 'id_medical_certificate_expiry_date',
    name: 'Médico'
  }
};

// Función para calcular la edad
function calculateAge(birthDateString) {
  if (!birthDateString) return null;
  const birthDate = new Date(birthDateString);
  const today = new Date();

  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age < 0 ? 0 : age; // Evitar edad negativa si la fecha es futura
}

// Función para inicializar el calculador de fecha de nacimiento y edad
function initializeBirthDateCalculator() {
  const birthDateInput = document.getElementById('id_birth_date'); // Asumiendo que el ID es id_birth_date
  const ageDisplay = document.getElementById('ageDisplay');

  if (!birthDateInput || !ageDisplay) {
    // console.warn('Elementos para cálculo de edad no encontrados.');
    return;
  }

  function updateAgeDisplay() {
    const birthDateString = birthDateInput.value;
    if (birthDateString) {
      const age = calculateAge(birthDateString);
      if (age !== null) {
        ageDisplay.textContent = `${age} año${age === 1 ? '' : 's'}`;
        ageDisplay.style.display = 'inline-flex';
      } else {
        ageDisplay.style.display = 'none';
      }
    } else {
      ageDisplay.style.display = 'none';
    }
  }

  birthDateInput.addEventListener('change', updateAgeDisplay);
  // Llamada inicial para mostrar la edad si ya hay una fecha
  if (birthDateInput.value) {
    updateAgeDisplay();
  }
}

// --- Funciones para Vacunaciones Temporales ---
function updateHiddenVaccinationsField() {
  const hiddenInput = document.getElementById('id_vaccinations_data'); // Asegúrate que este ID es correcto
  if (hiddenInput) {
    hiddenInput.value = JSON.stringify(tempVaccinations);
  }
}

function updateNoVaccinationsMessageVisibility() {
  const messageEl = document.getElementById('noVaccinationsMessage');
  const existingVaccinationsEl = document.getElementById('existingVaccinations');
  const existingCount = existingVaccinationsEl ? existingVaccinationsEl.children.length : 0;
  
  if (messageEl) {
    if (tempVaccinations.length === 0 && existingCount === 0) {
      messageEl.style.display = 'block';
    } else {
      messageEl.style.display = 'none';
    }
  }
}

function renderTempVaccinations() {
  const listEl = document.getElementById('tempVaccinationsList');
  if (!listEl) return;
  listEl.innerHTML = ''; // Limpiar lista

  tempVaccinations.forEach((vaccination, index) => {
    const item = document.createElement('div');
    item.className = 'border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors';
    item.innerHTML = `
      <div class="flex justify-between items-start">
        <div>
          <h4 class="font-medium text-gray-800">${vaccineTypeLabels[vaccination.vaccine_type] || vaccination.vaccine_type}</h4>
          <p class="text-sm text-gray-600 mt-1">
            <span class="font-medium">Aplicada:</span> 
            ${formatDate(vaccination.application_date)}
          </p>
          ${vaccination.dose_number ? `<p class="text-sm text-gray-600"><span class="font-medium">Dosis:</span> ${vaccination.dose_number}</p>` : ''}
          ${vaccination.next_dose_date ? `<p class="text-sm text-gray-600"><span class="font-medium">Próxima dosis:</span> ${formatDate(vaccination.next_dose_date)}</p>` : ''}
          ${vaccination.batch_number ? `<p class="text-xs text-gray-500 mt-1">Lote: ${vaccination.batch_number}</p>` : ''}
          ${vaccination.notes ? `<p class="text-xs text-gray-500 mt-1">Notas: ${vaccination.notes}</p>` : ''}
        </div>
        <div class="flex gap-1">
          <button type="button" class="btn btn-ghost btn-xs text-red-600" onclick="removeTempVaccination(${index})">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>
    `;
    listEl.appendChild(item);
  });
  updateHiddenVaccinationsField();
  updateNoVaccinationsMessageVisibility();
}

function addTempVaccination(vaccinationData) {
  tempVaccinations.push(vaccinationData);
  renderTempVaccinations();
}

function removeTempVaccination(index) {
  tempVaccinations.splice(index, 1);
  renderTempVaccinations();
}

// --- Funciones para Pases Técnicos Temporales ---
function updateHiddenPassesField() {
  const hiddenInput = document.getElementById('id_passes_data'); // Asegúrate que este ID es correcto
  if (hiddenInput) {
    hiddenInput.value = JSON.stringify(tempPasses);
  }
}

function updateNoPassesMessageVisibility() {
  const messageEl = document.getElementById('noPassesMessage');
  const existingPassesEl = document.getElementById('existingPasses');
  const existingCount = existingPassesEl ? existingPassesEl.children.length : 0;

  if (messageEl) {
    if (tempPasses.length === 0 && existingCount === 0) {
      messageEl.style.display = 'block';
    } else {
      messageEl.style.display = 'none';
    }
  }
}

function renderTempPasses() {
  const listEl = document.getElementById('tempPassesList');
  if (!listEl) return;
  listEl.innerHTML = ''; // Limpiar lista

  tempPasses.forEach((pass, index) => {
    const item = document.createElement('div');
    item.className = 'border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors';
    item.innerHTML = `
      <div class="flex justify-between items-start">
        <div>
          <h4 class="font-medium text-gray-800">${bloqueLabels[pass.bloque] || pass.bloque}</h4>
          <p class="text-sm text-gray-600 mt-1">
            <span class="font-medium">Vence:</span> 
            ${formatDate(pass.fecha_caducidad)}
          </p>
          <div class="mt-2">
            ${getPassStatus(pass.fecha_caducidad)}
          </div>
        </div>
        <div class="flex gap-1">
          <button type="button" class="btn btn-ghost btn-xs text-red-600" onclick="removeTempPass(${index})">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>
    `;
    listEl.appendChild(item);
  });
  updateHiddenPassesField();
  updateNoPassesMessageVisibility();
}

function addTempPass(passData) {
  tempPasses.push(passData);
  renderTempPasses();
}

function removeTempPass(index) {
  tempPasses.splice(index, 1);
  renderTempPasses();
}


// Configuración para cálculo automático de fechas de vencimiento
const expiryConfig = {
  'license': {
    issueField: 'id_license_issue_date',
    expiryField: 'id_license_expiry_date',
    duration: 5, // años
    durationUnit: 'years'
  },
  'defensiveDriving': {
    issueField: 'id_defensive_driving_certificate_issue_date',
    expiryField: 'id_defensive_driving_certificate_expiry_date',
    duration: 2, // años
    durationUnit: 'years'
  },
  'mae': {
    issueField: 'id_mae_certificate_issue_date',
    expiryField: 'id_mae_certificate_expiry_date',
    duration: 2, // años
    durationUnit: 'years'
  },
  'medical': {
    issueField: 'id_medical_certificate_issue_date',
    expiryField: 'id_medical_certificate_expiry_date',
    duration: 1, // año
    durationUnit: 'years'
  }
};

// Función para calcular fecha de vencimiento basada en fecha de emisión
function calculateExpiryDate(issueDate, duration, unit = 'years') {
  if (!issueDate) return null;
  
  const date = new Date(issueDate);
  
  switch(unit) {
    case 'years':
      date.setFullYear(date.getFullYear() + duration);
      break;
    case 'months':
      date.setMonth(date.getMonth() + duration);
      break;
    case 'days':
      date.setDate(date.getDate() + duration);
      break;
  }
  
  // Formato YYYY-MM-DD para input type="date"
  return date.toISOString().split('T')[0];
}

// Configurar el cálculo automático de fechas de vencimiento
function setupExpiryDateCalculations() {
  Object.keys(expiryConfig).forEach(key => {
    const config = expiryConfig[key];
    const issueField = document.getElementById(config.issueField);
    const expiryField = document.getElementById(config.expiryField);
    
    if (!issueField || !expiryField) return;
    
    issueField.addEventListener('change', function() {
      const newExpiryDate = calculateExpiryDate(
        this.value, 
        config.duration, 
        config.durationUnit
      );
      
      if (newExpiryDate) {
        expiryField.value = newExpiryDate;
        
        // Destacar visualmente el campo actualizado
        expiryField.style.backgroundColor = '#f0f9ff';
        expiryField.style.borderColor = '#0ea5e9';
        
        // Actualizar el badge si existe
        if (certificateDurations[key]) {
          updateExpiryBadge(certificateDurations[key]);
        }
        
        // Quitar el destacado después de un momento
        setTimeout(() => {
          expiryField.style.backgroundColor = '';
          expiryField.style.borderColor = '';
        }, 2000);
      }
    });
    
    // Calcular fecha inicial si ya hay valor
    if (issueField.value) {
      const newExpiryDate = calculateExpiryDate(
        issueField.value, 
        config.duration, 
        config.durationUnit
      );
      
      if (newExpiryDate && !expiryField.value) {
        expiryField.value = newExpiryDate;
      }
    }
  });
}

// Función para formatear fecha
function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES');
}

// Funciones para manejar modales de vacunación
function openVaccinationModal() {
  document.getElementById('vaccinationModal').classList.add('modal-open');
}

function closeVaccinationModal() {
  document.getElementById('vaccinationModal').classList.remove('modal-open');
  document.getElementById('vaccinationForm').reset();
}

// Funciones para manejar modales de pases técnicos
function openTechnicalPassModal() {
  document.getElementById('technicalPassModal').classList.add('modal-open');
}

function closeTechnicalPassModal() {
  document.getElementById('technicalPassModal').classList.remove('modal-open');
  document.getElementById('technicalPassForm').reset();
}

// Función para actualizar el modal de vacunación con esquemas automáticos
function updateVaccinationModal() {
  const vaccineTypeSelect = document.querySelector('#vaccinationForm select[name="vaccine_type"]');
  const doseNumberInput = document.querySelector('#vaccinationForm input[name="dose_number"]');
  const applicationDateInput = document.querySelector('#vaccinationForm input[name="application_date"]');
  const nextDoseDateInput = document.querySelector('#vaccinationForm input[name="next_dose_date"]');
  
  if (!vaccineTypeSelect || !applicationDateInput || !nextDoseDateInput) return;
  
  function calculateAndUpdateNextDose() {
    const vaccineType = vaccineTypeSelect.value;
    const doseNumber = doseNumberInput ? doseNumberInput.value || 1 : 1;
    const applicationDate = applicationDateInput.value;
    
    if (!vaccineType || !applicationDate) return;
    
    // Calcular próxima fecha basada en tipo de vacuna
    const nextDate = new Date(applicationDate);
    
    switch(vaccineType) {
      case 'HEPATITIS_A_B':
        if (doseNumber == 1) nextDate.setDate(nextDate.getDate() + 30);
        else if (doseNumber == 2) nextDate.setMonth(nextDate.getMonth() + 7);
        else if (doseNumber == 3) nextDate.setFullYear(nextDate.getFullYear() + 5);
        else return;
        break;
      case 'TETANUS':
        if (doseNumber == 1) nextDate.setDate(nextDate.getDate() + 30);
        else if (doseNumber == 2) nextDate.setMonth(nextDate.getMonth() + 7);
        else if (doseNumber == 3) nextDate.setFullYear(nextDate.getFullYear() + 1);
        else nextDate.setFullYear(nextDate.getFullYear() + 10);
        break;
      case 'TYPHOID':
        nextDate.setFullYear(nextDate.getFullYear() + 3);
        break;
      case 'INFLUENZA':
        nextDate.setFullYear(nextDate.getFullYear() + 1);
        break;
      case 'COVID':
        if (doseNumber <= 4) nextDate.setMonth(nextDate.getMonth() + 6);
        else return;
        break;
      case 'YELLOW_FEVER':
      case 'MEASLES':
        return; // Dosis única
      default:
        nextDate.setDate(nextDate.getDate() + 30);
    }
    
    if (nextDoseDateInput) {
      nextDoseDateInput.value = nextDate.toISOString().split('T')[0];
    }
  }
  
  // Agregar eventos para recalcular automáticamente
  if (vaccineTypeSelect) {
    vaccineTypeSelect.addEventListener('change', calculateAndUpdateNextDose);
  }
  
  if (doseNumberInput) {
    doseNumberInput.addEventListener('input', calculateAndUpdateNextDose);
  }
  
  if (applicationDateInput) {
    applicationDateInput.addEventListener('change', calculateAndUpdateNextDose);
  }
}

// Función para actualizar el badge de expiración de certificados
function updateExpiryBadge(config) {
  const startField = document.getElementById(config.startField);
  const endField = document.getElementById(config.endField);
  const badge = document.getElementById(config.badgeId);
  
  if (!badge || !endField) return;
  
  const endDate = endField.value ? new Date(endField.value) : null;
  
  if (!endDate) {
    badge.style.display = 'none';
    return;
  }
  
  const today = new Date();
  today.setHours(0, 0, 0, 0); // Normalizar la hora para comparación exacta
  endDate.setHours(0, 0, 0, 0);
  
  const timeDiff = endDate.getTime() - today.getTime();
  const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
  
  badge.style.display = 'inline-flex';
  
  if (daysDiff < 0) {
    // Vencido - mostrar días transcurridos en rojo
    const daysOverdue = Math.abs(daysDiff);
    badge.className = 'badge badge-error badge-soft';
    badge.textContent = `Vencido hace ${daysOverdue} día${daysOverdue === 1 ? '' : 's'}`;
    badge.style.backgroundColor = '#fecaca'; // rojo claro
    badge.style.color = '#991b1b'; // rojo oscuro
    badge.style.borderColor = '#f87171';
  } else if (daysDiff === 0) {
    // Vence hoy - rojo intenso
    badge.className = 'badge badge-error badge-soft';
    badge.textContent = 'Vence HOY';
    badge.style.backgroundColor = '#dc2626'; // rojo más intenso
    badge.style.color = '#ffffff'; // texto blanco
    badge.style.borderColor = '#dc2626';
    badge.style.fontWeight = 'bold';
  } else if (daysDiff <= 7) {
    // Vence en una semana - rojo urgente
    badge.className = 'badge badge-error badge-soft';
    badge.textContent = `Vence en ${daysDiff} día${daysDiff === 1 ? '' : 's'}`;
    badge.style.backgroundColor = '#fca5a5'; // rojo medio
    badge.style.color = '#7f1d1d'; // rojo muy oscuro
    badge.style.borderColor = '#ef4444';
    badge.style.fontWeight = 'bold';
  } else if (daysDiff <= 30) {
    // Vence en un mes - amarillo/naranja de advertencia
    badge.className = 'badge badge-warning badge-soft';
    badge.textContent = `Vence en ${daysDiff} día${daysDiff === 1 ? '' : 's'}`;
    badge.style.backgroundColor = '#fed7aa'; // naranja claro
    badge.style.color = '#9a3412'; // naranja oscuro
    badge.style.borderColor = '#fb923c';
  } else if (daysDiff <= 60) {
    // Próximo a vencer - amarillo suave
    badge.className = 'badge badge-warning badge-soft';
    badge.textContent = `Vence en ${daysDiff} días`;
    badge.style.backgroundColor = '#fef3c7'; // amarillo claro
    badge.style.color = '#92400e'; // amarillo oscuro
    badge.style.borderColor = '#fbbf24';
  } else {
    // Vigente - verde
    badge.className = 'badge badge-success badge-soft';
    if (daysDiff <= 365) {
      badge.textContent = `Vigente (${daysDiff} días)`;
    } else {
      const years = Math.floor(daysDiff / 365);
      const remainingDays = daysDiff % 365;
      if (remainingDays === 0) {
        badge.textContent = `Vigente (${years} año${years === 1 ? '' : 's'})`;
      } else {
        badge.textContent = `Vigente (${years}a ${remainingDays}d)`;
      }
    }
    badge.style.backgroundColor = '#dcfce7'; // verde claro
    badge.style.color = '#166534'; // verde oscuro
    badge.style.borderColor = '#4ade80';
  }
  
  // Añadir efecto de parpadeo para elementos críticos (vencidos o que vencen hoy)
  if (daysDiff <= 0) {
    badge.style.animation = 'pulse 2s infinite';
  } else {
    badge.style.animation = 'none';
  }
}

// Función mejorada para calcular estado del pase con días exactos
function getPassStatus(fechaCaducidad) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const expiry = new Date(fechaCaducidad);
  expiry.setHours(0, 0, 0, 0);
  
  const timeDiff = expiry.getTime() - today.getTime();
  const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
  
  if (daysDiff < 0) {
    const daysOverdue = Math.abs(daysDiff);
    return `<span class="badge badge-error badge-sm" style="background-color: #fecaca; color: #991b1b; border-color: #f87171; animation: pulse 2s infinite;">Vencido hace ${daysOverdue} día${daysOverdue === 1 ? '' : 's'}</span>`;
  } else if (daysDiff === 0) {
    return `<span class="badge badge-error badge-sm" style="background-color: #dc2626; color: #ffffff; border-color: #dc2626; font-weight: bold; animation: pulse 2s infinite;">Vence HOY</span>`;
  } else if (daysDiff <= 7) {
    return `<span class="badge badge-error badge-sm" style="background-color: #fca5a5; color: #7f1d1d; border-color: #ef4444; font-weight: bold;">Vence en ${daysDiff} día${daysDiff === 1 ? '' : 's'}</span>`;
  } else if (daysDiff <= 30) {
    return `<span class="badge badge-warning badge-sm" style="background-color: #fed7aa; color: #9a3412; border-color: #fb923c;">Vence en ${daysDiff} día${daysDiff === 1 ? '' : 's'}</span>`;
  } else if (daysDiff <= 60) {
    return `<span class="badge badge-warning badge-sm" style="background-color: #fef3c7; color: #92400e; border-color: #fbbf24;">Vence en ${daysDiff} días</span>`;
  } else {
    return `<span class="badge badge-success badge-sm" style="background-color: #dcfce7; color: #166534; border-color: #4ade80;">Vigente (${daysDiff} días)</span>`;
  }
}

document.addEventListener('DOMContentLoaded', function() {
  // Inicializar modal de vacunación con cálculos automáticos
  updateVaccinationModal();
  
  // Inicializar calculador de edad
  initializeBirthDateCalculator();

  // Renderizar listas temporales iniciales (si es necesario, aunque suelen empezar vacías)
  renderTempVaccinations();
  renderTempPasses();
  
  // Inicializar badges de expiración
  Object.keys(certificateDurations).forEach(key => {
    const config = certificateDurations[key];
    
    // Configurar eventos para actualizar badges
    const startField = document.getElementById(config.startField);
    const endField = document.getElementById(config.endField);
    
    if (startField) startField.addEventListener('change', () => updateExpiryBadge(config));
    if (endField) endField.addEventListener('change', () => updateExpiryBadge(config));
    
    // Actualizar badge inicial
    updateExpiryBadge(config);
  });
  
  // Configurar cálculo automático de fechas de vencimiento
  setupExpiryDateCalculations();
  
  // Configurar manejadores de formularios
  const vaccinationForm = document.getElementById('vaccinationForm');
  if (vaccinationForm) {
    vaccinationForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const vaccinationData = {
        vaccine_type: formData.get('vaccine_type'),
        application_date: formData.get('application_date'),
        dose_number: formData.get('dose_number') || null,
        batch_number: formData.get('batch_number') || null,
        next_dose_date: formData.get('next_dose_date') || null,
        notes: formData.get('notes') || null
      };
      
      // Validar campos requeridos
      if (!vaccinationData.vaccine_type || !vaccinationData.application_date) {
        // Considera usar una notificación más amigable que alert()
        // Por ejemplo, mostrar un mensaje de error en el modal.
        const errorMsgContainer = this.querySelector('.form-error-message'); // Necesitarías añadir este elemento al modal
        if (errorMsgContainer) errorMsgContainer.textContent = 'Por favor complete los campos requeridos: Tipo de Vacuna y Fecha de Aplicación.';
        else alert('Por favor complete los campos requeridos: Tipo de Vacuna y Fecha de Aplicación.');
        return;
      }
      
      addTempVaccination(vaccinationData);
      closeVaccinationModal();
    });
  }

  const technicalPassForm = document.getElementById('technicalPassForm');
  if (technicalPassForm) {
    technicalPassForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const passData = {
        bloque: formData.get('bloque'),
        fecha_caducidad: formData.get('fecha_caducidad')
      };
      
      // Validar campos requeridos
      if (!passData.bloque || !passData.fecha_caducidad) {
        // Similar al formulario de vacunación, considera una mejor UX para errores.
        alert('Por favor complete todos los campos del pase.');
        return;
      }
      
      addTempPass(passData);
      closeTechnicalPassModal();
    });
  }

  // Asegurarse de que los campos ocultos tengan los IDs correctos
  // Si {{ form.vaccinations_data }} renderiza <input ... name="vaccinations_data">
  // y no tiene ID, necesitarás seleccionarlo por nombre o añadirle un ID en el template de Django.
  // Por ahora, asumimos que los IDs son 'id_vaccinations_data' y 'id_passes_data'.
  // Si no es así, ajusta getElementById en updateHiddenVaccinationsField y updateHiddenPassesField.
  // Ejemplo: document.querySelector('input[name="vaccinations_data"]')

  // Actualizar visibilidad de mensajes "sin datos" al cargar la página
  updateNoVaccinationsMessageVisibility();
  updateNoPassesMessageVisibility();

});

// Actualizar todos los badges de certificados cada minuto
setInterval(() => {
  Object.keys(certificateDurations).forEach(fieldId => {
    const config = certificateDurations[fieldId];
    updateExpiryBadge(config);
  });
}, 60000); // 60 segundos
