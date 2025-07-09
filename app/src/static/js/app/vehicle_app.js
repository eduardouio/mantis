(function() {
  'use strict';
  
  // Verificar que Vue esté disponible
  if (typeof Vue === 'undefined') {
    console.error('Vue.js no está cargado');
    return;
  }

  // Verificar si ya existe una instancia global y desmontarla
  if (window.vehicleAppInstance) {
    try {
      window.vehicleAppInstance.unmount();
      console.log('Previous Vue instance unmounted');
    } catch (error) {
      console.warn('Error unmounting previous instance:', error);
    }
    window.vehicleAppInstance = null;
  }

  const { createApp } = Vue;

  const vehicleApp = createApp({
    delimiters: ['${', '}'],
    data() {
      return {
        certifications: [],
        passes: [],
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
        editingCertificationIndex: -1,
        editingPassIndex: -1
      }
    },
    
    mounted() {
      // Cargar datos existentes si estamos editando
      this.loadExistingData();
    },
    
    methods: {
      loadExistingData() {
        // Cargar certificaciones existentes si hay datos del vehículo
        if (window.vehicleData && window.vehicleData.certifications) {
          this.certifications = window.vehicleData.certifications;
        }
        
        // Cargar pases existentes si hay datos del vehículo
        if (window.vehicleData && window.vehicleData.passes) {
          this.passes = window.vehicleData.passes;
        }
      },
      
      openCertificationModal() {
        this.currentCertification = {
          name: '',
          date_start: '',
          date_end: '',
          description: ''
        };
        this.editingCertificationIndex = -1;
        
        const modal = document.getElementById('certificationModal');
        if (modal) {
          modal.showModal();
        }
      },
      
      closeCertificationModal() {
        const modal = document.getElementById('certificationModal');
        if (modal) {
          modal.close();
        }
      },
      
      openPassModal() {
        this.currentPass = {
          bloque: '',
          fecha_caducidad: ''
        };
        this.editingPassIndex = -1;
        
        const modal = document.getElementById('passModal');
        if (modal) {
          modal.showModal();
        }
      },
      
      closePassModal() {
        const modal = document.getElementById('passModal');
        if (modal) {
          modal.close();
        }
      },
      
      addCertification() {
        if (!this.currentCertification.name || !this.currentCertification.date_start) {
          this.showToast('error', 'Tipo de certificación y fecha de inicio son requeridos');
          return;
        }

        if (this.currentCertification.date_end && this.currentCertification.date_start > this.currentCertification.date_end) {
          this.showToast('error', 'La fecha de fin debe ser posterior a la fecha de inicio');
          return;
        }
        
        if (this.editingCertificationIndex >= 0) {
          // Editando certificación existente
          this.certifications[this.editingCertificationIndex] = { ...this.currentCertification };
          this.showToast('success', 'Certificación actualizada correctamente');
        } else {
          // Agregando nueva certificación
          this.certifications.push({ ...this.currentCertification });
          this.showToast('success', 'Certificación agregada correctamente');
        }
        
        this.updateFormData();
        this.closeCertificationModal();
      },
      
      editCertification(index) {
        this.currentCertification = { ...this.certifications[index] };
        this.editingCertificationIndex = index;
        this.openCertificationModal();
      },
      
      removeCertification(index) {
        if (confirm('¿Está seguro de eliminar esta certificación?')) {
          this.certifications.splice(index, 1);
          this.updateFormData();
          this.showToast('success', 'Certificación eliminada');
        }
      },
      
      addPass() {
        if (!this.currentPass.bloque || !this.currentPass.fecha_caducidad) {
          this.showToast('error', 'Bloque y fecha de caducidad son requeridos');
          return;
        }

        // Validar que la fecha no sea en el pasado
        const today = new Date();
        const passDate = new Date(this.currentPass.fecha_caducidad);
        if (passDate < today) {
          this.showToast('warning', 'La fecha de caducidad está en el pasado');
        }
        
        if (this.editingPassIndex >= 0) {
          // Editando pase existente
          this.passes[this.editingPassIndex] = { ...this.currentPass };
          this.showToast('success', 'Pase actualizado correctamente');
        } else {
          // Agregando nuevo pase
          this.passes.push({ ...this.currentPass });
          this.showToast('success', 'Pase agregado correctamente');
        }
        
        this.updateFormData();
        this.closePassModal();
      },
      
      editPass(index) {
        this.currentPass = { ...this.passes[index] };
        this.editingPassIndex = index;
        this.openPassModal();
      },
      
      removePass(index) {
        if (confirm('¿Está seguro de eliminar este pase?')) {
          this.passes.splice(index, 1);
          this.updateFormData();
          this.showToast('success', 'Pase eliminado');
        }
      },
      
      updateFormData() {
        // Actualizar campos ocultos del formulario
        const certificationsInput = document.querySelector('input[name="certifications_data"]');
        const passesInput = document.querySelector('input[name="passes_data"]');
        
        if (certificationsInput) {
          certificationsInput.value = JSON.stringify(this.certifications);
        }
        
        if (passesInput) {
          passesInput.value = JSON.stringify(this.passes);
        }
      },
      
      getCertificationDisplayName(name) {
        const displayNames = {
          'INSPECCION VOLUMETRICA': 'Inspección Volumétrica',
          'MEDICION DE ESPESORES': 'Medición de Espesores',
          'INSPECCION DE SEGURIDAD': 'Inspección de Seguridad',
          'PRUEBA HIDROSTATICA': 'Prueba Hidrostática'
        };
        return displayNames[name] || name;
      },
      
      getPassDisplayName(bloque) {
        return bloque; // Los bloques ya tienen el nombre correcto
      },
      
      formatDate(dateString) {
        if (!dateString) return '';
        return new Date(dateString).toLocaleDateString('es-ES');
      },
      
      getPassStatus(fechaCaducidad) {
        if (!fechaCaducidad) return 'Sin fecha';
        
        const today = new Date();
        const passDate = new Date(fechaCaducidad);
        const diffTime = passDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays < 0) {
          return 'Vencido';
        } else if (diffDays <= 30) {
          return 'Por vencer';
        } else {
          return 'Vigente';
        }
      },
      
      getPassStatusClass(fechaCaducidad) {
        const status = this.getPassStatus(fechaCaducidad);
        switch(status) {
          case 'Vencido':
            return 'badge-error';
          case 'Por vencer':
            return 'badge-warning';
          case 'Vigente':
            return 'badge-success';
          default:
            return 'badge-neutral';
        }
      },
      
      showToast(type, message) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'error'} fixed top-4 right-4 z-50 w-auto max-w-md`;
        toast.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${type === 'success' ? 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' : type === 'warning' ? 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.732 0l-8.898 12c-.77.833.192 2.5 1.732 2.5z' : 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'}" />
          </svg>
          <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
          toast.remove();
        }, 3000);
      }
    }
  });

  // Función para montar la aplicación de forma segura
  function mountVueApp() {
    const vehicleAppElement = document.getElementById('vehicleApp');
    
    if (!vehicleAppElement) {
      console.warn('Element #vehicleApp not found');
      return;
    }

    // Verificar si el elemento ya tiene una instancia de Vue
    if (vehicleAppElement.__vue_app__) {
      console.log('Unmounting existing Vue instance from element');
      try {
        vehicleAppElement.__vue_app__.unmount();
      } catch (error) {
        console.warn('Error unmounting existing instance:', error);
      }
    }

    try {
      const mountedApp = vehicleApp.mount('#vehicleApp');
      console.log('Vue app mounted successfully');
      
      // Guardar referencia global
      window.vehicleAppInstance = mountedApp;
      
      return mountedApp;
      
    } catch (error) {
      console.error('Error mounting Vue app:', error);
      return null;
    }
  }

  // Montar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountVueApp);
  } else {
    // El DOM ya está listo
    setTimeout(mountVueApp, 0);
  }

  // Funciones globales para compatibilidad con onclick
  window.openCertificationModal = function() {
    if (window.vehicleAppInstance && typeof window.vehicleAppInstance.openCertificationModal === 'function') {
      window.vehicleAppInstance.openCertificationModal();
    } else {
      console.warn('openCertificationModal function not available');
    }
  };

  window.closeCertificationModal = function() {
    if (window.vehicleAppInstance && typeof window.vehicleAppInstance.closeCertificationModal === 'function') {
      window.vehicleAppInstance.closeCertificationModal();
    } else {
      console.warn('closeCertificationModal function not available');
    }
  };

  window.openPassModal = function() {
    if (window.vehicleAppInstance && typeof window.vehicleAppInstance.openPassModal === 'function') {
      window.vehicleAppInstance.openPassModal();
    } else {
      console.warn('openPassModal function not available');
    }
  };

  window.closePassModal = function() {
    if (window.vehicleAppInstance && typeof window.vehicleAppInstance.closePassModal === 'function') {
      window.vehicleAppInstance.closePassModal();
    } else {
      console.warn('closePassModal function not available');
    }
  };

})();
