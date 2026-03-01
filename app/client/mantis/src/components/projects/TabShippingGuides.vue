<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UseProjectStore } from '@/stores/ProjectStore'
import { UseShippingGuideStore } from '@/stores/ShippingGuideStore'
import { appConfig } from '@/AppConfig'
import { useTableFilter } from '@/composables/useTableFilter'
import TableControls from '@/components/common/TableControls.vue'

const router = useRouter()
const projectStore = UseProjectStore()
const shippingGuideStore = UseShippingGuideStore()

const isProjectClosed = computed(() => projectStore.project?.is_closed === true)
const guides = computed(() => shippingGuideStore.shippingGuides || [])

// Tabla con filtrado, búsqueda y paginación
const tableFilter = useTableFilter(guides, {
  searchFields: ['guide_number', 'origin_place', 'destination_place', 'carrier_name', 'vehicle_plate'],
  pageSize: 10
})

onMounted(async () => {
  await shippingGuideStore.fetchGuidesByProject()
})

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Intl.DateTimeFormat('es-EC', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(new Date(date))
}

const openGuideForm = () => {
  router.push({ name: 'shipping-guide-form' })
}

const viewGuides = () => {
  router.push({ name: 'shipping-guide-list' })
}

const editGuide = (guide) => {
  router.push({ name: 'shipping-guide-form', params: { id: guide.id } })
}
</script>

<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center mb-4">
      <h2 class="font-semibold text-gray-800 flex items-center gap-2">
        <i class="las la-shipping-fast text-teal-600"></i>
        Guías de Remisión del Proyecto
      </h2>
      <div class="flex gap-2">
        <button
          v-if="guides.length > 0"
          @click="viewGuides"
          class="btn btn-outline btn-sm border-teal-500 text-teal-600"
        >
          <i class="las la-list"></i>
          Ver Todas
        </button>
        <button
          v-if="!isProjectClosed"
          @click="openGuideForm"
          class="btn btn-primary btn-sm bg-teal-600 border-teal-600 hover:bg-teal-700"
        >
          <i class="las la-plus"></i>
          Generar Guía
        </button>
        <div v-if="isProjectClosed" class="badge badge-error gap-1">
          <i class="las la-lock"></i> Proyecto Cerrado
        </div>
      </div>
    </div>

    <TableControls :tableFilter="tableFilter" position="top" searchPlaceholder="Buscar guía..." />

    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr class="bg-gray-500 text-white">
            <th class="p-2 border border-gray-100 text-center">Nro. Guía</th>
            <th class="p-2 border border-gray-100 text-center">Fecha Emisión</th>
            <th class="p-2 border border-gray-100 text-center">Origen</th>
            <th class="p-2 border border-gray-100 text-center">Destino</th>
            <th class="p-2 border border-gray-100 text-center">Transportista</th>
            <th class="p-2 border border-gray-100 text-center">Placa</th>
            <th class="p-2 border border-gray-100 text-center">Ítems</th>
            <th class="p-2 border border-gray-100 text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="guides.length === 0">
            <tr>
              <td colspan="8" class="text-center text-gray-500 py-8">
                <i class="las la-inbox text-4xl"></i>
                <p>No hay guías de remisión registradas para este proyecto</p>
                <button
                  v-if="!isProjectClosed"
                  @click="openGuideForm"
                  class="btn btn-primary btn-sm mt-3 bg-teal-600 border-teal-600"
                >
                  <i class="las la-plus"></i>
                  Crear Primera Guía
                </button>
              </td>
            </tr>
          </template>
          <template v-else-if="tableFilter.paginatedData.value.length === 0">
            <tr>
              <td colspan="8" class="text-center text-gray-500 py-8">
                <i class="las la-search text-4xl"></i>
                <p>No se encontraron resultados para "{{ tableFilter.searchQuery.value }}"</p>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="guide in tableFilter.paginatedData.value" :key="guide.id">
              <td class="p-2 border border-gray-300 font-mono font-bold text-center">
                {{ guide.guide_number }}
              </td>
              <td class="p-2 border border-gray-300 text-center">{{ formatDate(guide.issue_date) }}</td>
              <td class="p-2 border border-gray-300">{{ guide.origin_place || 'N/A' }}</td>
              <td class="p-2 border border-gray-300">{{ guide.destination_place || 'N/A' }}</td>
              <td class="p-2 border border-gray-300">{{ guide.carrier_name || 'N/A' }}</td>
              <td class="p-2 border border-gray-300 text-center font-mono">{{ guide.vehicle_plate || 'N/A' }}</td>
              <td class="p-2 border border-gray-300 text-center">
                <span class="badge badge-primary badge-sm">{{ guide.details?.length || 0 }}</span>
              </td>
              <td class="p-2 border border-gray-300 text-end">
                <div class="flex gap-2 justify-end">
                  <a
                    :href="appConfig.URLShippingGuideDownload.replace('${id}', guide.id)"
                    target="_blank"
                    class="btn btn-xs btn-outline btn-accent"
                    title="Descargar PDF"
                  >
                    <i class="las la-file-pdf"></i>
                    PDF
                  </a>
                  <button
                    @click="editGuide(guide)"
                    class="btn btn-xs border-teal-500 text-teal-500 bg-white"
                    title="Editar guía"
                  >
                    <i class="las la-edit"></i>
                    EDITAR
                  </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <TableControls :tableFilter="tableFilter" position="bottom" />
  </div>
</template>
