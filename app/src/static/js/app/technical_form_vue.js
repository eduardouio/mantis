/**
 * Componente Vue.js para el formulario de técnicos
 * Maneja la creación y edición de técnicos, sus pases y vacunas
 */

// Diccionarios para traducir valores de códigos a etiquetas legibles
const VACCINE_TYPE_LABELS = {
  'HEPATITIS_A_B': 'Hepatitis A y B',
  'TETANUS': 'Tétanos',
  'TYPHOID': 'Tifoidea',
  'YELLOW_FEVER': 'Fiebre Amarilla',
  'INFLUENZA': 'Influenza',
  'MEASLES': 'Sarampión',
  'COVID': 'Covid-19',
  'OTHER': 'Otra'
};

const BLOQUE_LABELS = {
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

// Configuración para cálculo automático de fechas de vencimiento
const EXPIRY_CONFIG = {
  'license': {
    issueField: 'license_issue_date',
    expiryField: 'license_expiry_date',
    duration: 5, // años
    durationUnit: 'years'
  },
  'defensiveDriving': {
    issueField: 'defensive_driving_certificate_issue_date',
    expiryField: 'defensive_driving_certificate_expiry_date',
    duration: 2, // años
    durationUnit: 'years'
  },
  'mae': {
    issueField: 'mae_certificate_issue_date',
    expiryField: 'mae_certificate_expiry_date',
    duration: 2, // años
    durationUnit: 'years'
  },
  'medical': {
    issueField: 'medical_certificate_issue_date',
    expiryField: 'medical_certificate_expiry_date',
    duration: 1, // año
    durationUnit: 'years'
  }
};

// Configuración de certificados para mostrar badges
const CERTIFICATE_DURATIONS = {
  'license': {
    badgeId: 'licenseExpiryBadge',
    name: 'Licencia'
  },
  'defensiveDriving': {
    badgeId: 'defensiveDrivingExpiryBadge',
    name: 'Manejo Defensivo'
  },
  'mae': {
    badgeId: 'maeExpiryBadge',
    name: 'MAE'
  },
  'medical': {
    badgeId: 'medicalExpiryBadge',
    name: 'Médico'
  }
};

/**
 * Funciones Utilitarias
 */

// Formatear fecha a formato YYYY-MM-DD para inputs date
function formatDateForInput(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toISOString().split('T')[0];
}

// Formatear fecha para mostrar en formato legible
function formatDisplayDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES');
}

// Calcular fecha de vencimiento basada en fecha de emisión
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
  
  return date.toISOString().split('T')[0]; // Formato YYYY-MM-DD
}

// Calcular estado del pase (válido, expirado, próximo a expirar)
function getPassStatus(fechaCaducidad) {
  if (!fechaCaducidad) return '';

  const hoy = new Date();
  const fechaExp = new Date(fechaCaducidad);
  const diffTime = fechaExp - hoy;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) {
    return `<span class="badge badge-error badge-sm">Expirado (${Math.abs(diffDays)} días)</span>`;
  } else if (diffDays <= 30) {
    return `<span class="badge badge-warning badge-sm">Expira en ${diffDays} días</span>`;
  } else {
    return `<span class="badge badge-success badge-sm">Válido (${diffDays} días)</span>`;
  }
}

// Calcular la edad desde una fecha de nacimiento
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

// Actualizar el estado visual de un certificado en la UI
function updateExpiryBadge(certificateKey) {
  const config = CERTIFICATE_DURATIONS[certificateKey];
  if (!config || !config.badgeId) return;
  
  const badgeEl = document.getElementById(config.badgeId);
  if (!badgeEl) return;
  
  const expiryField = EXPIRY_CONFIG[certificateKey]?.expiryField;
  if (!expiryField) return;
  
  // Obtener el valor de la fecha de vencimiento desde el objeto Vue
  const expiryDate = technicalApp.$data[expiryField];
  
  if (!expiryDate) {
    badgeEl.style.display = 'none';
    return;
  }
  
  const today = new Date();
  const expDate = new Date(expiryDate);
  const diffTime = expDate - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  badgeEl.style.display = 'inline-flex';
  
  if (diffDays < 0) {
    badgeEl.textContent = `Expirado (${Math.abs(diffDays)} días)`;
    badgeEl.className = 'badge badge-error badge-soft';
  } else if (diffDays <= 30) {
    badgeEl.textContent = `Expira en ${diffDays} días`;
    badgeEl.className = 'badge badge-warning badge-soft';
  } else {
    badgeEl.textContent = `Válido por ${diffDays} días`;
    badgeEl.className = 'badge badge-success badge-soft';
  }
}

/**
 * Inicialización del componente Vue
 */

