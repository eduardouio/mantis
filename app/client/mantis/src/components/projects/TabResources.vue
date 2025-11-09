<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-tools text-blue-600 text-xl"></i>
        Equipos Asignados
      </h2>
      <button class="btn btn-primary btn-sm">
        <i class="las la-plus text-lg"></i>
        Asignar Equipo
      </button>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-base-200">
            <th>#</th>
            <th>Tipo</th>
            <th>Código</th>
            <th>Nombre</th>
            <th>Estado</th>
            <th class="text-right">Costo Renta</th>
            <th class="text-right">Costo Mant.</th>
            <th>Frecuencia (días)</th>
            <th>Fecha Inicio</th>
            <th>Fecha Fin</th>
            <th class="text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colspan="11" class="text-center text-gray-500 py-8">
              <i class="las la-inbox text-4xl"></i>
              <p>No hay equipos asignados a este proyecto</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
