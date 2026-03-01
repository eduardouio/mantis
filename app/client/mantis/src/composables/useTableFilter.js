import { ref, computed, watch } from 'vue'

/**
 * Composable para agregar búsqueda, paginación y ordenamiento a tablas.
 * Equivalente a DataTables pero nativo de Vue 3.
 * 
 * @param {import('vue').Ref|import('vue').ComputedRef} dataSource - Ref o Computed con el array de datos
 * @param {Object} options - Opciones de configuración
 * @param {string[]} options.searchFields - Campos del objeto a incluir en la búsqueda
 * @param {number} options.pageSize - Tamaño de página por defecto (default: 10)
 * @param {number[]} options.pageSizeOptions - Opciones de tamaño de página
 * @param {Function} options.searchTransform - Función para transformar un registro a texto de búsqueda
 * 
 * @returns {Object} Estado y funciones para la tabla
 */
export function useTableFilter(dataSource, options = {}) {
  const {
    searchFields = [],
    pageSize = 10,
    pageSizeOptions = [5, 10, 25, 50, 100],
    searchTransform = null
  } = options

  // Estado
  const searchQuery = ref('')
  const currentPage = ref(1)
  const currentPageSize = ref(pageSize)
  const sortField = ref(null)
  const sortDirection = ref('asc') // 'asc' | 'desc'

  // Normalizar texto para búsqueda (quitar acentos, lowercase)
  const normalizeText = (text) => {
    if (text == null) return ''
    return String(text)
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
  }

  // Filtrar datos según búsqueda
  const filteredData = computed(() => {
    const data = dataSource.value || []
    if (!searchQuery.value.trim()) return data

    const query = normalizeText(searchQuery.value)
    const terms = query.split(/\s+/).filter(t => t.length > 0)

    return data.filter(item => {
      let searchText = ''

      if (searchTransform) {
        searchText = normalizeText(searchTransform(item))
      } else if (searchFields.length > 0) {
        searchText = searchFields.map(field => {
          const value = getNestedValue(item, field)
          return normalizeText(value)
        }).join(' ')
      } else {
        // Buscar en todos los valores del objeto
        searchText = normalizeText(Object.values(item).join(' '))
      }

      // Todos los términos deben coincidir
      return terms.every(term => searchText.includes(term))
    })
  })

  // Ordenar datos
  const sortedData = computed(() => {
    const data = [...filteredData.value]
    if (!sortField.value) return data

    return data.sort((a, b) => {
      const aVal = getNestedValue(a, sortField.value)
      const bVal = getNestedValue(b, sortField.value)

      let comparison = 0
      if (aVal == null && bVal == null) comparison = 0
      else if (aVal == null) comparison = -1
      else if (bVal == null) comparison = 1
      else if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal
      } else {
        comparison = String(aVal).localeCompare(String(bVal), 'es', { numeric: true })
      }

      return sortDirection.value === 'desc' ? -comparison : comparison
    })
  })

  // Paginación
  const totalPages = computed(() => {
    if (currentPageSize.value <= 0) return 1
    return Math.max(1, Math.ceil(sortedData.value.length / currentPageSize.value))
  })

  const paginatedData = computed(() => {
    if (currentPageSize.value <= 0) return sortedData.value
    const start = (currentPage.value - 1) * currentPageSize.value
    return sortedData.value.slice(start, start + currentPageSize.value)
  })

  // Info de paginación
  const paginationInfo = computed(() => {
    const total = sortedData.value.length
    const sourceTotal = (dataSource.value || []).length
    if (total === 0) {
      return { start: 0, end: 0, total, sourceTotal, filtered: total !== sourceTotal }
    }
    const start = (currentPage.value - 1) * currentPageSize.value + 1
    const end = Math.min(currentPage.value * currentPageSize.value, total)
    return { start, end, total, sourceTotal, filtered: total !== sourceTotal }
  })

  // Números de página visibles
  const visiblePages = computed(() => {
    const total = totalPages.value
    const current = currentPage.value
    const delta = 2
    const pages = []

    for (let i = Math.max(1, current - delta); i <= Math.min(total, current + delta); i++) {
      pages.push(i)
    }

    return pages
  })

  // Acciones
  const goToPage = (page) => {
    currentPage.value = Math.max(1, Math.min(page, totalPages.value))
  }

  const nextPage = () => goToPage(currentPage.value + 1)
  const prevPage = () => goToPage(currentPage.value - 1)
  const firstPage = () => goToPage(1)
  const lastPage = () => goToPage(totalPages.value)

  const setPageSize = (size) => {
    currentPageSize.value = size
    currentPage.value = 1
  }

  const toggleSort = (field) => {
    if (sortField.value === field) {
      if (sortDirection.value === 'asc') {
        sortDirection.value = 'desc'
      } else {
        // Reset sorting
        sortField.value = null
        sortDirection.value = 'asc'
      }
    } else {
      sortField.value = field
      sortDirection.value = 'asc'
    }
  }

  const clearSearch = () => {
    searchQuery.value = ''
    currentPage.value = 1
  }

  // Reset de página cuando cambian los datos o la búsqueda
  watch([searchQuery, () => dataSource.value], () => {
    currentPage.value = 1
  })

  // Helper para acceder a propiedades anidadas
  function getNestedValue(obj, path) {
    if (!path) return obj
    return path.split('.').reduce((acc, part) => acc?.[part], obj)
  }

  return {
    // Estado
    searchQuery,
    currentPage,
    currentPageSize,
    sortField,
    sortDirection,
    pageSizeOptions,

    // Datos computados
    filteredData,
    sortedData,
    paginatedData,
    totalPages,
    paginationInfo,
    visiblePages,

    // Acciones
    goToPage,
    nextPage,
    prevPage,
    firstPage,
    lastPage,
    setPageSize,
    toggleSort,
    clearSearch,
    
    // Indicadores
    hasData: computed(() => (dataSource.value || []).length > 0),
    isEmpty: computed(() => paginatedData.value.length === 0)
  }
}
