<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { appConfig } from '@/AppConfig.js'
import { UseProjectStore } from '@/stores/ProjectStore'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
import { UseShippingGuideStore } from '@/stores/ShippingGuideStore'
import { UseVehicleStore } from '@/stores/VehicleStore'

const projectStore = UseProjectStore()
const projectResourceStore = UseProjectResourceStore()
const shippingGuideStore = UseShippingGuideStore()
const vehicleStore = UseVehicleStore()

const router = useRouter()
const route = useRoute()
const isLoading = ref(false)

// ID de la guía desde la ruta
const guideId = computed(() => {
  const id = parseInt(route.params.id)
  return isNaN(id) ? 0 : id
})

const isEditMode = computed(() => guideId.value > 0)
const isProjectClosed = computed(() => projectStore.project?.is_closed === true)

// Datos del formulario
const guide = ref({
  project_id: appConfig.idProject,
  issue_date: new Date().toISOString().split('T')[0],
  start_date: '',
  end_date: '',
  origin_place: '',
  destination_place: '',
  carrier_name: '',
  carrier_ci: '',
  vehicle_plate: '',
  dispatcher_name: '',
  dispatcher_ci: '',
  contact_name: '',
  contact_phone: '',
  recibed_by: '',
  recibed_ci: '',
  notes: '',
})

// Detalles (ítems de la guía)
const details = ref([])

// Nuevo ítem manual
const newDetail = ref({
  description: '',
  quantity: 1,
  unit: 1.00,
})

// Recursos del proyecto disponibles para agregar (solo equipos físicos, sin importar si están activos)
const availableResources = computed(() => {
  return projectResourceStore.resourcesProject.filter(r => 
    !r.is_deleted && r.type_resource === 'EQUIPO'
  )
})

// Vehículos disponibles
const vehicles = computed(() => {
  return vehicleStore.vehicles.map(v => ({
    id: v.id,
    display: `${v.no_plate} - ${v.brand} ${v.model}`,
    plate: v.no_plate,
  }))
})

const selectedVehicleId = ref(null)

// Al seleccionar un vehículo, rellenar la placa
watch(selectedVehicleId, (newId) => {
  if (newId) {
    const vehicle = vehicleStore.vehicles.find(v => v.id === newId)
    if (vehicle) {
      guide.value.vehicle_plate = vehicle.no_plate
    }
  }
})

// Cargar datos en modo edición
const loadGuideData = async () => {
  if (!isEditMode.value) return

  try {
    isLoading.value = true
    const data = await shippingGuideStore.fetchGuideDetail(guideId.value)

    if (data) {
      guide.value = {
        id: data.id,
        project_id: data.project_id,
        issue_date: data.issue_date || '',
        start_date: data.start_date || '',
        end_date: data.end_date || '',
        origin_place: data.origin_place || '',
        destination_place: data.destination_place || '',
        carrier_name: data.carrier_name || '',
        carrier_ci: data.carrier_ci || '',
        vehicle_plate: data.vehicle_plate || '',
        dispatcher_name: data.dispatcher_name || '',
        dispatcher_ci: data.dispatcher_ci || '',
        contact_name: data.contact_name || '',
        contact_phone: data.contact_phone || '',
        recibed_by: data.recibed_by || '',
        recibed_ci: data.recibed_ci || '',
        notes: data.notes || '',
      }

      // Cargar detalles
      details.value = (data.details || []).map(d => ({
        description: d.description,
        quantity: d.quantity,
        unit: parseFloat(d.unit) || 0,
      }))

      // Buscar vehículo por placa
      if (data.vehicle_plate) {
        const vehicle = vehicleStore.vehicles.find(v => v.no_plate === data.vehicle_plate)
        if (vehicle) selectedVehicleId.value = vehicle.id
      }
    } else {
      alert('Guía de remisión no encontrada')
      router.push({ name: 'shipping-guide-list' })
    }
  } catch (error) {
    console.error('Error al cargar guía:', error)
    alert('Error al cargar los datos: ' + error.message)
    router.push({ name: 'shipping-guide-list' })
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await projectStore.fetchProjectData()
  await projectResourceStore.fetchResourcesProject()
  await vehicleStore.fetchVehicles()

  // Inicializar con datos del proyecto
  if (!isEditMode.value) {
    guide.value.contact_name = projectStore.project?.contact_name || ''
    guide.value.contact_phone = projectStore.project?.contact_phone || ''
    guide.value.origin_place = projectStore.project?.location || ''
  }

  if (isEditMode.value) {
    await loadGuideData()
  }
})

