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

  const vehicleAppInstance = createApp({
    delimiters: ['${', '}'],
    template: `
      <div class="max-w-6xl mx-auto p-6 bg-white rounded-2xl shadow-md border border-t-[15px] border-t-blue-500">
        <div class="flex justify-between items-center border-b-blue-500 border-b pb-1 mb-3">
          <h1 class="text-2xl font-semibold text-blue-500">\${ title || 'Formulario de Vehículo' }</h1>
          <div class="text-gray-500">
            <div class="flex flex-wrap gap-3">
              <button @click="cancelForm" class="btn btn-secondary">
                Cancelar
              </button>
            </div>
          </div>
        </div>

        <!-- Error Messages -->
        <div v-if="Object.keys(errors).length > 0" class="bg-red-50 border-l-4 border-red-400 p-6 mb-8 rounded-r-xl shadow-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-8 w-8 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-red-800">Error en el formulario</h3>
              <p class="text-red-700">Por favor, corrige los errores marcados en rojo antes de continuar.</p>
            </div>
          </div>
        </div>

        <form @submit.prevent="saveVehicle" class="space-y-4">
          <!-- Información básica en 3 columnas -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
            <!-- Columna 1: Datos del vehículo -->
            <div class="space-y-4 border-l-blue-300 border-l-[1px] pl-5">
              <h3 class="font-medium text-gray-700 mb-4 text-base">Datos del Vehículo</h3>
              
              <!-- Placa -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <span class="w-2 h-2 bg-red-500 rounded-full"></span>
                    Placa
                  </span>
                </label>
                <input type="text" 
                       v-model="vehicle.no_plate" 
                       class="input input-bordered w-full h-10" 
                       placeholder="Ingrese la placa del vehículo"
                       required>
                <label v-if="errors.no_plate" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.no_plate }</span>
                </label>
              </div>

              <!-- Tipo de Vehículo -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <span class="w-2 h-2 bg-red-500 rounded-full"></span>
                    Tipo
                  </span>
                </label>
                <select v-model="vehicle.type_vehicle" 
                        class="select select-bordered w-full h-10"
                        required>
                  <option value="">Seleccione un tipo</option>
                  <option v-for="choice in choices.type_vehicle" :key="choice[0]" :value="choice[0]">
                    \${ choice[1] }
                  </option>
                </select>
                <label v-if="errors.type_vehicle" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.type_vehicle }</span>
                </label>
              </div>

              <!-- Marca / Modelo -->
              <div class="grid grid-cols-2 gap-3">
                <div class="form-control">
                  <label class="label pb-2">
                    <span class="label-text text-sm font-semibold text-gray-700">Marca</span>
                  </label>
                  <input type="text" 
                         v-model="vehicle.brand" 
                         class="input input-bordered w-full h-10" 
                         placeholder="Marca">
                  <label v-if="errors.brand" class="label">
                    <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.brand }</span>
                  </label>
                </div>
                <div class="form-control">
                  <label class="label pb-2">
                    <span class="label-text text-sm font-semibold text-gray-700">Modelo</span>
                  </label>
                  <input type="text" 
                         v-model="vehicle.model" 
                         class="input input-bordered w-full h-10" 
                         placeholder="Modelo">
                  <label v-if="errors.model" class="label">
                    <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.model }</span>
                  </label>
                </div>
              </div>

              <!-- Año / Color -->
              <div class="grid grid-cols-2 gap-3">
                <div class="form-control">
                  <label class="label pb-2">
                    <span class="label-text text-sm font-semibold text-gray-700">Año</span>
                  </label>
                  <input type="number" 
                         v-model="vehicle.year" 
                         class="input input-bordered w-full h-10" 
                         placeholder="2024" 
                         min="1900" 
                         max="2030">
                  <label v-if="errors.year" class="label">
                    <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.year }</span>
                  </label>
                </div>
                <div class="form-control">
                  <label class="label pb-2">
                    <span class="label-text text-sm font-semibold text-gray-700">Color</span>
                  </label>
                  <input type="text" 
                         v-model="vehicle.color" 
                         class="input input-bordered w-full h-10" 
                         placeholder="Color">
                  <label v-if="errors.color" class="label">
                    <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.color }</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Columna 2: Información adicional -->
            <div class="space-y-4 border-l-blue-300 border-l-[1px] pl-5">
              <h3 class="font-medium text-gray-700 mb-4 text-base">Información Adicional</h3>

              <!-- Propietario -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700">Propietario</span>
                </label>
                <select v-model="vehicle.owner_transport" 
                        class="select select-bordered w-full h-10">
                  <option v-for="choice in choices.owner_transport" :key="choice[0]" :value="choice[0]">
                    \${ choice[1] }
                  </option>
                </select>
                <label v-if="errors.owner_transport" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.owner_transport }</span>
                </label>
              </div>

              <!-- Estado -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700">Estado</span>
                </label>
                <select v-model="vehicle.status_vehicle" 
                        class="select select-bordered w-full h-10">
                  <option v-for="choice in choices.status_vehicle" :key="choice[0]" :value="choice[0]">
                    \${ choice[1] }
                  </option>
                </select>
                <label v-if="errors.status_vehicle" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.status_vehicle }</span>
                </label>
              </div>

              <!-- Número de Chasis -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700">Número de Chasis</span>
                </label>
                <input type="text" 
                       v-model="vehicle.chassis_number" 
                       class="input input-bordered w-full h-10" 
                       placeholder="Número de chasis">
                <label v-if="errors.chassis_number" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.chassis_number }</span>
                </label>
              </div>

              <!-- Número de Motor -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700">Número de Motor</span>
                </label>
                <input type="text" 
                       v-model="vehicle.engine_number" 
                       class="input input-bordered w-full h-10" 
                       placeholder="Número de motor">
                <label v-if="errors.engine_number" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.engine_number }</span>
                </label>
              </div>

              <!-- Número de Serie -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700">Número de Serie</span>
                </label>
                <input type="text" 
                       v-model="vehicle.serial_number" 
                       class="input input-bordered w-full h-10" 
                       placeholder="Número de serie">
                <label v-if="errors.serial_number" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.serial_number }</span>
                </label>
              </div>
            </div>

            <!-- Columna 3: Documentación -->
            <div class="space-y-4 border-l-blue-300 border-l-[1px] pl-5">
              <h3 class="font-medium text-gray-700 mb-4 text-base">Documentación</h3>

              <!-- Seguros -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700">Compañía de Seguros</span>
                </label>
                <input type="text" 
                       v-model="vehicle.insurance_company" 
                       class="input input-bordered w-full h-10" 
                       placeholder="Compañía de seguros">
                <label v-if="errors.insurance_company" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.insurance_company }</span>
                </label>
              </div>

              <!-- Número de Póliza -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700">Número de Póliza</span>
                </label>
                <input type="text" 
                       v-model="vehicle.nro_poliza" 
                       class="input input-bordered w-full h-10" 
                       placeholder="Número de póliza">
                <label v-if="errors.nro_poliza" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.nro_poliza }</span>
                </label>
              </div>

              <!-- Fechas del Seguro -->
              <div class="grid grid-cols-2 gap-3">
                <div class="form-control">
                  <label class="label pb-2">
                    <span class="label-text text-sm font-semibold text-gray-700">Fecha Emisión</span>
                  </label>
                  <input type="date" 
                         v-model="vehicle.insurance_issue_date" 
                         class="input input-bordered w-full h-10">
                  <label v-if="errors.insurance_issue_date" class="label">
                    <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.insurance_issue_date }</span>
                  </label>
                </div>
                <div class="form-control">
                  <label class="label pb-2">
                    <span class="label-text text-sm font-semibold text-gray-700">Fecha Vencimiento</span>
                  </label>
                  <input type="date" 
                         v-model="vehicle.insurance_expiration_date" 
                         class="input input-bordered w-full h-10">
                  <label v-if="errors.insurance_expiration_date" class="label">
                    <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.insurance_expiration_date }</span>
                  </label>
                </div>
              </div>

              <!-- Notas -->
              <div class="form-control">
                <label class="label pb-2">
                  <span class="label-text text-sm font-semibold text-gray-700">Notas</span>
                </label>
                <textarea v-model="vehicle.notes" 
                          class="textarea textarea-bordered w-full min-h-20" 
                          placeholder="Notas adicionales"></textarea>
                <label v-if="errors.notes" class="label">
                  <span class="label-text-alt text-red-500 font-medium text-xs">\${ errors.notes }</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Sección de Certificaciones -->
          <div class="mt-8 p-4 bg-gray-50 rounded-lg">
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-medium text-gray-700">Certificaciones</h3>
              <button type="button" @click="openCertificationModal" class="btn btn-primary btn-sm">
                Agregar Certificación
              </button>
            </div>
            
            <div v-if="certifications.length === 0" class="text-gray-500 text-center py-4">
              No hay certificaciones registradas
            </div>
            
            <div v-else class="space-y-2">
              <div v-for="(cert, index) in certifications" :key="index" 
                   class="flex justify-between items-center p-3 bg-white rounded border">
                <div>
                  <span class="font-medium">\${ cert.name }</span>
                  <span class="text-sm text-gray-500 ml-2">
                    (\${ formatDate(cert.date_start) } - \${ formatDate(cert.date_end) })
                  </span>
                </div>
                <button type="button" @click="removeCertification(index)" class="btn btn-error btn-sm">
                  Eliminar
                </button>
              </div>
            </div>
          </div>

          <!-- Sección de Pases -->
          <div class="mt-8 p-4 bg-gray-50 rounded-lg">
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-medium text-gray-700">Pases</h3>
              <button type="button" @click="openPassModal" class="btn btn-primary btn-sm">
                Agregar Pase
              </button>
            </div>
            
            <div v-if="passes.length === 0" class="text-gray-500 text-center py-4">
              No hay pases registrados
            </div>
            
            <div v-else class="space-y-2">
              <div v-for="(pass, index) in passes" :key="index" 
                   class="flex justify-between items-center p-3 bg-white rounded border">
                <div>
                  <span class="font-medium">\${ pass.bloque }</span>
                  <span class="text-sm text-gray-500 ml-2">
                    (Caduca: \${ formatDate(pass.fecha_caducidad) })
                  </span>
                </div>
                <button type="button" @click="removePass(index)" class="btn btn-error btn-sm">
                  Eliminar
                </button>
              </div>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="flex flex-wrap justify-center gap-2 mt-6 border-t pt-4">
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              <span v-if="isLoading" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">
                <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                <path d="M6 4h10l4 4v10a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12a2 2 0 0 1 2 -2"/>
                <path d="M12 14m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>
                <path d="M14 4l0 4l-6 0l0 -4"/>
              </svg>
              \${ isLoading ? 'Guardando...' : 'Guardar Vehículo' }
            </button>
            <button type="button" @click="cancelForm" class="btn btn-secondary">
              <svg xmlns="http://www.w3.org/2000/svg" class="inline-block mr-1" width="12" height="12" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                <path d="M9 6l-6 6l6 6" />
              </svg>
              Cancelar
            </button>
          </div>
        </form>

        <!-- Modal para Certificaciones -->
        <div v-if="showCertificationModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
              <h3 class="font-bold text-lg text-gray-800">Agregar Certificación</h3>
              <button type="button" @click="closeCertificationModal" class="text-gray-400 hover:text-gray-600">
                ✕
              </button>
            </div>
            
            <form @submit.prevent="addCertification" class="space-y-4">
              <div class="form-control">
                <label class="label">
                  <span class="label-text font-semibold">Tipo de Certificación</span>
                </label>
                <input type="text" v-model="currentCertification.name" class="input input-bordered w-full" required>
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text font-semibold">Fecha de Inicio</span>
                </label>
                <input type="date" v-model="currentCertification.date_start" class="input input-bordered w-full" required>
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text font-semibold">Fecha de Fin</span>
                </label>
                <input type="date" v-model="currentCertification.date_end" class="input input-bordered w-full">
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text font-semibold">Descripción</span>
                </label>
                <textarea v-model="currentCertification.description" class="textarea textarea-bordered w-full min-h-20" placeholder="Descripción de la certificación (opcional)"></textarea>
              </div>

              <div class="flex justify-end gap-2 mt-6">
                <button type="button" @click="closeCertificationModal" class="btn btn-secondary">Cancelar</button>
                <button type="submit" class="btn btn-primary">Guardar Certificación</button>
              </div>
            </form>
          </div>
        </div>

        <!-- Modal para Pases -->
        <div v-if="showPassModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
              <h3 class="font-bold text-lg text-gray-800">Agregar Pase</h3>
              <button type="button" @click="closePassModal" class="text-gray-400 hover:text-gray-600">
                ✕
              </button>
            </div>
            
            <form @submit.prevent="addPass" class="space-y-4">
              <div class="form-control">
                <label class="label">
                  <span class="label-text font-semibold">Bloque</span>
                </label>
                <select v-model="currentPass.bloque" class="select select-bordered w-full" required>
                  <option value="">Seleccione un bloque</option>
                  <option value="petroecuador">Tarjeta de Petroecuador</option>
                  <option value="shaya">Shaya</option>
                  <option value="consorcio_shushufindi">Consorcio Shushufindi</option>
                  <option value="enap_sipec">ENAP SIPEC</option>
                  <option value="orion">Tarjeta Orion</option>
                  <option value="andes_petroleum">Andes Petroleum</option>
                  <option value="pardalis_services">Pardalis Services</option>
                  <option value="frontera_energy">Frontera Energy</option>
                  <option value="gran_tierra">Gran Tierra</option>
                  <option value="pcr">PCR</option>
                  <option value="halliburton">Halliburton</option>
                  <option value="gente_oil">Gente Oil</option>
                  <option value="tribiol_gas">Tribiol Gas</option>
                  <option value="adico">Adico</option>
                  <option value="cuyaveno_petro">Cuyaveno Petro</option>
                  <option value="geopark">Geopark</option>
                </select>
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text font-semibold">Fecha de Caducidad</span>
                </label>
                <input type="date" v-model="currentPass.fecha_caducidad" class="input input-bordered w-full" required>
              </div>

              <div class="flex justify-end gap-2 mt-6">
                <button type="button" @click="closePassModal" class="btn btn-secondary">Cancelar</button>
                <button type="submit" class="btn btn-primary">Guardar Pase</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    `,
    data() {
      return {
        title: 'Formulario de Vehículo',
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
        // Mostrar modal usando DaisyUI
        const modal = document.getElementById('certificationModal');
        if (modal) {
          modal.showModal();
        }
      },
      
      closeCertificationModal() {
        this.showCertificationModal = false;
        // Cerrar modal usando DaisyUI
        const modal = document.getElementById('certificationModal');
        if (modal) {
          modal.close();
        }
      },
      
      openPassModal() {
        this.showPassModal = true;
        this.currentPass = {
          bloque: '',
          fecha_caducidad: ''
        };
        // Mostrar modal usando DaisyUI
        const modal = document.getElementById('passModal');
        if (modal) {
          modal.showModal();
        }
      },
      
      closePassModal() {
        this.showPassModal = false;
        // Cerrar modal usando DaisyUI
        const modal = document.getElementById('passModal');
        if (modal) {
          modal.close();
        }
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
      
      cancelForm() {
        // Navegar de vuelta a la lista de vehículos
        window.location.href = '/vehiculos/'; // Ajusta la URL según tu configuración
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

    // Limpiar el contenido del elemento si es necesario
    if (vehicleAppElement.children.length === 0) {
      console.warn('vehicleApp container is empty, Vue might not work correctly');
    }

    try {
      const mountedApp = vehicleAppInstance.mount('#vehicleApp');
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
