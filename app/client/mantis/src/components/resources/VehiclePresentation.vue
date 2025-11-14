<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({
  vehicle: {
    type: Object,
    default: null
  }
})

// Función auxiliar para formatear fechas
const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('es-ES')
}

// Determinar clase de badge según estado
const getStatusBadgeClass = (status) => {
  switch(status) {
    case 'DISPONIBLE':
      return 'badge-success'
    case 'VIGENTE':
      return 'badge-success'
    case 'VENCIDO':
      return 'badge-error'
    case 'PROXIMO_A_VENCER':
      return 'badge-warning'
    default:
      return 'badge-ghost'
  }
}

// Verificar si una fecha está próxima a vencer (dentro de 30 días)
const isExpiringSoon = (dueDate) => {
  if (!dueDate) return false
  const today = new Date()
  const due = new Date(dueDate)
  const daysUntilExpiry = Math.floor((due - today) / (1000 * 60 * 60 * 24))
  return daysUntilExpiry <= 30 && daysUntilExpiry > 0
}
</script>

<template>
  <div v-if="vehicle" class="max-w-4xl mx-auto p-1">
    <!-- Encabezado -->
    <h5 class="text-xl font-bold mb-6">
      {{ vehicle.brand }} {{ vehicle.model }}
    </h5>

    <!-- Estado General del Vehículo -->
    <div class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Estado del Vehículo</h6>
      
      <div class="grid grid-cols-2 gap-3 text-sm border p-2 rounded border-gray-300 bg-base-100">
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">ID:</span>
          <span class="ml-2">{{ vehicle.id }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Placa:</span>
          <span class="ml-2 font-mono">{{ vehicle.no_plate }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Marca:</span>
          <span class="ml-2">{{ vehicle.brand }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Modelo:</span>
          <span class="ml-2">{{ vehicle.model }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Tipo:</span>
          <span class="ml-2">{{ vehicle.type_vehicle }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Año:</span>
          <span class="ml-2">{{ vehicle.year }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Estado:</span>
          <span class="ml-2 badge" :class="getStatusBadgeClass(vehicle.status_vehicle)">
            {{ vehicle.status_vehicle }}
          </span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Número de Motor:</span>
          <span class="ml-2 font-mono text-xs">{{ vehicle.engine_number }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Número de Chasis:</span>
          <span class="ml-2 font-mono text-xs">{{ vehicle.chassis_number }}</span>
        </div>
      </div>
    </div>

    <!-- Documentos y Certificaciones -->
    <div class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Documentos y Certificaciones</h6>
      
      <div class="grid grid-cols-2 gap-3 text-sm border p-2 rounded border-gray-300 bg-base-100">
        <!-- Matrícula -->
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Matrícula (Fecha):</span>
          <span class="ml-2">{{ formatDate(vehicle.date_matricula) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Matrícula (Vence):</span>
          <span class="ml-2" :class="isExpiringSoon(vehicle.due_date_matricula) ? 'text-warning font-semibold' : ''">
            {{ formatDate(vehicle.due_date_matricula) }}
          </span>
        </div>

        <!-- Certificado Operacional -->
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Cert. Operacional:</span>
          <span class="ml-2 badge" :class="getStatusBadgeClass(vehicle.status_cert_oper)">
            {{ vehicle.status_cert_oper }}
          </span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Cert. Oper. (Vence):</span>
          <span class="ml-2" :class="isExpiringSoon(vehicle.due_date_cert_oper) ? 'text-warning font-semibold' : ''">
            {{ formatDate(vehicle.due_date_cert_oper) }}
          </span>
        </div>

        <!-- MTOP -->
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">MTOP (Fecha):</span>
          <span class="ml-2">{{ formatDate(vehicle.date_mtop) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">MTOP (Vence):</span>
          <span class="ml-2">{{ formatDate(vehicle.due_date_mtop) }}</span>
        </div>

        <!-- Revisión Técnica -->
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Revisión Técnica:</span>
          <span class="ml-2">{{ formatDate(vehicle.date_technical_review) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Rev. Técnica (Vence):</span>
          <span class="ml-2">{{ formatDate(vehicle.due_date_technical_review) }}</span>
        </div>

        <!-- Satélite -->
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Satélite (Fecha):</span>
          <span class="ml-2">{{ formatDate(vehicle.date_satellite) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Satélite (Vence):</span>
          <span class="ml-2" :class="isExpiringSoon(vehicle.due_date_satellite) ? 'text-warning font-semibold' : ''">
            {{ formatDate(vehicle.due_date_satellite) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Información de Seguros -->
    <div class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Seguro</h6>
      
      <div class="grid grid-cols-2 gap-3 text-sm border p-2 rounded border-gray-300 bg-base-100">
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Aseguradora:</span>
          <span class="ml-2">{{ vehicle.insurance_company }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Póliza Nro:</span>
          <span class="ml-2">{{ vehicle.nro_poliza || 'N/A' }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Fecha Expedición:</span>
          <span class="ml-2">{{ formatDate(vehicle.insurance_issue_date) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Vencimiento:</span>
          <span class="ml-2" :class="isExpiringSoon(vehicle.insurance_expiration_date) ? 'text-warning font-semibold' : ''">
            {{ formatDate(vehicle.insurance_expiration_date) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Notas -->
    <div v-if="vehicle.notes" class="bg-sky-50 rounded-lg p-4 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Notas</h6>
      <p class="text-sm bg-base-100 p-3 rounded border border-gray-300">{{ vehicle.notes }}</p>
    </div>
  </div>
</template>
