<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { appConfig } from '@/AppConfig'
import { UseProjectStore } from '@/stores/ProjectStore'

const projectStore = UseProjectStore()
const project = computed(() => projectStore.project)
const isProjectClosed = computed(() => project.value?.is_closed === true)

// ── Estado del árbol ─────────────────────────────────────────
const treeData = ref(null)
const loading = ref(true)
const errorMsg = ref('')

// ── Estado de nodos expandidos ───────────────────────────────
const expandedNodes = ref(new Set())

// ── Estado del modal de upload individual ────────────────────
const uploadModal = ref(false)
const uploadTarget = ref(null) // { model_type, object_id, field_name, label }
const uploadFile = ref(null)
const uploading = ref(false)
const uploadMsg = ref('')
const uploadMsgType = ref('')

// ── Estado del modal de carga masiva ─────────────────────────
const bulkModal = ref(false)
const bulkSheetId = ref(null)
const bulkSheetLabel = ref('')
const bulkChains = ref([])
const bulkSelectedIds = ref([])
const bulkFile = ref(null)
const bulkPageCount = ref(0)
const bulkUploading = ref(false)
const bulkMsg = ref('')
const bulkMsgType = ref('')

// ═══════════════════════════════════════════════════════════════
//  Fetch del árbol
// ═══════════════════════════════════════════════════════════════
async function fetchTree() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await fetch(appConfig.URLProjectDocTree, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    })
    const data = await res.json()
    if (data.success) {
      treeData.value = data.data
    } else {
      errorMsg.value = data.error || 'Error al cargar documentos'
    }
  } catch (e) {
    errorMsg.value = 'Error de conexión: ' + e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchTree)

// ═══════════════════════════════════════════════════════════════
//  Helpers del árbol
// ═══════════════════════════════════════════════════════════════
function toggleNode(nodeKey) {
  if (expandedNodes.value.has(nodeKey)) {
    expandedNodes.value.delete(nodeKey)
  } else {
    expandedNodes.value.add(nodeKey)
  }
}

function isExpanded(nodeKey) {
  return expandedNodes.value.has(nodeKey)
}

function expandAll() {
  if (!treeData.value) return
  treeData.value.sheets.forEach((s, i) => {
    expandedNodes.value.add(`sheet-${i}`)
    s.custody_chains.forEach((_, j) => expandedNodes.value.add(`chain-${i}-${j}`))
  })
  expandedNodes.value.add('guides')
}

function collapseAll() {
  expandedNodes.value.clear()
}

// Contadores
const statsTotal = computed(() => treeData.value?.stats?.total || 0)
const statsLoaded = computed(() => treeData.value?.stats?.loaded || 0)
const statsPending = computed(() => statsTotal.value - statsLoaded.value)
const statsPercent = computed(() => {
  if (statsTotal.value === 0) return 0
  return Math.round((statsLoaded.value / statsTotal.value) * 100)
})

// ═══════════════════════════════════════════════════════════════
//  Upload Individual
// ═══════════════════════════════════════════════════════════════
function openUpload(file) {
  uploadTarget.value = {
    model_type: file.model_type,
    object_id: file.object_id,
    field_name: file.field_name,
    label: file.field_label,
    current_file: file.file_name,
  }
  uploadFile.value = null
  uploadMsg.value = ''
  uploading.value = false
  uploadModal.value = true
}

function closeUploadModal() {
  uploadModal.value = false
  uploadTarget.value = null
}

function onUploadFileChange(e) {
  uploadFile.value = e.target.files[0] || null
}

