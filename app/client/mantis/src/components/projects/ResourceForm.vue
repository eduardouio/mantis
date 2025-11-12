<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'

const props = defineProps({
  resource: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])
const projectResourceStore = UseProjectResourceStore()

const form = ref({
  cost: 0,
  interval_days: 1,
  operation_start_date: '',
  is_retired: false,
  retirement_date: '',
  retirement_reason: ''
})

// Cargar datos del recurso si está en modo edición
watch(() => props.resource, (newResource) => {
  if (newResource) {
    form.value = {
      cost: newResource.cost || 0,
      interval_days: newResource.interval_days || 1,
      operation_start_date: newResource.operation_start_date || '',
      is_retired: newResource.is_retired || false,
      retirement_date: newResource.retirement_date || '',
      retirement_reason: newResource.retirement_reason || ''
    }
  }
}, { immediate: true })

const submitForm = async () => {
  try {
    if (props.resource) {
      // Modo edición
      await projectResourceStore.updateResourceProject(props.resource.id, form.value)
      console.log('Recurso actualizado exitosamente')
    } else {
      // Modo creación (si fuera necesario)
      console.log('Crear nuevo recurso:', form.value)
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
    <div class="max-w-2xl mx-auto p-6">
        <h2 class="text-2xl font-bold mb-6">
          {{ resource ? 'Editar Recurso del Proyecto' : 'Formulario de Recurso del Proyecto' }}
        </h2>
        
        <form @submit.prevent="submitForm" class="space-y-4">
            <!-- Costo -->
            <div class="form-control w-full">
                <label class="label" for="cost">
                    <span class="label-text font-medium">Costo *</span>
                </label>
                <input 
                    type="number" 
                    id="cost" 
                    v-model="form.cost"
                    step="0.01"
                    min="0"
                    required
                    placeholder="0.00"
                    class="input input-bordered w-full"
                />
            </div>

            <!-- Frecuencia en días -->
            <div class="form-control w-full">
                <label class="label" for="interval_days">
                    <span class="label-text font-medium">Frecuencia (días) *</span>
                </label>
                <input 
                    type="number" 
                    id="interval_days" 
                    v-model="form.interval_days"
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
                    v-model="form.operation_start_date"
                    required
                    class="input input-bordered w-full"
                />
            </div>

            <!-- Retirado -->
            <div class="form-control">
                <label class="label cursor-pointer justify-start gap-3">
                    <input 
                        type="checkbox" 
                        v-model="form.is_retired"
                        class="checkbox"
                    />
                    <span class="label-text font-medium">Retirar de Proyecto</span>
                </label>
            </div>

            <!-- Fecha de Retiro (solo si está retirado) -->
            <div class="form-control w-full" v-if="form.is_retired">
                <label class="label" for="retirement_date">
                    <span class="label-text font-medium">Fecha de Retiro</span>
                </label>
                <input 
                    type="date" 
                    id="retirement_date" 
                    v-model="form.retirement_date"
                    class="input input-bordered w-full"
                />
            </div>

            <!-- Motivo de Retiro (solo si está retirado) -->
            <div class="form-control w-full" v-if="form.is_retired">
                <label class="label" for="retirement_reason">
                    <span class="label-text font-medium">Motivo de Retiro</span>
                </label>
                <textarea 
                    id="retirement_reason" 
                    v-model="form.retirement_reason"
                    rows="3"
                    placeholder="Describe el motivo del retiro..."
                    class="textarea textarea-bordered w-full"
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