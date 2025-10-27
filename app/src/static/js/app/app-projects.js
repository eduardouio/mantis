// Configuración de Vue.js con delimitadores personalizados
const { createApp } = Vue;

const ProjectApp = {
  delimiters: ['${', '}'],
  data() {
    // Obtener datos del proyecto desde window.PROJECT_DATA
    const projectData = window.PROJECT_DATA || {};
    
    return {
      csrf_token: projectData.csrf_token || '',
      project_id: projectData.project_id || 0,
      project_start_date: projectData.project_start_date || '',
      project_end_date: projectData.project_end_date || '',
      
      // Estado de equipos
      availableEquipment: [],
      selectedEquipmentId: null,
      selectedEquipment: null,
      isLoadingEquipment: false,
      showAssignmentForm: false,
      equipmentDataTable: null,
      
      // Formulario de asignación de equipos
      assignmentForm: {
        rent_cost: '',
        maintenance_cost: '',
        operation_start_date: projectData.project_start_date || '',
        operation_end_date: projectData.project_end_date || '',
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
      return this.availableEquipment.length > 0;
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
          this.isLoadingEquipment = false;
          this.refreshEquipmentDataTable();
        } else {
          this.showError('Error al cargar equipos: ' + data.error);
          this.availableEquipment = [];
          this.isLoadingEquipment = false;
          this.destroyEquipmentDataTable();
        }
      } catch (error) {
        this.showError('Error de conexión: ' + error.message);
        this.availableEquipment = [];
        this.isLoadingEquipment = false;
        this.destroyEquipmentDataTable();
      }
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
     * Inicializar o reiniciar DataTable del listado de equipos
     */
    refreshEquipmentDataTable() {
      this.$nextTick(() => {
        if (!window.jQuery) {
          return;
        }

        const tableElement = this.$refs.equipmentTable;
        if (!tableElement) {
          return;
        }

        this.destroyEquipmentDataTable();

        if (!this.availableEquipment.length) {
          return;
        }

        this.equipmentDataTable = window.jQuery(tableElement).DataTable({
          pageLength: 10,
          lengthMenu: [5, 10, 25, 50],
          language: this.getSpanishDataTableMessages()
        });
      });
    },

    /**
     * Destruir DataTable activo para evitar reinicializaciones
     */
    destroyEquipmentDataTable() {
      if (this.equipmentDataTable) {
        this.equipmentDataTable.destroy();
        this.equipmentDataTable = null;
      }
    },

    /**
     * Textos de DataTable en español
     */
    getSpanishDataTableMessages() {
      return {
        decimal: ',',
        thousands: '.',
        emptyTable: 'No hay equipos disponibles',
        info: 'Mostrando _START_ a _END_ de _TOTAL_ equipos',
        infoEmpty: 'Mostrando 0 a 0 de 0 equipos',
        infoFiltered: '(filtrado de _MAX_ equipos en total)',
        lengthMenu: 'Mostrar _MENU_',
        loadingRecords: 'Cargando...',
        processing: 'Procesando...',
        search: 'Buscar:',
        zeroRecords: 'No se encontraron resultados',
        paginate: {
          first: 'Primero',
          last: 'Último',
          next: 'Siguiente',
          previous: 'Anterior'
        }
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
      this.destroyEquipmentDataTable();
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