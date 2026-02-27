/**
 * app-file-manager.js
 * Gestor de Documentos – árbol interactivo con carga / descarga / eliminación.
 * Usa la API centralizada /api/load_files/ y /api/load_files/tree/
 */
(function () {
  'use strict';

  const API_TREE   = '/api/load_files/tree/';
  const API_FILES  = '/api/load_files/';
  const CSRF       = getCookie('csrftoken');

  // ── Estado global ──────────────────────────────────────────────
  let treeData     = {};          // respuesta cruda del backend
  let activeTab    = 'technicals';
  let uploadTarget = null;        // { model_type, object_id, field_name }

  // ── Inicialización ─────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    fetchTree();
    document.getElementById('searchInput').addEventListener('input', debounce(onSearch, 300));
  });

  // ── Fetch del árbol ────────────────────────────────────────────
  function fetchTree() {
    showLoading(true);
    fetch(API_TREE)
      .then(r => r.json())
      .then(json => {
        if (!json.success) throw new Error(json.error);
        treeData = json.data;
        updateStats();
        renderTab();
        showLoading(false);
      })
      .catch(err => {
        showLoading(false);
        showToast('Error al cargar documentos: ' + err.message, 'error');
      });
  }

  // ── Estadísticas ───────────────────────────────────────────────
  function updateStats() {
    let total = 0, loaded = 0;
    const count = (nodes) => {
      if (!nodes) return;
      (Array.isArray(nodes) ? nodes : [nodes]).forEach(n => {
        if (n.files) n.files.forEach(f => { total++; if (f.has_file) loaded++; });
        if (n.children) count(n.children);
      });
    };
    Object.values(treeData).forEach(cat => count(cat));

    const pending = total - loaded;
    const pct = total > 0 ? Math.round((loaded / total) * 100) : 0;

    document.getElementById('statTotal').textContent   = total;
    document.getElementById('statLoaded').textContent  = loaded;
    document.getElementById('statPending').textContent = pending;
    document.getElementById('statPercent').textContent = pct + '%';
  }

  // ── Tabs ───────────────────────────────────────────────────────
  window.switchTab = function (tab) {
    activeTab = tab;
    document.querySelectorAll('.fm-tab').forEach(t => {
      t.classList.toggle('tab-active', t.dataset.tab === tab);
    });
    renderTab();
  };

  // ── Render del tab activo ──────────────────────────────────────
  function renderTab() {
    const container = document.getElementById('treeContent');
    container.innerHTML = '';

    const nodes = treeData[activeTab];
    if (!nodes || nodes.length === 0) {
      container.innerHTML = `
        <div class="flex flex-col items-center justify-center py-16 text-gray-400">
          <i class="las la-folder-open text-5xl mb-2"></i>
          <p class="text-sm">No hay registros en esta categoría</p>
        </div>`;
      return;
    }

    nodes.forEach(node => container.appendChild(buildNode(node, 0)));
  }

  // ── Construir un nodo del árbol ────────────────────────────────
  function buildNode(node, depth) {
    const div = document.createElement('div');
    div.className = 'tree-node';
    div.dataset.search = (node.label || '').toLowerCase() + ' ' + (node.dni || '').toLowerCase();

    const hasChildren = node.children && node.children.length > 0;
    const hasFiles    = node.files && node.files.length > 0;

    // Toggle header
    const toggle = document.createElement('div');
    toggle.className = 'tree-toggle';
    toggle.innerHTML = buildToggleHTML(node, hasChildren, hasFiles, depth);

    // Children container
    const childrenDiv = document.createElement('div');
    childrenDiv.className = 'tree-children';

    // Archivos del nodo
    if (hasFiles) {
      childrenDiv.appendChild(buildFilesTable(node.files, node.detail_url));
    }

    // Hijos recursivos
    if (hasChildren) {
      node.children.forEach(child => {
        childrenDiv.appendChild(buildNode(child, depth + 1));
      });
    }

    // Click para expandir/colapsar
    if (hasChildren || hasFiles) {
      toggle.addEventListener('click', () => {
        childrenDiv.classList.toggle('open');
        const chevron = toggle.querySelector('.tree-chevron');
        if (chevron) chevron.classList.toggle('rotated');
      });
    }

    div.appendChild(toggle);
    div.appendChild(childrenDiv);
    return div;
  }

  // ── HTML del toggle ────────────────────────────────────────────
  function buildToggleHTML(node, hasChildren, hasFiles, depth) {
    const icon   = getNodeIcon(node, depth);
    const chevron = (hasChildren || hasFiles)
      ? '<i class="las la-angle-right tree-chevron"></i>'
      : '<span style="width:1rem;display:inline-block"></span>';

    // Resumen rápido de archivos
    let badges = '';
    if (node.files) {
      const loaded = node.files.filter(f => f.has_file).length;
      const total  = node.files.length;
      if (loaded === total && total > 0) {
        badges = `<span class="file-badge has-file"><i class="las la-check-circle"></i> ${loaded}/${total}</span>`;
      } else {
        badges = `<span class="file-badge no-file"><i class="las la-exclamation-circle"></i> ${loaded}/${total}</span>`;
      }
    }

    // Contar archivos en hijos recursivamente
    if (node.children && node.children.length > 0) {
      let cTotal = 0, cLoaded = 0;
      countChildFiles(node, (t, l) => { cTotal += t; cLoaded += l; });
      if (cTotal > 0) {
        const cls = cLoaded === cTotal ? 'has-file' : 'no-file';
        badges += ` <span class="file-badge ${cls}" style="margin-left:2px"><i class="las la-folder"></i> ${cLoaded}/${cTotal}</span>`;
      }
    }

    // Link a la vista correspondiente
    const detailLink = node.detail_url
      ? `<a href="${node.detail_url}" class="text-blue-500 hover:text-blue-700 ml-1" title="Ver ficha" onclick="event.stopPropagation()"><i class="las la-external-link-alt text-sm"></i></a>`
      : '';

    // Link a documentos del proyecto (solo para nodos raíz en tab proyectos)
    const docsLink = (activeTab === 'projects' && !node.type)
      ? `<a href="/documentos/proyecto/${node.id}/" class="text-indigo-500 hover:text-indigo-700 ml-1" title="Ver documentos del proyecto" onclick="event.stopPropagation()"><i class="las la-folder-open text-sm"></i></a>`
      : '';

    return `${chevron} <i class="${icon} text-lg"></i>
            <span class="text-sm font-medium">${node.label}</span>
            ${detailLink} ${docsLink} ${badges}`;
  }

  function countChildFiles(node, cb) {
    if (node.files) {
      cb(node.files.length, node.files.filter(f => f.has_file).length);
    }
    if (node.children) node.children.forEach(c => countChildFiles(c, cb));
  }

  // ── Iconos por tipo/profundidad ────────────────────────────────
  function getNodeIcon(node, depth) {
    if (node.type === 'pass_technical' || node.type === 'pass_vehicle') return 'las la-id-card text-amber-500';
    if (node.type === 'vaccination_record')  return 'las la-syringe text-green-500';
    if (node.type === 'certification_vehicle') return 'las la-certificate text-purple-500';
    if (node.type === 'sheet_project')  return 'las la-file-invoice text-indigo-500';
    if (node.type === 'custody_chain')  return 'las la-link text-cyan-600';
    if (node.type === 'shipping_guide') return 'las la-shipping-fast text-orange-500';

    // Por tab
    if (activeTab === 'technicals') return 'las la-user-tie text-blue-500';
    if (activeTab === 'vehicles')   return 'las la-truck text-emerald-500';
    if (activeTab === 'equipment')  return 'las la-desktop text-violet-500';
    if (activeTab === 'projects')   return 'las la-project-diagram text-rose-500';
    return 'las la-folder text-gray-500';
  }

  // ── Tabla de archivos ──────────────────────────────────────────
  function buildFilesTable(files, detailUrl) {
    const wrapper = document.createElement('div');
    wrapper.className = 'ml-6 mb-1';

    const table = document.createElement('table');
    table.className = 'file-table';

    files.forEach(f => {
      const tr = document.createElement('tr');
      tr.id = `file-row-${f.model_type}-${f.object_id}-${f.field_name}`;

      const tdLabel = document.createElement('td');
      tdLabel.className = 'font-medium whitespace-nowrap';
      tdLabel.textContent = f.field_label;

      const tdStatus = document.createElement('td');
      tdStatus.className = 'w-48';
      if (f.has_file) {
        tdStatus.innerHTML = `<span class="text-green-600 text-xs flex items-center gap-1">
          <i class="las la-check-circle"></i> ${f.file_name}
        </span>`;
      } else {
        tdStatus.innerHTML = `<span class="text-red-400 text-xs flex items-center gap-1">
          <i class="las la-times-circle"></i> Sin archivo
        </span>`;
      }

      const tdActions = document.createElement('td');
      tdActions.className = 'text-right whitespace-nowrap';
      tdActions.innerHTML = buildFileActions(f);

      tr.appendChild(tdLabel);
      tr.appendChild(tdStatus);
      tr.appendChild(tdActions);
      table.appendChild(tr);
    });

    wrapper.appendChild(table);
    return wrapper;
  }

  // ── Botones de acción por archivo ──────────────────────────────
  function buildFileActions(f) {
    const mt = f.model_type, oid = f.object_id, fn = f.field_name;
    let html = '';

    // Subir / Reemplazar
    html += `<button class="btn btn-xs btn-success btn-outline mr-1"
               title="${f.has_file ? 'Reemplazar' : 'Subir'}"
               onclick="openUploadModal('${mt}', ${oid}, '${fn}', '${escapeHtml(f.field_label)}')">
               <i class="las ${f.has_file ? 'la-sync-alt' : 'la-upload'}"></i>
             </button>`;

    if (f.has_file) {
      // Descargar
      html += `<a href="${f.file_url}" target="_blank" download
                 class="btn btn-xs btn-info btn-outline mr-1" title="Descargar">
                 <i class="las la-download"></i>
               </a>`;
      // Eliminar
      html += `<button class="btn btn-xs btn-error btn-outline"
                 title="Eliminar"
                 onclick="deleteFileAction('${mt}', ${oid}, '${fn}', '${escapeHtml(f.field_label)}')">
                 <i class="las la-trash"></i>
               </button>`;
    }

    return html;
  }

  // ── Modal de carga ─────────────────────────────────────────────
  window.openUploadModal = function (modelType, objectId, fieldName, label) {
    uploadTarget = { model_type: modelType, object_id: objectId, field_name: fieldName };
    document.getElementById('uploadLabel').textContent = label;
    document.getElementById('uploadContext').textContent =
      `Modelo: ${modelType} | ID: ${objectId} | Campo: ${fieldName}`;
    document.getElementById('uploadFileInput').value = '';
    document.getElementById('uploadMsg').classList.add('hidden');
    document.getElementById('uploadProgressContainer').classList.add('hidden');
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
    document.getElementById('uploadProgressContainer').classList.remove('hidden');

    fetch(API_FILES, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF },
      body: fd,
    })
      .then(r => r.json())
      .then(json => {
        document.getElementById('uploadProgressContainer').classList.add('hidden');
        if (json.success) {
          showToast('Archivo subido correctamente', 'success');
          closeUploadModal();
          fetchTree();  // recargar todo el árbol
        } else {
          showUploadMsg(json.error || 'Error al subir', 'error');
          document.getElementById('uploadConfirmBtn').disabled = false;
        }
      })
      .catch(err => {
        document.getElementById('uploadProgressContainer').classList.add('hidden');
        document.getElementById('uploadConfirmBtn').disabled = false;
        showUploadMsg('Error de conexión: ' + err.message, 'error');
      });
  };

  // ── Eliminar archivo ───────────────────────────────────────────
  window.deleteFileAction = function (modelType, objectId, fieldName, label) {
    if (!confirm(`¿Eliminar el archivo "${label}"?\nEsta acción no se puede deshacer.`)) return;

    const url = `${API_FILES}?model_type=${modelType}&object_id=${objectId}&field_name=${fieldName}`;
    fetch(url, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': CSRF },
    })
      .then(r => r.json())
      .then(json => {
        if (json.success) {
          showToast('Archivo eliminado', 'success');
          fetchTree();
        } else {
          showToast(json.error || 'Error al eliminar', 'error');
        }
      })
      .catch(err => showToast('Error de conexión: ' + err.message, 'error'));
  };

  // ── Expandir / Colapsar todo ───────────────────────────────────
  window.expandAll = function () {
    document.querySelectorAll('#treeContent .tree-children').forEach(el => el.classList.add('open'));
    document.querySelectorAll('#treeContent .tree-chevron').forEach(el => el.classList.add('rotated'));
  };

  window.collapseAll = function () {
    document.querySelectorAll('#treeContent .tree-children').forEach(el => el.classList.remove('open'));
    document.querySelectorAll('#treeContent .tree-chevron').forEach(el => el.classList.remove('rotated'));
  };

  // ── Búsqueda ───────────────────────────────────────────────────
  function onSearch() {
    const query = document.getElementById('searchInput').value.trim().toLowerCase();
    const nodes = document.querySelectorAll('#treeContent .tree-node');

    if (!query) {
      nodes.forEach(n => n.style.display = '');
      return;
    }

    nodes.forEach(n => {
      const text = n.dataset.search || '';
      const label = n.querySelector('.tree-toggle span.font-medium');
      if (text.includes(query)) {
        n.style.display = '';
        // Expandir padres
        let parent = n.parentElement;
        while (parent) {
          if (parent.classList.contains('tree-children')) parent.classList.add('open');
          const chevron = parent.previousElementSibling?.querySelector('.tree-chevron');
          if (chevron) chevron.classList.add('rotated');
          parent = parent.parentElement;
        }
      } else {
        // Ocultar solo nodos hoja que no coinciden
        const hasVisibleChild = Array.from(n.querySelectorAll('.tree-node'))
          .some(child => (child.dataset.search || '').includes(query));
        n.style.display = hasVisibleChild ? '' : 'none';
      }
    });
  }

  // ── Utilidades ─────────────────────────────────────────────────
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
    const toast   = document.getElementById('fmToast');
    const content = document.getElementById('fmToastContent');
    const text    = document.getElementById('fmToastText');

    content.className = 'alert ' + (type === 'success' ? 'alert-success' : 'alert-error');
    text.textContent = msg;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3500);
  }

  function escapeHtml(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
  }

  function debounce(fn, ms) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), ms);
    };
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
})();