async function confirmUpload() {
  if (!uploadFile.value || !uploadTarget.value) return
  uploading.value = true
  uploadMsg.value = ''

  const fd = new FormData()
  fd.append('file', uploadFile.value)
  fd.append('model_type', uploadTarget.value.model_type)
  fd.append('object_id', uploadTarget.value.object_id)
  fd.append('field_name', uploadTarget.value.field_name)

  try {
    const res = await fetch(appConfig.URLLoadFiles, {
      method: 'POST',
      headers: { 'X-CSRFToken': appConfig.csrfToken },
      body: fd,
    })
    const data = await res.json()
    if (data.success) {
      uploadMsg.value = 'Archivo subido correctamente'
      uploadMsgType.value = 'success'
      await fetchTree() // refrescar
      setTimeout(closeUploadModal, 1200)
    } else {
      uploadMsg.value = data.error || 'Error al subir'
      uploadMsgType.value = 'error'
    }
  } catch (e) {
    uploadMsg.value = 'Error de conexión: ' + e.message
    uploadMsgType.value = 'error'
  } finally {
    uploading.value = false
  }
}

async function deleteFile(file) {
  if (!confirm(`¿Eliminar "${file.file_name}"?`)) return
  try {
    const params = new URLSearchParams({
      model_type: file.model_type,
      object_id: file.object_id,
      field_name: file.field_name,
    })
    const res = await fetch(`${appConfig.URLLoadFiles}?${params}`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': appConfig.csrfToken },
    })
    const data = await res.json()
    if (data.success) {
      await fetchTree()
    } else {
      alert(data.error || 'Error al eliminar')
    }
  } catch (e) {
    alert('Error: ' + e.message)
  }
}

// ═══════════════════════════════════════════════════════════════
//  Carga Masiva
// ═══════════════════════════════════════════════════════════════
function openBulkModal(sheet) {
  bulkSheetId.value = sheet.id
  bulkSheetLabel.value = sheet.label
  bulkChains.value = sheet.custody_chains || []
  bulkSelectedIds.value = bulkChains.value.map(c => c.id)
  bulkFile.value = null
  bulkPageCount.value = 0
  bulkMsg.value = ''
  bulkUploading.value = false
  bulkModal.value = true
}

function closeBulkModal() {
  bulkModal.value = false
  bulkSheetId.value = null
  bulkChains.value = []
  bulkSelectedIds.value = []
}

function bulkSelectAll() { bulkSelectedIds.value = bulkChains.value.map(c => c.id) }
function bulkSelectNone() { bulkSelectedIds.value = [] }
function bulkSelectEvens() {
  bulkSelectedIds.value = bulkChains.value.filter((_, i) => (i + 1) % 2 === 0).map(c => c.id)
}
function bulkSelectOdds() {
  bulkSelectedIds.value = bulkChains.value.filter((_, i) => (i + 1) % 2 !== 0).map(c => c.id)
}

function onBulkFileChange(e) {
  const file = e.target.files[0]
  bulkFile.value = file || null
  bulkPageCount.value = 0
  if (file && file.type === 'application/pdf') {
    countPDFPages(file)
  }
}

async function countPDFPages(file) {
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch(appConfig.URLPdfPageCount, {
      method: 'POST',
      headers: { 'X-CSRFToken': appConfig.csrfToken },
      body: fd,
    })
    const data = await res.json()
    bulkPageCount.value = data.success ? data.pages : 0
  } catch {
    bulkPageCount.value = 0
  }
}

const bulkIsValid = computed(() => {
  return bulkFile.value && bulkSelectedIds.value.length > 0 &&
    bulkPageCount.value === bulkSelectedIds.value.length
})

async function confirmBulkUpload() {
  if (!bulkIsValid.value) return
  bulkUploading.value = true
  bulkMsg.value = ''

  const fd = new FormData()
  fd.append('file', bulkFile.value)
  fd.append('chain_ids', JSON.stringify(bulkSelectedIds.value))

  try {
    const res = await fetch(appConfig.URLProjectBulkCustody, {
      method: 'POST',
      headers: { 'X-CSRFToken': appConfig.csrfToken },
      body: fd,
    })
    const data = await res.json()
    if (data.success) {
      bulkMsg.value = data.message || `Se asignaron ${data.saved} archivo(s) correctamente.`
      bulkMsgType.value = 'success'
      await fetchTree()
      setTimeout(closeBulkModal, 2000)
    } else {
      bulkMsg.value = data.error || 'Error en la carga masiva'
      bulkMsgType.value = 'error'
    }
  } catch (e) {
    bulkMsg.value = 'Error: ' + e.message
    bulkMsgType.value = 'error'
  } finally {
    bulkUploading.value = false
  }
}

