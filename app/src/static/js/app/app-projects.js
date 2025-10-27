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
      showEquipmentTable: true,
      equipmentLoaded: false,
      
      // Equipos asignados al proyecto
      assignedEquipment: window.ASSIGNED_EQUIPMENT || [],
      
      // Formulario de asignación de equipos
      assignmentForm: {
        rent_cost: '',
        maintenance_cost: '',
        operation_start_date: projectData.project_start_date || '',
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
      // Si ya se están cargando, no volver a cargar
      if (this.isLoadingEquipment) {
        return;
      }
      
      // Si ya se cargaron y hay equipos, no recargar
      if (this.equipmentLoaded && this.availableEquipment.length > 0) {
        return;
      }
      
      this.isLoadingEquipment = true;
      
      try {
        const response = await fetch('/api/projects/resources/available?exclude_services=true');
        const data = await response.json();
        
        if (data.success) {
          this.availableEquipment = data.data;
          this.equipmentLoaded = true;
          console.log(`Se cargaron ${data.data.length} equipos disponibles`);
        } else {
          this.showError('Error al cargar equipos: ' + data.error);
          this.availableEquipment = [];
        }
      } catch (error) {
        this.showError('Error de conexión: ' + error.message);
        this.availableEquipment = [];
      } finally {
        this.isLoadingEquipment = false;
      }
    },
    
    /**
     * Seleccionar equipo
     */
    selectEquipment(equipmentId) {
      this.selectedEquipmentId = equipmentId;
      this.selectedEquipment = this.availableEquipment.find(eq => eq.id === equipmentId);
      
      if (this.selectedEquipment) {
        this.hideEquipmentList();
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
        maintenance_interval: 15
      };

      this.displayEquipmentList();
    },

    /**
     * Inicializar o reiniciar DataTable del listado de equipos
     */
    refreshEquipmentDataTable() {
      if (!this.showEquipmentTable) {
        return;
      }

      this.$nextTick(() => {
        if (!window.jQuery) {
          console.warn('jQuery no está disponible');
          return;
        }

        const tableElement = this.$refs.equipmentTable;
        if (!tableElement) {
          console.warn('Elemento de tabla no encontrado');
          return;
        }

        // Siempre destruir cualquier instancia existente primero
        this.destroyEquipmentDataTable();

        if (!this.availableEquipment.length) {
          console.log('No hay equipos para mostrar en DataTable');
          return;
        }

        try {
          // Crear nueva instancia de DataTable
          this.equipmentDataTable = window.jQuery(tableElement).DataTable({
            pageLength: 10,
            lengthMenu: [5, 10, 25, 50],
            language: this.getSpanishDataTableMessages(),
            destroy: true,
            retrieve: false
          });
          console.log('DataTable inicializado correctamente');
        } catch (error) {
          console.error('Error al inicializar DataTable:', error);
        }
      });
    },

    /**
     * Destruir DataTable activo para evitar reinicializaciones
     */
    destroyEquipmentDataTable() {
      try {
        // Destruir la referencia guardada
        if (this.equipmentDataTable) {
          this.equipmentDataTable.destroy();
          this.equipmentDataTable = null;
        }
        
        // También verificar si existe una instancia sin referencia
        const tableElement = this.$refs.equipmentTable;
        if (tableElement && window.jQuery) {
          const $table = window.jQuery(tableElement);
          if (window.jQuery.fn.DataTable.isDataTable(tableElement)) {
            $table.DataTable().destroy();
          }
          // Limpiar cualquier markup de DataTable
          $table.find('tbody').off('click');
          $table.off('click');
        }
      } catch (error) {
        console.warn('Error al destruir DataTable:', error);
      }
    },
    
    /**
     * Mostrar nuevamente el listado de equipos
     */
    displayEquipmentList() {
      if (this.showEquipmentTable) {
        this.refreshEquipmentDataTable();
        return;
      }

      this.showEquipmentTable = true;
      this.$nextTick(() => {
        this.refreshEquipmentDataTable();
      });
    },

    /**
     * Ocultar listado y limpiar DataTable
     */
    hideEquipmentList() {
      this.destroyEquipmentDataTable();
      this.showEquipmentTable = false;
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
        operation_end_date: null,
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
          
          // Agregar el equipo a la lista de asignados
          if (data.assigned_resource) {
            this.assignedEquipment.push(data.assigned_resource);
            
            // Remover el equipo de la lista de disponibles
            const index = this.availableEquipment.findIndex(eq => eq.id === this.selectedEquipmentId);
            if (index > -1) {
              this.availableEquipment.splice(index, 1);
            }
          }
          
          // Cerrar modal y resetear formulario
          document.getElementById('modal_assign_equipment').close();
          this.resetAssignmentForm();
          
          // Actualizar totales
          this.updateTotals();
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
     * Actualizar totales de costos
     */
    updateTotals() {
      this.totalMonthlyRent = this.assignedEquipment.reduce(
        (sum, eq) => sum + parseFloat(eq.rent_cost || 0), 0
      );
      this.totalMonthlyMaintenance = this.assignedEquipment.reduce(
        (sum, eq) => sum + parseFloat(eq.maintenance_cost || 0), 0
      );
    },
    
    /**
     * Eliminar equipo asignado
     */
    async removeAssignedEquipment(assignmentId, equipmentName) {
      if (!confirm(`¿Está seguro de retirar el equipo "${equipmentName}" del proyecto?`)) {
        return;
      }
      
      try {
        const response = await fetch('/api/projects/resources/delete', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrf_token
          },
          body: JSON.stringify({
            assignment_id: assignmentId
          })
        });
        
        const data = await response.json();
        
        if (data.success) {
          this.showSuccess('Equipo retirado del proyecto');
          
          // Remover de la lista de asignados
          const index = this.assignedEquipment.findIndex(eq => eq.assignment_id === assignmentId);
          if (index > -1) {
            const removed = this.assignedEquipment.splice(index, 1)[0];
            
            // Si los equipos disponibles ya están cargados, agregar el equipo de vuelta
            if (this.equipmentLoaded && data.resource_item) {
              this.availableEquipment.push(data.resource_item);
            }
          }
          
          // Actualizar totales
          this.updateTotals();
        } else {
          this.showError(data.error || 'Error al retirar equipo');
        }
      } catch (error) {
        this.showError('Error de conexión: ' + error.message);
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
      console.log('Abriendo modal de equipos');
      this.resetAssignmentForm();
      this.showEquipmentTable = true;
      
      // Si los equipos ya están cargados, solo refrescar el DataTable
      if (this.equipmentLoaded && this.availableEquipment.length > 0) {
        console.log('Equipos ya cargados, refrescando DataTable');
        this.$nextTick(() => {
          this.refreshEquipmentDataTable();
        });
      } else {
        console.log('Cargando equipos por primera vez en el modal');
        this.loadAvailableEquipment().then(() => {
          this.refreshEquipmentDataTable();
        });
      }
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
    
    // Calcular totales iniciales
    this.updateTotals();
    
    // Cargar equipos disponibles al inicio (en segundo plano)
    this.loadAvailableEquipment().then(() => {
      console.log('Equipos disponibles cargados:', this.availableEquipment.length);
    }).catch(error => {
      console.error('Error al cargar equipos inicialmente:', error);
    });
    
    // Observer para detectar cuando se abre el modal de equipos
    const modalEquipment = document.getElementById('modal_assign_equipment');
    if (modalEquipment) {
      const observerEquipment = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.attributeName === 'open' && modalEquipment.hasAttribute('open')) {
            this.handleEquipmentModalOpen();
          }
        });
      });
      
      observerEquipment.observe(modalEquipment, { attributes: true });
    }
    
    // Observer para detectar cuando se abre el modal de planilla
    const modalSheet = document.getElementById('modal_create_sheet');
    if (modalSheet) {
      const observerSheet = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.attributeName === 'open' && modalSheet.hasAttribute('open')) {
            this.handleSheetModalOpen();
          }
        });
      });
      
      observerSheet.observe(modalSheet, { attributes: true });
    }
  },
  
  beforeUnmount() {
    // Limpiar DataTable antes de desmontar el componente
    this.destroyEquipmentDataTable();
  }
};

// Inicializar aplicación Vue
document.addEventListener('DOMContentLoaded', function() {
  createApp(ProjectApp).mount('#project-app');
});