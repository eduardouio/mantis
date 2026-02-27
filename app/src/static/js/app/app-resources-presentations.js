// Interactividad para la ficha de recurso: toggles del checklist, cambio de activo/inactivo y actualización de estado técnico
(() => {
	const container = document.querySelector('[data-equipment-id][data-api-update]');
	if (!container) return;

	const equipmentId = container.getAttribute('data-equipment-id');
	const apiUrl = container.getAttribute('data-api-update');

	// Helpers UI
	const techStatusEls = Array.from(document.querySelectorAll('[data-tech-status]'));
	const setTechStatus = (status) => {
		techStatusEls.forEach((el) => {
			const variant = el.getAttribute('data-variant') || 'badge';
			// Limpiar clases de color
			if (variant === 'badge') {
				el.classList.remove('badge-success', 'badge-warning', 'badge-error', 'badge-neutral');
			} else {
				el.classList.remove('bg-green-600', 'bg-yellow-600', 'bg-red-600', 'bg-gray-600');
			}
			// Asignar por estado
			let cls;
			if (variant === 'badge') {
				if (status === 'FUNCIONANDO') cls = 'badge-success';
				else if (status === 'INCOMPLETO') cls = 'badge-warning';
				else if (status === 'EN REPARACION' || status === 'DAÑADO' || status === 'DANADO') cls = 'badge-error';
				else cls = 'badge-neutral';
			} else {
				if (status === 'FUNCIONANDO') cls = 'bg-green-600';
				else if (status === 'INCOMPLETO') cls = 'bg-yellow-600';
				else if (status === 'EN REPARACION' || status === 'DAÑADO' || status === 'DANADO') cls = 'bg-red-600';
				else cls = 'bg-gray-600';
			}
			el.classList.add(cls);
			el.textContent = status || '—';
		});
	};

	// Badge Activo/Inactivo
	const activeBadge = document.querySelector('[data-active-badge]');
	const setActiveBadge = (isActive) => {
		if (!activeBadge) return;
		activeBadge.classList.remove('badge-success', 'badge-error');
		if (isActive) {
			activeBadge.classList.add('badge-success');
			activeBadge.textContent = 'ACTIVO';
		} else {
			activeBadge.classList.add('badge-error');
			activeBadge.textContent = 'INACTIVO';
		}
	};

	// Notificación mínima (fallback con alert)
	const notify = (msg, type = 'info') => {
		if (window.toast) {
			window.toast(msg, { type });
		} else {
			// Evitar bloquear demasiado
			console.log(`[${type}]`, msg);
		}
	};

	const sendUpdate = async (payload) => {
		const resp = await fetch(apiUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload),
			credentials: 'same-origin',
		});
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok || !data.success) {
			const err = (data && (data.error || data.details)) || `HTTP ${resp.status}`;
			throw new Error(typeof err === 'string' ? err : JSON.stringify(err));
		}
		return data;
	};

	// Delegación de eventos para checkboxes
	container.addEventListener('change', async (ev) => {
		const target = ev.target;
		if (!(target instanceof HTMLInputElement)) return;

		const isFieldToggle = target.classList.contains('js-field-toggle');
		const isHaveToggle = target.classList.contains('js-have-toggle');
		if (!isFieldToggle && !isHaveToggle) return;

		const field = target.getAttribute('data-field');
		if (!field) return;

		const newVal = !!target.checked;
		const previous = !newVal; // para revertir si falla
		target.disabled = true;
		target.classList.add('opacity-60', 'cursor-wait');
		try {
			const payload = { id: Number(equipmentId) };
			payload[field] = newVal;
			const res = await sendUpdate(payload);
			if (res && res.data) {
				if (isHaveToggle && res.data.stst_status_equipment) {
					setTechStatus(res.data.stst_status_equipment);
				}
				if (field === 'is_active' && typeof res.data.is_active !== 'undefined') {
					setActiveBadge(!!res.data.is_active);
				}
			}
			notify('Actualizado', 'success');
		} catch (e) {
			// revertir UI
			target.checked = previous;
			notify(`No se pudo actualizar: ${e.message || e}`, 'error');
		} finally {
			target.disabled = false;
			target.classList.remove('opacity-60', 'cursor-wait');
		}
	});

	// ---- FILE UPLOAD via /api/load_files/ ----
	const UPLOAD_API = '/api/load_files/';
	const globalMsg = document.getElementById('uploadGlobalMsg');

	function showGlobalMsg(msg, ok=true){
		if(!globalMsg) return;
		globalMsg.textContent = msg;
		globalMsg.className = ok
			? 'mb-4 p-3 rounded-lg text-sm bg-green-50 text-green-700 border border-green-200'
			: 'mb-4 p-3 rounded-lg text-sm bg-red-50 text-red-700 border border-red-200';
		globalMsg.classList.remove('hidden');
		setTimeout(()=> globalMsg.classList.add('hidden'), 4000);
	}

	function setRowLoading(row, loading){
		const btns = row.querySelectorAll('.btn');
		btns.forEach(b => { b.disabled = loading; if(loading) b.classList.add('opacity-50'); else b.classList.remove('opacity-50'); });
	}

	function rebuildRowButtons(row, fileUrl){
		const actionsDiv = row.querySelector('.flex.items-center.gap-1');
		if(!actionsDiv) return;
		actionsDiv.innerHTML = '';

		if(fileUrl){
			const link = document.createElement('a');
			link.href = fileUrl; link.target = '_blank';
			link.className = 'btn btn-xs btn-info'; link.title = 'Ver';
			link.innerHTML = '<i class="las la-eye"></i>';
			actionsDiv.appendChild(link);

			const delBtn = document.createElement('button');
			delBtn.type = 'button';
			delBtn.className = 'btn btn-xs btn-error btn-file-delete'; delBtn.title = 'Eliminar archivo';
			delBtn.innerHTML = '<i class="las la-trash"></i>';
			actionsDiv.appendChild(delBtn);
		}

		const label = document.createElement('label');
		label.className = 'btn btn-xs btn-success btn-file-upload'; label.title = 'Subir imagen';
		label.innerHTML = '<i class="las la-upload"></i><input type="file" accept="image/*" class="hidden file-input-hidden">';
		actionsDiv.appendChild(label);

		bindRowEvents(row);
	}

	async function uploadFile(row, file){
		const modelType = row.dataset.modelType;
		const objectId = row.dataset.objectId;
		const fieldName = row.dataset.fieldName;

		const formData = new FormData();
		formData.append('model_type', modelType);
		formData.append('object_id', objectId);
		formData.append('field_name', fieldName);
		formData.append('file', file);

		setRowLoading(row, true);
		try {
			const resp = await fetch(UPLOAD_API, { method: 'POST', body: formData, credentials: 'same-origin' });
			const data = await resp.json();
			if(!resp.ok || !data.success) throw new Error(data.error || 'Error al subir');
			showGlobalMsg('Imagen subida correctamente');
			rebuildRowButtons(row, data.data.file_url);
		} catch(err){
			showGlobalMsg(err.message, false);
		} finally {
			setRowLoading(row, false);
		}
	}

	async function deleteFile(row){
		const modelType = row.dataset.modelType;
		const objectId = row.dataset.objectId;
		const fieldName = row.dataset.fieldName;

		if(!confirm('¿Eliminar esta imagen?')) return;

		setRowLoading(row, true);
		try {
			const url = `${UPLOAD_API}?model_type=${modelType}&object_id=${objectId}&field_name=${fieldName}`;
			const resp = await fetch(url, { method: 'DELETE', credentials: 'same-origin' });
			const data = await resp.json();
			if(!resp.ok || !data.success) throw new Error(data.error || 'Error al eliminar');
			showGlobalMsg('Imagen eliminada correctamente');
			rebuildRowButtons(row, null);
		} catch(err){
			showGlobalMsg(err.message, false);
		} finally {
			setRowLoading(row, false);
		}
	}

	function bindRowEvents(row){
		const fileInput = row.querySelector('.file-input-hidden');
		if(fileInput && !fileInput.dataset.bound){
			fileInput.addEventListener('change', function(){ if(this.files[0]) uploadFile(row, this.files[0]); this.value = ''; });
			fileInput.dataset.bound = '1';
		}
		const delBtn = row.querySelector('.btn-file-delete');
		if(delBtn && !delBtn.dataset.bound){
			delBtn.addEventListener('click', function(){ deleteFile(row); });
			delBtn.dataset.bound = '1';
		}
	}

	document.querySelectorAll('.file-upload-row').forEach(row => bindRowEvents(row));
})();

