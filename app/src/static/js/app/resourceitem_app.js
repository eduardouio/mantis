/**
 * ResourceItem Vue App
 * Maneja un asistente paso a paso para la creación/edición de equipos y servicios
 * Con formularios dinámicos según el tipo y subtipo seleccionado
 */

// Usar un IIFE para evitar contaminar el scope global y prevenir errores de redeclaración
(function() {
// Solo declarar si no existe ya
if (typeof window.ResourceItemApp === 'undefined') {
window.ResourceItemApp = {
  // NO incluir delimiters aquí, se configurará al crear la app
  data() {
    return {
      // Estado del asistente
      currentStep: 1,
      totalSteps: 3,
      stepTitles: [
        'Seleccionar Tipo de Registro',
        'Seleccionar Subtipo',
        'Completar Información'
      ],
      
      // Estado de UI
      isLoading: false,
      isSaving: false,
      errors: {},
      successMessage: '',
      isEditMode: false,
      testMessage: 'Vue is working!',
      
      // Tabs de navegación para el paso 3
      activeTab: 'general',
      tabs: [
        { id: 'general', name: 'Información General' },
        { id: 'dimensions', name: 'Dimensiones' },
        { id: 'characteristics', name: 'Características Específicas' },
        { id: 'technical', name: 'Datos Técnicos' },
        { id: 'notes', name: 'Notas' }
      ],
      
      // Campos y configuración
      formData: {
        // Campos básicos
        id: '',
        type: '',
        subtype: '',
        name: '',
        code: '',
        serial_number: '',
        brand: '',
        model: '',
        date_purchase: '',
        status: '',
        base_price: '',
        is_active: true, // Campo del modelo base, por defecto activo
        notes: '',
        
        // Dimensiones
        height: '',
        width: '',
        depth: '',
        weight: '',
        
        // Capacidad
        capacity_gallons: '',
        plant_capacity: '',
        
        // Motivo de reparación
        repair_reason: '',
        
        // Campos booleanos específicos para lavamanos
        foot_pumps: false,
        sink_soap_dispenser: false,
        paper_towels: false,
        
        // Campos booleanos para baterías sanitarias
        paper_dispenser: false,
        soap_dispenser: false,
        napkin_dispenser: false,
        urinals: false,
        seats: false,
        toilet_pump: false,
        sink_pump: false,
        toilet_lid: false,
        bathroom_bases: false,
        ventilation_pipe: false,
        
        // Campos específicos para plantas de tratamiento
        blower_brand: '',
        blower_model: '',
        engine_brand: '',
        engine_model: '',
        belt_brand: '',
        belt_model: '',
        belt_type: '',
        blower_pulley_brand: '',
        blower_pulley_model: '',
        motor_pulley_brand: '',
        motor_pulley_model: '',
        electrical_panel_brand: '',
        electrical_panel_model: '',
        motor_guard_brand: '',
        motor_guard_model: ''
      },
      
      // Visibilidad de secciones según tipo y subtipo
      visibility: {
        equipmentFields: false,
        repairReasonField: false,
        plantCapacityField: false,
        lavandinosSection: false,
        sanitarySection: false,
        urinalsField: false,
        specialFieldsSection: false
      },
      
      // Definiciones de subtipo
      equipmentSubtypes: [
        { value: 'LAVAMANOS', label: 'Lavamanos' },
        { value: 'BATERIA SANITARIA HOMBRE', label: 'Batería Sanitaria Hombre' },
        { value: 'BATERIA SANITARIA MUJER', label: 'Batería Sanitaria Mujer' },
        { value: 'PLANTA DE TRATAMIENTO DE AGUA', label: 'Planta de Tratamiento de Agua' },
        { value: 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL', label: 'Planta de Tratamiento de Agua Residual' },
        { value: 'TANQUES DE ALMACENAMIENTO AGUA CRUDA', label: 'Tanques de Almacenamiento Agua Cruda' },
        { value: 'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL', label: 'Tanques de Almacenamiento Agua Residual' },
        { value: 'CAMPER BAÑO', label: 'Camper Baño' },
        { value: 'ESTACION CUADRUPLE URINARIO', label: 'Estación Cuádruple Urinario' }
      ],
      
      // Definiciones de subtipo para mostrar campos especiales (solo plantas)
      specialSubtypes: [
        'PLANTA DE TRATAMIENTO DE AGUA',
        'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL'
      ],
      
      // Definiciones de subtipos de tanques para mostrar capacidad en galones
      tankSubtypes: [
        'TANQUES DE ALMACENAMIENTO AGUA CRUDA',
        'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL'
      ],
      
      // Datos para mostrar instrucciones según el tipo seleccionado
      typeInstructions: {
        'EQUIPO': 'Los equipos requieren información específica según su subtipo.',
        'SERVICIO': 'Los servicios solo requieren información básica.'
      }
    }
  },
  
  mounted() {
    console.log("Vue app mounted");
    this.initialize();
  },
  
  computed: {
    showWizard() {
      return this.currentStep < 3 && !this.isEditMode;
    }
  },
  
  methods: {
    /**
     * Avanza al siguiente paso del asistente
     */
    nextStep() {
      // Validar antes de avanzar
      if (!this.validateCurrentStep()) {
        return false;
      }
      
      // Si estamos en paso 1 y se seleccionó Servicio, saltamos al paso 3
      if (this.currentStep === 1 && this.formData.type === 'SERVICIO') {
        this.currentStep = 3;
      } else if (this.currentStep < this.totalSteps) {
        this.currentStep++;
      }
      
      this.updateWizardStyles();
      return true;
    },
    
    /**
     * Retrocede al paso anterior del asistente
     */
    prevStep() {
      // Si estamos en paso 3 y el tipo es SERVICIO, volvemos al paso 1
      if (this.currentStep === 3 && this.formData.type === 'SERVICIO') {
        this.currentStep = 1;
      } else if (this.currentStep > 1) {
        this.currentStep--;
      }
      
      this.updateWizardStyles();
    },
    
    /**
     * Valida los datos del paso actual
     */
    validateCurrentStep() {
      switch(this.currentStep) {
        case 1:
          return this.formData.type !== '';
        case 2:
          return this.formData.type !== 'EQUIPO' || this.formData.subtype !== '';
        default:
          return true;
      }
    },
    
    /**
     * Actualiza los estilos del asistente según el paso actual
     */
    updateWizardStyles() {
      // Gestionar la visibilidad del formulario original según el paso
      const formElement = document.querySelector('#resourceItemApp form');
      if (formElement) {
        // En el paso 3, mostramos el formulario completo
        if (this.currentStep === 3) {
          // Mostrar todos los elementos del formulario excepto el encabezado (que siempre está visible)
          Array.from(formElement.children).forEach(child => {
            // Excluimos el encabezado y los elementos de navegación superior
            const isHeaderElement = child.classList && child.classList.contains('flex') && 
                                    child.classList.contains('justify-between');
            if (!isHeaderElement) {
              child.style.display = child.dataset.originalDisplay || '';
            }
          });
        } else {
          // En los pasos 1 y 2, ocultamos el formulario excepto el encabezado
          Array.from(formElement.children).forEach(child => {
            const isHeaderElement = child.classList && child.classList.contains('flex') && 
                                    child.classList.contains('justify-between');
            if (!isHeaderElement) {
              // Guardamos el display original si no lo hemos hecho ya
              if (!child.dataset.originalDisplay) {
                child.dataset.originalDisplay = child.style.display || '';
              }
              child.style.display = 'none';
            }
          });
        }
      }
    },
    
    /**
     * Selecciona un tipo de registro (Equipo/Servicio) y avanza al siguiente paso
     */
    selectType(type) {
      this.formData.type = type;
      
      // Si selecciona servicio, no necesitamos subtipo y establecemos el estado como DISPONIBLE por defecto
      if (type === 'SERVICIO') {
        this.formData.subtype = '';
        this.formData.status = 'DISPONIBLE';
      }
      
      const typeSelector = document.querySelector('[name="type"]');
      if (typeSelector) {
        typeSelector.value = type;
        // Disparar evento change para activar validaciones de Django
        typeSelector.dispatchEvent(new Event('change'));
      }
      
      this.nextStep();
      this.updateVisibility();
    },
    
    /**
     * Selecciona un subtipo de equipo y avanza al siguiente paso
     */
    selectSubtype(subtype) {
      this.formData.subtype = subtype;
      
      // Actualizar el select del formulario Django
      const subtypeSelector = document.querySelector('[name="subtype"]');
      if (subtypeSelector) {
        subtypeSelector.value = subtype;
        // Disparar evento change para activar validaciones de Django
        subtypeSelector.dispatchEvent(new Event('change'));
      }
      
      this.nextStep();
      this.updateVisibility();
    },
    
    /**
     * Inicializa la aplicación Vue, cargando datos si es modo edición.
     */
    initialize() {
      const isUpdateEl = document.getElementById('is_update');
      const isUpdateMode = isUpdateEl && isUpdateEl.value === 'true';

      if (isUpdateMode && window.equipmentData) {
        console.log("Modo edición detectado. Cargando datos iniciales...");
        // Usar Object.assign para fusionar los datos sin perder reactividad
        Object.assign(this.formData, window.equipmentData);
        this.isEditMode = true;
        this.currentStep = 3;
        console.log("Datos cargados en formData:", this.formData);
      } else {
        console.log("Modo creación. Iniciando en el paso 1.");
        this.currentStep = 1;
      }
      
      this.updateVisibility();
      this.updateWizardStyles();
    },
    
    /**
     * Actualiza la visibilidad de campos según el tipo y subtipo seleccionado
     */
    updateVisibility() {
      // Visibilidad basada en tipo de equipo
      this.visibility.equipmentFields = this.formData.type === 'EQUIPO';
      
      // Visibilidad basada en estado
      this.visibility.repairReasonField = this.formData.status === 'EN REPARACION';
      
      // Visibilidad basada en subtipo
      if (this.formData.type === 'EQUIPO' && this.formData.subtype) {
        // Lavamanos
        this.visibility.lavandinosSection = this.formData.subtype === 'LAVAMANOS';
        
        // Baterías sanitarias, Camper Baño y Estación Cuádruple Urinario (comparten los mismos campos)
        this.visibility.sanitarySection = 
          this.formData.subtype === 'BATERIA SANITARIA HOMBRE' || 
          this.formData.subtype === 'BATERIA SANITARIA MUJER' ||
          this.formData.subtype === 'CAMPER BAÑO' ||
          this.formData.subtype === 'ESTACION CUADRUPLE URINARIO';
        
        // Urinales (solo para baterías sanitarias de hombre y camper baño)
        this.visibility.urinalsField = 
          this.formData.subtype === 'BATERIA SANITARIA HOMBRE' || 
          this.formData.subtype === 'CAMPER BAÑO';
        
        // Si es batería sanitaria de mujer, desmarcamos los urinales
        if (this.formData.subtype === 'BATERIA SANITARIA MUJER') {
          const urinalsCheckbox = document.querySelector('[name="urinals"]');
          if (urinalsCheckbox) urinalsCheckbox.checked = false;
        }
        
        // Capacidad de planta (plantas de tratamiento)
        this.visibility.plantCapacityField = 
          this.formData.subtype === 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL';
        
        // Campos especiales para plantas y tanques
        this.visibility.specialFieldsSection = this.specialSubtypes.includes(this.formData.subtype);
        
        // Campo de capacidad en galones (tanques)
        const isTank = this.tankSubtypes.includes(this.formData.subtype);
        
        // Mostrar sección de dimensiones para todos los tipos
        this.toggleElement('#dimensions_section', true);
        
        // Mostrar/ocultar campos específicos según subtipo
        if (isTank) {
          this.toggleElement('#capacity_gallons_field', true);
        } else {
          this.toggleElement('#capacity_gallons_field', false);
        }
        
      } else {
        // Ocultar todas las secciones especiales si no es equipo o no tiene subtipo
        this.visibility.lavandinosSection = false;
        this.visibility.sanitarySection = false;
        this.visibility.urinalsField = false;
        this.visibility.plantCapacityField = false;
        this.visibility.specialFieldsSection = false;
      }
      
      // Si no es equipo, ocultar todas las secciones relacionadas con equipos
      if (this.formData.type !== 'EQUIPO') {
        this.toggleElement('#dimensions_section, #caracteristicas_section', false);
      }
      
      // Aplicamos los cambios de visibilidad al DOM después de que Vue actualice
      this.$nextTick(() => {
        this.updateDOMVisibility();
      });
    },
    
    /**
     * Actualiza la visibilidad de elementos DOM según el estado de Vue
     */
    updateDOMVisibility() {
      // Mostrar/ocultar el formulario de Django según el paso actual
      const djangoForm = document.querySelector('form.form-django');
      if (djangoForm) {
        djangoForm.style.display = this.currentStep === 3 ? 'block' : 'none';
      }
      
      // Campos generales de equipo
      this.toggleElement('#brand_div, #model_div, #date_purchase_div, #dimensions_section, #subtipo_div, #capacidad_div', 
                         this.visibility.equipmentFields);
      
      // Campo de motivo de reparación
      this.toggleElement('#motivo_reparacion_div', this.visibility.repairReasonField);
      const repairReasonField = document.querySelector('[name="repair_reason"]');
      if (repairReasonField) {
        repairReasonField.required = this.visibility.repairReasonField;
      }
      
      // Sección de características específicas
      this.toggleElement('#caracteristicas_section', 
        this.visibility.lavandinosSection || 
        this.visibility.sanitarySection || 
        this.visibility.specialFieldsSection);
      
      // Características de lavamanos
      this.toggleElement('#lavamanos_caracteristicas', this.visibility.lavandinosSection);
      
      // Características de baterías sanitarias
      this.toggleElement('#bateria_caracteristicas', this.visibility.sanitarySection);
      
      // Campo de urinales
      this.toggleElement('#urinales_field', this.visibility.urinalsField);
      
      // Campo de capacidad de planta
      this.toggleElement('#capacidad_planta_div', this.visibility.plantCapacityField);
      
      // Características especiales de plantas de tratamiento
      this.toggleElement('#planta_tratamiento_caracteristicas', this.visibility.specialFieldsSection);
      
      // Campos especiales para plantas y tanques
      this.toggleElement('.special-fields-section', this.visibility.specialFieldsSection);
    },
    
    /**
     * Utility para mostrar/ocultar elementos con animación
     */
    toggleElement(selector, show) {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        if (show) {
          $(el).fadeIn('slow');
        } else {
          $(el).fadeOut('slow');
        }
      });
    },
    
    /**
     * Cambia la pestaña activa
     */
    setActiveTab(tabId) {
      this.activeTab = tabId;
    },
    
    /**
     * Cancela el formulario y regresa a la lista de equipos/servicios
     */
    cancelForm() {
      // Redirigir a la lista de equipos/servicios
      window.location.href = '/equipos/'; // Ajustar según la URL real
    },
    
    /**
     * Guarda los datos del servicio usando AJAX
     */
    saveService() {
      this.isLoading = true;
      this.errors = {};

      if (!this.validateServiceForm()) {
        this.isLoading = false;
        return;
      }

      // Preparar datos para envío AJAX
      const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
      const csrfToken = csrfTokenElement ? csrfTokenElement.value : '';
      
      // Usar la URL actual para el envío del formulario
      const url = window.location.pathname;
      const method = 'POST'; // Usar siempre POST

      fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(this.formData)
      })
      .then(response => response.json().then(data => ({ response, data })))
      .then(({ response, data }) => {
        if (!response.ok) {
          if (response.status === 400) {
            this.showErrors(data);
          } else {
            throw new Error(data.detail || 'Error al guardar el servicio');
          }
        } else {
          this.successMessage = '¡Servicio guardado exitosamente!';
          
          // Update form data with response (in case of new IDs, etc)
          this.formData = { ...this.formData, ...data };
          
          // Verificar si hay una URL de redirección en la respuesta
          if (data.redirect) {
            // Mostrar mensaje de éxito brevemente antes de redireccionar
            setTimeout(() => {
              window.location.href = data.redirect;
            }, 1000); // Redireccionar después de 1 segundo
          } else {
            // Si no hay redirección, actualizar la URL si es un nuevo elemento
            if (!this.formData.id && data.id) {
              window.history.pushState({}, '', `/service/edit/${data.id}/`);
            }
            
            // Scroll to top to show success message
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }
        }
      })
      .catch(error => {
        console.error('Error saving service:', error);
        this.errors = { general: error.message };
        this.scrollToError();
      })
      .finally(() => {
        this.isLoading = false;
      });
    },
    
    /**
     * Guarda los datos del equipo usando AJAX
     */
    saveEquipment() {
      // Validar el formulario según el tipo antes de continuar
      let isValid = false;
      this.errors = {};
      
      if (this.formData.type === 'SERVICIO') {
        isValid = this.validateServiceForm();
      } else if (this.formData.type === 'EQUIPO') {
        isValid = this.validateEquipmentForm();
      } else {
        this.errors = { general: 'Debe seleccionar un tipo de registro (Equipo o Servicio)' };
      }
      
      // Si no es válido, mostrar errores y salir
      if (!isValid) {
        this.scrollToError();
        return false; // Evita el envío del formulario
      }
      
      this.isSaving = true;
      
      // Preparar datos para envío AJAX
      const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
      const csrfToken = csrfTokenElement ? csrfTokenElement.value : '';
      
      // Usar la URL actual para el envío del formulario
      const url = window.location.pathname;
      const method = 'POST'; // Usar siempre POST
      
      fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(this.formData)
      })
      .then(response => response.json().then(data => ({ response, data })))
      .then(({ response, data }) => {
        if (!response.ok) {
          if (response.status === 400) {
            this.showErrors(data);
          } else {
            throw new Error(data.detail || 'Error al guardar el equipo');
          }
        } else {
          this.successMessage = '¡Equipo guardado exitosamente!';
          
          // Actualizar datos del formulario con la respuesta (en caso de nuevos IDs, etc)
          this.formData = { ...this.formData, ...data };
          
          // Verificar si hay una URL de redirección en la respuesta
          if (data.redirect) {
            // Mostrar mensaje de éxito brevemente antes de redireccionar
            setTimeout(() => {
              window.location.href = data.redirect;
            }, 1000); // Redireccionar después de 1 segundo
          } else {
            // Si no hay redirección, actualizar la URL si es un nuevo elemento
            if (!this.formData.id && data.id) {
              window.history.pushState({}, '', `/equipos/editar/${data.id}/`);
            }
            
            // Scroll to top to show success message
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }
        }
      })
      .catch(error => {
        console.error('Error guardando equipo:', error);
        this.errors = { general: error.message };
        this.scrollToError();
      })
      .finally(() => {
        this.isSaving = false;
      });
      
      return false; // Prevenir el envío del formulario HTML tradicional
    },
    
    /**
     * Sincroniza los datos del formData de Vue con los campos reales del formulario HTML
     * para que Django los procese correctamente
     */
    syncFormDataToHtmlForm() {
      // Obtener todos los campos de entrada del formulario
      const form = document.querySelector('form');
      if (!form) return;
      
      // Recorrer todas las propiedades en formData y buscar campos correspondientes
      for (const [key, value] of Object.entries(this.formData)) {
        // Buscar el campo por ID o por nombre
        let field = form.querySelector(`#id_${key}`) || form.querySelector(`[name="${key}"]`);
        
        // Si no se encuentra, intentar crear un campo oculto
        if (!field && value !== undefined && value !== null) {
          field = document.createElement('input');
          field.type = 'hidden';
          field.name = key;
          form.appendChild(field);
        }
        
        // Asignar el valor al campo si existe
        if (field) {
          // Para checkboxes necesitamos un tratamiento especial
          if (field.type === 'checkbox') {
            field.checked = Boolean(value);
          } else {
            field.value = value !== null && value !== undefined ? value : '';
          }
        }
      }
    },
    
    /**
     * Helper para desplazarse al primer error en el formulario
     */
    scrollToError() {
      this.$nextTick(() => {
        const firstError = document.querySelector('.text-error');
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    },
    
    /**
     * Valida el formulario de servicio
     * @returns {boolean} - True si el formulario es válido
     */
    validateServiceForm() {
      let valid = true;
      this.errors = {};
      
      // Validar nombre (requerido)
      if (!this.formData.name || this.formData.name.trim() === '') {
        this.errors.name = 'El nombre del servicio es requerido';
        valid = false;
      }
      
      // El código ya no es obligatorio (opcional en el modelo)
      // pero si se proporciona, debe tener un formato válido
      if (this.formData.code && this.formData.code.trim() === '') {
        // Si se proporciona un valor pero está vacío, establecerlo como null
        this.formData.code = null;
      }
      
      // Validar precio base (debe ser un número positivo si se proporciona)
      if (this.formData.base_price && (isNaN(this.formData.base_price) || parseFloat(this.formData.base_price) < 0)) {
        this.errors.base_price = 'El precio base debe ser un valor numérico positivo';
        valid = false;
      }
      // Otras validaciones específicas pueden agregarse aquí
      
      return valid;
    },
    
    /**
     * Valida el formulario de equipo según su tipo/subtipo
     * @returns {boolean} - True si el formulario es válido
     */
    validateEquipmentForm() {
      let valid = true;
      this.errors = {};
      
      // Validaciones comunes para todos los equipos
      
      // Nombre (requerido)
      if (!this.formData.name || this.formData.name.trim() === '') {
        this.errors.name = 'El nombre del equipo es requerido';
        valid = false;
      }
      
      // Código del equipo (requerido y único)
      if (!this.formData.code || this.formData.code.trim() === '') {
        this.errors.code = 'El código del equipo es requerido';
        valid = false;
      }
      
      // Marca (requerido)
      if (!this.formData.brand || this.formData.brand.trim() === '') {
        this.errors.brand = 'La marca del equipo es requerida';
        valid = false;
      }
      
      // Subtipo (requerido para equipos)
      if (!this.formData.subtype || this.formData.subtype.trim() === '') {
        this.errors.subtype = 'Debe seleccionar un tipo de equipo';
        valid = false;
      }
      
      // Estado (requerido)
      if (!this.formData.status || this.formData.status.trim() === '') {
        this.errors.status = 'Debe seleccionar un estado para el equipo';
        valid = false;
      }
      
      // Precio base (debe ser un número positivo si se proporciona)
      if (this.formData.base_price && (isNaN(this.formData.base_price) || parseFloat(this.formData.base_price) < 0)) {
        this.errors.base_price = 'El precio base debe ser un valor numérico positivo';
        valid = false;
      }
      
      // Validar dimensiones (deben ser números positivos si se proporcionan)
      const dimensionFields = ['height', 'width', 'depth', 'weight'];
      dimensionFields.forEach(field => {
        if (this.formData[field] && (isNaN(this.formData[field]) || parseInt(this.formData[field]) < 0)) {
          this.errors[field] = `El valor de ${this.getFieldLabel(field)} debe ser un número positivo`;
          valid = false;
        }
      });
      
      // Validaciones específicas según el subtipo
      if (this.formData.subtype) {
        // PLANTAS DE TRATAMIENTO
        if (this.specialSubtypes.includes(this.formData.subtype)) {
          // PLANTA DE TRATAMIENTO DE AGUA RESIDUAL - capacidad obligatoria
          if (this.formData.subtype === 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL' && !this.formData.plant_capacity) {
            this.errors.plant_capacity = 'Debe especificar la capacidad de la planta';
            valid = false;
          }
          
          // Solo verificamos campos específicos para plantas de tratamiento de agua residual
          if (this.formData.subtype === 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL') {
            // Estos campos son opcionales - no mostraremos advertencias
            // Ya que confunde al usuario y no son realmente requeridos
            // Dejamos los comentarios como referencia pero eliminamos las validaciones
            /*
            const plantFields = [
              { field: 'blower_brand', label: 'Marca del Blower' },
              { field: 'engine_brand', label: 'Marca del Motor' },
              { field: 'belt_brand', label: 'Marca de la Banda' }
            ];
            
            for (const { field, label } of plantFields) {
              if (!this.formData[field] || this.formData[field].trim() === '') {
                // No son obligatorios pero mostramos una advertencia
                this.errors[field] = `Se recomienda especificar ${label} para este tipo de equipo`;
                // No establecemos valid = false porque no son obligatorios
              }
            }
            */
          }
        }
        
        // TANQUES
        if (this.tankSubtypes.includes(this.formData.subtype)) {
          if (!this.formData.capacity_gallons || parseFloat(this.formData.capacity_gallons) <= 0) {
            this.errors.capacity_gallons = 'Debe especificar una capacidad válida en galones para el tanque';
            valid = false;
          }
        }
        
        // LAVAMANOS
        if (this.formData.subtype === 'LAVAMANOS') {
          // Para lavamanos todos los campos booleanos son opcionales
          // Si no están definidos, se establecerán como false en el backend
          // No se requiere validación adicional
          
          // Aseguramos que los campos estén definidos con valores booleanos
          if (this.formData.foot_pumps === undefined) {
            this.formData.foot_pumps = false;
          }
          
          if (this.formData.sink_soap_dispenser === undefined) {
            this.formData.sink_soap_dispenser = false;
          }
          
          if (this.formData.paper_towels === undefined) {
            this.formData.paper_towels = false;
          }
        }
        
        // BATERIAS SANITARIAS y similares
        const bathroomTypes = ['BATERIA SANITARIA HOMBRE', 'BATERIA SANITARIA MUJER', 'CAMPER BAÑO', 'ESTACION CUADRUPLE URINARIO'];
        if (bathroomTypes.includes(this.formData.subtype)) {
          // Para baterías sanitarias, se recomienda especificar características específicas
          const bathroomFields = [
            'paper_dispenser', 'soap_dispenser', 'napkin_dispenser', 
            'seats', 'toilet_pump', 'toilet_lid', 'bathroom_bases', 'ventilation_pipe'
          ];
          
          // Verificar que al menos una característica esté especificada
          const hasAnyFeature = bathroomFields.some(field => this.formData[field] === true);
          if (!hasAnyFeature) {
            this.errors.general = 'Se recomienda especificar al menos una característica para este tipo de baño';
            // No es obligatorio, no afecta la validación
          }
          
          // Urinales solo aplican a baterías de hombre y estación cuádruple urinario
          if (this.formData.subtype === 'BATERIA SANITARIA MUJER' && this.formData.urinals === true) {
            this.errors.urinals = 'Los urinales no aplican para baterías sanitarias de mujer';
            valid = false;
          }
        }
        
        // Estado EN REPARACION
        if (this.formData.status === 'EN REPARACION' && (!this.formData.repair_reason || this.formData.repair_reason.trim() === '')) {
          this.errors.repair_reason = 'Debe especificar el motivo de reparación cuando el estado es "EN REPARACION"';
          valid = false;
        }
      }
      
      return valid;
    },
    
    /**
     * Obtiene la etiqueta legible de un campo para mostrar en mensajes de error
     * @param {string} field - Nombre del campo
     * @returns {string} - Etiqueta legible
     */
    getFieldLabel(field) {
      const labels = {
        'height': 'altura',
        'width': 'ancho',
        'depth': 'profundidad',
        'weight': 'peso',
        'capacity_gallons': 'capacidad en galones',
        'plant_capacity': 'capacidad de planta'
      };
      
      return labels[field] || field;
    },
    
    /**
     * Obtiene la etiqueta legible de un subtipo de equipo
     * @param {string} subtype - Valor del subtipo
     * @returns {string} - Etiqueta legible
     */
    getSubtypeLabel(subtype) {
      const subtypeObj = this.equipmentSubtypes.find(s => s.value === subtype);
      return subtypeObj ? subtypeObj.label : subtype;
    },
    
    /**
     * Muestra errores en el formulario
     */
    showErrors(errors) {
      this.errors = errors || {};
      
      // Agregar un mensaje general de error en la parte superior del formulario
      if (Object.keys(this.errors).length > 0) {
        // Mostrar mensaje de error general
        this.successMessage = ''; // Limpiar cualquier mensaje de éxito previo
        
        // Convertir errores del servidor a mensajes más amigables
        if (this.errors.code && this.errors.code.includes('Ya existe Recurso/Equipo con este Equipment Code')) {
          this.errors.code = 'El código ingresado ya existe. Por favor, utilice otro código.';
        }
        
        // Hacer scroll al primer error
        const firstErrorField = document.querySelector(`[data-field="${Object.keys(this.errors)[0]}"]`);
        if (firstErrorField) {
          firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
          // Si no se encuentra el campo, hacer scroll al principio del formulario
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      }
    },
    
    /**
     * Establece los datos de un equipo existente para edición
     * Usado cuando se carga la página en modo edición
     */
    setEquipmentData(equipmentData) {
      if (!equipmentData) return;
      
      console.log("Cargando datos de equipo para edición:", equipmentData);
      
      // Marcar como modo edición
      this.isEditMode = true;
      this.currentStep = 3; // Ir directamente al paso final (formulario completo)
      
      // Establecer datos básicos del equipo
      this.formData.id = equipmentData.id;
      this.formData.type = equipmentData.type;
      this.formData.subtype = equipmentData.subtype || '';
      this.formData.name = equipmentData.name || '';
      this.formData.code = equipmentData.code || '';
      this.formData.serial_number = equipmentData.serial_number || '';
      this.formData.brand = equipmentData.brand || '';
      this.formData.model = equipmentData.model || '';
      this.formData.date_purchase = equipmentData.date_purchase || '';
      this.formData.status = equipmentData.status || '';
      this.formData.base_price = equipmentData.base_price || '';
      
      // Datos de dimensiones
      this.formData.height = equipmentData.height || '';
      this.formData.width = equipmentData.width || '';
      this.formData.depth = equipmentData.depth || '';
      this.formData.weight = equipmentData.weight || '';
      
      // Datos de capacidad
      this.formData.capacity_gallons = equipmentData.capacity_gallons || '';
      this.formData.plant_capacity = equipmentData.plant_capacity || '';
      
      // Motivo de reparación
      this.formData.repair_reason = equipmentData.repair_reason || '';
      
      // Campos booleanos específicos - todos por defecto false
      this.formData.foot_pumps = equipmentData.foot_pumps || false;
      this.formData.sink_soap_dispenser = equipmentData.sink_soap_dispenser || false;
      this.formData.paper_towels = equipmentData.paper_towels || false;
      this.formData.paper_dispenser = equipmentData.paper_dispenser || false;
      this.formData.soap_dispenser = equipmentData.soap_dispenser || false;
      this.formData.napkin_dispenser = equipmentData.napkin_dispenser || false;
      this.formData.urinals = equipmentData.urinals || false;
      this.formData.seats = equipmentData.seats || false;
      this.formData.toilet_pump = equipmentData.toilet_pump || false;
      this.formData.sink_pump = equipmentData.sink_pump || false;
      this.formData.toilet_lid = equipmentData.toilet_lid || false;
      this.formData.bathroom_bases = equipmentData.bathroom_bases || false;
      this.formData.ventilation_pipe = equipmentData.ventilation_pipe || false;
      
      // Campos específicos para plantas de tratamiento
      this.formData.blower_brand = equipmentData.blower_brand || '';
      this.formData.blower_model = equipmentData.blower_model || '';
      this.formData.engine_brand = equipmentData.engine_brand || '';
      this.formData.engine_model = equipmentData.engine_model || '';
      this.formData.belt_brand = equipmentData.belt_brand || '';
      this.formData.belt_model = equipmentData.belt_model || '';
      this.formData.belt_type = equipmentData.belt_type || '';
      this.formData.blower_pulley_brand = equipmentData.blower_pulley_brand || '';
      this.formData.blower_pulley_model = equipmentData.blower_pulley_model || '';
      this.formData.motor_pulley_brand = equipmentData.motor_pulley_brand || '';
      this.formData.motor_pulley_model = equipmentData.motor_pulley_model || '';
      this.formData.electrical_panel_brand = equipmentData.electrical_panel_brand || '';
      this.formData.electrical_panel_model = equipmentData.electrical_panel_model || '';
      this.formData.motor_guard_brand = equipmentData.motor_guard_brand || '';
      this.formData.motor_guard_model = equipmentData.motor_guard_model || '';
      
      // Actualizar los campos del formulario HTML con los datos
      this.syncFormDataToHtmlForm();
      
      // Actualizar visibilidad de campos según el tipo/subtipo
      this.updateVisibility();
      
      // Forzar la actualización del DOM después de que Vue procese los cambios
      this.$nextTick(() => {
        this.updateVisibility();
      });
      
      console.log("Datos de equipo cargados para edición:", this.formData);
    }
  }
};

// Filtro para capitalizar campos
window.ResourceItemApp.filters = {
  capitalize: function(value) {
    if (!value) return '';
    value = value.toString();
    return value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, ' ');
  }
};

