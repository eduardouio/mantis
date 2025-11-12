<script setup>
import { defineProps, defineEmits } from 'vue'
import { UseProjectResourceStore } from '@/stores/ProjectResourceStore'

const props = defineProps({
  resource: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])
const projectResourceStore = UseProjectResourceStore()

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
    <div class="max-w-2xl mx-auto p-6">
        <h5 class="text-xl font-bold mb-6">
          {{ resource.detailed_description  }}
        </h5>
        
        <form @submit.prevent="submitForm" class="space-y-4">
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
            <div class="form-control w-full">
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