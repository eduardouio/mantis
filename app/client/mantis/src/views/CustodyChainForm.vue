<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { UseCustodyChainStore } from '@/stores/CustoduChainStore'
import { UseProjectStore } from '@/stores/ProjectStore'
import { UseSheetProjectsStore } from '@/stores/SheetProjectsStore'
import { RouterLink } from 'vue-router'

const router = useRouter()
const custodyChainStore = UseCustodyChainStore()
const projectStore = UseProjectStore()
const sheetProjectsStore = UseSheetProjectsStore()

const newCustodyChain = ref(JSON.parse(JSON.stringify(custodyChainStore.newCustodyChain)))
newCustodyChain.value.location = projectStore.project.location
newCustodyChain.value.id_sheet_project = sheetProjectsStore.getLastActiveSheetProjectID()
newCustodyChain.value.issue_date = new Date().toISOString().split('T')[0]

const isSubmitting = ref(false)

const handleSubmit = async () => {
  isSubmitting.value = true
  try {
    const result = await custodyChainStore.addCustodyChain(newCustodyChain.value)
    if (result) {
      // Redirigir a la vista de la planilla después de guardar
      router.push({ 
        name: 'sheet-view', 
        params: { id: newCustodyChain.value.id_sheet_project } 
      })
    }
  } catch (error) {
    console.error('Error al guardar la cadena de custodia:', error)
    alert('Error al guardar la cadena de custodia')
  } finally {
    isSubmitting.value = false
  }
}
</script>
<template>
  <div class="container mx-auto mt-8 px-4">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-header bg-primary text-primary-content p-4">
        <h5 class="text-xl font-semibold">Formulario de Cadena de Custodia</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-control mb-4">
            <label for="sheet_project" class="label">
              <span class="label-text">ID Sheet Project</span>
            </label>
            <input
              type="number"
              class="input input-bordered w-full" 
              id="sheet_project"
              v-model="newCustodyChain.id_sheet_project"
              readonly
            />
          </div>

          <div class="form-control mb-4">
            <label for="location" class="label">
              <span class="label-text">Ubicación</span>
            </label>
            <input
              type="text"
              class="input input-bordered w-full"
              id="location"
              v-model="newCustodyChain.location"
              placeholder="Ingrese la ubicación"
            />
          </div>

          <div class="form-control mb-4">
            <label for="issue_date" class="label">
              <span class="label-text">Fecha</span>
            </label>
            <input
              type="date"
              class="input input-bordered w-full"
              id="issue_date"
              v-model="newCustodyChain.issue_date"
            />
          </div>

          <div class="flex gap-2">
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
              <i v-else class="las la-save"></i>
              {{ isSubmitting ? 'Guardando...' : 'Guardar' }}
            </button>
            <RouterLink :to="{ name: 'sheet-view', params: { id: newCustodyChain.id_sheet_project } }" class="btn btn-ghost">
              <i class="las la-times"></i>
              Cancelar
            </RouterLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>