// Agregar recurso del proyecto como ítem de la guía
const addResourceAsDetail = (resource) => {
  details.value.push({
    description: resource.detailed_description || resource.resource_item_name || `Recurso #${resource.id}`,
    quantity: 1,
    unit: parseFloat(resource.cost) || 1.00,
  })
}

// Agregar ítem manual
const addManualDetail = () => {
  if (!newDetail.value.description.trim()) return
  details.value.push({
    description: newDetail.value.description,
    quantity: newDetail.value.quantity || 1,
    unit: newDetail.value.unit || 1.00,
  })
  newDetail.value = { description: '', quantity: 1, unit: 1.00 }
}

// Remover ítem
const removeDetail = (index) => {
  details.value.splice(index, 1)
}

// Enviar formulario
const submitForm = async () => {
  try {
    isLoading.value = true

    if (!guide.value.issue_date) {
      alert('La fecha de emisión es requerida')
      return
    }

    const payload = {
      ...guide.value,
      project_id: appConfig.idProject,
      details: details.value.map(d => ({
        description: d.description,
        quantity: d.quantity,
        unit: d.unit,
      })),
    }

    if (isEditMode.value) {
      payload.id = guideId.value
      await shippingGuideStore.updateGuide(payload)
    } else {
      await shippingGuideStore.createGuide(payload)
    }

    router.push({ name: 'shipping-guide-list' })
  } catch (error) {
    console.error('Error al guardar:', error)
    alert('Error al ' + (isEditMode.value ? 'actualizar' : 'crear') + ' la guía: ' + error.message)
  } finally {
    isLoading.value = false
  }
}

const cancelForm = () => {
  router.push({ name: 'shipping-guide-list' })
}
</script>

