<script setup>
/**
 * Componente reutilizable de controles de tabla (búsqueda + paginación).
 * Equivalente visual a DataTables con estilo DaisyUI/TailwindCSS.
 * 
 * Props:
 *  - tableFilter: objeto retornado por useTableFilter()
 *  - showSearch: mostrar campo de búsqueda (default: true)
 *  - showPagination: mostrar controles de paginación (default: true)
 *  - showInfo: mostrar info "Mostrando X de Y" (default: true)
 *  - showPageSize: mostrar selector de registros por página (default: true)
 *  - searchPlaceholder: placeholder del input de búsqueda
 *  - position: 'top' | 'bottom' - afecta qué controles se muestran
 */
const props = defineProps({
  tableFilter: { type: Object, required: true },
  showSearch: { type: Boolean, default: true },
  showPagination: { type: Boolean, default: true },
  showInfo: { type: Boolean, default: true },
  showPageSize: { type: Boolean, default: true },
  searchPlaceholder: { type: String, default: 'Buscar en la tabla...' },
  position: { type: String, default: 'top' }
})
</script>

<template>
  <!-- TOP: Búsqueda + selector de registros por página -->
  <div v-if="position === 'top'" class="flex flex-wrap items-center justify-between gap-3 mb-3">
    <!-- Selector de registros por página -->
    <div v-if="showPageSize" class="flex items-center gap-2 text-sm text-gray-600">
      <label>Mostrar</label>
      <select 
        class="select select-bordered select-xs w-20"
        :value="tableFilter.currentPageSize.value"
        @change="tableFilter.setPageSize(Number($event.target.value))"
      >
        <option v-for="size in tableFilter.pageSizeOptions" :key="size" :value="size">{{ size }}</option>
      </select>
      <span>registros</span>
    </div>

    <!-- Campo de búsqueda -->
    <div v-if="showSearch" class="relative">
      <i class="las la-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
      <input 
        type="text"
        v-model="tableFilter.searchQuery.value"
        :placeholder="searchPlaceholder"
        class="input input-bordered input-sm pl-9 pr-8 w-64"
      />
      <button 
        v-if="tableFilter.searchQuery.value"
        @click="tableFilter.clearSearch()"
        class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        title="Limpiar búsqueda"
      >
        <i class="las la-times"></i>
      </button>
    </div>
  </div>

  <!-- BOTTOM: Info de paginación + controles de navegación -->
  <div v-if="position === 'bottom'" class="flex flex-wrap items-center justify-between gap-3 mt-3">
    <!-- Info de registros -->
    <div v-if="showInfo" class="text-sm text-gray-500">
      <template v-if="tableFilter.paginationInfo.value.total === 0">
        No se encontraron registros
        <template v-if="tableFilter.paginationInfo.value.filtered">
          (filtrado de {{ tableFilter.paginationInfo.value.sourceTotal }} registros)
        </template>
      </template>
      <template v-else>
        Mostrando {{ tableFilter.paginationInfo.value.start }} a {{ tableFilter.paginationInfo.value.end }}
        de {{ tableFilter.paginationInfo.value.total }} registros
        <template v-if="tableFilter.paginationInfo.value.filtered">
          (filtrado de {{ tableFilter.paginationInfo.value.sourceTotal }} totales)
        </template>
      </template>
    </div>

    <!-- Controles de paginación -->
    <div v-if="showPagination && tableFilter.totalPages.value > 1" class="join">
      <button 
        class="join-item btn btn-xs"
        :disabled="tableFilter.currentPage.value === 1"
        @click="tableFilter.firstPage()"
        title="Primera página"
      >
        <i class="las la-angle-double-left"></i>
      </button>
      <button 
        class="join-item btn btn-xs"
        :disabled="tableFilter.currentPage.value === 1"
        @click="tableFilter.prevPage()"
        title="Página anterior"
      >
        <i class="las la-angle-left"></i>
      </button>
      
      <button 
        v-for="page in tableFilter.visiblePages.value" 
        :key="page"
        class="join-item btn btn-xs"
        :class="{ 'btn-active btn-primary': page === tableFilter.currentPage.value }"
        @click="tableFilter.goToPage(page)"
      >
        {{ page }}
      </button>

      <button 
        class="join-item btn btn-xs"
        :disabled="tableFilter.currentPage.value === tableFilter.totalPages.value"
        @click="tableFilter.nextPage()"
        title="Página siguiente"
      >
        <i class="las la-angle-right"></i>
      </button>
      <button 
        class="join-item btn btn-xs"
        :disabled="tableFilter.currentPage.value === tableFilter.totalPages.value"
        @click="tableFilter.lastPage()"
        title="Última página"
      >
        <i class="las la-angle-double-right"></i>
      </button>
    </div>
  </div>
</template>
