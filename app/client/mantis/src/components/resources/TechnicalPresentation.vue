<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({
  technical: {
    type: Object,
    default: null
  }
})

// Función auxiliar para formatear fechas
const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('es-ES')
}

// Determinar clase de badge según estado de certificado
const getCertificateBadgeClass = (issueDate, expiryDate) => {
  if (!expiryDate) return 'badge-ghost'
  
  const today = new Date()
  const expiry = new Date(expiryDate)
  const daysUntilExpiry = Math.floor((expiry - today) / (1000 * 60 * 60 * 24))
  
  if (daysUntilExpiry < 0) return 'badge-error'
  if (daysUntilExpiry <= 30) return 'badge-warning'
  return 'badge-success'
}

const getCertificateStatus = (expiryDate) => {
  if (!expiryDate) return 'Sin vencer'
  
  const today = new Date()
  const expiry = new Date(expiryDate)
  const daysUntilExpiry = Math.floor((expiry - today) / (1000 * 60 * 60 * 24))
  
  if (daysUntilExpiry < 0) return 'VENCIDO'
  if (daysUntilExpiry <= 30) return 'PRÓXIMO A VENCER'
  return 'VIGENTE'
}

// Agrupar vacunas por tipo
const groupedVaccinations = computed(() => {
  if (!props.technical?.vaccination_records) return {}
  
  return props.technical.vaccination_records.reduce((acc, vaccine) => {
    const type = vaccine.vaccine_type_display
    if (!acc[type]) acc[type] = []
    acc[type].push(vaccine)
    return acc
  }, {})
})
</script>