<template>
  <div class="max-w-7xl mx-auto p-4">
    <!-- Título -->
    <div class="bg-white rounded-lg p-4 mb-4 border border-gray-200 shadow-sm">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-xl font-semibold text-gray-800">
            <i class="las la-shipping-fast text-teal-600"></i>
            {{ isEditMode ? `Editar Guía de Remisión #${guideId}` : 'Nueva Guía de Remisión' }}
          </h2>
          <p class="text-sm text-gray-600 mt-1">
            {{ isEditMode ? 'Modifique los datos de la guía de remisión' : 'Complete los datos para generar una nueva guía de remisión' }}
          </p>
        </div>
        <div>
          <span class="badge badge-lg badge-primary">
            Proyecto #{{ appConfig.idProject }}
          </span>
        </div>
      </div>
    </div>

    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Información General -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Información General</h6>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Fecha de Emisión -->
          <div class="form-control w-full">
            <label class="label" for="issue_date">
              <span class="label-text font-medium">Fecha de Emisión *</span>
            </label>
            <input
              type="date"
              id="issue_date"
              v-model="guide.issue_date"
              required
              class="input input-bordered w-full"
            />
          </div>

          <!-- Fecha Inicio Transporte -->
          <div class="form-control w-full">
            <label class="label" for="start_date">
              <span class="label-text font-medium">Fecha Inicio Transporte</span>
            </label>
            <input
              type="date"
              id="start_date"
              v-model="guide.start_date"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Fecha Fin Transporte -->
          <div class="form-control w-full">
            <label class="label" for="end_date">
              <span class="label-text font-medium">Fecha Fin Transporte</span>
            </label>
            <input
              type="date"
              id="end_date"
              v-model="guide.end_date"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Lugar de Origen -->
          <div class="form-control w-full">
            <label class="label" for="origin_place">
              <span class="label-text font-medium">Lugar de Origen</span>
            </label>
            <input
              type="text"
              id="origin_place"
              v-model="guide.origin_place"
              placeholder="Ej: Quito, Bodega Central"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Lugar de Destino -->
          <div class="form-control w-full">
            <label class="label" for="destination_place">
              <span class="label-text font-medium">Lugar de Destino</span>
            </label>
            <input
              type="text"
              id="destination_place"
              v-model="guide.destination_place"
              placeholder="Ej: Campamento Norte"
              class="input input-bordered w-full"
            />
          </div>

          <!-- Vehículo -->
          <div class="form-control w-full">
            <label class="label" for="vehicle_select">
              <span class="label-text font-medium">Vehículo</span>
            </label>
            <select
              id="vehicle_select"
              v-model.number="selectedVehicleId"
              class="select select-bordered w-full"
            >
              <option :value="null">Seleccione un vehículo (opcional)</option>
              <option v-for="v in vehicles" :key="v.id" :value="v.id">
                {{ v.display }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Información del Transportista -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Información del Transportista</h6>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="form-control w-full">
            <label class="label" for="carrier_name">
              <span class="label-text font-medium">Nombre del Transportista</span>
            </label>
            <input
              type="text"
              id="carrier_name"
              v-model="guide.carrier_name"
              placeholder="Nombre completo"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="carrier_ci">
              <span class="label-text font-medium">Cédula del Transportista</span>
            </label>
            <input
              type="text"
              id="carrier_ci"
              v-model="guide.carrier_ci"
              placeholder="Número de identificación"
              maxlength="20"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="vehicle_plate">
              <span class="label-text font-medium">Placa del Vehículo</span>
            </label>
            <input
              type="text"
              id="vehicle_plate"
              v-model="guide.vehicle_plate"
              placeholder="Ej: ABC-1234"
              maxlength="20"
              class="input input-bordered w-full"
            />
          </div>
        </div>
      </div>

      <!-- Despachador -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Despachador</h6>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label" for="dispatcher_name">
              <span class="label-text font-medium">Nombre del Despachador</span>
            </label>
            <input
              type="text"
              id="dispatcher_name"
              v-model="guide.dispatcher_name"
              placeholder="Nombre completo"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="dispatcher_ci">
              <span class="label-text font-medium">Cédula del Despachador</span>
            </label>
            <input
              type="text"
              id="dispatcher_ci"
              v-model="guide.dispatcher_ci"
              placeholder="Número de identificación"
              maxlength="20"
              class="input input-bordered w-full"
            />
          </div>
        </div>
      </div>

      <!-- Contacto en el Proyecto -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Contacto en el Proyecto</h6>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label" for="contact_name">
              <span class="label-text font-medium">Nombre de Contacto</span>
            </label>
            <input
              type="text"
              id="contact_name"
              v-model="guide.contact_name"
              placeholder="Nombre completo"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="contact_phone">
              <span class="label-text font-medium">Teléfono de Contacto</span>
            </label>
            <input
              type="text"
              id="contact_phone"
              v-model="guide.contact_phone"
              placeholder="Teléfono"
              maxlength="15"
              class="input input-bordered w-full"
            />
          </div>
        </div>
      </div>

      <!-- Recibido por -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Recepción</h6>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label" for="recibed_by">
              <span class="label-text font-medium">Recibido Por</span>
            </label>
            <input
              type="text"
              id="recibed_by"
              v-model="guide.recibed_by"
              placeholder="Nombre de quien recibe"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label" for="recibed_ci">
              <span class="label-text font-medium">Cédula de Quien Recibe</span>
            </label>
            <input
              type="text"
              id="recibed_ci"
              v-model="guide.recibed_ci"
              placeholder="Número de identificación"
              maxlength="20"
              class="input input-bordered w-full"
            />
          </div>
        </div>
      </div>

      <!-- Detalle de Ítems -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">
          Detalle de Ítems
          <span class="badge badge-primary ml-2">{{ details.length }} ítems</span>
        </h6>

        <!-- Agregar desde recursos del proyecto -->
        <div class="mb-4">
          <h6 class="text-sm font-semibold text-gray-600 mb-2">
            <i class="las la-toolbox text-teal-500"></i>
            Agregar desde Equipos del Proyecto
          </h6>
          <div class="overflow-x-auto max-h-48 border rounded border-gray-200">
            <table class="table table-sm table-zebra w-full">
              <thead class="sticky top-0">
                <tr class="bg-gray-500 text-white">
                  <th class="border border-gray-300">#</th>
                  <th class="border border-gray-300">Equipo / Recurso</th>
                  <th class="border border-gray-300">Tipo</th>
                  <th class="border border-gray-300 text-right">Costo</th>
                  <th class="border border-gray-300 w-24 text-center">Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(resource, idx) in availableResources" :key="resource.id" class="hover:bg-teal-50">
                  <td class="border border-gray-300">{{ idx + 1 }}</td>
                  <td class="border border-gray-300">{{ resource.detailed_description || resource.resource_item_name }}</td>
                  <td class="border border-gray-300">
                    <span class="badge badge-sm" :class="resource.type_resource === 'EQUIPO' ? 'badge-info' : 'badge-warning'">
                      {{ resource.type_resource }}
                    </span>
                  </td>
                  <td class="border border-gray-300 text-right font-mono">${{ parseFloat(resource.cost || 0).toFixed(2) }}</td>
                  <td class="border border-gray-300 text-center">
                    <button
                      type="button"
                      class="btn btn-xs btn-primary"
                      @click="addResourceAsDetail(resource)"
                      title="Agregar a la guía"
                    >
                      <i class="las la-plus"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="availableResources.length === 0">
                  <td colspan="5" class="text-center py-4 text-gray-500">
                    No hay recursos asignados al proyecto
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Agregar ítem manual -->
        <div class="mb-4 p-3 bg-gray-50 rounded border border-gray-200">
          <h6 class="text-sm font-semibold text-gray-600 mb-2">
            <i class="las la-pen text-teal-500"></i>
            Agregar Ítem Manual
          </h6>
          <div class="flex gap-2 items-end">
            <div class="form-control flex-1">
              <label class="label py-0">
                <span class="label-text text-xs">Descripción</span>
              </label>
              <input
                type="text"
                v-model="newDetail.description"
                placeholder="Descripción del ítem"
                class="input input-bordered input-sm w-full"
                @keyup.enter="addManualDetail"
              />
            </div>
            <div class="form-control w-24">
              <label class="label py-0">
                <span class="label-text text-xs">Cantidad</span>
              </label>
              <input
                type="number"
                v-model.number="newDetail.quantity"
                min="1"
                class="input input-bordered input-sm w-full"
              />
            </div>
            <div class="form-control w-28">
              <label class="label py-0">
                <span class="label-text text-xs">Unidad</span>
              </label>
              <input
                type="number"
                v-model.number="newDetail.unit"
                min="0"
                step="0.01"
                class="input input-bordered input-sm w-full"
              />
            </div>
            <button
              type="button"
              class="btn btn-sm btn-primary"
              @click="addManualDetail"
              :disabled="!newDetail.description.trim()"
            >
              <i class="las la-plus"></i>
              Agregar
            </button>
          </div>
        </div>

        <!-- Tabla de ítems agregados -->
        <div class="overflow-x-auto">
          <table class="table table-sm table-zebra w-full">
            <thead>
              <tr class="bg-teal-600 text-white">
                <th class="border border-gray-300 w-10 text-center">#</th>
                <th class="border border-gray-300">Descripción</th>
                <th class="border border-gray-300 w-24 text-center">Cantidad</th>
                <th class="border border-gray-300 w-28 text-right">Unidad</th>
                <th class="border border-gray-300 w-20 text-center">Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(detail, index) in details" :key="index" class="hover:bg-yellow-50">
                <td class="border border-gray-300 text-center">{{ index + 1 }}</td>
                <td class="border border-gray-300">
                  <input
                    type="text"
                    v-model="detail.description"
                    class="input input-bordered input-sm w-full"
                  />
                </td>
                <td class="border border-gray-300">
                  <input
                    type="number"
                    v-model.number="detail.quantity"
                    min="1"
                    class="input input-bordered input-sm w-full text-center"
                  />
                </td>
                <td class="border border-gray-300">
                  <input
                    type="number"
                    v-model.number="detail.unit"
                    min="0"
                    step="0.01"
                    class="input input-bordered input-sm w-full text-right"
                  />
                </td>
                <td class="border border-gray-300 text-center">
                  <button
                    type="button"
                    class="btn btn-xs btn-error"
                    @click="removeDetail(index)"
                    title="Eliminar ítem"
                  >
                    <i class="las la-trash"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="details.length === 0">
                <td colspan="5" class="text-center py-8 text-gray-500">
                  <i class="las la-inbox text-4xl"></i>
                  <p class="mt-2">No hay ítems agregados. Use los equipos del proyecto o agregue manualmente.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Notas -->
      <div class="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h6 class="font-semibold text-lg mb-4 text-gray-700 border-b pb-2">Observaciones</h6>

        <div class="form-control w-full">
          <textarea
            id="notes"
            v-model="guide.notes"
            rows="3"
            placeholder="Observaciones o notas adicionales..."
            class="textarea textarea-bordered w-full"
          ></textarea>
        </div>
      </div>

      <!-- Botones -->
      <div class="flex gap-3 justify-end mt-6">
        <button type="button" class="btn btn-outline" @click="cancelForm" :disabled="isLoading">
          <i class="las la-times"></i>
          Cancelar
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="isLoading || isProjectClosed"
        >
          <i v-if="!isLoading" class="las la-save"></i>
          <i v-else class="las la-spinner animate-spin"></i>
          {{ isLoading ? 'Guardando...' : (isEditMode ? 'Actualizar Guía' : 'Guardar Guía') }}
        </button>
      </div>
    </form>
  </div>
</template>
