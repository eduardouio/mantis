<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { appConfig } from '@/AppConfig.js'
import { useProjectStore } from '@/stores/ProjectStore'
import { useTechnicalStore } from '@/stores/TechnicalsStore'
import { useVehicleStore } from '@/stores/VehiclesStore'
import { useProjectResourceStore } from '@/stores/ProjectResourceStore'

const projectStore = useProjectStore()
const technicalStore = useTechnicalStore()
const vehicleStore = useVehicleStore()
const projectResourceStore = useProjectResourceStore()

onMounted(async () => {
  await projectStore.fetchProjects()
  await technicalStore.fetchTechnicals()
  await vehicleStore.fetchVehicles()
  await projectResourceStore.fetchProjectResources()
})


const router = useRouter()

const custodyChain = ref({
  technical: null,
  sheet_project: null,
  consecutive: '',
  activity_date: '',
  location: '',
  issue_date: '',
  start_time: '',
  end_time: '',
  time_duration: 0,
  contact_name: '',
  dni_contact: '',
  contact_position: '',
  date_contact: '',
  driver_name: '',
  dni_driver: '',
  driver_position: '',
  driver_date: '',
  total_gallons: 0,
  total_barrels: 0,
  total_cubic_meters: 0,
  notes: ''
})

const technicals = ref([
  { id: 1, name: 'Juan Pérez García' },
  { id: 2, name: 'María López' }
])

const sheetProjects = ref([
  { id: 1, code: 'SP-001', description: 'TORRES ULLOA VIVIANA - ORELLANA IV' },
  { id: 2, code: 'SP-002', description: 'Proyecto Demo' }
])

const availableResources = ref([
  {
    id: 21,
    detailed_description: "MANTENIMIENTO PSL-BT-103",
    cost: "35.00",
    resource_item_code: "PEISOL-SERV00",
    selected: false
  },
  {
    id: 22,
    detailed_description: "MANTENIMIENTO PSL-BT-108",
    cost: "34.00",
    resource_item_code: "PEISOL-SERV00",
    selected: false
  },
  {
    id: 23,
    detailed_description: "MANTENIMIENTO PSL-BT-111",
    cost: "35.00",
    resource_item_code: "PEISOL-SERV00",
    selected: false
  }
])

const selectedResources = computed(() => {
  return availableResources.value.filter(r => r.selected)
})

const toggleResourceSelection = (resource) => {
  resource.selected = !resource.selected
}

const calculateDuration = () => {
  if (custodyChain.value.start_time && custodyChain.value.end_time) {
    const start = custodyChain.value.start_time.split(':')
    const end = custodyChain.value.end_time.split(':')
    
    const startMinutes = parseInt(start[0]) * 60 + parseInt(start[1])
    const endMinutes = parseInt(end[0]) * 60 + parseInt(end[1])
    
    const duration = (endMinutes - startMinutes) / 60
    custodyChain.value.time_duration = duration > 0 ? duration.toFixed(2) : 0
  }
}

const submitForm = () => {
  console.log('Datos de Cadena de Custodia:', custodyChain.value)
  console.log('Recursos Seleccionados:', selectedResources.value)
}

const cancelForm = () => {
  router.push({ name: 'chain-custody' })
}
</script>

