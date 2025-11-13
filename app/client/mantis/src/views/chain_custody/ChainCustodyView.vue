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
    cargo: 'Conductor Técnico',
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
        "id": 21,
        "project_id": 2,
        "type": "SERVIC",
        "resource_item_id": 264,
        "resource_item_code": "PEISOL-SERV00",
        "resource_item_name": "Mantenimiento Y Limpieza General",
        "detailed_description": "MANTENIMIENTO PSL-BT-103",
        "cost": "35.00",
        "interval_days": 2,
        "operation_start_date": "2025-11-01",
        "is_active": true,
        "is_selected": false,
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null,
        "is_confirm_delete": false,
        "is_deleteable": true,
        "notes": null
    },
    {
        "id": 22,
        "project_id": 2,
        "type": "SERVIC",
        "resource_item_id": 264,
        "resource_item_code": "PEISOL-SERV00",
        "resource_item_name": "Mantenimiento Y Limpieza General",
        "detailed_description": "MANTENIMIENTO PSL-BT-108",
        "cost": "34.00",
        "interval_days": 3,
        "operation_start_date": "2025-11-01",
        "is_active": true,
        "is_selected": false,
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null,
        "is_confirm_delete": false,
        "is_deleteable": true,
        "notes": null
    },
    {
        "id": 23,
        "project_id": 2,
        "type": "SERVIC",
        "resource_item_id": 264,
        "resource_item_code": "PEISOL-SERV00",
        "resource_item_name": "Mantenimiento Y Limpieza General",
        "detailed_description": "MANTENIMIENTO PSL-BT-111",
        "cost": "35.00",
        "interval_days": 4,
        "operation_start_date": "2025-11-01",
        "is_active": true,
        "is_selected": false,
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null,
        "is_confirm_delete": false,
        "is_deleteable": true,
        "notes": null
    },
    {
        "id": 24,
        "project_id": 2,
        "type": "SERVIC",
        "resource_item_id": 264,
        "resource_item_code": "PEISOL-SERV00",
        "resource_item_name": "Mantenimiento Y Limpieza General",
        "detailed_description": "MANTENIMIENTO PSL-BT-114",
        "cost": "32.00",
        "interval_days": 3,
        "operation_start_date": "2025-11-01",
        "is_active": true,
        "is_selected": false,
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null,
        "is_confirm_delete": false,
        "is_deleteable": true,
        "notes": null
    },
    {
        "id": 25,
        "project_id": 2,
        "type": "SERVIC",
        "resource_item_id": 264,
        "resource_item_code": "PEISOL-SERV00",
        "resource_item_name": "Mantenimiento Y Limpieza General",
        "detailed_description": "MANTENIMIENTO PSL-BT-112",
        "cost": "31.00",
        "interval_days": 2,
        "operation_start_date": "2025-11-01",
        "is_active": true,
        "is_selected": false,
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null,
        "is_confirm_delete": false,
        "is_deleteable": true,
        "notes": null
    },
    {
        "id": 26,
        "project_id": 2,
        "type": "SERVIC",
        "resource_item_id": 264,
        "resource_item_code": "PEISOL-SERV00",
        "resource_item_name": "Mantenimiento Y Limpieza General",
        "detailed_description": "MANTENIMIENTO PSL-BT-115",
        "cost": "42.00",
        "interval_days": 3,
        "operation_start_date": "2025-11-01",
        "is_active": true,
        "is_selected": false,
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null,
        "is_confirm_delete": false,
        "is_deleteable": true,
        "notes": null
    },
    {
        "id": 27,
        "project_id": 2,
        "type": "SERVIC",
        "resource_item_id": 264,
        "resource_item_code": "PEISOL-SERV00",
        "resource_item_name": "Mantenimiento Y Limpieza General",
        "detailed_description": "MANTENIMIENTO PSL-BT-101",
        "cost": "41.00",
        "interval_days": 1,
        "operation_start_date": "2025-11-01",
        "is_active": true,
        "is_selected": false,
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null,
        "is_confirm_delete": false,
        "is_deleteable": true,
        "notes": null
    },
    {
        "id": 28,
        "project_id": 2,
        "type": "SERVIC",
        "resource_item_id": 264,
        "resource_item_code": "PEISOL-SERV00",
        "resource_item_name": "Mantenimiento Y Limpieza General",
        "detailed_description": "MANTENIMIENTO PSL-BT-116",
        "cost": "37.00",
        "interval_days": 5,
        "operation_start_date": "2025-11-01",
        "is_active": true,
        "is_selected": false,
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null,
        "is_confirm_delete": false,
        "is_deleteable": true,
        "notes": null
    },
    {
        "id": 29,
        "project_id": 2,
        "type": "SERVIC",
        "resource_item_id": 264,
        "resource_item_code": "PEISOL-SERV00",
        "resource_item_name": "Mantenimiento Y Limpieza General",
        "detailed_description": "MANTENIMIENTO PSL-BT-113",
        "cost": "36.00",
        "interval_days": 3,
        "operation_start_date": "2025-11-01",
        "is_active": true,
        "is_selected": false,
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null,
        "is_confirm_delete": false,
        "is_deleteable": true,
        "notes": null
    }
]
)
</script>

