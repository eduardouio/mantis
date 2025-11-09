<script setup>
  import { RouterLink } from 'vue-router';
</script>
<template>
  <div class="container mx-auto p-4 max-w-4xl">
    <span class="font-bold text-lg bg-gray-100 rounded-md px-2 py-1 mb-4 inline-block w-full text-center">
      Agregar Recurso al Proyecto
    </span>
    <form class="card bg-base-100 shadow-xl border border-gray-200 rounded-lg">
      <div class="card-body space-y-4">
        
        <!-- Descripción Detallada - Ancho completo -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text">Descripción</span>
          </label>
          <input 
            type="text" 
            id="detailed_description" 
            class="input input-bordered w-full" 
            placeholder="Descripción adicional del recurso en este proyecto" 
          />
        </div>

        <!-- Costo y Frecuencia - Grid 2 columnas -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Costo *</span>
            </label>
            <input
              id="cost"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Frecuencia de Mantenimiento (días) *</span>
            </label>
            <input
              id="interval_days"
              type="number"
              min="1"
              placeholder="1"
              class="input input-bordered w-full"
            />
          </div>
        </div>

        <!-- Fechas de Operación - Grid 2 columnas -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Fecha de Inicio de Operaciones *</span>
            </label>
            <input
              id="operation_start_date"
              type="date"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Fecha de Fin de Operaciones *</span>
            </label>
            <input
              id="operation_end_date"
              type="date"
              class="input input-bordered w-full"
            />
          </div>
        </div>

        <!-- Notas - Ancho completo -->
        <div class="form-control w-full">
          <label class="label">
            <span class="label-text">Notas</span>
          </label>
          <textarea
            id="notes"
            rows="3"
            placeholder="Notas adicionales sobre este recurso en el proyecto"
            class="textarea textarea-bordered w-full"
          />
        </div>

        <!-- Divisor visual -->
        <div class="divider"></div>

        <!-- Estado de Retiro -->
        <div class="form-control">
          <label class="label cursor-pointer justify-start gap-2">
            <input
              id="is_retired"
              type="checkbox"
              class="checkbox checkbox-warning"
            />
            <span class="label-text font-semibold">Recurso Retirado</span>
          </label>
        </div>

        <!-- Campos de Retiro (condicionales) -->
        <div class="bg-yellow-100 bg-opacity-10 p-6 rounded-lg border-l-4 border-yellow-400 space-y-4">
          <h3 class="font-semibold text-lg mb-4">Información de Retiro</h3>
          
          <div class="form-control w-full md:w-1/2">
            <label class="label">
              <span class="label-text">Fecha de Retiro *</span>
            </label>
            <input
              id="retirement_date"
              type="date"
              class="input input-bordered w-full"
            />
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Motivo de Retiro *</span>
            </label>
            <textarea
              id="retirement_reason"
              rows="4"
              placeholder="Describa el motivo del retiro del recurso"
              class="textarea textarea-bordered w-full"
            />
          </div>
        </div>

        <!-- Divisor final -->
        <div class="divider"></div>

        <!-- Botones de Acción -->
        <div class="flex flex-col-reverse sm:flex-row gap-3 sm:justify-end">
          <RouterLink to="/project" class="btn btn-ghost">
            Cancelar
          </RouterLink>
          <button type="submit" class="btn btn-primary">
            Agregar Recurso
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<style scoped>
/* Sin estilos personalizados - usando DaisyUI */
</style>