// ═══════════════════════════════════════════════════════════════
//  Merge / descarga
// ═══════════════════════════════════════════════════════════════
function downloadMerge(scope = 'all', sheetId = null) {
  let url = appConfig.URLProjectDocMerge + `?scope=${scope}`
  if (sheetId) url += `&sheet_id=${sheetId}`
  window.open(url, '_blank')
}
</script>

<template>
  <div class="space-y-3">
    <!-- Header -->
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-xl font-semibold text-gray-800 flex items-center gap-3">
        <i class="las la-folder-open text-blue-600 text-3xl"></i>
        Documentos del Proyecto
      </h2>
      <div class="flex gap-2">
        <button class="btn btn-sm btn-outline" @click="expandAll" title="Expandir todo">
          <i class="las la-expand-arrows-alt text-lg"></i>
        </button>
        <button class="btn btn-sm btn-outline" @click="collapseAll" title="Colapsar todo">
          <i class="las la-compress-arrows-alt text-lg"></i>
        </button>
        <button
          v-if="statsLoaded > 0"
          class="btn btn-sm btn-primary"
          @click="downloadMerge('all')"
          title="Descargar todos los documentos en un solo PDF"
        >
          <i class="las la-file-pdf mr-1 text-lg"></i> Descargar Todo
        </button>
      </div>
    </div>

    <!-- Progress bar -->
    <div v-if="!loading && treeData" class="flex items-center gap-3 mb-2">
      <div class="flex-1">
        <progress
          class="progress progress-primary w-full"
          :value="statsLoaded"
          :max="statsTotal"
        ></progress>
      </div>
      <span class="text-sm font-semibold text-gray-600 whitespace-nowrap">
        {{ statsLoaded }}/{{ statsTotal }} archivos
        <span class="text-primary">({{ statsPercent }}%)</span>
      </span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-3 py-6">
      <div v-for="i in 5" :key="i" class="skeleton h-4 rounded" :class="i % 2 ? 'w-3/4' : 'w-1/2'"></div>
    </div>

    <!-- Error -->
    <div v-else-if="errorMsg" class="alert alert-error text-base">
      <i class="las la-exclamation-circle text-2xl"></i>
      {{ errorMsg }}
    </div>

    <!-- Árbol de documentos -->
    <div v-else-if="treeData" class="space-y-1">

      <!-- ── Planillas ──────────────────────────────────────── -->
      <div v-for="(sheet, si) in treeData.sheets" :key="'s'+si" class="border border-gray-200 rounded-lg mb-2">
        <!-- Encabezado de planilla -->
        <div
          class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-base-200 rounded-t-lg"
          @click="toggleNode('sheet-'+si)"
        >
          <i
            class="las text-gray-500 transition-transform duration-200 text-xl"
            :class="isExpanded('sheet-'+si) ? 'la-angle-down' : 'la-angle-right'"
          ></i>
          <i class="las la-file-invoice text-blue-500 text-2xl"></i>
          <span class="font-medium text-base flex-1">{{ sheet.label }}</span>
          <span class="text-sm text-gray-400">{{ sheet.period }}</span>

          <!-- Badge de archivos de la planilla -->
          <span
            class="badge badge-sm"
            :class="sheet.files.filter(f => f.has_file).length === sheet.files.length ? 'badge-success' : 'badge-warning'"
          >
            {{ sheet.files.filter(f => f.has_file).length }}/{{ sheet.files.length }}
          </span>

          <!-- Badge cadenas -->
          <span class="badge badge-sm badge-info" v-if="sheet.custody_chains.length">
            {{ sheet.custody_chains.filter(c => c.files.some(f => f.has_file)).length }}/{{ sheet.custody_chains.length }} cadenas
          </span>

          <!-- Botón carga masiva -->
          <button
            v-if="sheet.custody_chains.length > 0"
            class="btn btn-sm btn-accent"
            @click.stop="openBulkModal(sheet)"
            title="Carga masiva de cadenas de custodia"
          >
            <i class="las la-cloud-upload-alt mr-1 text-lg"></i> Masiva
          </button>

          <!-- Botón merge de la planilla -->
          <button
            class="btn btn-sm btn-ghost"
            @click.stop="downloadMerge('all', sheet.id)"
            title="Descargar documentos de esta planilla"
          >
            <i class="las la-download text-lg"></i>
          </button>
        </div>

        <!-- Contenido expandible -->
        <div v-if="isExpanded('sheet-'+si)" class="px-4 pb-3 space-y-2">
          <!-- Archivos de la planilla -->
          <div
            v-for="file in sheet.files"
            :key="file.field_name"
            class="flex items-center gap-3 py-2 pl-6 text-base border-b border-gray-100 last:border-0"
          >
            <i
              class="las text-xl"
              :class="file.has_file ? 'la-check-circle text-success' : 'la-times-circle text-error'"
            ></i>
            <span class="flex-1">{{ file.field_label }}</span>
            <template v-if="file.has_file">
              <a :href="file.file_url" target="_blank" class="btn btn-sm btn-ghost text-blue-500" title="Ver archivo">
                <i class="las la-eye text-lg"></i>
              </a>
              <button class="btn btn-sm btn-ghost text-error" @click="deleteFile(file)" title="Eliminar" :disabled="isProjectClosed" :class="{ 'opacity-50 cursor-not-allowed': isProjectClosed }">
                <i class="las la-trash text-lg"></i>
              </button>
            </template>
            <button class="btn btn-sm btn-primary btn-outline" @click="openUpload(file)" :title="file.has_file ? 'Reemplazar' : 'Subir'" :disabled="isProjectClosed && file.has_file" :class="{ 'opacity-50 cursor-not-allowed': isProjectClosed && file.has_file }">
              <i class="las la-upload text-lg"></i>
            </button>
          </div>

          <!-- Cadenas de custodia -->
          <div v-if="sheet.custody_chains.length > 0" class="mt-3">
            <div class="text-sm font-semibold text-gray-500 mb-2 pl-6 flex items-center gap-2">
              <i class="las la-link text-lg"></i> Cadenas de Custodia
            </div>
            <div
              v-for="(chain, ci) in sheet.custody_chains"
              :key="'c'+ci"
              class="flex items-center gap-3 py-2 pl-10 text-base border-b border-gray-50 last:border-0"
            >
              <i
                class="las text-xl"
                :class="chain.files[0]?.has_file ? 'la-check-circle text-success' : 'la-times-circle text-error'"
              ></i>
              <span class="flex-1 text-sm">
                {{ chain.label }}
                <span class="text-gray-400 ml-1">{{ chain.date }}</span>
              </span>
              <template v-if="chain.files[0]?.has_file">
                <a :href="chain.files[0].file_url" target="_blank" class="btn btn-sm btn-ghost text-blue-500" title="Ver">
                  <i class="las la-eye text-lg"></i>
                </a>
                <button class="btn btn-sm btn-ghost text-error" @click="deleteFile(chain.files[0])" title="Eliminar" :disabled="isProjectClosed" :class="{ 'opacity-50 cursor-not-allowed': isProjectClosed }">
                  <i class="las la-trash text-lg"></i>
                </button>
              </template>
              <button class="btn btn-sm btn-primary btn-outline" @click="openUpload(chain.files[0])" :title="chain.files[0]?.has_file ? 'Reemplazar' : 'Subir'" :disabled="isProjectClosed && chain.files[0]?.has_file" :class="{ 'opacity-50 cursor-not-allowed': isProjectClosed && chain.files[0]?.has_file }">
                <i class="las la-upload text-lg"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Guías de remisión ──────────────────────────────── -->
      <div v-if="treeData.shipping_guides.length > 0" class="border border-gray-200 rounded-lg">
        <div
          class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-base-200 rounded-t-lg"
          @click="toggleNode('guides')"
        >
          <i
            class="las text-gray-500 transition-transform duration-200 text-xl"
            :class="isExpanded('guides') ? 'la-angle-down' : 'la-angle-right'"
          ></i>
          <i class="las la-truck text-amber-500 text-2xl"></i>
          <span class="font-medium text-base flex-1">Guías de Remisión</span>
          <span
            class="badge badge-sm"
            :class="treeData.shipping_guides.filter(g => g.files.some(f => f.has_file)).length === treeData.shipping_guides.length ? 'badge-success' : 'badge-warning'"
          >
            {{ treeData.shipping_guides.filter(g => g.files.some(f => f.has_file)).length }}/{{ treeData.shipping_guides.length }}
          </span>
        </div>
        <div v-if="isExpanded('guides')" class="px-5 pb-4">
          <div
            v-for="guide in treeData.shipping_guides"
            :key="guide.id"
            class="flex items-center gap-3 py-2 pl-6 text-base border-b border-gray-100 last:border-0"
          >
            <i
              class="las text-xl"
              :class="guide.files[0]?.has_file ? 'la-check-circle text-success' : 'la-times-circle text-error'"
            ></i>
            <span class="flex-1">{{ guide.label }} <span class="text-gray-400 text-sm">{{ guide.date }}</span></span>
            <template v-if="guide.files[0]?.has_file">
              <a :href="guide.files[0].file_url" target="_blank" class="btn btn-sm btn-ghost text-blue-500" title="Ver">
                <i class="las la-eye text-lg"></i>
              </a>
              <button class="btn btn-sm btn-ghost text-error" @click="deleteFile(guide.files[0])" title="Eliminar" :disabled="isProjectClosed" :class="{ 'opacity-50 cursor-not-allowed': isProjectClosed }">
                <i class="las la-trash text-lg"></i>
              </button>
            </template>
            <button class="btn btn-sm btn-primary btn-outline" @click="openUpload(guide.files[0])" :title="guide.files[0]?.has_file ? 'Reemplazar' : 'Subir'" :disabled="isProjectClosed && guide.files[0]?.has_file" :class="{ 'opacity-50 cursor-not-allowed': isProjectClosed && guide.files[0]?.has_file }">
              <i class="las la-upload text-lg"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Vacío -->
      <div v-if="treeData.sheets.length === 0 && treeData.shipping_guides.length === 0" class="text-center text-gray-400 py-10">
        <i class="las la-folder-open text-6xl"></i>
        <p class="mt-3 text-lg">No hay documentos registrados para este proyecto</p>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════ -->
    <!--  Modal: Upload Individual                              -->
    <!-- ═══════════════════════════════════════════════════════ -->
    <div class="modal" :class="{ 'modal-open': uploadModal }">
      <div class="modal-box max-w-lg">
        <h3 class="font-bold text-xl flex items-center gap-3 mb-5">
          <i class="las la-cloud-upload-alt text-blue-500 text-3xl"></i>
          Subir Archivo
        </h3>
        <div v-if="uploadTarget">
          <p class="text-base text-gray-600 mb-2">
            <strong>{{ uploadTarget.label }}</strong>
          </p>
          <p v-if="uploadTarget.current_file" class="text-sm text-gray-400 mb-4">
            Archivo actual: {{ uploadTarget.current_file }} (se reemplazará)
          </p>
          <input
            type="file"
            class="file-input file-input-bordered file-input-md w-full"
            @change="onUploadFileChange"
          />
          <!-- Progreso -->
          <div v-if="uploading" class="mt-4">
            <progress class="progress progress-primary w-full"></progress>
            <p class="text-sm text-gray-500 mt-1">Subiendo...</p>
          </div>
          <!-- Mensaje -->
          <div v-if="uploadMsg" class="mt-3 text-base" :class="uploadMsgType === 'success' ? 'text-success' : 'text-error'">
            {{ uploadMsg }}
          </div>
        </div>
        <div class="modal-action">
          <button class="btn btn-md" @click="closeUploadModal">Cancelar</button>
          <button
            class="btn btn-md btn-primary"
            :disabled="!uploadFile || uploading"
            @click="confirmUpload"
          >
            <i class="las la-upload mr-1 text-lg"></i> Subir
          </button>
        </div>
      </div>
      <div class="modal-backdrop" @click="closeUploadModal"></div>
    </div>

    <!-- ═══════════════════════════════════════════════════════ -->
    <!--  Modal: Carga Masiva                                   -->
    <!-- ═══════════════════════════════════════════════════════ -->
    <div class="modal" :class="{ 'modal-open': bulkModal }">
      <div class="modal-box max-w-3xl">
        <h3 class="font-bold text-xl flex items-center gap-3 mb-5">
          <i class="las la-layer-group text-accent text-3xl"></i>
          Carga Masiva — {{ bulkSheetLabel }}
        </h3>

        <!-- Selección de cadenas -->
        <div class="mb-4">
          <p class="text-base font-semibold mb-3">Seleccione las cadenas de custodia:</p>
          <div class="flex gap-3 mb-3">
            <button class="btn btn-sm btn-outline" @click="bulkSelectAll">Todas</button>
            <button class="btn btn-sm btn-outline" @click="bulkSelectNone">Ninguna</button>
            <button class="btn btn-sm btn-outline" @click="bulkSelectEvens">Pares</button>
            <button class="btn btn-sm btn-outline" @click="bulkSelectOdds">Impares</button>
          </div>
          <div class="max-h-64 overflow-y-auto border rounded-lg p-3 space-y-1">
            <label
              v-for="(chain, i) in bulkChains"
              :key="chain.id"
              class="flex items-center gap-3 py-2 px-3 rounded cursor-pointer hover:bg-base-200 text-base"
            >
              <input
                type="checkbox"
                class="checkbox checkbox-sm checkbox-primary"
                :value="chain.id"
                v-model="bulkSelectedIds"
              />
              <span class="font-mono text-sm text-gray-500">{{ i + 1 }}.</span>
              <span>{{ chain.label }}</span>
              <span class="text-sm text-gray-400">{{ chain.date }}</span>
              <i
                v-if="chain.files[0]?.has_file"
                class="las la-check-circle text-success text-lg ml-auto"
                title="Ya tiene archivo"
              ></i>
            </label>
          </div>
          <p class="text-sm text-gray-500 mt-2">
            {{ bulkSelectedIds.length }} cadena(s) seleccionada(s)
          </p>
        </div>

        <!-- File input -->
        <div class="mb-4">
          <p class="text-base font-semibold mb-2">Archivo PDF (una página por cadena):</p>
          <input
            type="file"
            accept=".pdf"
            class="file-input file-input-bordered file-input-md w-full"
            @change="onBulkFileChange"
          />
          <div v-if="bulkFile" class="mt-2 text-sm">
            <span v-if="bulkPageCount > 0">
              Páginas detectadas:
              <strong :class="bulkPageCount === bulkSelectedIds.length ? 'text-success' : 'text-error'">
                {{ bulkPageCount }}
              </strong>
              <span v-if="bulkPageCount !== bulkSelectedIds.length" class="text-error">
                — deben ser {{ bulkSelectedIds.length }}
              </span>
              <span v-else class="text-success"> ✓</span>
            </span>
            <span v-else class="text-gray-400">Contando páginas...</span>
          </div>
        </div>

        <!-- Progreso -->
        <div v-if="bulkUploading" class="mb-4">
          <progress class="progress progress-accent w-full"></progress>
          <p class="text-sm text-gray-500 mt-1">Procesando carga masiva...</p>
        </div>

        <!-- Mensaje -->
        <div v-if="bulkMsg" class="mb-4 text-base" :class="bulkMsgType === 'success' ? 'text-success' : 'text-error'">
          {{ bulkMsg }}
        </div>

        <div class="modal-action">
          <button class="btn btn-md" @click="closeBulkModal">Cancelar</button>
          <button
            class="btn btn-md btn-accent"
            :disabled="!bulkIsValid || bulkUploading"
            @click="confirmBulkUpload"
          >
            <i class="las la-cloud-upload-alt mr-1 text-lg"></i>
            Subir {{ bulkSelectedIds.length }} archivo(s)
          </button>
        </div>
      </div>
      <div class="modal-backdrop" @click="closeBulkModal"></div>
    </div>
  </div>
</template>
