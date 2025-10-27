// Configuración de Vue.js con delimitadores personalizados
const { createApp } = Vue;

const ProjectApp = {
  delimiters: ['${', '}'],
  data() {
    return {
      // Variables globales
      csrf_token: '{{ csrf_token }}',
      project_id: {{ project.id }},
      project_start_date: '{{ project.start_date|date:"Y-m-d" }}',
      project_end_date: '{{ project.end_date|date:"Y-m-d" }}',
      
      // Estado de equipos
      availableEquipment: [],
      filteredEquipment: [],
      selectedEquipmentId: null,
      selectedEquipment: null,
      searchEquipmentTerm: '',
      isLoadingEquipment: false,
      showAssignmentForm: false,
      
      // Formulario de asignación de equipos
      assignmentForm: {
        rent_cost: '',
        maintenance_cost: '',
        operation_start_date: '{{ project.start_date|date:"Y-m-d" }}',
        operation_end_date: '{{ project.end_date|date:"Y-m-d" }}',
        maintenance_interval: 15
      },
      
      // Estado de planillas
      sheetForm: {
        series_code: 'Cargando...',
        service_type: 'ALQUILER DE EQUIPOS',
        issue_date: '',
        period_start: '',
        period_end: '',
        contact_reference: '',
        contact_phone_reference: ''
      },
      
      // Estado de guardado
      isSavingAssignment: false,
      isSavingSheet: false
    };
  },
  
  computed: {
    hasEquipment() {
      return this.filteredEquipment.length > 0;
    }
  },
  
  watch: {
    searchEquipmentTerm(newValue) {
      this.filterEquipment();
    }
  },
  
  methods: {
    /**
     * Cargar equipos disponibles desde la API
     */
    async loadAvailableEquipment() {
      this.isLoadingEquipment = true;
      
      try {
        const response = await fetch('/api/projects/resources/available?exclude_services=true');
        const data = await response.json();
        
        if (data.success) {
          this.availableEquipment = data.data;
          this.filteredEquipment = data.data;
        } else {
          this.showError('Error al cargar equipos: ' + data.error);
        }
      } catch (error) {
        this.showError('Error de conexión: ' + error.message);
      } finally {
        this.isLoadingEquipment = false;
      }
    },
    
    /**
     * Filtrar equipos por búsqueda
     */
    filterEquipment() {
      const searchTerm = this.searchEquipmentTerm.toLowerCase();
      
      this.filteredEquipment = this.availableEquipment.filter(eq => {
        return !searchTerm || 
          eq.code.toLowerCase().includes(searchTerm) ||
          eq.name.toLowerCase().includes(searchTerm);
      });
    },
    
    /**
     * Seleccionar equipo
     */
    selectEquipment(equipmentId) {
      this.selectedEquipmentId = equipmentId;
      this.selectedEquipment = this.availableEquipment.find(eq => eq.id === equipmentId);
      
      if (this.selectedEquipment) {
        this.showAssignmentForm = true;
        
        // Hacer scroll al formulario
        this.$nextTick(() => {
          const formElement = this.$refs.assignmentForm;
          if (formElement) {
            formElement.scrollIntoView({ behavior: 'smooth' });
          }
        });
      }
    },
    
    /**
     * Resetear formulario de asignación
     */
    resetAssignmentForm() {
      this.showAssignmentForm = false;
      this.selectedEquipmentId = null;
      this.selectedEquipment = null;
      
      this.assignmentForm = {
        rent_cost: '',
        maintenance_cost: '',
        operation_start_date: this.project_start_date,
        operation_end_date: this.project_end_date,
        maintenance_interval: 15
      };
    },
    
    /**
     * Guardar asignación
     */
    async saveAssignment() {
      if (!this.selectedEquipmentId) {
        this.showError('Debe seleccionar un equipo');
        return;
      }
      
      // Validar campos requeridos
      if (!this.assignmentForm.rent_cost || !this.assignmentForm.maintenance_cost || !this.assignmentForm.operation_start_date) {
        this.showError('Debe completar todos los campos requeridos');
        return;
      }
      
      // Preparar datos
      const assignmentData = {
        project_id: this.project_id,
        resource_item_id: this.selectedEquipmentId,
        rent_cost: parseFloat(this.assignmentForm.rent_cost).toFixed(2),
        maintenance_cost: parseFloat(this.assignmentForm.maintenance_cost).toFixed(2),
        operation_start_date: this.assignmentForm.operation_start_date,
        operation_end_date: this.assignmentForm.operation_end_date || null,
        maintenance_interval_days: parseInt(this.assignmentForm.maintenance_interval)
      };
      
      this.isSavingAssignment = true;
      
      try {
        const response = await fetch('/api/projects/resources/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrf_token
          },
          body: JSON.stringify(assignmentData)
        });
        
        const data = await response.json();
        
        if (data.success) {
          this.showSuccess(data.message || 'Equipo asignado correctamente');
          
          // Cerrar modal y recargar página después de 1.5 segundos
          setTimeout(() => {
            document.getElementById('modal_assign_equipment').close();
            location.reload();
          }, 1500);
        } else {
          this.showError(data.error || 'Error al asignar equipo');
        }
      } catch (error) {
        this.showError('Error de conexión: ' + error.message);
      } finally {
        this.isSavingAssignment = false;
      }
    },
    
    /**
     * Cargar el siguiente código de serie
     */
    async loadNextSeriesCode() {
      try {
        const response = await fetch('/api/workorders/sheets/?next_series=true');
        const data = await response.json();
        
        if (data.success && data.series_code) {
          this.sheetForm.series_code = data.series_code;
        }
      } catch (error) {
        console.error('Error al cargar código de serie:', error);
      }
    },
    
    /**
     * Resetear formulario de planilla
     */
    resetSheetForm() {
      this.sheetForm = {
        series_code: 'Cargando...',
        service_type: 'ALQUILER DE EQUIPOS',
        issue_date: new Date().toISOString().split('T')[0],
        period_start: '',
        period_end: '',
        contact_reference: '',
        contact_phone_reference: ''
      };
      
      document.getElementById('modal_create_sheet').close();
    },
    
    /**
     * Guardar planilla
     */
    async saveSheet() {
      // Validar campo requerido
      if (!this.sheetForm.period_start) {
        this.showError('El período de inicio es requerido');
        return;
      }
      
      // Preparar datos
      const sheetData = {
        project_id: this.project_id,
        series_code: this.sheetForm.series_code,
        service_type: this.sheetForm.service_type,
        issue_date: this.sheetForm.issue_date || null,
        period_start: this.sheetForm.period_start,
        period_end: this.sheetForm.period_end || null,
        contact_reference: this.sheetForm.contact_reference || null,
        contact_phone_reference: this.sheetForm.contact_phone_reference || null,
        status: 'IN_PROGRESS',
        subtotal: 0,
        tax_amount: 0,
        total: 0
      };
      
      this.isSavingSheet = true;
      
      try {
        const response = await fetch('/api/workorders/sheets/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrf_token
          },
          body: JSON.stringify(sheetData)
        });
        
        const data = await response.json();
        
        if (data.success) {
          this.showSuccess(data.message || 'Planilla creada correctamente');
          
          // Cerrar modal y recargar página después de 1.5 segundos
          setTimeout(() => {
            this.resetSheetForm();
            location.reload();
          }, 1500);
        } else {
          this.showError(data.error || 'Error al crear planilla');
        }
      } catch (error) {
        this.showError('Error de conexión: ' + error.message);
      } finally {
        this.isSavingSheet = false;
      }
    },
    
    /**
     * Mostrar mensaje de error
     */
    showError(message) {
      const toast = document.createElement('div');
      toast.className = 'alert alert-error shadow-lg fixed top-4 right-4 w-96 z-50';
      toast.innerHTML = `
        <div>
          <i class="las la-exclamation-circle text-2xl"></i>
          <span>${message}</span>
        </div>
      `;
      
      document.body.appendChild(toast);
      
      setTimeout(() => {
        toast.remove();
      }, 5000);
    },
    
    /**
     * Mostrar mensaje de éxito
     */
    showSuccess(message) {
      const toast = document.createElement('div');
      toast.className = 'alert alert-success shadow-lg fixed top-4 right-4 w-96 z-50';
      toast.innerHTML = `
        <div>
          <i class="las la-check-circle text-2xl"></i>
          <span>${message}</span>
        </div>
      `;
      
      document.body.appendChild(toast);
      
      setTimeout(() => {
        toast.remove();
      }, 5000);
    },
    
    /**
     * Manejar apertura de modal de equipos
     */
    handleEquipmentModalOpen() {
      this.loadAvailableEquipment();
    },
    
    /**
     * Manejar apertura de modal de planilla
     */
    handleSheetModalOpen() {
      this.loadNextSeriesCode();
      this.sheetForm.issue_date = new Date().toISOString().split('T')[0];
    }
  },
  
  mounted() {
    console.log('Presentación del proyecto cargada - ID:', this.project_id);
    
    // Observer para detectar cuando se abre el modal de equipos
    const modalEquipment = document.getElementById('modal_assign_equipment');
    const observerEquipment = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'open' && modalEquipment.hasAttribute('open')) {
          this.handleEquipmentModalOpen();
        }
      });
    });
    
    observerEquipment.observe(modalEquipment, { attributes: true });
    
    // Observer para detectar cuando se abre el modal de planilla
    const modalSheet = document.getElementById('modal_create_sheet');
    const observerSheet = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'open' && modalSheet.hasAttribute('open')) {
          this.handleSheetModalOpen();
        }
      });
    });
    
    observerSheet.observe(modalSheet, { attributes: true });
  }
};

// Inicializar aplicación Vue
document.addEventListener('DOMContentLoaded', function() {
  createApp(ProjectApp).mount('#project-app');
});