<template>
  <div v-if="technical" class="max-w-4xl mx-auto p-1">
    <!-- Encabezado -->
    <h5 class="text-xl font-bold mb-6">
      {{ technical.first_name }} {{ technical.last_name }}
    </h5>

    <!-- Datos Personales -->
    <div class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Datos Personales</h6>
      
      <div class="grid grid-cols-2 gap-3 text-sm border p-2 rounded border-gray-300 bg-base-100">
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">ID:</span>
          <span class="ml-2">{{ technical.id }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Nombre:</span>
          <span class="ml-2">{{ technical.first_name }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Apellido:</span>
          <span class="ml-2">{{ technical.last_name }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Cédula (DNI):</span>
          <span class="ml-2 font-mono">{{ technical.dni }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Email:</span>
          <span class="ml-2 text-blue-600">{{ technical.email }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Teléfono:</span>
          <span class="ml-2">{{ technical.nro_phone }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Fecha Nacimiento:</span>
          <span class="ml-2">{{ formatDate(technical.birth_date) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Fecha Ingreso:</span>
          <span class="ml-2">{{ formatDate(technical.date_joined) }}</span>
        </div>
      </div>
    </div>

    <!-- Información Laboral -->
    <div class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Información Laboral</h6>
      
      <div class="grid grid-cols-2 gap-3 text-sm border p-2 rounded border-gray-300 bg-base-100">
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Área de Trabajo:</span>
          <span class="ml-2">{{ technical.work_area_display }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Afiliado IESS:</span>
          <span class="ml-2 badge" :class="technical.is_iess_affiliated ? 'badge-success' : 'badge-ghost'">
            {{ technical.is_iess_affiliated ? 'Sí' : 'No' }}
          </span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Seguro de Vida:</span>
          <span class="ml-2 badge" :class="technical.has_life_insurance_policy ? 'badge-success' : 'badge-ghost'">
            {{ technical.has_life_insurance_policy ? 'Sí' : 'No' }}
          </span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Código QUEST NCST:</span>
          <span class="ml-2 font-mono text-xs">{{ technical.quest_ncst_code }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Instructor QUEST:</span>
          <span class="ml-2">{{ technical.quest_instructor }}</span>
        </div>
      </div>
    </div>

    <!-- Licencias y Certificados -->
    <div class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Licencias y Certificados</h6>
      
      <div class="grid grid-cols-2 gap-3 text-sm border p-2 rounded border-gray-300 bg-base-100">
        <!-- Licencia de Conducir -->
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Licencia (Expedida):</span>
          <span class="ml-2">{{ formatDate(technical.license_issue_date) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Licencia (Vence):</span>
          <span class="ml-2">
            <span class="badge" :class="getCertificateBadgeClass(technical.license_issue_date, technical.license_expiry_date)">
              {{ formatDate(technical.license_expiry_date) }}
            </span>
          </span>
        </div>

        <!-- Certificado Conducción Defensiva -->
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Cond. Defensiva (Expedida):</span>
          <span class="ml-2">{{ formatDate(technical.defensive_driving_certificate_issue_date) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Cond. Defensiva (Vence):</span>
          <span class="ml-2">
            <span class="badge" :class="getCertificateBadgeClass(technical.defensive_driving_certificate_issue_date, technical.defensive_driving_certificate_expiry_date)">
              {{ formatDate(technical.defensive_driving_certificate_expiry_date) }}
            </span>
          </span>
        </div>

        <!-- Certificado MAE -->
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Certificado MAE (Expedida):</span>
          <span class="ml-2">{{ formatDate(technical.mae_certificate_issue_date) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Certificado MAE (Vence):</span>
          <span class="ml-2">{{ formatDate(technical.mae_certificate_expiry_date) }}</span>
        </div>

        <!-- Certificado Médico -->
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Certificado Médico (Expedida):</span>
          <span class="ml-2">{{ formatDate(technical.medical_certificate_issue_date) }}</span>
        </div>
        <div class="border-b-1 border-r-1 border-sky-200">
          <span class="font-medium">Certificado Médico (Vence):</span>
          <span class="ml-2">{{ formatDate(technical.medical_certificate_expiry_date) }}</span>
        </div>
      </div>
    </div>

    <!-- Pases de Acceso -->
    <div v-if="technical.passes && technical.passes.length > 0" class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Pases de Acceso ({{ technical.passes.length }})</h6>
      
      <div class="overflow-x-auto border border-gray-300 rounded">
        <table class="table table-sm w-full">
          <thead class="bg-sky-100">
            <tr>
              <th class="border-r border-gray-300">Bloque</th>
              <th class="border-r border-gray-300">Vencimiento</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pass in technical.passes" :key="pass.id" class="hover">
              <td class="border-r border-gray-300">{{ pass.bloque_display || pass.bloque }}</td>
              <td class="border-r border-gray-300 font-mono text-sm">{{ formatDate(pass.fecha_caducidad) }}</td>
              <td>
                <span class="badge" :class="getCertificateBadgeClass(null, pass.fecha_caducidad)">
                  {{ getCertificateStatus(pass.fecha_caducidad) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Vacunas -->
    <div v-if="technical.vaccination_records && technical.vaccination_records.length > 0" class="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Registro de Vacunaciones ({{ technical.vaccination_records.length }})</h6>
      
      <div class="space-y-4">
        <div v-for="(vaccines, type) in groupedVaccinations" :key="type" class="border border-gray-300 rounded p-3 bg-base-100">
          <h7 class="font-semibold text-sm mb-2 text-blue-700">{{ type }}</h7>
          
          <div class="overflow-x-auto">
            <table class="table table-xs w-full">
              <thead class="bg-sky-50">
                <tr>
                  <th class="border-r border-gray-300">Dosis</th>
                  <th class="border-r border-gray-300">Fecha Aplicación</th>
                  <th class="border-r border-gray-300">Lote</th>
                  <th class="border-r border-gray-300">Próx. Dosis</th>
                  <th>Notas</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="vaccine in vaccines" :key="vaccine.id" class="hover:bg-sky-50">
                  <td class="border-r border-gray-300">{{ vaccine.dose_number }}</td>
                  <td class="border-r border-gray-300 font-mono text-xs">{{ formatDate(vaccine.application_date) }}</td>
                  <td class="border-r border-gray-300 font-mono text-xs">{{ vaccine.batch_number || 'N/A' }}</td>
                  <td class="border-r border-gray-300 font-mono text-xs">{{ formatDate(vaccine.next_dose_date) }}</td>
                  <td class="text-xs">{{ vaccine.notes || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Notas -->
    <div v-if="technical.notes" class="bg-sky-50 rounded-lg p-4 border-gray-200 border">
      <h6 class="font-semibold text-lg mb-3">Notas</h6>
      <p class="text-sm bg-base-100 p-3 rounded border border-gray-300">{{ technical.notes }}</p>
    </div>
  </div>
</template>
