<script setup>
// La lógica será manejada por el componente padre o un composable
</script>

<template>
  <div class="w-[95%] mx-auto p-6">
    <!-- Header -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <i class="las la-file-invoice text-blue-500"></i>
          Cadena de Custodia de Proyecto
        </h1>
        <div class="flex gap-2">
          <button class="btn btn-secondary btn-sm">
            <i class="las la-arrow-left"></i>
            Cancelar
          </button>
          <button class="btn btn-primary btn-sm">
            <i class="las la-plus"></i>
            Nueva Cadena de Custodia
          </button>
        </div>
      </div>  
    </div>

    <!-- Lista de Cadenas de Custodia -->
    <div class="grid grid-cols-1 gap-4">
      <!-- Cadena de Custodia Card (Maestro) -->
      <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
        <!-- Cabecera de la Cadena -->
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-t-lg">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <span class="badge badge-primary badge-sm">000001</span>
                <h2 class="text-xl font-bold">Cadena de Custodia</h2>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <i class="las la-calendar text-yellow-300 mr-1"></i>
                  <span class="opacity-90">Fecha:</span>
                  <span class="font-semibold ml-1">--/--/--</span>
                </div>
                <div>
                  <i class="las la-clock text-yellow-300 mr-1"></i>
                  <span class="opacity-90">Inicio - Fin:</span>
                  <span class="font-semibold ml-1">-- - --</span>
                </div>
                <div>
                  <i class="las la-hourglass text-yellow-300 mr-1"></i>
                  <span class="opacity-90">Horas:</span>
                  <span class="font-semibold ml-1">0.00</span>
                </div>
                <div>
                  <i class="las la-map-marker text-yellow-300 mr-1"></i>
                  <span class="opacity-90">Ubicación:</span>
                  <span class="font-semibold ml-1">--</span>
                </div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-xs opacity-80">Total Cadena</div>
              <div class="text-2xl font-bold">$0.00</div>
            </div>
          </div>
        </div>

        <!-- Información del Técnico -->
        <div class="p-4 border-b">
          <div class="flex items-center gap-2 text-sm text-gray-600">
            <i class="las la-user text-blue-500 text-lg"></i>
            <span class="font-semibold">Técnico:</span>
            <span class="badge badge-outline">Nombre Técnico</span>
            <span class="text-gray-500 ml-4">Contacto:</span>
            <span>Nombre de Contacto - Cargo</span>
          </div>
        </div>

        <!-- Volúmenes -->
        <div class="p-4 border-b">
          <h3 class="font-semibold text-gray-700 mb-3">Volúmenes</h3>
          <div class="grid grid-cols-3 gap-2">
            <div class="bg-amber-50 rounded p-3 text-center">
              <i class="las la-flask text-amber-600 text-2xl"></i>
              <div class="text-xs text-gray-600 mt-1">Galones</div>
              <div class="font-bold text-amber-700 text-lg">0</div>
            </div>
            <div class="bg-purple-50 rounded p-3 text-center">
              <i class="las la-cube text-purple-600 text-2xl"></i>
              <div class="text-xs text-gray-600 mt-1">Barriles</div>
              <div class="font-bold text-purple-700 text-lg">0</div>
            </div>
            <div class="bg-cyan-50 rounded p-3 text-center">
              <i class="las la-boxes text-cyan-600 text-2xl"></i>
              <div class="text-xs text-gray-600 mt-1">M³</div>
              <div class="font-bold text-cyan-700 text-lg">0</div>
            </div>
          </div>
        </div>

        <!-- Información de Facturación (Maestro) -->
        <div class="p-4 border-b">
          <h3 class="font-semibold text-gray-700 mb-3">Información de Facturación</h3>
          <div class="bg-gray-50 rounded p-3">
            <div class="grid grid-cols-4 gap-3 text-xs">
              <div>
                <span class="text-gray-500">Unidad:</span>
                <span class="font-semibold block">DÍAS</span>
              </div>
              <div>
                <span class="text-gray-500">Cantidad:</span>
                <span class="font-semibold block">0.00</span>
              </div>
              <div>
                <span class="text-gray-500">Precio Unitario:</span>
                <span class="font-semibold block">$0.00</span>
              </div>
              <div>
                <span class="text-gray-500">Total Línea:</span>
                <span class="font-semibold block">$0.00</span>
              </div>
            </div>
            <div class="mt-2 pt-2 border-t text-xs text-gray-600">
              <i class="las la-comment-alt"></i>
              <span>Detalle de la cadena de custodia</span>
            </div>
          </div>
        </div>

        <!-- Detalles de Recursos (Detalle) -->
        <div class="p-4 border-b">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-700 flex items-center gap-2">
              <i class="las la-tools text-green-500"></i>
              Recursos Utilizados
              <span class="badge badge-sm badge-neutral">0</span>
            </h3>
          </div>

          <!-- Sin Recursos -->
          <div class="text-center py-6 text-gray-400">
            <i class="las la-inbox text-2xl"></i>
            <p class="mt-2 text-sm">No hay recursos asignados</p>
          </div>

          <!-- Lista de Recursos (ChainCustodyDetail) -->
          <div class="space-y-2">
            <div class="border rounded-lg p-3 hover:bg-gray-50 transition-colors">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="font-semibold text-gray-700 text-sm">
                    <i class="las la-wrench text-green-500 mr-1"></i>
                    CODIGO-RECURSO - Nombre del Recurso
                  </div>
                  <div class="text-xs text-gray-500 mt-1">
                    Código: CODIGO-RECURSO
                  </div>
                </div>
                <div class="text-right">
                  <button class="btn btn-xs btn-ghost">
                    <i class="las la-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Botón Agregar Recurso -->
          <div class="mt-3">
            <button class="btn btn-sm btn-outline btn-primary w-full">
              <i class="las la-plus"></i>
              Agregar Recurso
            </button>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 p-4 rounded-b-lg flex justify-between gap-2">
          <button class="btn btn-sm btn-ghost">
            <i class="las la-arrow-left"></i>
            Cancelar
          </button>
          <div class="flex gap-2">
            <button class="btn btn-sm btn-ghost">
              <i class="las la-edit"></i>
              Editar
            </button>
            <button class="btn btn-sm btn-ghost">
              <i class="las la-print"></i>
              Imprimir
            </button>
            <button class="btn btn-sm btn-ghost">
              <i class="las la-download"></i>
              Exportar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Sin resultados -->
    <div class="bg-white rounded-lg shadow-md p-12 text-center">
      <i class="las la-folder-open text-6xl text-gray-300"></i>
      <p class="text-gray-500 mt-4">No hay Cadenas de Custodia registradas</p>
      <div class="flex items-center gap-2 w-full justify-center mt-4">
        <button class="btn btn-secondary btn-sm">
          <i class="las la-arrow-left"></i>
          Cancelar
        </button>
        <button class="btn btn-primary btn-sm">
          <i class="las la-plus"></i>
          Crear Cadena de Custodia
        </button>
      </div>
    </div>
  </div>
</template>