<script setup>
import { defineProps, defineEmits, computed } from 'vue'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'

const props = defineProps({
  resource: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])
const projectResourceStore = UseProjectResourceStore()

// Detectar si el recurso ya venía retirado desde el origen
const wasInitiallyRetired = computed(() => {
  return props.resource?.is_retired === true && props.resource?.retirement_date !== null
})

const submitForm = async () => {
  try {
    // Validación adicional para campos de retiro
    if (props.resource.is_retired) {
      if (!props.resource.retirement_date) {
        alert('La fecha de retiro es obligatoria cuando se marca para retiro');
        return;
      }
      if (!props.resource.retirement_reason || props.resource.retirement_reason.trim() === '') {
        alert('El motivo de retiro es obligatorio cuando se marca para retiro');
        return;
      }
    }

    if (props.resource) {
      await projectResourceStore.updateResourceProject(props.resource)
      console.log('Recurso actualizado exitosamente')
    } else {
      console.log('Crear nuevo recurso:', props.resource)
    }
    emit('close')
  } catch (error) {
    console.error('Error al guardar el recurso:', error)
  }
}

const cancelForm = () => {
  emit('close')
}
</script>

<template>
    <div class="max-w-2xl mx-auto p-1">
        <h5 class="text-xl font-bold mb-6">
          {{ resource.detailed_description  }}
        </h5>
        
        <!-- Detalles del Registro -->
        <div class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
            <h6 class="font-semibold text-lg mb-3">Detalles del Recurso</h6>
            
            <div class="grid grid-cols-2 gap-3 text-sm border p-2 rounded border-gray-300 bg-base-100">
                <div class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">ID:</span>
                    <span class="ml-2">{{ resource.id }}</span>
                </div>
                <div class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Proyecto ID:</span>
                    <span class="ml-2">{{ resource.project_id }}</span>
                </div>
                <div class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Tipo:</span>
                    <span class="ml-2">{{ resource.type }}</span>
                </div>
                <div class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Código:</span>
                    <span class="ml-2">{{ resource.resource_item_code }}</span>
                </div>
                <div class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Costo Actual:</span>
                    <span class="ml-2">${{ resource.cost }}</span>
                </div>
                <div class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Nombre:</span>
                    <span class="ml-2">{{ resource.resource_item_name }}</span>
                </div>
                <div class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Descripción:</span>
                    <span class="ml-2">{{ resource.detailed_description }}</span>
                </div>
                <div v-if="resource.interval_days" class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Frecuencia (días):</span>
                    <span class="ml-2">{{ resource.interval_days }}</span>
                </div>
                <div class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Fecha Inicio Operación:</span>
                    <span class="ml-2">{{ resource.operation_start_date }}</span>
                </div>
                <div class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Retirado:</span>
                    <span class="ml-2 badge" :class="resource.is_retired ? 'badge-warning' : 'badge-ghost'">
                        {{ resource.is_retired ? 'Sí' : 'No' }}
                    </span>
                </div>
                <div v-if="resource.is_retired" class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Fecha Retiro:</span>
                    <span class="ml-2">{{ resource.retirement_date }}</span>
                </div>
                <div v-if="resource.is_retired" class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Motivo Retiro:</span>
                    <span class="ml-2">{{ resource.retirement_reason }}</span>
                </div>
                <div v-if="resource.notes" class="border-b-1 border-r-1 border-sky-200">
                    <span class="font-medium">Notas:</span>
                    <span class="ml-2">{{ resource.notes }}</span>
                </div>
            </div>
        </div>

        <!-- Mensaje informativo si ya estaba retirado -->
        <div v-if="wasInitiallyRetired" class="space-y-4">
            <div class="alert alert-warning">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>Este recurso ya fue retirado del proyecto y no puede ser modificado.</span>
            </div>
            
            <div class="flex justify-end">
                <button type="button" class="btn btn-outline" @click="cancelForm">
                    Cerrar
                </button>
            </div>
        </div>

        <!-- Formulario solo si NO está retirado -->
        <form v-else @submit.prevent="submitForm" class="space-y-4">
            <!-- Costo -->
            <div class="form-control w-full">
                <label class="label" for="cost">
                    <span class="label-text font-medium">Costo *</span>
                </label>
                <input 
                    type="number" 
                    id="cost" 
                    v-model="resource.cost"
                    step="0.01"
                    min="0"
                    required
                    placeholder="0.00"
                    class="input input-bordered w-full"
                />
            </div>

            <!-- Frecuencia en días -->
            <div class="form-control w-full" v-if="resource.type === 'SERVIC'">
                <label class="label" for="interval_days">
                    <span class="label-text font-medium">Frecuencia (días) *</span>
                </label>
                <input 
                    type="number" 
                    id="interval_days" 
                    v-model="resource.interval_days"
                    min="1"
                    required
                    placeholder="1"
                    class="input input-bordered w-full"
                />
            </div>

            <!-- Fecha de Inicio de Operaciones -->
            <div class="form-control w-full">
                <label class="label" for="operation_start_date">
                    <span class="label-text font-medium">Fecha de Inicio Operaciones *</span>
                </label>
                <input 
                    type="date" 
                    id="operation_start_date" 
                    v-model="resource.operation_start_date"
                    required
                    class="input input-bordered w-full"
                />
            </div>

            <!-- Retirado -->
            <div class="form-control">
                <label class="label cursor-pointer justify-start gap-3">
                    <input 
                        type="checkbox" 
                        v-model="resource.is_retired"
                        class="checkbox"
                    />
                    <span class="label-text font-medium">Retirar de Proyecto</span>
                </label>
            </div>

            <!-- Fecha de Retiro (solo si está retirado) -->
            <div class="form-control w-full" v-if="resource.is_retired">
                <label class="label" for="retirement_date">
                    <span class="label-text font-medium">Fecha de Retiro *</span>
                </label>
                <input 
                    type="date" 
                    id="retirement_date" 
                    v-model="resource.retirement_date"
                    :required="resource.is_retired"
                    class="input input-bordered w-full border-red-500"
                />
            </div>

            <!-- Motivo de Retiro (solo si está retirado) -->
            <div class="form-control w-full" v-if="resource.is_retired">
                <label class="label" for="retirement_reason">
                    <span class="label-text font-medium">Motivo de Retiro *</span>
                </label>
                <textarea 
                    id="retirement_reason" 
                    v-model="resource.retirement_reason"
                    rows="3"
                    placeholder="Describe el motivo del retiro..."
                    :required="resource.is_retired"
                    class="textarea textarea-bordered w-full border-red-500"
                ></textarea>
            </div>

            <!-- Botones -->
            <div class="flex gap-3 justify-end mt-6">
                <button type="button" class="btn btn-outline" @click="cancelForm">
                    Cancelar
                </button>
                <button type="submit" class="btn btn-primary">
                    {{ resource ? 'Actualizar' : 'Guardar' }} Recurso
                </button>
            </div>
        </form>
    </div>
</template>