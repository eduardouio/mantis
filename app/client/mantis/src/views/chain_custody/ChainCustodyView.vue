<script setup>
import { ref } from 'vue'

// Datos de prueba
const cadenaCustodia = ref({
  numero: '0000123',
  fecha: '15/01/2024',
  horaInicio: '08:00',
  horaFin: '17:00',
  horas: 9.00,
  ubicacion: 'Bloque 31',
  tecnico: {
    nombre: 'Juan Pérez García',
    contacto: 'María López - Gerente de IT'
  },
  facturacion: {
    equipo: 'DÍAS',
    codigo: 3.00,
    precioUnitario: 950.00,
    totalLinea: 2850.00
  },
  detalle: 'Mantenimiento preventivo y correctivo de equipos de cómputo en área administrativa'
})

const recursos = ref([
  {
    id: 1,
    tipo: 'Material',
    descripcion: 'Cable de red Cat6 (10m)',
    cantidad: 5,
    unidad: 'und',
    precioUnitario: 25.00,
    total: 125.00
  },
  {
    id: 2,
    tipo: 'Herramienta',
    descripcion: 'Kit de destornilladores',
    cantidad: 1,
    unidad: 'und',
    precioUnitario: 0.00,
    total: 0.00
  },
  {
    id: 3,
    tipo: 'Material',
    descripcion: 'Pasta térmica premium',
    cantidad: 2,
    unidad: 'tubo',
    precioUnitario: 45.00,
    total: 90.00
  },
  {
    id: 4,
    tipo: 'Repuesto',
    descripcion: 'Memoria RAM DDR4 8GB',
    cantidad: 3,
    unidad: 'und',
    precioUnitario: 180.00,
    total: 540.00
  }
])
</script>

<template>
  <div class="w-[95%] mx-auto p-6">
    <!-- Header -->
    <div class="bg-white rounded-lg shadow-md p-2 mb-2 border border-gray-200">
      <div class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-gray-800 flex items-center gap-2">
          <i class="las la-file-invoice text-blue-500"></i>
          #12 TORRES ULLOA VIVIANA - ORELLANA IV
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
        <div class="bg-gradient-to-r from-blue-500 to-sky-600 text-white p-4 rounded-t-lg backdrop-blur-sm">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h2 class="text-xl font-bold">Cadena de Custodia</h2>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <i class="las la-calendar text-yellow-300 mr-1"></i>
                  <span class="font-bold">Fecha:</span>
                  <span class="font-bold ml-1 text-gray-100">{{ cadenaCustodia.fecha }}</span>
                </div>
                <div>
                  <i class="las la-clock text-yellow-300 mr-1"></i>
                  <span class="font-bold">Inicio - Fin:</span>
                  <span class="font-bold ml-1 text-gray-100">{{ cadenaCustodia.horaInicio }} - {{ cadenaCustodia.horaFin }}</span>
                </div>
                <div>
                  <i class="las la-hourglass text-yellow-300 mr-1"></i>
                  <span class="font-bold">Horas:</span>
                  <span class="font-bold ml-1 text-gray-100">{{ cadenaCustodia.horas.toFixed(2) }}</span>
                </div>
                <div>
                  <i class="las la-map-marker text-yellow-300 mr-1"></i>
                  <span class="font-bold">Ubicación:</span>
                  <span class="font-bold ml-1 text-gray-100">{{ cadenaCustodia.ubicacion }}</span>
                </div>
              </div>
            </div>
            <div class="text-right">
              <div class=" text-2xl p1 rounded text-error bg-gray-100 w-100% font-mono border border-sky-600 border-2">
                <span class="text-gray-700 ms-5">Nro.</span>
                <span class="me-2">
                  {{ cadenaCustodia.numero }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Información del Técnico -->
        <div class="p-4 border-b">
          <div class="flex items-center gap-2 text-sm text-gray-600">
            <i class="las la-user text-blue-500 text-lg"></i>
            <span class="font-semibold">Técnico:</span>
            <span class="badge badge-outline">{{ cadenaCustodia.tecnico.nombre }}</span>
            <span class="text-gray-500 ml-4">Contacto:</span>
            <span>{{ cadenaCustodia.tecnico.contacto }}</span>
          </div>
        </div>

        
<!-- Información de Facturación (Maestro) -->
<div class="p-4 border-b">
  <h3 class="font-semibold text-gray-700 mb-3">Información de Facturación</h3>
  <div class="overflow-x-auto">
    <table class="table table-sm w-full">
      <thead>
        <tr class="bg-gray-100">
          <th class="text-left">Equipo</th>
          <th class="text-left">Código</th>
          <th class="text-right">Precio Unitario</th>
          <th class="text-right">Total Línea</th>
        </tr>
      </thead>
      <tbody>
        <tr class="hover:bg-gray-50">
          <td class="font-semibold">{{ cadenaCustodia.facturacion.equipo }}</td>
          <td>{{ cadenaCustodia.facturacion.codigo.toFixed(2) }}</td>
          <td class="text-right">${{ cadenaCustodia.facturacion.precioUnitario.toFixed(2) }}</td>
          <td class="text-right font-semibold">${{ cadenaCustodia.facturacion.totalLinea.toFixed(2) }}</td>
        </tr>
      </tbody>
      <tfoot>
        <tr class="bg-gray-50">
          <td colspan="4" class="text-sm text-gray-600">
            <i class="las la-comment-alt"></i>
            <span>{{ cadenaCustodia.detalle }}</span>
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</div>


        <!-- Footer -->
        <div class="bg-gray-50 p-4 rounded-b-lg flex justify-between gap-2">
          <button class="btn btn-sm btn-primary">
            <i class="las la-arrow-left"></i>
            Cancelar
          </button>
          <div class="flex gap-2">
            <button class="btn btn-sm btn-primary">
              <i class="las la-edit"></i>
              Editar
            </button>
            <button class="btn btn-sm btn-primary">
              <i class="las la-print"></i>
              Imprimir
            </button>
           <button class="btn btn-sm bg-red-600 text-white">
            <i class="las la-times-circle"></i>
            Anular
          </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>