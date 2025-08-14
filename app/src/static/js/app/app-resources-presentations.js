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
})();