<template>
  <div class="w-[95%] mx-auto p-6">
    <!-- Header -->
    <div class="bg-white rounded-lg shadow-md p-2 mb-2 border border-gray-200">
      <div class="flex justify-between items-center">
        <h1 class="text-gray-800 flex items-center gap-2 font-semibold">
          <i class="las la-file-invoice text-blue-500"></i>
          Cadena de Custodia
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
                <h2 class="text-xl font-bold"> #12 TORRES ULLOA VIVIANA - ORELLANA IV</h2>
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

        <!-- Información General -->
        <div class="p-2">
          <div class="grid grid-cols-4 gap-4">
            <!-- Fecha -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Fecha:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">{{ cadenaCustodia.fecha }}</span>
            </div>
            <!-- Inicio - Fin -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Inicio - Fin:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ cadenaCustodia.horaInicio }} - {{ cadenaCustodia.horaFin }} 
                <span class="ml-2 me-2 text-gray-200">|</span>
                {{ cadenaCustodia.horas.toFixed(2) }} HRS
              </span>
            </div>
            <!-- Ubicación -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Ubicación:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">{{ cadenaCustodia.ubicacion }}</span>
            </div>
            <!-- Placa Vehículo -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Placa Vehiculo:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                PAE-2445
                <span class="ml-2 me-2 text-gray-200">|</span>
                Logística: 
                <span class="text-green-700 ml-2 me-2">SI</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Información del Técnico -->
        <div class="p-2 border-b bg-gray-50 border-b-gray-200">
          <div class="grid grid-cols-4 gap-4">
            <!-- Técnico -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Técnico:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ cadenaCustodia.tecnico.nombre }} 
                <span class="ml-2 me-2 text-gray-200">|</span>
                <span class="">CI: 1722919725</span></span>
            </div>
            <!-- Cargo -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Cargo:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">{{ cadenaCustodia.tecnico.cargo }}</span>
            </div>
            <!-- Contacto -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Contacto:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">
                {{ cadenaCustodia.tecnico.nombre }}
                 <span class="ml-2 me-2 text-gray-200">|</span> 
                 <span>CI: 1722919725</span></span>
            </div>
            <!-- Cargo Contacto -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 font-medium whitespace-nowrap w-28">Cargo Contacto:</span>
              <span class="text-sm text-gray-800 font-semibold border rounded p-1 border-gray-300 flex-1">Maquinista</span>
            </div>
          </div>
        </div>
        

        
<!-- Información de Facturación (Maestro) -->
<div class="p-4 border-b border-b-gray-200">
  <h3 class="font-semibold text-gray-700 mb-3">Detalle de Cadena de Custodia</h3>
  <div class="overflow-x-auto">
    <table class="table table-sm w-full table-zebra">
      <thead>
        <tr class="bg-gray-500 text-white text-center">
          <th class="border border-gray-300 w-10">#</th>
          <th class="border border-gray-300">Equipo</th>
          <th class="border border-gray-300 w-30">Precio</th>
          <th class="border border-gray-300 w-30">Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr class="hover:bg-yellow-100" v-for="(recurso, index) in recursos" :key="recurso.id">
          <td class="border border-gray-300">{{ index + 1 }}</td>
          <td class="border border-gray-300">{{ recurso.detailed_description }}</td>
          <td class="border border-gray-300 text-end">{{ recurso.cost }}</td>
          <td class="border border-gray-300 text-end">
            quitar
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="pt-2 pb-2">
    <div class="flex gap-4">
      <div class="flex gap-4">
        <div class="p-3 border rounded border-gray-200">
          Galones:
          <span class="text-xl text-primary ml-5">20</span>
        </div>
        <div class="p-3 border rounded border-gray-200">
          Metro Cubicos:
          <span class="text-xl text-primary ml-5">5</span>
        </div>
        <div class="p-3 border rounded border-gray-200">
          Barriles:
          <span class="text-xl text-primary ml-5">2</span>
        </div>
      </div>
      <div class="flex-1 border rounded p-3 border-gray-200">
        <span class="font-semibold">Notas:</span>
        <span class="text-primary ml-5">{{ cadenaCustodia.detalle  }}</span>
      </div>
    </div>
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