// Crear la aplicación Vue 3
const app = Vue.createApp({
  // Estado inicial del componente
  data() {
    return {
      // Datos del formulario principal
      id: null,
      first_name: '',
      last_name: '',
      email: '',
      work_area: '',
      dni: '',
      nro_phone: '',
      birth_date: '',
      date_joined: '',
      is_active: true,
      is_iess_affiliated: false,
      has_life_insurance_policy: false,
      
      // Fechas de certificados
      license_issue_date: '',
      license_expiry_date: '',
      defensive_driving_certificate_issue_date: '',
      defensive_driving_certificate_expiry_date: '',
      mae_certificate_issue_date: '',
      mae_certificate_expiry_date: '',
      medical_certificate_issue_date: '',
      medical_certificate_expiry_date: '',
      
      // Datos de certificación Quest
      quest_ncst_code: '',
      quest_instructor: '',
      quest_start_date: '',
      quest_end_date: '',
      notes: '',
      
      // Colecciones relacionadas
      passes: [],
      vaccinations: [],
      
      // Diccionarios para labels
      VACCINE_TYPE_LABELS: VACCINE_TYPE_LABELS,
      BLOQUE_LABELS: BLOQUE_LABELS,
      
      // Variables para el modal de vacunación
      currentVaccination: {
        id: null,
        vaccine_type: '',
        application_date: '',
        dose_number: '',
        batch_number: '',
        next_dose_date: '',
        notes: ''
      },
      vaccinationEditIndex: -1, // -1 para nueva vacunación, índice >= 0 para edición
      
      // Variables para el modal de pase
      currentPass: {
        id: null,
        bloque: '',
        fecha_caducidad: ''
      },
      passEditIndex: -1, // -1 para nuevo pase, índice >= 0 para edición
      
      // Estado del formulario
      formErrors: [],
      isSubmitting: false,
      
      // Alertas y errores
      showAlert: false,
      alertMessage: '',
      alertType: 'info',
      errors: {}
    };
  },
  
  // Propiedades computadas
  computed: {
    // Nombre completo del técnico
    fullName() {
      return `${this.first_name} ${this.last_name}`.trim();
    },
    
    // Edad calculada a partir de la fecha de nacimiento
    age() {
      return calculateAge(this.birth_date);
    },
    
    // Verifica si el formulario tiene datos suficientes para ser enviado
    isFormValid() {
      return this.first_name && this.last_name && this.dni;
    }
  },
  
  // Métodos del componente
  methods: {
    /**
     * Inicializa los datos a partir de un técnico existente
     * @param {Object} technicalData - Datos del técnico
     */
    initFromExistingTechnical(technicalData) {
      if (!technicalData) return;
      
      // Copiar propiedades directas del técnico
      for (const key in technicalData) {
        if (key in this.$data && key !== 'vaccinations' && key !== 'passes') {
          this[key] = technicalData[key];
        }
      }
      
      // Inicializar colecciones relacionadas
      if (technicalData.vaccinations && Array.isArray(technicalData.vaccinations)) {
        this.vaccinations = [...technicalData.vaccinations];
      }
      
      if (technicalData.passes && Array.isArray(technicalData.passes)) {
        this.passes = [...technicalData.passes];
      }
      
      // Actualizar estados visuales
      this.$nextTick(() => {
        this.updateAllExpiryBadges();
        this.updateAgeDisplay();
      });
    },
    
    /**
     * Actualiza todos los badges de fechas de vencimiento
     */
    updateAllExpiryBadges() {
      for (const key in CERTIFICATE_DURATIONS) {
        updateExpiryBadge(key);
      }
    },
    
    /**
     * Actualiza la visualización de la edad
     */
    updateAgeDisplay() {
      const ageDisplay = document.getElementById('ageDisplay');
      if (!ageDisplay) return;
      
      if (this.birth_date) {
        const age = this.age;
        if (age !== null) {
          ageDisplay.textContent = `${age} año${age === 1 ? '' : 's'}`;
          ageDisplay.style.display = 'inline-flex';
        } else {
          ageDisplay.style.display = 'none';
        }
      } else {
        ageDisplay.style.display = 'none';
      }
    },
    
    /**
     * Calcula la fecha de vencimiento según la configuración al cambiar una fecha de emisión
     */
    handleIssueDateChange(configKey) {
      const config = EXPIRY_CONFIG[configKey];
      if (!config) return;
      
      const issueDate = this[config.issueField];
      if (!issueDate) return;
      
      const newExpiryDate = calculateExpiryDate(
        issueDate, 
        config.duration, 
        config.durationUnit
      );
      
      if (newExpiryDate) {
        this[config.expiryField] = newExpiryDate;
        
        // Actualizar el badge si existe
        this.$nextTick(() => {
          updateExpiryBadge(configKey);
        });
      }
    },
    
    /**
     * Maneja los cambios en las fechas de vencimiento
     */
    handleExpiryDateChange(configKey) {
      this.$nextTick(() => {
        updateExpiryBadge(configKey);
      });
    },
    
    /**
     * Abre el modal para agregar una nueva vacunación
     */
    openVaccinationModal() {
      this.currentVaccination = {
        id: null,
        vaccine_type: '',
        application_date: formatDateForInput(new Date()),
        dose_number: '',
        batch_number: '',
        next_dose_date: '',
        notes: ''
      };
      this.editingVaccinationIndex = -1;
      document.getElementById('vaccinationModal').classList.add('modal-open');
    },
    
    /**
     * Cierra el modal de vacunación
     */
    closeVaccinationModal() {
      document.getElementById('vaccinationModal').classList.remove('modal-open');
    },
    
    /**
     * Guarda la vacunación actual desde el modal
     */
    saveVaccination() {
      // Validar campos requeridos
      if (!this.currentVaccination.vaccine_type || !this.currentVaccination.application_date) {
        this.showAlert = true;
        this.alertMessage = 'Tipo de vacuna y fecha de aplicación son requeridos';
        this.alertType = 'error';
        return;
      }
      
      // Crear copia para evitar referencias
      const vaccinationData = JSON.parse(JSON.stringify(this.currentVaccination));
      
      // Si estamos editando, actualizar el elemento existente
      if (this.editingVaccinationIndex >= 0) {
        this.vaccinations[this.editingVaccinationIndex] = vaccinationData;
      } else {
        // Caso contrario, agregar al array
        this.vaccinations.push(vaccinationData);
      }
      
      // Cerrar modal y limpiar estado
      this.closeVaccinationModal();
      this.currentVaccination = {
        id: null,
        vaccine_type: '',
        application_date: '',
        dose_number: '',
        batch_number: '',
        next_dose_date: '',
        notes: ''
      };
      this.editingVaccinationIndex = -1;
    },
    
    /**
     * Edita una vacunación existente
     */
    editVaccination(index) {
      if (index >= 0 && index < this.vaccinations.length) {
        this.currentVaccination = JSON.parse(JSON.stringify(this.vaccinations[index]));
        this.editingVaccinationIndex = index;
        document.getElementById('vaccinationModal').classList.add('modal-open');
      }
    },
    
    /**
     * Elimina una vacunación
     */
    deleteVaccination(index) {
      if (confirm('¿Estás seguro de eliminar este registro de vacunación?')) {
        this.vaccinations.splice(index, 1);
      }
    },
    
    /**
     * Abre el modal para agregar un nuevo pase
     */
    openPassModal() {
      this.currentPass = {
        id: null,
        bloque: '',
        fecha_caducidad: formatDateForInput(new Date())
      };
      this.editingPassIndex = -1;
      document.getElementById('technicalPassModal').classList.add('modal-open');
    },
    
    /**
     * Cierra el modal de pase
     */
    closePassModal() {
      document.getElementById('technicalPassModal').classList.remove('modal-open');
    },
    
    /**
     * Guarda el pase actual desde el modal
     */
    savePass() {
      // Validar campos requeridos
      if (!this.currentPass.bloque || !this.currentPass.fecha_caducidad) {
        this.showAlert = true;
        this.alertMessage = 'Bloque y fecha de caducidad son requeridos';
        this.alertType = 'error';
        return;
      }
      
      // Crear copia para evitar referencias
      const passData = JSON.parse(JSON.stringify(this.currentPass));
      
      // Si estamos editando, actualizar el elemento existente
      if (this.editingPassIndex >= 0) {
        this.passes[this.editingPassIndex] = passData;
      } else {
        // Caso contrario, agregar al array
        this.passes.push(passData);
      }
      
      // Cerrar modal y limpiar estado
      this.closePassModal();
      this.currentPass = {
        id: null,
        bloque: '',
        fecha_caducidad: ''
      };
      this.editingPassIndex = -1;
    },
    
    /**
     * Edita un pase existente
     */
    editPass(index) {
      if (index >= 0 && index < this.passes.length) {
        this.currentPass = JSON.parse(JSON.stringify(this.passes[index]));
        this.editingPassIndex = index;
        document.getElementById('technicalPassModal').classList.add('modal-open');
      }
    },
    
    /**
     * Elimina un pase
     */
    deletePass(index) {
      if (confirm('¿Estás seguro de eliminar este pase?')) {
        this.passes.splice(index, 1);
      }
    },
    
    /**
     * Actualiza los campos ocultos antes del envío del formulario
     */
    updateHiddenFields() {
      // Actualizar campo oculto de vacunas
      const vaccinationsInput = document.getElementById('id_vaccinations_data');
      if (vaccinationsInput) {
        vaccinationsInput.value = JSON.stringify(this.vaccinations);
      }
      
      // Actualizar campo oculto de pases
      const passesInput = document.getElementById('id_passes_data');
      if (passesInput) {
        passesInput.value = JSON.stringify(this.passes);
      }
    },
    
    /**
     * Envía el formulario mediante AJAX
     */
    submitForm() {
      // Evitar envíos múltiples
      if (this.formSubmitting) return;
      
      // Validación básica
      if (!this.isFormValid) {
        this.showAlert = true;
        this.alertMessage = 'Por favor completa todos los campos requeridos';
        this.alertType = 'error';
        return;
      }
      
      this.formSubmitting = true;
      this.showAlert = false;
      this.errors = {};
      
      // Preparar datos para el envío
      const formData = new FormData();
      
      // Añadir datos del técnico principal
      for (const key in this.$data) {
        // No incluir objetos complejos, estados de UI o colecciones
        if (typeof this[key] !== 'object' && 
            key !== 'errors' && 
            key !== 'showAlert' && 
            key !== 'alertMessage' && 
            key !== 'alertType' &&
            key !== 'formSubmitting' &&
            key !== 'editingVaccinationIndex' &&
            key !== 'editingPassIndex' &&
            !Array.isArray(this[key])) {
          
          // Convertir booleanos a valores esperados por Django
          if (typeof this[key] === 'boolean') {
            formData.append(key, this[key] ? 'on' : '');
          } else if (this[key] !== null && this[key] !== undefined) {
            formData.append(key, this[key]);
          }
        }
      }
      
      // Añadir colecciones relacionadas
      formData.append('vaccinations_data', JSON.stringify(this.vaccinations));
      formData.append('passes_data', JSON.stringify(this.passes));
      
      // Añadir token CSRF
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      formData.append('csrfmiddlewaretoken', csrfToken);
      
      // Enviar solicitud
      fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        if (!response.ok) {
          return response.json().then(data => Promise.reject(data));
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Redirección en caso de éxito
          window.location.href = data.redirect_url || data.redirect;
        } else {
          // Mostrar errores
          this.formSubmitting = false;
          this.showAlert = true;
          this.alertMessage = data.message || 'Error al procesar el formulario';
          this.alertType = 'error';
          
          if (data.errors) {
            this.errors = data.errors;
          }
        }
      })
      .catch(error => {
        this.formSubmitting = false;
        this.showAlert = true;
        this.alertMessage = 'Error al enviar el formulario';
        this.alertType = 'error';
        console.error('Error:', error);
      });
    },
    
    /**
     * Calcula la próxima fecha de dosis basada en el tipo de vacuna
     */
    calculateNextDoseDate() {
      const vaccineType = this.currentVaccination.vaccine_type;
      const doseNumber = this.currentVaccination.dose_number || 1;
      const applicationDate = this.currentVaccination.application_date;
      
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
          nextDate.setFullYear(nextDate.getFullYear() + 10);
          break;
        case 'TYPHOID':
          nextDate.setFullYear(nextDate.getFullYear() + 3);
          break;
        case 'YELLOW_FEVER':
          nextDate.setFullYear(nextDate.getFullYear() + 10);
          break;
        case 'INFLUENZA':
          nextDate.setFullYear(nextDate.getFullYear() + 1);
          break;
        case 'COVID':
          if (doseNumber < 3) nextDate.setMonth(nextDate.getMonth() + 3);
          else nextDate.setFullYear(nextDate.getFullYear() + 1);
          break;
        default:
          return;
      }
      
      this.currentVaccination.next_dose_date = formatDateForInput(nextDate);
    }
  },
  
  // Hooks del ciclo de vida
  mounted() {
    // Si hay datos técnicos existentes, inicializar el formulario con ellos
    if (window.existingTechnicalData) {
      this.initFromExistingTechnical(window.existingTechnicalData);
    }
    
    // Configurar watchers para fechas de certificados
    for (const key in EXPIRY_CONFIG) {
      // Observar cambios en la fecha de emisión para actualizar la fecha de vencimiento
      const issueField = EXPIRY_CONFIG[key].issueField;
      this.$watch(issueField, () => {
        this.handleIssueDateChange(key);
      });
      
      // Observar cambios en la fecha de vencimiento para actualizar el badge
      const expiryField = EXPIRY_CONFIG[key].expiryField;
      this.$watch(expiryField, () => {
        this.handleExpiryDateChange(key);
      });
    }
    
    // Observar cambios en la fecha de nacimiento para actualizar la edad
    this.$watch('birth_date', () => {
      this.updateAgeDisplay();
    });
    
    // Inicializar estados visuales
    this.updateAllExpiryBadges();
    this.updateAgeDisplay();
  }
});

// Montar la aplicación Vue en el elemento correspondiente cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  // Montar la aplicación en el elemento con ID 'technical-form-app'
  app.mount('#technical-form-app');
});