<template>
  <div class="max-w-7xl mx-auto p-4">
    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Información General -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Información General</h6>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Técnico -->
          <div class="form-control w-full">
            <label class="label" for="technical">
              <span class="label-text font-medium">Técnico *</span>
            </label>
            <select 
              id="technical"
              v-model="custodyChain.technical"
              required
              class="select select-bordered w-full"
            >
              <option :value="null">Seleccione un técnico</option>
              <option v-for="tech in technicals" :key="tech.id" :value="tech.id">
                {{ tech.name }}
              </option>
            </select>
          </div>

          <!-- Hoja de Proyecto -->
          <div class="form-control w-full">
            <label class="label" for="sheet_project">
              <span class="label-text font-medium">Hoja de Proyecto *</span>
            </label>
            <select 
              id="sheet_project"
              v-model="custodyChain.sheet_project"
              required
              class="select select-bordered w-full"
            >
              <option :value="null">Seleccione un proyecto</option>
              <option v-for="sheet in sheetProjects" :key="sheet.id" :value="sheet.id">
                {{ sheet.code }} - {{ sheet.description }}
              </option>
            </select>
          </div>

          <!-- Consecutivo -->
          <div class="form-control w-full">
            <label class="label" for="consecutive">
              <span class="label-text font-medium">Consecutivo</span>
            </label>
            <input 
              type="text"
              id="consecutive"
              v-model="custodyChain.consecutive"
              readonly
              placeholder="Se generará automáticamente"
              class="input input-bordered w-full bg-gray-100"
            />
          </div>

          <!-- Fecha de Actividad -->
          <div class="form-control w-full">
            <label class="label" for="activity_date">
              <span class="label-text font-medium">Fecha de Actividad *</span>
            </label>
            <input 
              type="date"
              id="activity_date"
              v-model="custodyChain.activity_date"
              required
              class="input input-bordered w-full"
            />
          </div>

          <!-- Ubicación -->
          <div class="form-control w-full">
            <label class="label" for="location">
              <span class="label-text font-medium">Ubicación</span>
            </label>
            <input 
              type="text"
              id="location"
              v-model="custodyChain.location"
              placeholder="Ej: Bloque 31"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Fecha de Emisión -->
          <div class="form-control w-full">
            <label class="label" for="issue_date">
              <span class="label-text font-medium">Fecha de Emisión</span>
            </label>
            <input 
              type="date"
              id="issue_date"
              v-model="custodyChain.issue_date"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Hora de Inicio -->
          <div class="form-control w-full">
            <label class="label" for="start_time">
              <span class="label-text font-medium">Hora de Inicio</span>
            </label>
            <input 
              type="time"
              id="start_time"
              v-model="custodyChain.start_time"
              @change="calculateDuration"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Hora de Fin -->
          <div class="form-control w-full">
            <label class="label" for="end_time">
              <span class="label-text font-medium">Hora de Fin</span>
            </label>
            <input 
              type="time"
              id="end_time"
              v-model="custodyChain.end_time"
              @change="calculateDuration"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Duración -->
          <div class="form-control w-full">
            <label class="label" for="time_duration">
              <span class="label-text font-medium">Duración (horas)</span>
            </label>
            <input 
              type="number"
              id="time_duration"
              v-model="custodyChain.time_duration"
              step="0.01"
              readonly
              class="input input-bordered w-full bg-gray-100"
            />
          </div>
        </div>
      </div>

      <!-- Información de Contacto -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Información de Contacto</h6>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Nombre de Contacto -->
          <div class="form-control w-full">
            <label class="label" for="contact_name">
              <span class="label-text font-medium">Nombre de Contacto</span>
            </label>
            <input 
              type="text"
              id="contact_name"
              v-model="custodyChain.contact_name"
              placeholder="Nombre completo"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Cédula de Contacto -->
          <div class="form-control w-full">
            <label class="label" for="dni_contact">
              <span class="label-text font-medium">Cédula de Contacto</span>
            </label>
            <input 
              type="text"
              id="dni_contact"
              v-model="custodyChain.dni_contact"
              placeholder="Número de identificación"
              maxlength="15"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Cargo de Contacto -->
          <div class="form-control w-full">
            <label class="label" for="contact_position">
              <span class="label-text font-medium">Cargo de Contacto</span>
            </label>
            <input 
              type="text"
              id="contact_position"
              v-model="custodyChain.contact_position"
              placeholder="Ej: Maquinista"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Fecha de Contacto -->
          <div class="form-control w-full">
            <label class="label" for="date_contact">
              <span class="label-text font-medium">Fecha de Contacto</span>
            </label>
            <input 
              type="date"
              id="date_contact"
              v-model="custodyChain.date_contact"
              class="input input-bordered w-full"
            />
          </div>
        </div>
      </div>

      <!-- Información del Transportista -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Información del Transportista</h6>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Nombre de Transportista -->
          <div class="form-control w-full">
            <label class="label" for="driver_name">
              <span class="label-text font-medium">Nombre de Transportista</span>
            </label>
            <input 
              type="text"
              id="driver_name"
              v-model="custodyChain.driver_name"
              placeholder="Nombre completo"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Cédula de Transportista -->
          <div class="form-control w-full">
            <label class="label" for="dni_driver">
              <span class="label-text font-medium">Cédula de Transportista</span>
            </label>
            <input 
              type="text"
              id="dni_driver"
              v-model="custodyChain.dni_driver"
              placeholder="Número de identificación"
              maxlength="15"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Cargo de Transportista -->
          <div class="form-control w-full">
            <label class="label" for="driver_position">
              <span class="label-text font-medium">Cargo de Transportista</span>
            </label>
            <input 
              type="text"
              id="driver_position"
              v-model="custodyChain.driver_position"
              placeholder="Ej: Conductor"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Fecha de Transportista -->
          <div class="form-control w-full">
            <label class="label" for="driver_date">
              <span class="label-text font-medium">Fecha de Transportista</span>
            </label>
            <input 
              type="date"
              id="driver_date"
              v-model="custodyChain.driver_date"
              class="input input-bordered w-full"
            />
          </div>
        </div>
      </div>

      <!-- Recursos del Proyecto (Detalle) -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">
          Recursos del Proyecto
          <span class="badge badge-primary ml-2">{{ selectedResources.length }} seleccionados</span>
        </h6>
        
        <div class="overflow-x-auto">
          <table class="table table-zebra w-full table-sm">
            <thead>
              <tr class="bg-gray-500 text-white">
                <th class="border border-gray-300 w-16 text-center">
                  <input type="checkbox" class="checkbox checkbox-sm" />
                </th>
                <th class="border border-gray-300">#</th>
                <th class="border border-gray-300">Código</th>
                <th class="border border-gray-300">Descripción</th>
                <th class="border border-gray-300 text-right">Costo</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(resource, index) in availableResources" 
                :key="resource.id"
                class="cursor-pointer hover:bg-blue-50"
                :class="{ 'bg-blue-100': resource.selected }"
                @click="toggleResourceSelection(resource)"
              >
                <td class="border border-gray-300 text-center">
                  <input 
                    type="checkbox" 
                    class="checkbox checkbox-sm checkbox-primary"
                    :checked="resource.selected"
                    @click.stop="toggleResourceSelection(resource)"
                  />
                </td>
                <td class="border border-gray-300">{{ index + 1 }}</td>
                <td class="border border-gray-300">{{ resource.resource_item_code }}</td>
                <td class="border border-gray-300">{{ resource.detailed_description }}</td>
                <td class="border border-gray-300 text-right font-mono">${{ resource.cost }}</td>
              </tr>
              <tr v-if="availableResources.length === 0">
                <td colspan="5" class="text-center text-gray-500 py-8">
                  <i class="las la-inbox text-4xl"></i>
                  <p>No hay recursos disponibles</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Totales -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Totales</h6>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Total Galones -->
          <div class="form-control w-full">
            <label class="label" for="total_gallons">
              <span class="label-text font-medium">Total Galones</span>
            </label>
            <input 
              type="number"
              id="total_gallons"
              v-model="custodyChain.total_gallons"
              min="0"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Total Barriles -->
          <div class="form-control w-full">
            <label class="label" for="total_barrels">
              <span class="label-text font-medium">Total Barriles</span>
            </label>
            <input 
              type="number"
              id="total_barrels"
              v-model="custodyChain.total_barrels"
              min="0"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Total Metros Cúbicos -->
          <div class="form-control w-full">
            <label class="label" for="total_cubic_meters">
              <span class="label-text font-medium">Total Metros Cúbicos</span>
            </label>
            <input 
              type="number"
              id="total_cubic_meters"
              v-model="custodyChain.total_cubic_meters"
              min="0"
              class="input input-bordered w-full"
            />
          </div>
        </div>
      </div>

      <!-- Notas -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Notas</h6>
        
        <div class="form-control w-full">
          <textarea 
            id="notes"
            v-model="custodyChain.notes"
            rows="4"
            placeholder="Observaciones o notas adicionales..."
            class="textarea textarea-bordered w-full"
          ></textarea>
        </div>
      </div>

      <!-- Botones -->
      <div class="flex gap-3 justify-end mt-6">
        <button type="button" class="btn btn-outline" @click="cancelForm">
          <i class="las la-times"></i>
          Cancelar
        </button>
        <button type="submit" class="btn btn-primary">
          <i class="las la-save"></i>
          Guardar Cadena de Custodia
        </button>
      </div>
    </form>
  </div>
</template>
