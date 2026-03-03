<script setup>
import { ref, computed, watch } from 'vue'
import { UseCalendarEventStore } from '@/stores/CalendarEventStore'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'
import { appConfig } from '@/AppConfig'
import { storeToRefs } from 'pinia'

const props = defineProps({
  event: { type: Object, default: null },
  defaultDate: { type: String, default: null },
})

const emit = defineEmits(['saved', 'close'])

const calendarEventStore = UseCalendarEventStore()
const projectResourceStore = UseProjectResourceStore()
const { resourcesProject } = storeToRefs(projectResourceStore)

const saving = ref(false)
const errorMessage = ref(null)
const technicals = ref([])

// Formulario
const form = ref({
  title: '',
  description: '',
  event_type: 'MAINTENANCE',
  priority: 'MEDIUM',
  start_date: '',
  end_date: '',
  start_time: '',
  end_time: '',
  responsible_technical_id: '',
  color: '#3B82F6',
  notes: '',
  details: [],
})

const isEditing = computed(() => !!props.event)

const eventTypes = [
  { value: 'MAINTENANCE', label: 'Mantenimiento' },
  { value: 'INSTALLATION', label: 'Instalación' },
  { value: 'REMOVAL', label: 'Retiro' },
  { value: 'INSPECTION', label: 'Inspección' },
  { value: 'OTHER', label: 'Otro' },
]

const priorities = [
  { value: 'LOW', label: 'Baja' },
  { value: 'MEDIUM', label: 'Media' },
  { value: 'HIGH', label: 'Alta' },
  { value: 'URGENT', label: 'Urgente' },
]

const statuses = [
  { value: 'SCHEDULED', label: 'Programado' },
  { value: 'IN_PROGRESS', label: 'En Progreso' },
  { value: 'COMPLETED', label: 'Completado' },
  { value: 'CANCELLED', label: 'Cancelado' },
]

// Cargar técnicos disponibles
const fetchTechnicals = async () => {
  try {
    const response = await fetch(appConfig.URLTechnicalsAvailable, {
      method: 'GET',
      headers: appConfig.headers,
    })
    if (response.ok) {
      const data = await response.json()
      technicals.value = data.data || []
    }
  } catch (error) {
    console.error('Error fetching technicals:', error)
  }
}

// Inicializar formulario
watch(() => props.event, (newEvent) => {
  if (newEvent) {
    form.value = {
      title: newEvent.title || '',
      description: newEvent.description || '',
      event_type: newEvent.event_type || 'MAINTENANCE',
      priority: newEvent.priority || 'MEDIUM',
      status: newEvent.status || 'SCHEDULED',
      start_date: newEvent.start_date || '',
      end_date: newEvent.end_date || '',
      start_time: newEvent.start_time || '',
      end_time: newEvent.end_time || '',
      responsible_technical_id: newEvent.responsible_technical_id || '',
      color: newEvent.color || '#3B82F6',
      notes: newEvent.notes || '',
      details: newEvent.details || [],
    }
  } else {
    form.value.start_date = props.defaultDate || ''
    form.value.end_date = props.defaultDate || ''
  }
}, { immediate: true })

// Agregar detalle
const addDetail = () => {
  form.value.details.push({
    resource_item_id: '',
    project_resource_item_id: '',
    description: '',
    cost: 0,
  })
}

// Eliminar detalle
const removeDetail = (index) => {
  form.value.details.splice(index, 1)
}

// Guardar
const handleSubmit = async () => {
  saving.value = true
  errorMessage.value = null

  try {
    const payload = {
      ...form.value,
      project_id: appConfig.idProject,
      responsible_technical_id: form.value.responsible_technical_id || null,
    }

    // Limpiar detalles vacíos
    payload.details = payload.details.filter(d => d.resource_item_id)

    let result
    if (isEditing.value) {
      payload.id = props.event.id
      result = await calendarEventStore.updateEvent(payload)
    } else {
      result = await calendarEventStore.createEvent(payload)
    }

    emit('saved', result)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    saving.value = false
  }
}

