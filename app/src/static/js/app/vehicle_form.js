// Aplicación Vue para el formulario de vehículos
const VehicleFormApp = {
  delimiters: ['${', '}'],
  data() {
    return {
      // Datos del vehículo
      vehicle: {
        no_plate: '',
        type: '',
        brand: '',
        model: '',
        year: new Date().getFullYear(),
        color: '',
        vin: '',
        engine_number: '',
        chassis_number: '',
        fuel_type: '',
        transmission: '',
        capacity: '',
        status: 'active',
        purchase_date: '',
        purchase_price: '',
        current_value: '',
        insurance_company: '',
        insurance_policy: '',
        insurance_start_date: '',
        insurance_end_date: '',
        insurance_amount: '',
        notes: ''
      },
      // Listas temporales
      certifications: [],
      passes: [],
      // Estado del formulario
      loading: false,
      errors: {},
      // Datos para selects
      vehicleTypes: [],
      fuelTypes: [],
      transmissionTypes: [],
      statusTypes: []
    };
  },
  computed: {
    // Validación del formulario
    isFormValid() {
      return this.vehicle.no_plate && this.vehicle.type && this.vehicle.brand && this.vehicle.model;
    },
    // Datos completos para enviar
    formData() {
      return {
        ...this.vehicle,
        certifications_data: JSON.stringify(this.certifications),
        passes_data: JSON.stringify(this.passes)
      };
    }
  },
  created() {
    // Cargar datos iniciales si estamos en modo edición
    this.loadInitialData();
    // Cargar opciones de los selects
    this.loadSelectOptions();
  },
  methods: {
    // Cargar datos iniciales del vehículo si estamos en modo edición
    loadInitialData() {
      const vehicleData = document.getElementById('vehicle-data');
      if (vehicleData) {
        try {
          const data = JSON.parse(vehicleData.textContent);
          this.vehicle = { ...this.vehicle, ...data.vehicle };
          this.certifications = data.certifications || [];
          this.passes = data.passes || [];
        } catch (e) {
          console.error('Error al cargar datos iniciales:', e);
        }
      }
    },
    // Cargar opciones para los selects
    async loadSelectOptions() {
      try {
        // Aquí irían las llamadas a la API para cargar las opciones
        // Por ahora usamos valores por defecto
        this.vehicleTypes = [
          { value: 'sedan', text: 'Sedán' },
          { value: 'suv', text: 'SUV' },
          { value: 'truck', text: 'Camión' },
          { value: 'van', text: 'Van' },
          { value: 'motorcycle', text: 'Motocicleta' }
        ];

        this.fuelTypes = [
          { value: 'gasoline', text: 'Gasolina' },
          { value: 'diesel', text: 'Diesel' },
          { value: 'electric', text: 'Eléctrico' },
          { value: 'hybrid', text: 'Híbrido' }
        ];

        this.transmissionTypes = [
          { value: 'manual', text: 'Manual' },
          { value: 'automatic', text: 'Automático' },
          { value: 'semi_automatic', text: 'Semi-automático' }
        ];

        this.statusTypes = [
          { value: 'active', text: 'Activo' },
          { value: 'maintenance', text: 'En Mantenimiento' },
          { value: 'inactive', text: 'Inactivo' },
          { value: 'sold', text: 'Vendido' }
        ];
      } catch (error) {
        console.error('Error al cargar opciones:', error);
        this.showError('Error al cargar opciones del formulario');
      }
    },
    // Manejar envío del formulario
    async submitForm() {
      if (!this.isFormValid) {
        this.showError('Por favor complete los campos requeridos');
        return;
      }

      this.loading = true;
      this.errors = {};

      try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = window.location.href;
        const method = this.vehicle.id ? 'PUT' : 'POST';

        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify(this.formData)
        });

        const data = await response.json();

        if (!response.ok) {
          if (response.status === 400) {
            this.errors = data.errors || {};
            this.showError('Por favor corrija los errores del formulario');
          } else {
            throw new Error(data.message || 'Error al procesar la solicitud');
          }
        } else {
          // Redirigir a la vista de detalle
          window.location.href = data.redirect_url || `/vehiculos/${data.id}/`;
        }
      } catch (error) {
        console.error('Error:', error);
        this.showError(error.message || 'Error al guardar el vehículo');
      } finally {
        this.loading = false;
      }
    },
    // Métodos para manejar certificaciones
    openCertificationModal() {
      this.$refs.certificationModal.showModal();
    },
    addCertification(certification) {
      this.certifications.push({
        id: Date.now(),
        ...certification,
        is_active: true
      });
      this.$refs.certificationModal.close();
    },
    removeCertification(index) {
      this.certifications.splice(index, 1);
    },
    // Métodos para manejar pases
    openPassModal() {
      this.$refs.passModal.showModal();
    },
    addPass(pass) {
      this.passes.push({
        id: Date.now(),
        ...pass
      });
      this.$refs.passModal.close();
    },
    removePass(index) {
      this.passes.splice(index, 1);
    },
    // Utilidades
    showError(message) {
      // Implementar lógica para mostrar mensajes de error
      console.error(message);
      // Aquí podrías usar un toast o similar
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES');
    }
  }
};

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  // Verificar si el contenedor existe antes de montar Vue
  const appElement = document.getElementById('vehicle-form-app');
  if (appElement) {
    Vue.createApp(VehicleFormApp).mount('#vehicle-form-app');
  }
});
