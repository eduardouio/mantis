const { createApp } = Vue;

createApp({
  delimiters: ['${', '}'],
  data() {
    return {
      vehicle: {
        brand: '',
        model: '',
        type_vehicle: '',
        year: null,
        no_plate: '',
        owner_transport: 'PEISOL',
        status_vehicle: 'DISPONIBLE',
        color: '',
        chassis_number: '',
        engine_number: '',
        serial_number: '',
        is_active: true,
        notes: '',
        insurance_company: '',
        nro_poliza: '',
        insurance_issue_date: '',
        insurance_expiration_date: '',
        duedate_satellite: '',
        date_matricula: '',
        due_date_matricula: '',
        due_date_cert_oper: '',
        date_mtop: '',
        date_technical_review: ''
      },
      certifications: [],
      passes: [],
      errors: {},
      isLoading: false,
      showCertificationModal: false,
      showPassModal: false,
      currentCertification: {
        name: '',
        date_start: '',
        date_end: '',
        description: ''
      },
      currentPass: {
        bloque: '',
        fecha_caducidad: ''
      },
      choices: {
        type_vehicle: [],
        owner_transport: [],
        status_vehicle: [],
        certifications: [],
        passes: []
      }
    }
  },
  
  mounted() {
    // Cargar opciones desde el contexto de Django
    if (window.vehicleChoices) {
      this.choices = window.vehicleChoices;
    }
    
    // Si estamos editando, cargar datos del vehículo
    if (window.vehicleData) {
      this.loadVehicleData(window.vehicleData);
    }
  },
  
  methods: {
    loadVehicleData(data) {
      this.vehicle = { ...this.vehicle, ...data.vehicle };
      this.certifications = data.certifications || [];
      this.passes = data.passes || [];
    },
    
    openCertificationModal() {
      this.showCertificationModal = true;
      this.currentCertification = {
        name: '',
        date_start: '',
        date_end: '',
        description: ''
      };
    },
    
    closeCertificationModal() {
      this.showCertificationModal = false;
    },
    
    openPassModal() {
      this.showPassModal = true;
      this.currentPass = {
        bloque: '',
        fecha_caducidad: ''
      };
    },
    
    closePassModal() {
      this.showPassModal = false;
    },
    
    addCertification() {
      if (!this.currentCertification.name || !this.currentCertification.date_start) {
        this.showError('Tipo de certificación y fecha de inicio son requeridos');
        return;
      }
      
      this.certifications.push({ ...this.currentCertification });
      this.closeCertificationModal();
      this.showSuccess('Certificación agregada correctamente');
    },
    
    removeCertification(index) {
      this.certifications.splice(index, 1);
    },
    
    addPass() {
      if (!this.currentPass.bloque || !this.currentPass.fecha_caducidad) {
        this.showError('Bloque y fecha de caducidad son requeridos');
        return;
      }
      
      this.passes.push({ ...this.currentPass });
      this.closePassModal();
      this.showSuccess('Pase agregado correctamente');
    },
    
    removePass(index) {
      this.passes.splice(index, 1);
    },
    
    async saveVehicle() {
      this.isLoading = true;
      this.errors = {};
      
      const payload = {
        vehicle: this.vehicle,
        certifications: this.certifications,
        passes: this.passes
      };
      
      try {
        const response = await fetch(window.location.href, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken()
          },
          body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (result.success) {
          this.showSuccess(result.message);
          if (result.redirect_url) {
            setTimeout(() => {
              window.location.href = result.redirect_url;
            }, 1500);
          }
        } else {
          this.errors = result.errors || {};
          this.showError(result.message || 'Error al guardar el vehículo');
        }
      } catch (error) {
        this.showError('Error de conexión al servidor');
      } finally {
        this.isLoading = false;
      }
    },
    
    getCsrfToken() {
      return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    },
    
    showSuccess(message) {
      this.showToast('success', message);
    },
    
    showError(message) {
      this.showToast('error', message);
    },
    
    showToast(type, message) {
      const toast = document.createElement('div');
      toast.className = `alert alert-${type === 'success' ? 'success' : 'error'} fixed top-4 right-4 z-50 w-auto max-w-md`;
      toast.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${type === 'success' ? 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' : 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'}" />
        </svg>
        <span>${message}</span>
      `;
      
      document.body.appendChild(toast);
      
      setTimeout(() => {
        toast.remove();
      }, 3000);
    },
    
    getChoiceLabel(choices, value) {
      const choice = choices.find(c => c[0] === value);
      return choice ? choice[1] : value;
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString('es-ES');
    }
  }
}).mount('#vehicleApp');