fetchTechnicals()
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <!-- Error -->
    <div v-if="errorMessage" class="alert alert-error text-sm">
      <i class="las la-exclamation-circle"></i>
      <span>{{ errorMessage }}</span>
    </div>

    <!-- Título y Tipo -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div class="form-control">
        <label class="label"><span class="label-text font-semibold">Título *</span></label>
        <input
          v-model="form.title"
          type="text"
          class="input input-bordered input-sm"
          placeholder="Nombre del evento"
          required
        />
      </div>
      <div class="form-control">
        <label class="label"><span class="label-text font-semibold">Tipo de Evento</span></label>
        <select v-model="form.event_type" class="select select-bordered select-sm">
          <option v-for="t in eventTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
        </select>
      </div>
    </div>

    <!-- Prioridad, Estado y Color -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <div class="form-control">
        <label class="label"><span class="label-text font-semibold">Prioridad</span></label>
        <select v-model="form.priority" class="select select-bordered select-sm">
          <option v-for="p in priorities" :key="p.value" :value="p.value">{{ p.label }}</option>
        </select>
      </div>
      <div v-if="isEditing" class="form-control">
        <label class="label"><span class="label-text font-semibold">Estado</span></label>
        <select v-model="form.status" class="select select-bordered select-sm">
          <option v-for="s in statuses" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
      </div>
      <div class="form-control">
        <label class="label"><span class="label-text font-semibold">Color</span></label>
        <input v-model="form.color" type="color" class="input input-bordered input-sm h-8 w-full" />
      </div>
    </div>

    <!-- Fechas -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div class="form-control">
        <label class="label"><span class="label-text font-semibold">Fecha Inicio *</span></label>
        <input v-model="form.start_date" type="date" class="input input-bordered input-sm" required />
      </div>
      <div class="form-control">
        <label class="label"><span class="label-text font-semibold">Fecha Fin</span></label>
        <input v-model="form.end_date" type="date" class="input input-bordered input-sm" />
      </div>
      <div class="form-control">
        <label class="label"><span class="label-text font-semibold">Hora Inicio</span></label>
        <input v-model="form.start_time" type="time" class="input input-bordered input-sm" />
      </div>
      <div class="form-control">
        <label class="label"><span class="label-text font-semibold">Hora Fin</span></label>
        <input v-model="form.end_time" type="time" class="input input-bordered input-sm" />
      </div>
    </div>

    <!-- Técnico Responsable -->
    <div class="form-control">
      <label class="label"><span class="label-text font-semibold">Técnico Responsable</span></label>
      <select v-model="form.responsible_technical_id" class="select select-bordered select-sm">
        <option value="">-- Sin asignar --</option>
        <option v-for="tech in technicals" :key="tech.id" :value="tech.id">
          {{ tech.first_name }} {{ tech.last_name }}
        </option>
      </select>
    </div>

    <!-- Descripción -->
    <div class="form-control">
      <label class="label"><span class="label-text font-semibold">Descripción</span></label>
      <textarea
        v-model="form.description"
        class="textarea textarea-bordered textarea-sm"
        rows="2"
        placeholder="Descripción del evento..."
      ></textarea>
    </div>

    <!-- Detalles (Recursos) -->
    <div class="border rounded-lg p-3 bg-gray-50">
      <div class="flex items-center justify-between mb-2">
        <h4 class="font-semibold text-sm text-gray-700">Recursos / Equipos</h4>
        <button type="button" @click="addDetail" class="btn btn-xs btn-primary">
          <i class="las la-plus"></i> Agregar
        </button>
      </div>

      <div v-if="form.details.length === 0" class="text-xs text-gray-500 text-center py-2">
        Sin recursos asignados. Click en "Agregar" para incluir equipos.
      </div>

      <div v-for="(detail, index) in form.details" :key="index" class="grid grid-cols-12 gap-2 mb-2 items-end">
        <div class="col-span-4">
          <label v-if="index === 0" class="label"><span class="label-text text-xs">Recurso</span></label>
          <select v-model="detail.resource_item_id" class="select select-bordered select-xs w-full">
            <option value="">-- Seleccionar --</option>
            <option v-for="r in resourcesProject" :key="r.resource_item_id" :value="r.resource_item_id">
              {{ r.resource_item_code }} - {{ r.resource_item_name }}
            </option>
          </select>
        </div>
        <div class="col-span-4">
          <label v-if="index === 0" class="label"><span class="label-text text-xs">Descripción</span></label>
          <input v-model="detail.description" type="text" class="input input-bordered input-xs w-full" placeholder="Actividad..." />
        </div>
        <div class="col-span-3">
          <label v-if="index === 0" class="label"><span class="label-text text-xs">Costo</span></label>
          <input v-model.number="detail.cost" type="number" step="0.01" min="0" class="input input-bordered input-xs w-full" />
        </div>
        <div class="col-span-1">
          <button type="button" @click="removeDetail(index)" class="btn btn-xs btn-circle btn-ghost text-error">
            <i class="las la-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Notas -->
    <div class="form-control">
      <label class="label"><span class="label-text font-semibold">Notas</span></label>
      <textarea
        v-model="form.notes"
        class="textarea textarea-bordered textarea-sm"
        rows="2"
        placeholder="Notas adicionales..."
      ></textarea>
    </div>

    <!-- Botones -->
    <div class="flex justify-end gap-2 pt-2 border-t">
      <button type="button" @click="$emit('close')" class="btn btn-sm btn-ghost">
        Cancelar
      </button>
      <button type="submit" class="btn btn-sm btn-primary" :disabled="saving">
        <span v-if="saving" class="loading loading-spinner loading-xs"></span>
        {{ isEditing ? 'Actualizar' : 'Crear' }} Evento
      </button>
    </div>
  </form>
</template>
