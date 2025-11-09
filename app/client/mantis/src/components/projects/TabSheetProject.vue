<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-file-invoice-dollar text-blue-600 text-xl"></i>
        Planillas del Proyecto
      </h2>
      <button class="btn btn-primary btn-sm">
        <i class="las la-plus text-lg"></i>
        Crear Primera Planilla
      </button>
    </div>
    
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-base-200">
            <th>#</th>
            <th>Serie</th>
            <th>Estado</th>
            <th>Fecha Emisión</th>
            <th>Período Inicio</th>
            <th>Período Fin</th>
            <th>Tipo Servicio</th>
            <th class="text-right">Galones</th>
            <th class="text-right">Barriles</th>
            <th class="text-right">M³</th>
            <th class="text-right">Subtotal</th>
            <th class="text-right">IVA</th>
            <th class="text-right">Total</th>
            <th class="text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colspan="14" class="text-center text-gray-500 py-8">
              <i class="las la-inbox text-4xl"></i>
              <p>No hay planillas registradas para este proyecto</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
