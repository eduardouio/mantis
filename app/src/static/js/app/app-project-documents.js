/**
 * app-project-documents.js
 * Árbol de documentos de un proyecto con descarga individual y merge PDF.
 * Requiere variable global PROJECT_ID definida en el template.
 */
(function () {
  'use strict';

  const API_TREE  = `/api/load_files/project/${PROJECT_ID}/tree/`;
  const API_MERGE = `/api/load_files/project/${PROJECT_ID}/merge/`;
  const API_FILES = '/api/load_files/';
  const CSRF      = getCookie('csrftoken');

  let treeData    = null;
  let uploadTarget = null;

  // ── Init ───────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', fetchTree);

  // ── Fetch ──────────────────────────────────────────────────────
  function fetchTree() {
    showLoading(true);
    fetch(API_TREE)
      .then(r => r.json())
      .then(json => {
        if (!json.success) throw new Error(json.error);
        treeData = json.data;
        updateStats(treeData.stats);
        renderTree();
        showLoading(false);
      })
      .catch(err => {
        showLoading(false);
        showToast('Error al cargar: ' + err.message, 'error');
      });
  }

  // ── Stats ──────────────────────────────────────────────────────
  function updateStats(s) {
    const pending = s.total - s.loaded;
    const pct = s.total > 0 ? Math.round((s.loaded / s.total) * 100) : 0;
    document.getElementById('statTotal').textContent   = s.total;
    document.getElementById('statLoaded').textContent  = s.loaded;
    document.getElementById('statPending').textContent = pending;
    document.getElementById('statPercent').textContent = pct + '%';
  }

  // ── Render ─────────────────────────────────────────────────────
  function renderTree() {
    const container = document.getElementById('treeContent');
    container.innerHTML = '';

    if (!treeData || (!treeData.sheets.length && !treeData.shipping_guides.length)) {
      container.innerHTML = `
        <div class="flex flex-col items-center justify-center py-20 text-gray-400">
          <i class="las la-folder-open text-7xl mb-3"></i>
          <p class="text-base">No hay documentos registrados para este proyecto</p>
        </div>`;
      return;
    }

    // ── Sección Planillas ────────────────────────────────────────
    if (treeData.sheets.length) {
      const sheetsSection = makeSection(
        'las la-file-invoice text-indigo-500',
        `Planillas (${treeData.sheets.length})`
      );
      const sheetsBody = sheetsSection.querySelector('.section-body');

      treeData.sheets.forEach(sheet => {
        sheetsBody.appendChild(buildSheetNode(sheet));
      });

      container.appendChild(sheetsSection);
    }

    // ── Sección Guías de Remisión ────────────────────────────────
    if (treeData.shipping_guides.length) {
      const guidesSection = makeSection(
        'las la-shipping-fast text-orange-500',
        `Guías de Remisión (${treeData.shipping_guides.length})`
      );
      const guidesBody = guidesSection.querySelector('.section-body');

      treeData.shipping_guides.forEach(guide => {
        guidesBody.appendChild(buildSimpleNode(guide, 'las la-shipping-fast text-orange-400'));
      });

      container.appendChild(guidesSection);
    }
  }

  // ── Section wrapper ────────────────────────────────────────────
  function makeSection(iconClass, title) {
    const section = document.createElement('div');
    section.className = 'mb-4';

    const header = document.createElement('div');
    header.className = 'doc-toggle font-semibold text-sm bg-gray-50 rounded';
    header.innerHTML = `
      <i class="las la-angle-right doc-chevron rotated"></i>
      <i class="${iconClass} text-lg"></i>
      <span>${title}</span>`;

    const body = document.createElement('div');
    body.className = 'doc-children open section-body';

    header.addEventListener('click', () => {
      body.classList.toggle('open');
      header.querySelector('.doc-chevron').classList.toggle('rotated');
    });

    section.appendChild(header);
    section.appendChild(body);
    return section;
  }

  // ── Sheet node ─────────────────────────────────────────────────
  function buildSheetNode(sheet) {
    const div = document.createElement('div');
    div.className = 'doc-tree';

    // Header de la planilla
    const toggle = document.createElement('div');
    toggle.className = 'doc-toggle';

    const chainCount = sheet.custody_chains.length;
    const chainLoaded = sheet.custody_chains.filter(c =>
      c.files.some(f => f.has_file)
    ).length;
    const sheetLoaded = sheet.files.filter(f => f.has_file).length;
    const sheetTotal  = sheet.files.length;

    // Botón de merge solo cadenas de esta planilla
    const mergeBtn = chainCount > 0
      ? `<button class="btn btn-sm btn-outline btn-secondary ml-2"
           title="Merge PDF de cadenas de esta planilla"
           onclick="event.stopPropagation(); downloadMerge('custody_chains', ${sheet.id})">
           <i class="las la-object-group mr-1"></i>Merge Cadenas
         </button>`
      : '';

    // Botón de carga masiva de cadenas
    const bulkBtn = chainCount > 0
      ? `<button class="btn btn-sm btn-outline btn-accent ml-1"
           title="Carga masiva: subir un PDF con todas las cadenas"
           onclick="event.stopPropagation(); openBulkCustodyModal(${sheet.id})">
           <i class="las la-file-import mr-1"></i>Carga Masiva
         </button>`
      : '';

    toggle.innerHTML = `
      <i class="las la-angle-right doc-chevron"></i>
      <i class="las la-file-invoice text-indigo-500 text-2xl"></i>
      <span class="text-base font-medium">${sheet.label}</span>
      <span class="text-sm text-gray-400 ml-1">${sheet.period}</span>
      <span class="badge-sm ${sheetLoaded === sheetTotal ? 'badge-ok' : 'badge-miss'}">
        <i class="las ${sheetLoaded === sheetTotal ? 'la-check-circle' : 'la-exclamation-circle'}"></i>
        ${sheetLoaded}/${sheetTotal}
      </span>
      ${chainCount > 0 ? `<span class="badge-sm ${chainLoaded === chainCount ? 'badge-ok' : 'badge-miss'}" style="margin-left:2px">
        <i class="las la-link"></i> ${chainLoaded}/${chainCount} cadenas
      </span>` : ''}
      ${mergeBtn}
      ${bulkBtn}`;

    const children = document.createElement('div');
    children.className = 'doc-children';

    // Archivos de la planilla
    sheet.files.forEach(f => children.appendChild(buildFileRow(f)));

    // Cadenas de custodia
    if (chainCount > 0) {
      const chainsHeader = document.createElement('div');
      chainsHeader.className = 'doc-toggle text-sm font-semibold text-gray-500 ml-4 mt-2';
      chainsHeader.innerHTML = `
        <i class="las la-angle-right doc-chevron"></i>
        <i class="las la-link text-cyan-600 text-xl"></i>
        <span>Cadenas de Custodia (${chainCount})</span>`;

      const chainsBody = document.createElement('div');
      chainsBody.className = 'doc-children';

      sheet.custody_chains.forEach(chain => {
        chainsBody.appendChild(buildSimpleNode(chain, 'las la-link text-cyan-500'));
      });

      chainsHeader.addEventListener('click', () => {
        chainsBody.classList.toggle('open');
        chainsHeader.querySelector('.doc-chevron').classList.toggle('rotated');
      });

      children.appendChild(chainsHeader);
      children.appendChild(chainsBody);
    }

    toggle.addEventListener('click', (e) => {
      if (e.target.closest('button') || e.target.closest('a')) return;
      children.classList.toggle('open');
      toggle.querySelector('.doc-chevron').classList.toggle('rotated');
    });

    div.appendChild(toggle);
    div.appendChild(children);
    return div;
  }

  // ── Simple node (cadena / guía) ────────────────────────────────
  function buildSimpleNode(node, iconClass) {
    const div = document.createElement('div');
    div.className = 'doc-tree';

    const hasFile = node.files.some(f => f.has_file);

    if (node.files.length === 1) {
      // Nodo inline: una sola fila con icono + label + acciones
      const f = node.files[0];
      const row = document.createElement('div');
      row.className = 'file-row';
      row.style.paddingLeft = '1.5rem';

      row.innerHTML = `
        <i class="${iconClass} text-lg"></i>
        <span class="file-label">
          <span class="font-medium">${node.label}</span>
          <span class="text-sm text-gray-400 ml-1">${node.date || ''}</span>
          ${f.has_file
            ? `<span class="text-green-600 text-sm ml-2"><i class="las la-check-circle"></i> ${f.file_name}</span>`
            : `<span class="text-red-400 text-sm ml-2"><i class="las la-times-circle"></i> Sin archivo</span>`
          }
        </span>
        ${buildActionButtons(f)}`;

      div.appendChild(row);
    } else {
      // Nodo con toggle
      const toggle = document.createElement('div');
      toggle.className = 'doc-toggle';
      toggle.innerHTML = `
        <i class="las la-angle-right doc-chevron"></i>
        <i class="${iconClass} text-2xl"></i>
        <span class="text-base font-medium">${node.label}</span>
        <span class="text-sm text-gray-400 ml-1">${node.date || ''}</span>`;

      const children = document.createElement('div');
      children.className = 'doc-children';
      node.files.forEach(f => children.appendChild(buildFileRow(f)));

      toggle.addEventListener('click', () => {
        children.classList.toggle('open');
        toggle.querySelector('.doc-chevron').classList.toggle('rotated');
      });

      div.appendChild(toggle);
      div.appendChild(children);
    }

    return div;
  }

  // ── File row ───────────────────────────────────────────────────
  function buildFileRow(f) {
    const row = document.createElement('div');
    row.className = 'file-row';
    row.id = `file-${f.model_type}-${f.object_id}-${f.field_name}`;

    row.innerHTML = `
      <i class="las la-file-pdf text-red-400"></i>
      <span class="file-label">
        <span class="font-medium">${f.field_label}</span>
        ${f.has_file
          ? `<span class="text-green-600 text-sm ml-2"><i class="las la-check-circle"></i> ${f.file_name}</span>`
          : `<span class="text-red-400 text-sm ml-2"><i class="las la-times-circle"></i> Sin archivo</span>`
        }
      </span>
      ${buildActionButtons(f)}`;

    return row;
  }

  // ── Botones de acción ──────────────────────────────────────────
  function buildActionButtons(f) {
    const mt = f.model_type, oid = f.object_id, fn = f.field_name;
    let html = '';

    // Subir / Reemplazar
    html += `<button class="btn btn-sm btn-success btn-outline"
               title="${f.has_file ? 'Reemplazar' : 'Subir'}"
               onclick="event.stopPropagation(); openUploadModal('${mt}', ${oid}, '${fn}', '${esc(f.field_label)}')">
               <i class="las ${f.has_file ? 'la-sync-alt' : 'la-upload'}"></i>
             </button>`;

    if (f.has_file) {
      // Descargar
      html += ` <a href="${f.file_url}" target="_blank" download
                   class="btn btn-sm btn-info btn-outline" title="Descargar"
                   onclick="event.stopPropagation()">
                   <i class="las la-download"></i>
                 </a>`;
      // Eliminar
      html += ` <button class="btn btn-sm btn-error btn-outline"
                   title="Eliminar"
                   onclick="event.stopPropagation(); deleteFileAction('${mt}', ${oid}, '${fn}', '${esc(f.field_label)}')">
                   <i class="las la-trash"></i>
                 </button>`;
    }

    return html;
  }

  // ── Merge download ─────────────────────────────────────────────
  window.downloadMerge = function (scope, sheetId) {
    let url = `${API_MERGE}?scope=${scope}`;
    if (sheetId) url += `&sheet_id=${sheetId}`;

    showToast('Generando PDF combinado…', 'info');

    fetch(url)
      .then(r => {
        if (!r.ok) {
          return r.json().then(j => { throw new Error(j.error || 'Error al generar merge'); });
        }
        return r.blob();
      })
      .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        const disposition = scope === 'all' ? 'Completo' : scope;
        a.download = `Merge_${disposition}_Proyecto_${PROJECT_ID}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(a.href);
        showToast('PDF descargado correctamente', 'success');
      })
      .catch(err => showToast(err.message, 'error'));
  };

  // ── Upload modal ───────────────────────────────────────────────
  window.openUploadModal = function (modelType, objectId, fieldName, label) {
    uploadTarget = { model_type: modelType, object_id: objectId, field_name: fieldName };
    document.getElementById('uploadLabel').textContent = label;
    document.getElementById('uploadContext').textContent =
      `Modelo: ${modelType} | ID: ${objectId} | Campo: ${fieldName}`;
    document.getElementById('uploadFileInput').value = '';
    document.getElementById('uploadMsg').classList.add('hidden');
    document.getElementById('uploadProgress').classList.add('hidden');
    document.getElementById('uploadConfirmBtn').disabled = false;
    document.getElementById('uploadModal').showModal();
  };

  window.closeUploadModal = function () {
    document.getElementById('uploadModal').close();
    uploadTarget = null;
  };

  window.confirmUpload = function () {
    if (!uploadTarget) return;
    const fileInput = document.getElementById('uploadFileInput');
    if (!fileInput.files.length) {
      showUploadMsg('Selecciona un archivo primero.', 'warning');
      return;
    }

    const fd = new FormData();
    fd.append('model_type', uploadTarget.model_type);
    fd.append('object_id', uploadTarget.object_id);
    fd.append('field_name', uploadTarget.field_name);
    fd.append('file', fileInput.files[0]);

    document.getElementById('uploadConfirmBtn').disabled = true;
    document.getElementById('uploadProgress').classList.remove('hidden');

    fetch(API_FILES, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF },
      body: fd,
    })
      .then(r => r.json())
      .then(json => {
        document.getElementById('uploadProgress').classList.add('hidden');
        if (json.success) {
          showToast('Archivo subido correctamente', 'success');
          closeUploadModal();
          fetchTree();
        } else {
          showUploadMsg(json.error || 'Error', 'error');
          document.getElementById('uploadConfirmBtn').disabled = false;
        }
      })
      .catch(err => {
        document.getElementById('uploadProgress').classList.add('hidden');
        document.getElementById('uploadConfirmBtn').disabled = false;
        showUploadMsg('Error: ' + err.message, 'error');
      });
  };

  // ── Delete ─────────────────────────────────────────────────────
  window.deleteFileAction = function (modelType, objectId, fieldName, label) {
    if (!confirm(`¿Eliminar "${label}"?\nEsta acción no se puede deshacer.`)) return;

    fetch(`${API_FILES}?model_type=${modelType}&object_id=${objectId}&field_name=${fieldName}`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': CSRF },
    })
      .then(r => r.json())
      .then(json => {
        if (json.success) {
          showToast('Archivo eliminado', 'success');
          fetchTree();
        } else {
          showToast(json.error || 'Error', 'error');
        }
      })
      .catch(err => showToast('Error: ' + err.message, 'error'));
  };

  // ── Expand / Collapse ──────────────────────────────────────────
  window.expandAllDoc = function () {
    document.querySelectorAll('#treeContent .doc-children').forEach(el => el.classList.add('open'));
    document.querySelectorAll('#treeContent .doc-chevron').forEach(el => el.classList.add('rotated'));
  };

  window.collapseAllDoc = function () {
    document.querySelectorAll('#treeContent .doc-children').forEach(el => el.classList.remove('open'));
    document.querySelectorAll('#treeContent .doc-chevron').forEach(el => el.classList.remove('rotated'));
  };

  // ── Helpers ────────────────────────────────────────────────────
  function showLoading(show) {
    document.getElementById('loadingSkeleton').classList.toggle('hidden', !show);
    document.getElementById('treeContent').classList.toggle('hidden', show);
  }

  function showUploadMsg(msg, type) {
    const el = document.getElementById('uploadMsg');
    const cls = type === 'error' ? 'alert-error' : type === 'success' ? 'alert-success' : 'alert-warning';
    el.innerHTML = `<div class="alert ${cls} text-sm py-1 px-2">${msg}</div>`;
    el.classList.remove('hidden');
  }

  function showToast(msg, type) {
    const toast   = document.getElementById('pdToast');
    const content = document.getElementById('pdToastContent');
    const text    = document.getElementById('pdToastText');
    const cls = type === 'success' ? 'alert-success' : type === 'info' ? 'alert-info' : 'alert-error';
    content.className = 'alert ' + cls;
    text.textContent = msg;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3500);
  }

  function esc(str) {
    return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
  }

  function getCookie(name) {
    let v = null;
    if (document.cookie && document.cookie !== '') {
      document.cookie.split(';').forEach(c => {
        c = c.trim();
        if (c.startsWith(name + '=')) v = decodeURIComponent(c.substring(name.length + 1));
      });
    }
    return v;
  }

  // ═══════════════════════════════════════════════════════════════
  //  Carga Masiva de Cadenas de Custodia
  // ═══════════════════════════════════════════════════════════════

  const API_BULK = `/api/load_files/project/${PROJECT_ID}/bulk_custody/`;
  let bulkSheetId     = null;
  let bulkChains      = [];   // [{id, consecutive, label, date}]
  let bulkSelectedIds = [];   // IDs seleccionados en orden

  /**
   * Abre el modal de carga masiva para una planilla.
   * Recupera las cadenas de la planilla del treeData en memoria.
   */
  window.openBulkCustodyModal = function (sheetId) {
    bulkSheetId = sheetId;
    bulkChains  = [];
    bulkSelectedIds = [];

    // Buscar la planilla y sus cadenas en treeData
    const sheet = treeData.sheets.find(s => s.id === sheetId);
    if (!sheet || !sheet.custody_chains.length) {
      showToast('No hay cadenas de custodia en esta planilla.', 'error');
      return;
    }

    document.getElementById('bulkSheetLabel').textContent =
      `${sheet.label} — ${sheet.period}`;

    bulkChains = sheet.custody_chains.map((c, idx) => ({
      id: c.id,
      consecutive: c.label,
      date: c.date || '',
      index: idx,
      hasFile: c.files.some(f => f.has_file),
    }));

    renderBulkChainList();
    resetBulkUI();
    document.getElementById('bulkCustodyModal').showModal();
  };

  /** Renderiza el listado con checkboxes */
  function renderBulkChainList() {
    const container = document.getElementById('bulkChainList');
    container.innerHTML = '';

    bulkChains.forEach((chain, idx) => {
      const row = document.createElement('label');
      row.className = 'flex items-center gap-3 p-2 rounded-md hover:bg-gray-100 cursor-pointer';
      row.innerHTML = `
        <input type="checkbox" class="checkbox checkbox-sm checkbox-primary bulk-chain-cb"
               data-chain-id="${chain.id}" data-index="${idx}"
               onchange="bulkSelectionChanged()" />
        <span class="text-sm font-medium flex-1">
          <span class="font-semibold">${idx + 1}.</span>
          ${chain.consecutive}
          <span class="text-gray-400 ml-1">${chain.date}</span>
        </span>
        ${chain.hasFile
          ? '<span class="badge badge-sm badge-success gap-1"><i class="las la-check-circle"></i> Cargado</span>'
          : '<span class="badge badge-sm badge-error gap-1"><i class="las la-times-circle"></i> Pendiente</span>'
        }`;
      container.appendChild(row);
    });
  }

  /** Actualiza el conteo y habilita/deshabilita el botón */
  window.bulkSelectionChanged = function () {
    const checked = document.querySelectorAll('.bulk-chain-cb:checked');
    bulkSelectedIds = Array.from(checked).map(cb => parseInt(cb.dataset.chainId));
    document.getElementById('bulkSelectedCount').textContent = bulkSelectedIds.length;
    validateBulkReady();
  };

  // ── Selección rápida ──────────────────────────────────────
  window.bulkSelectAll = function () {
    document.querySelectorAll('.bulk-chain-cb').forEach(cb => cb.checked = true);
    bulkSelectionChanged();
  };

  window.bulkSelectNone = function () {
    document.querySelectorAll('.bulk-chain-cb').forEach(cb => cb.checked = false);
    bulkSelectionChanged();
  };

  window.bulkSelectEvens = function () {
    document.querySelectorAll('.bulk-chain-cb').forEach((cb, i) => cb.checked = (i % 2 === 1)); // posiciones pares (2,4,6…)
    bulkSelectionChanged();
  };

  window.bulkSelectOdds = function () {
    document.querySelectorAll('.bulk-chain-cb').forEach((cb, i) => cb.checked = (i % 2 === 0)); // posiciones impares (1,3,5…)
    bulkSelectionChanged();
  };

  // ── Validar archivo seleccionado ──────────────────────────
  window.bulkFileSelected = function () {
    const fileInput = document.getElementById('bulkFileInput');
    const infoDiv   = document.getElementById('bulkFileInfo');

    if (!fileInput.files.length) {
      infoDiv.classList.add('hidden');
      validateBulkReady();
      return;
    }

    const file = fileInput.files[0];
    document.getElementById('bulkFileName').textContent = file.name;

    // Leer el PDF para contar páginas en el cliente
    const reader = new FileReader();
    reader.onload = function (e) {
      const data = new Uint8Array(e.target.result);
      const pageCount = countPDFPages(data);
      document.getElementById('bulkPageCount').textContent = pageCount;
      infoDiv.classList.remove('hidden');
      infoDiv.dataset.pages = pageCount;
      validateBulkReady();
    };
    reader.readAsArrayBuffer(file);
  };

  /**
   * Cuenta páginas de un PDF de forma básica buscando /Type /Page
   * (sin dependencias externas). Es una aproximación.
   */
  function countPDFPages(data) {
    // Buscar en el PDF la cantidad de /Page entries
    // Método simple: buscar /Type /Page o /Type/Page
    const text = new TextDecoder('latin1').decode(data);
    const matches = text.match(/\/Type\s*\/Page(?!s)/g);
    return matches ? matches.length : 0;
  }

  /** Valida si todo está listo para el envío */
  function validateBulkReady() {
    const btn = document.getElementById('bulkConfirmBtn');
    const msgDiv = document.getElementById('bulkMsg');
    const fileInput = document.getElementById('bulkFileInput');
    const infoDiv = document.getElementById('bulkFileInfo');

    const numSelected = bulkSelectedIds.length;
    const hasFile = fileInput.files.length > 0;
    const numPages = parseInt(infoDiv.dataset.pages || '0');

    // Resetear mensajes
    msgDiv.classList.add('hidden');

    if (numSelected === 0 || !hasFile) {
      btn.disabled = true;
      return;
    }

    if (numPages > 0 && numPages !== numSelected) {
      msgDiv.innerHTML = `
        <div class="alert alert-error text-sm py-2">
          <i class="las la-exclamation-triangle text-lg"></i>
          <span>El PDF tiene <strong>${numPages}</strong> página(s) pero se seleccionaron
          <strong>${numSelected}</strong> cadena(s). Deben coincidir exactamente.</span>
        </div>`;
      msgDiv.classList.remove('hidden');
      btn.disabled = true;
      return;
    }

    btn.disabled = false;
  }

  /** Confirma y envía la carga masiva al backend */
  window.confirmBulkUpload = function () {
    const fileInput = document.getElementById('bulkFileInput');
    if (!fileInput.files.length || bulkSelectedIds.length === 0) return;

    const fd = new FormData();
    fd.append('file', fileInput.files[0]);
    fd.append('chain_ids', JSON.stringify(bulkSelectedIds));

    document.getElementById('bulkConfirmBtn').disabled = true;
    document.getElementById('bulkProgress').classList.remove('hidden');
    document.getElementById('bulkMsg').classList.add('hidden');
    document.getElementById('bulkResult').classList.add('hidden');

    fetch(API_BULK, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF },
      body: fd,
    })
      .then(r => r.json())
      .then(json => {
        document.getElementById('bulkProgress').classList.add('hidden');

        if (json.success) {
          document.getElementById('bulkResultText').textContent = json.message;
          document.getElementById('bulkResult').classList.remove('hidden');
          showToast(json.message, 'success');

          // Refrescar el árbol después de un momento
          setTimeout(() => {
            closeBulkModal();
            fetchTree();
          }, 1500);
        } else {
          const errorMsg = json.error || 'Error desconocido';
          document.getElementById('bulkMsg').innerHTML = `
            <div class="alert alert-error text-sm py-2">
              <i class="las la-exclamation-triangle text-lg"></i>
              <span>${errorMsg}</span>
            </div>`;
          document.getElementById('bulkMsg').classList.remove('hidden');
          document.getElementById('bulkConfirmBtn').disabled = false;
        }
      })
      .catch(err => {
        document.getElementById('bulkProgress').classList.add('hidden');
        document.getElementById('bulkMsg').innerHTML = `
          <div class="alert alert-error text-sm py-2">
            <i class="las la-exclamation-triangle text-lg"></i>
            <span>Error: ${err.message}</span>
          </div>`;
        document.getElementById('bulkMsg').classList.remove('hidden');
        document.getElementById('bulkConfirmBtn').disabled = false;
      });
  };

  /** Cerrar el modal */
  window.closeBulkModal = function () {
    document.getElementById('bulkCustodyModal').close();
    bulkSheetId = null;
    bulkChains = [];
    bulkSelectedIds = [];
  };

  /** Reset UI del modal */
  function resetBulkUI() {
    document.getElementById('bulkFileInput').value = '';
    document.getElementById('bulkFileInfo').classList.add('hidden');
    document.getElementById('bulkFileInfo').dataset.pages = '0';
    document.getElementById('bulkMsg').classList.add('hidden');
    document.getElementById('bulkProgress').classList.add('hidden');
    document.getElementById('bulkResult').classList.add('hidden');
    document.getElementById('bulkConfirmBtn').disabled = true;
    document.getElementById('bulkSelectedCount').textContent = '0';
  }
})();
