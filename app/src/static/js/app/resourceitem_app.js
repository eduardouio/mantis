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
        type: '',
        subtype: '',
        status: ''
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
      
      // Definiciones de subtipo para mostrar campos especiales
      specialSubtypes: [
        'PLANTA DE TRATAMIENTO DE AGUA',
        'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL',
        'TANQUES DE ALMACENAMIENTO AGUA CRUDA',
        'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL'
      ],
      
      // Datos para mostrar instrucciones según el tipo seleccionado
      typeInstructions: {
        'EQUIPO': 'Los equipos requieren información específica según su subtipo.',
        'SERVICIO': 'Los servicios solo requieren información básica.'
      },
      
      // Guarda el modo de edición (crear nuevo o editar existente)
      isEditMode: false
    }
  },
  
  mounted() {
    // Inicializa con los valores actuales del formulario Django
    this.initializeFromForm();
    
    // Verificar si estamos en modo edición o creación
    // Para un formulario de creación nuevo, siempre iniciar en el paso 1
    const isCreateForm = window.location.pathname.includes('/crear/');
    
    // Si estamos editando un registro existente y ya tiene datos, podemos saltar pasos
    if (!isCreateForm && this.formData.type) {
      this.isEditMode = true;
      
      // Si es un equipo y ya tiene subtipo, vamos directo al paso 3
      if (this.formData.type === 'EQUIPO' && this.formData.subtype) {
        this.currentStep = 3;
      }
      // Si es un servicio, saltamos el paso 2
      else if (this.formData.type === 'SERVICIO') {
        this.currentStep = 3;
      }
      // Si es un equipo sin subtipo, vamos al paso 2
      else if (this.formData.type === 'EQUIPO') {
        this.currentStep = 2;
      }
    } else {
      // Para formularios nuevos, siempre comenzar en paso 1
      this.currentStep = 1;
    }
    
    this.updateVisibility();
    
    // Inicializar el contenedor del formulario con las clases de estilo del asistente
    this.updateWizardStyles();
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
      
      // Si selecciona servicio, no necesitamos subtipo
      if (type === 'SERVICIO') {
        this.formData.subtype = '';
      }
      
      // Actualizar el select del formulario Django
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
     * Inicializa el estado de Vue con valores del formulario Django
     */
    initializeFromForm() {
      // Recuperamos los selectores de los campos principales
      const typeSelector = document.querySelector('[name="type"]');
      const subtypeSelector = document.querySelector('[name="subtype"]');
      const statusSelector = document.querySelector('[name="status"]');
      
      if (typeSelector) {
        this.formData.type = typeSelector.value;
        typeSelector.addEventListener('change', (e) => {
          this.formData.type = e.target.value;
          this.updateVisibility();
        });
      }
      
      if (subtypeSelector) {
        this.formData.subtype = subtypeSelector.value;
        subtypeSelector.addEventListener('change', (e) => {
          this.formData.subtype = e.target.value;
          this.updateVisibility();
        });
      }
      
      if (statusSelector) {
        this.formData.status = statusSelector.value;
        statusSelector.addEventListener('change', (e) => {
          this.formData.status = e.target.value;
          this.updateVisibility();
        });
      }
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
        
        // Baterías sanitarias y Camper Baño (comparten los mismos campos)
        this.visibility.sanitarySection = 
          this.formData.subtype === 'BATERIA SANITARIA HOMBRE' || 
          this.formData.subtype === 'BATERIA SANITARIA MUJER' ||
          this.formData.subtype === 'CAMPER BAÑO';
        
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
        const isTank = 
          this.formData.subtype === 'TANQUES DE ALMACENAMIENTO AGUA CRUDA' || 
          this.formData.subtype === 'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL';
        
        // Mostrar/ocultar sección de dimensiones para todos excepto Estación Cuádruple Urinario
        const showDimensions = this.formData.subtype !== 'ESTACION CUADRUPLE URINARIO';
        this.toggleElement('#dimensions_section', showDimensions);
        
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
    }
  }
};

// Inicializa la app de Vue cuando el documento esté listo
document.addEventListener('DOMContentLoaded', () => {
  const appElement = document.querySelector('#resourceItemApp');
  if (appElement) {
    Vue.createApp(window.ResourceItemApp).mount('#resourceItemApp');
    
    // Ocultamos el formulario original hasta que llegue al paso 3 donde se muestra
    const formElement = document.querySelector('#resourceItemApp form');
    if (formElement) {
      // Mantenemos visible solo el título y los botones de navegación superior
      const headerElement = document.querySelector('#resourceItemApp .flex.justify-between');
      if (headerElement) {
        headerElement.style.display = 'flex';
      }
      
      // Ocultamos el resto del formulario inicialmente
      Array.from(formElement.children).forEach(child => {
        if (child !== headerElement) {
          child.dataset.originalDisplay = child.style.display;
          child.style.display = 'none';
        }
      });
    }
  }
});

// Cerramos el if y la IIFE
}
})();