// Inicializa la app de Vue cuando el documento esté listo
// Variable para evitar múltiples inicializaciones
let vueAppInitialized = false;

function initializeVueApp() {
  console.log("Initializing Vue app");
  
  // Verificar si Vue ya está inicializado
  if (vueAppInitialized) {
    console.log("Vue app already initialized, skipping...");
    return;
  }
  
  const appElement = document.querySelector('#resourceItemApp');
  console.log("App element found:", appElement);
  
  if (appElement) {
    try {
      console.log("Creating Vue app");
      
      // Crear la aplicación Vue con delimitadores personalizados para evitar conflictos con Django
      const app = Vue.createApp({
        ...window.ResourceItemApp,
        delimiters: ['${', '}']
      });
      
      console.log("Mounting Vue app");
      const vueInstance = app.mount('#resourceItemApp');
      console.log("Vue app mounted successfully", vueInstance);
      
      // Marcar como inicializado
      vueAppInitialized = true;
      
      // Hacer el método setEquipmentData accesible globalmente
      window.ResourceItemApp.setEquipmentData = function(equipmentData) {
        if (vueInstance && vueInstance.setEquipmentData) {
          vueInstance.setEquipmentData(equipmentData);
        }
      };
      
    } catch (error) {
      console.error("Error mounting Vue app:", error);
      // Mostrar un mensaje de error al usuario
      appElement.innerHTML = `
        <div class="alert alert-error">
          <div>
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 class="font-bold">Error de aplicación</h3>
              <div class="text-xs">No se pudo inicializar la aplicación Vue. Por favor, recarga la página.</div>
            </div>
          </div>
        </div>
      `;
    }
  }
}

// Intentar múltiples eventos para asegurar la inicialización
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeVueApp);
} else {
  // DOM ya está cargado
  initializeVueApp();
}

// También escuchar el evento load como respaldo
window.addEventListener('load', function() {
  console.log("Window load event fired");
  if (!vueAppInitialized) {
    console.log("Vue not initialized, trying again");
    initializeVueApp();
  }
});

// Cerramos el if y la IIFE
}
})();
