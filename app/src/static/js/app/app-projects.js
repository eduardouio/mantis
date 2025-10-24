// App de Proyecto (Vue 3) con delimitadores ${ }
// Esta app evita conflictos con Django ({{ }}) usando ${ } para interpolación.
// Reemplaza la lógica imperativa anterior por un estado y métodos en Vue.

(function () {
	if (!window.Vue) {
		console.warn('[projectApp] Vue no está cargado');
		return;
	}

	const { createApp } = window.Vue;

	const root = document.getElementById('projectApp');
	if (!root) return;

	const dataset = root.dataset || {};

	const app = createApp({
		// Evitamos conflicto con Django
		delimiters: ['${', '}'],
		data() {
			return {
				csrfToken: dataset.csrf || '',
				projectId: Number(dataset.projectId || 0),
				projectStart: dataset.startDate || '',
				projectEnd: dataset.endDate || '',
				// Estado de equipos
				availableEquipment: [],
				selectedEquipmentId: null,
				searchTerm: '',
				// Flags
				loadingEquipment: false,
			};
		},
		methods: {
			// ===== Equipos asignables =====
			loadAvailableEquipment() {
				const tbody = document.getElementById('available_equipment_tbody');
				if (tbody) {
					tbody.innerHTML = `
						<tr>
							<td colspan="8" class="text-center py-4">
								<span class="loading loading-spinner loading-md"></span>
								<p>Cargando equipos disponibles...</p>
							</td>
						</tr>
					`;
				}
				this.loadingEquipment = true;
				fetch('/api/projects/resources/available?exclude_services=true')
					.then(r => r.json())
					.then(data => {
						// Normalización básica de respuesta
						const items = (data && (data.data || data.results || data.items || data)) || [];
						this.availableEquipment = Array.isArray(items) ? items : [];
						this.renderEquipmentTable(this.availableEquipment);
					})
					.catch(err => {
						this.showError('Error de conexión: ' + err.message);
					})
					.finally(() => {
						this.loadingEquipment = false;
					});
			},
			renderEquipmentTable(equipment) {
				const tbody = document.getElementById('available_equipment_tbody');
				if (!tbody) return;

				if (!equipment || equipment.length === 0) {
					tbody.innerHTML = `
						<tr>
							<td colspan="8" class="text-center py-4 text-gray-500">
								<i class="las la-inbox text-4xl"></i>
								<p>No hay equipos disponibles</p>
							</td>
						</tr>
					`;
					return;
				}

				// Renderizado mínimo compatible (id, code, name, etc.)
				tbody.innerHTML = equipment.map(eq => `
					<tr class="hover">
						<td>
							<input 
								type="radio" 
								name="equipment_selection" 
								class="radio radio-primary radio-sm" 
								value="${eq.id}"
								onchange="selectEquipment(${eq.id})"
							/>
						</td>
						<td class="font-mono text-xs">${(eq.code || '').toString()}</td>
						<td class="text-xs">${(eq.name || '').toString()}</td>
						<td class="text-xs">${eq.type_equipment_display || eq.type_equipment || 'N/A'}</td>
						<td class="text-xs">${eq.brand || 'N/A'}</td>
						<td class="text-xs">${eq.model || 'N/A'}</td>
						<td class="text-xs">${eq.status_equipment || 'N/A'}</td>
						<td class="text-xs">${eq.current_location || 'N/A'}</td>
					</tr>
				`).join('');
			},
			filterEquipment() {
				const input = document.getElementById('search_equipment');
				const term = (input ? input.value : this.searchTerm || '').toLowerCase();
				const filtered = this.availableEquipment.filter(eq => {
					const code = (eq.code || '').toString().toLowerCase();
					const name = (eq.name || '').toString().toLowerCase();
					const brand = (eq.brand || '').toString().toLowerCase();
					const model = (eq.model || '').toString().toLowerCase();
					return !term || code.includes(term) || name.includes(term) || brand.includes(term) || model.includes(term);
				});
				this.renderEquipmentTable(filtered);
			},
			selectEquipment(equipmentId) {
				this.selectedEquipmentId = equipmentId;
				const equipment = this.availableEquipment.find(eq => eq.id === equipmentId);
				if (equipment) {
					const form = document.getElementById('assignment_form');
					if (form) form.classList.remove('hidden');
					const nameEl = document.getElementById('selected_equipment_name');
					const codeEl = document.getElementById('selected_equipment_code');
					if (nameEl) nameEl.value = equipment.name || '';
					if (codeEl) codeEl.value = equipment.code || '';
					form && form.scrollIntoView({ behavior: 'smooth' });
				}
			},
			resetAssignmentForm() {
				const form = document.getElementById('assignment_form');
				if (form) form.classList.add('hidden');
				this.selectedEquipmentId = null;
				// Limpiar selección de radios
				document.querySelectorAll('input[name="equipment_selection"]').forEach(r => (r.checked = false));
				// Limpiar campos
				const rent = document.getElementById('rent_cost');
				const maint = document.getElementById('maintenance_cost');
				const start = document.getElementById('operation_start_date');
				const end = document.getElementById('operation_end_date');
				const interval = document.getElementById('maintenance_interval');
				if (rent) rent.value = '';
				if (maint) maint.value = '';
				if (start) start.value = this.projectStart || '';
				if (end) end.value = this.projectEnd || '';
				if (interval) interval.value = '15';
			},
			saveAssignment() {
				if (!this.selectedEquipmentId) {
					this.showError('Debe seleccionar un equipo');
					return;
				}
				const rentCost = (document.getElementById('rent_cost') || {}).value;
				const maintenanceCost = (document.getElementById('maintenance_cost') || {}).value;
				const startDate = (document.getElementById('operation_start_date') || {}).value;
				if (!rentCost || !maintenanceCost || !startDate) {
					this.showError('Debe completar todos los campos requeridos');
					return;
				}
				const assignmentData = {
					project_id: this.projectId,
					resource_item_id: this.selectedEquipmentId,
					rent_cost: Number.parseFloat(rentCost).toFixed(2),
					maintenance_cost: Number.parseFloat(maintenanceCost).toFixed(2),
					operation_start_date: startDate,
					operation_end_date: (document.getElementById('operation_end_date') || {}).value || null,
					maintenance_interval_days: parseInt((document.getElementById('maintenance_interval') || {}).value || '0') || 0,
				};
				const btn = document.getElementById('btn_save_assignment');
				if (btn) {
					btn.disabled = true;
					btn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Guardando...';
				}
				fetch('/api/projects/resources/add', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						'X-CSRFToken': this.csrfToken,
					},
					body: JSON.stringify(assignmentData),
				})
					.then(r => r.json())
					.then(data => {
						if (data && data.success) {
							this.showSuccess('Equipo asignado correctamente');
							setTimeout(() => {
								const modal = document.getElementById('modal_assign_equipment');
								if (modal && typeof modal.close === 'function') modal.close();
								this.resetAssignmentForm();
							}, 1500);
						} else {
							this.showError('Error al guardar: ' + (data && (data.error || data.message) || 'Desconocido'));
							if (btn) {
								btn.disabled = false;
								btn.innerHTML = '<i class="las la-save"></i> Guardar Asignación';
							}
						}
					})
					.catch(err => {
						this.showError('Error de conexión: ' + err.message);
						if (btn) {
							btn.disabled = false;
							btn.innerHTML = '<i class="las la-save"></i> Guardar Asignación';
						}
					});
			},
			// ===== Toasts =====
			showError(message) {
				const toast = document.createElement('div');
				toast.className = 'alert alert-error shadow-lg fixed top-4 right-4 w-96 z-50';
				toast.innerHTML = `
					<div>
						<i class="las la-times-circle"></i>
						<span>${message}</span>
					</div>
				`;
				document.body.appendChild(toast);
				setTimeout(() => toast.remove(), 5000);
			},
			showSuccess(message) {
				const toast = document.createElement('div');
				toast.className = 'alert alert-success shadow-lg fixed top-4 right-4 w-96 z-50';
				toast.innerHTML = `
					<div>
						<i class="las la-check-circle"></i>
						<span>${message}</span>
					</div>
				`;
				document.body.appendChild(toast);
				setTimeout(() => toast.remove(), 5000);
			},
			// ===== Planillas (SheetProject) =====
			loadNextSeriesCode() {
				fetch('/api/workorders/sheets/?next_series=true')
					.then(r => r.json())
					.then(data => {
						const code = data && (data.data && data.data.series_code || data.series_code);
						const input = document.getElementById('sheet_series_code');
						if (input && code) input.value = code;
					})
					.catch(() => {/* opcional: silencioso */});
			},
			resetSheetForm() {
				const ids = [
					'sheet_series_code',
					'sheet_service_type',
					'sheet_issue_date',
					'sheet_period_start',
					'sheet_period_end',
					'sheet_contact_reference',
					'sheet_contact_phone_reference',
				];
				ids.forEach(id => {
					const el = document.getElementById(id);
					if (!el) return;
					if (id === 'sheet_series_code') el.value = 'Cargando...';
					else if (id === 'sheet_service_type') el.value = 'ALQUILER DE EQUIPOS';
					else el.value = '';
				});
				const modal = document.getElementById('modal_create_sheet');
				if (modal && typeof modal.close === 'function') modal.close();
			},
			saveSheet() {
				const periodStart = (document.getElementById('sheet_period_start') || {}).value;
				if (!periodStart) {
					this.showError('El período de inicio es requerido');
					return;
				}
				const sheetData = {
					project_id: this.projectId,
					series_code: (document.getElementById('sheet_series_code') || {}).value,
					service_type: (document.getElementById('sheet_service_type') || {}).value,
					issue_date: (document.getElementById('sheet_issue_date') || {}).value || null,
					period_start: periodStart,
					period_end: (document.getElementById('sheet_period_end') || {}).value || null,
					contact_reference: (document.getElementById('sheet_contact_reference') || {}).value || null,
					contact_phone_reference: (document.getElementById('sheet_contact_phone_reference') || {}).value || null,
					status: 'IN_PROGRESS',
					subtotal: 0,
					tax_amount: 0,
					total: 0,
				};
				const btn = document.getElementById('btn_save_sheet');
				if (btn) {
					btn.disabled = true;
					btn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Guardando...';
				}
				fetch('/api/workorders/sheets/create', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						'X-CSRFToken': this.csrfToken,
					},
					body: JSON.stringify(sheetData),
				})
					.then(r => r.json())
					.then(data => {
						if (data && data.success) {
							this.showSuccess('Planilla creada correctamente');
							setTimeout(() => {
								const modal = document.getElementById('modal_create_sheet');
								if (modal && typeof modal.close === 'function') modal.close();
								this.resetSheetForm();
							}, 1500);
						} else {
							this.showError(data && (data.error || data.message) || 'Error al crear planilla');
							if (btn) {
								btn.disabled = false;
								btn.innerHTML = '<i class="las la-save"></i> Crear Planilla';
							}
						}
					})
					.catch(err => {
						this.showError('Error de conexión: ' + err.message);
						if (btn) {
							btn.disabled = false;
							btn.innerHTML = '<i class="las la-save"></i> Crear Planilla';
						}
					});
			},
		},
		mounted() {
			// Observa apertura de modal de equipos para cargar lista
			const modalEquipment = document.getElementById('modal_assign_equipment');
			if (modalEquipment) {
				const observerEquipment = new MutationObserver((mutations) => {
					mutations.forEach((mutation) => {
						if (mutation.attributeName === 'open' && modalEquipment.hasAttribute('open')) {
							this.loadAvailableEquipment();
						}
					});
				});
				observerEquipment.observe(modalEquipment, { attributes: true });
			}

			// Observa apertura de modal de planilla para precargar serie
			const modalSheet = document.getElementById('modal_create_sheet');
			if (modalSheet) {
				const observerSheet = new MutationObserver((mutations) => {
					mutations.forEach((mutation) => {
						if (mutation.attributeName === 'open' && modalSheet.hasAttribute('open')) {
							this.loadNextSeriesCode();
						}
					});
				});
				observerSheet.observe(modalSheet, { attributes: true });
			}

			// Wire de controles existentes
			const searchInput = document.getElementById('search_equipment');
			if (searchInput) {
				searchInput.addEventListener('input', () => this.filterEquipment());
			}
			const btnSaveAssignment = document.getElementById('btn_save_assignment');
			if (btnSaveAssignment) {
				btnSaveAssignment.addEventListener('click', () => this.saveAssignment());
			}
			const btnSaveSheet = document.getElementById('btn_save_sheet');
			if (btnSaveSheet) {
				btnSaveSheet.addEventListener('click', () => this.saveSheet());
			}
			// Fecha por defecto para emisión
			const issueDate = document.getElementById('sheet_issue_date');
			if (issueDate && !issueDate.value) {
				issueDate.value = new Date().toISOString().split('T')[0];
			}

			// Exponer seleccionador para radios renderizados dinámicamente
			window.selectEquipment = (id) => this.selectEquipment(id);
			// Exponer helpers (opcional)
			window.ProjectApp = this;
		},
	});

	app.mount('#projectApp');
})();

