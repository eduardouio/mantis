// App de gestión de Pases y Vacunas para ficha de Técnico (vanilla JS)
// Usa endpoints:
//  Pases:  POST/PUT   /api/technicals/create_update_pass_technical/
//          DELETE     /api/technicals/delete_pass_technical/
//  Vacunas: POST/PUT  /api/technicals/create_update_vaccine/
//           DELETE    /api/technicals/delete_vaccine/

(function(){
	if(window.__TECH_PRES_INIT__){ return; }
	window.__TECH_PRES_INIT__ = true;
	const jsonEl = document.getElementById('technical-data');
	if(!jsonEl) return;
	let state = {};
	try { state = JSON.parse(jsonEl.textContent.trim()); } catch(e){ console.error('JSON technical-data invalido', e); return; }

	// ---- Utilidades ----
	const fetchJSON = async (url, options={}) => {
		const headers = options.headers || {}; headers['Content-Type'] = 'application/json';
		// CSRF token (Django) si existe cookie csrftoken
		const csrftoken = document.cookie.split(';').map(c=>c.trim()).find(c=>c.startsWith('csrftoken='));
		if(csrftoken) headers['X-CSRFToken'] = csrftoken.split('=')[1];
		const resp = await fetch(url, {credentials:'same-origin', ...options, headers});
		let data; try { data = await resp.json(); } catch(_){ data = {success:false, error:'No JSON'}; }
		if(!resp.ok || data.success === false) throw new Error(data.error || 'Error HTTP');
		return data;
	};

	const fmt = d => d ? new Date(d).toLocaleDateString('es-EC') : '';
	const qs = sel => document.querySelector(sel);
	const el = id => document.getElementById(id);
	const setMsg = (container, msg, ok=true) => { container.textContent = msg; container.className = ok? 'text-xs text-green-600':'text-xs text-red-600'; };

	// ---- PASES ----
	const passForm = el('passForm');
	const passId = el('pass_id');
	const passBloque = el('pass_bloque');
	const passFecha = el('pass_fecha_caducidad');
	const passSaveBtn = el('passSaveBtn');
	const passResetBtn = el('passResetBtn');
	const passDeleteBtn = el('passDeleteBtn');
	const passMsg = el('passFormMsg');
	const passList = el('passList');
	const passMeta = el('passMeta');
	const passMetaContent = el('passMetaContent');

	// Guardar opciones originales de bloque para reconstruir
	let originalBloqueOptions = null;
	function cacheOriginalBloqueOptions(){
		if(originalBloqueOptions) return; // ya cacheado
		originalBloqueOptions = Array.from(passBloque.options).map(o=>({value:o.value, text:o.textContent}));
	}

	function refreshPassBloqueOptions(currentEditingBloque=null){
		if(!passBloque) return;
		cacheOriginalBloqueOptions();
		const used = new Set(state.passes.map(p=>p.bloque));
		// Si estamos editando, permitir que el bloque actual siga visible
		if(currentEditingBloque) used.delete(currentEditingBloque);
		// Reconstruir
		passBloque.innerHTML = '';
		originalBloqueOptions.forEach(o=>{
			if(o.value && used.has(o.value)) return; // ocultar usados
			const opt = document.createElement('option');
			opt.value = o.value; opt.textContent = o.text;
			passBloque.appendChild(opt);
		});
	}

	function renderPassList(){
		passList.innerHTML = '';
		if(!state.passes || !state.passes.length){
			passList.innerHTML = '<p class="text-sm text-gray-500">Sin pases</p>';
			return;
		}
		state.passes.sort((a,b)=> a.fecha_caducidad.localeCompare(b.fecha_caducidad));
		state.passes.forEach(p => {
			const remaining = daysRemaining(p.fecha_caducidad);
			const badge = badgeFromRemaining(remaining);
			const div = document.createElement('div');
			div.className = 'p-2 border rounded-lg cursor-pointer hover:bg-blue-50 flex justify-between items-center gap-2';
			div.innerHTML = `<div><p class="text-sm font-medium">${displayBloque(p.bloque)}</p><p class="text-xs text-gray-500">Caduca: ${fmt(p.fecha_caducidad)} ${badge}</p></div>`;
			div.addEventListener('click', ()=> loadPass(p.id));
			passList.appendChild(div);
		});
	}

	function displayBloque(code){
		const map = {
			petroecuador:'Petroecuador', shaya:'Shaya', consorcio_shushufindi:'Consorcio Shushufindi', enap_sipec:'ENAP SIPEC', orion:'Tarjeta Orion', andes_petroleum:'Andes Petroleum', pardalis_services:'Pardalis Services', frontera_energy:'Frontera Energy', gran_tierra:'Gran Tierra', pcr:'PCR', halliburton:'Halliburton', gente_oil:'Gente Oil', tribiol_gas:'Tribiol Gas', adico:'Adico', cuyaveno_petro:'Cuyaveno Petro', geopark:'Geopark'
		}; return map[code] || code;
	}

	function loadPass(id){
		const p = state.passes.find(x=>x.id===id); if(!p) return;
		passId.value = p.id; refreshPassBloqueOptions(p.bloque); passBloque.value = p.bloque; passBloque.disabled = true; passFecha.value = p.fecha_caducidad; passDeleteBtn.classList.remove('hidden');
		// Mostrar metadatos simples
		if(passMeta && passMetaContent){
			const remaining = daysRemaining(p.fecha_caducidad);
			const estado = remaining===null? 'Sin fecha': (remaining<0? 'Vencido': remaining+' días');
			passMetaContent.textContent = `ID: ${p.id}\nBloque: ${displayBloque(p.bloque)}\nCaducidad: ${fmt(p.fecha_caducidad)} (${estado})\nCreado: ${p.created_at||''}\nActualizado: ${p.updated_at||''}\nActivo: ${p.is_active? 'Sí':'No'}${p.notes? `\nNotas: ${p.notes}`:''}`;
			passMeta.classList.remove('hidden');
		}
	}

	function resetPass(){ passId.value=''; passBloque.disabled = false; refreshPassBloqueOptions(null); passBloque.value=''; passFecha.value=''; passDeleteBtn.classList.add('hidden'); setMsg(passMsg,'',true); if(passMeta) passMeta.classList.add('hidden'); }
	passResetBtn && passResetBtn.addEventListener('click', resetPass);

	let passSubmitting = false;
	if(passForm && !passForm.dataset.bound){
	passForm.addEventListener('submit', async e => {
		e.preventDefault();
		if(passSubmitting) return; // evitar doble envío
		passSubmitting = true; passSaveBtn.disabled = true;
		try {
			// Validar que el bloque aún no esté tomado (por seguridad extra frontend)
			const bloqueVal = passBloque.value;
			if(!passId.value && state.passes.some(p=>p.bloque===bloqueVal)){
				setMsg(passMsg, 'Bloque ya registrado', false); return;
			}
			const payload = { technical_id: state.technical_id, bloque: passBloque.value, fecha_caducidad: passFecha.value };
			if(passId.value){ payload.id = parseInt(passId.value,10); }
			const method = passId.value ? 'PUT':'POST';
			const data = await fetchJSON('/api/technicals/create_update_pass_technical/', {method, body: JSON.stringify(payload)});
			const rec = data.data;
			const idx = state.passes.findIndex(p=>p.id===rec.id);
			if(idx>=0) state.passes[idx]=rec; else state.passes.push(rec);
			renderPassList();
			setMsg(passMsg, passId.value? 'Actualizado':'Creado');
			if(!passId.value){ resetPass(); } else { // si editando, refrescar lista de opciones manteniendo bloque
				refreshPassBloqueOptions(rec.bloque); passBloque.value = rec.bloque;
			}
		} catch(err){ setMsg(passMsg, err.message,false); }
		finally { passSubmitting = false; passSaveBtn.disabled = false; }
	});
	passForm.dataset.bound = '1';
	}

	// Evitar doble registro del listener y doble confirmación
	if(passDeleteBtn && !passDeleteBtn.dataset.bound){
		let deletingPass = false;
		passDeleteBtn.addEventListener('click', async ()=>{
			if(deletingPass) return; // ya en proceso
			if(!passId.value) return;
			deletingPass = true;
			try {
				const ok = confirm('Eliminar pase?');
				if(!ok){ deletingPass = false; return; }
				await fetchJSON('/api/technicals/delete_pass_technical/', {method:'DELETE', body: JSON.stringify({id: parseInt(passId.value,10)})});
				state.passes = state.passes.filter(p=>p.id!==parseInt(passId.value,10));
				renderPassList(); resetPass(); refreshPassBloqueOptions(null); setMsg(passMsg,'Eliminado');
			} catch(err){ setMsg(passMsg, err.message,false); }
			finally { deletingPass = false; }
		});
		passDeleteBtn.dataset.bound = '1';
	}

	// ---- VACUNAS ----
	const vaccineForm = el('vaccineForm');
	const vaccineId = el('vaccine_id');
	const vaccineType = el('vaccine_type');
	const applicationDate = el('application_date');
	const nextDoseDate = el('next_dose_date');
	const batchNumber = el('batch_number');
	const doseNumber = el('dose_number');
	const vaccineNotes = el('vaccine_notes');
	const vaccineSaveBtn = el('vaccineSaveBtn');
	const vaccineResetBtn = el('vaccineResetBtn');
	const vaccineDeleteBtn = el('vaccineDeleteBtn');
	const vaccineMsg = el('vaccineFormMsg');
	const vaccineTableBody = qs('#vaccineTable tbody');

	function renderVaccines(){
		vaccineTableBody.innerHTML = '';
		if(!state.vaccines || !state.vaccines.length){
			vaccineTableBody.innerHTML = '<tr><td colspan="4" class="text-center text-xs text-gray-500">Sin vacunas</td></tr>';
			return;
		}
		state.vaccines.sort((a,b)=> b.application_date.localeCompare(a.application_date));
		state.vaccines.forEach(v => {
			const tr = document.createElement('tr');
			tr.className = 'cursor-pointer hover:bg-blue-50';
			tr.innerHTML = `
				<td class="text-xs">${displayVaccine(v.vaccine_type)}</td>
				<td class="text-xs">${fmt(v.application_date)}</td>
				<td class="text-xs">${v.next_dose_date? fmt(v.next_dose_date): ''}</td>
				<td class="text-xs">${v.batch_number||''}</td>`;
			tr.addEventListener('click', ()=> loadVaccine(v.id));
			vaccineTableBody.appendChild(tr);
		});
	}

	function displayVaccine(code){
		const map = {HEPATITIS_A_B:'Hepatitis A y B', TETANUS:'Tétanos', TYPHOID:'Tifoidea', YELLOW_FEVER:'Fiebre Amarilla', INFLUENZA:'Influenza', MEASLES:'Sarampión', COVID:'Covid-19', OTHER:'Otra'}; return map[code]||code;
	}

	function loadVaccine(id){
		const v = state.vaccines.find(x=>x.id===id); if(!v) return;
		vaccineId.value = v.id; vaccineType.value = v.vaccine_type; applicationDate.value = v.application_date; nextDoseDate.value = v.next_dose_date || ''; batchNumber.value = v.batch_number || ''; doseNumber.value = v.dose_number || ''; vaccineNotes.value = v.notes || ''; vaccineDeleteBtn.classList.remove('hidden');
	}
	function resetVaccine(){ vaccineId.value=''; vaccineType.value=''; applicationDate.value=''; nextDoseDate.value=''; batchNumber.value=''; doseNumber.value=''; vaccineNotes.value=''; vaccineDeleteBtn.classList.add('hidden'); setMsg(vaccineMsg,'',true); }
	vaccineResetBtn && vaccineResetBtn.addEventListener('click', resetVaccine);

	vaccineForm && vaccineForm.addEventListener('submit', async e => {
		e.preventDefault();
		try {
			const payload = {
				technical_id: state.technical_id,
				vaccine_type: vaccineType.value,
				application_date: applicationDate.value,
				batch_number: batchNumber.value || null,
				dose_number: doseNumber.value? parseInt(doseNumber.value,10): null,
				next_dose_date: nextDoseDate.value || null,
				notes: vaccineNotes.value || null
			};
			if(vaccineId.value){ payload.id = parseInt(vaccineId.value,10); }
			const method = vaccineId.value ? 'PUT':'POST';
			const data = await fetchJSON('/api/technicals/create_update_vaccine/', {method, body: JSON.stringify(payload)});
			const rec = data.data;
			// Recalcular is_complete heurísticamente
			rec.is_complete = !!rec.application_date && (!rec.next_dose_date || new Date(rec.next_dose_date) < new Date());
			const idx = state.vaccines.findIndex(v=>v.id===rec.id);
			if(idx>=0) state.vaccines[idx]=rec; else state.vaccines.push(rec);
			renderVaccines();
			setMsg(vaccineMsg, vaccineId.value? 'Actualizada':'Creada');
			if(!vaccineId.value) resetVaccine();
		} catch(err){ setMsg(vaccineMsg, err.message,false); }
	});

	if(vaccineDeleteBtn && !vaccineDeleteBtn.dataset.bound){
		let deletingVaccine = false;
		vaccineDeleteBtn.addEventListener('click', async ()=>{
			if(deletingVaccine) return;
			if(!vaccineId.value) return;
			deletingVaccine = true;
			try {
				const ok = confirm('Eliminar vacuna?');
				if(!ok){ deletingVaccine = false; return; }
				await fetchJSON('/api/technicals/delete_vaccine/', {method:'DELETE', body: JSON.stringify({id: parseInt(vaccineId.value,10)})});
				state.vaccines = state.vaccines.filter(v=>v.id!==parseInt(vaccineId.value,10));
				renderVaccines(); resetVaccine(); setMsg(vaccineMsg,'Eliminada');
			} catch(err){ setMsg(vaccineMsg, err.message,false); }
			finally { deletingVaccine = false; }
		});
		vaccineDeleteBtn.dataset.bound = '1';
	}

	// ---- Cálculo helper expiración ----
	function daysRemaining(dateStr){ if(!dateStr) return null; const today = new Date(); today.setHours(0,0,0,0); const d = new Date(dateStr); if(isNaN(d)) return null; d.setHours(0,0,0,0); return Math.ceil((d - today)/86400000); }
	function badgeFromRemaining(days){ if(days===null) return ''; if(days<0) return '<span class="badge badge-error badge-xs">Vencido</span>'; if(days===0) return '<span class="badge badge-error badge-xs">HOY</span>'; if(days<15) return `<span class=\"badge badge-error badge-xs\">${days}d</span>`; if(days<60) return `<span class=\"badge badge-warning badge-xs\">${days}d</span>`; if(days<90) return `<span class=\"badge badge-info badge-xs\">${days}d</span>`; return `<span class=\"badge badge-success badge-xs\">${days}d</span>`; }

	// ---- MODAL CARNET DE VACUNAS ----
	const openVaccineCardBtn = el('openVaccineCardBtn');
	const vaccineCardModal = el('vaccineCardModal');
	const vaccineCardTableBody = el('vaccineCardTableBody');
	const modalEmissionDate = el('modalEmissionDate');
	const printVaccineCardBtn = el('printVaccineCard');

	function openVaccineCardModal(){
		// Establecer fecha de emisión (hoy)
		if(modalEmissionDate){
			modalEmissionDate.textContent = new Date().toLocaleDateString('es-EC');
		}
		
		// Limpiar tabla
		vaccineCardTableBody.innerHTML = '';
		
		// Definir estructura predefinida de vacunas como en la imagen
		const vaccineStructure = [
			{ type: 'HEPATITIS_A', name: 'HEPAT. A', doses: 5 },
			{ type: 'HEPATITIS_B', name: 'HEPAT. B', doses: 5 },
			{ type: 'YELLOW_FEVER', name: 'F. AMARILLA', doses: 1, isUnique: true },
			{ type: 'TETANUS', name: 'TETANOS', doses: 5 },
			{ type: 'TYPHOID', name: 'TIFOIDEA', doses: 3 }
		];
		
		// Crear un mapa de vacunas registradas por tipo
		const registeredVaccines = {};
		state.vaccines.forEach(v => {
			// Mapear HEPATITIS_A_B a ambos tipos
			if (v.vaccine_type === 'HEPATITIS_A_B') {
				// Si es Hepatitis A y B combinada, agregarla a ambos tipos
				if (!registeredVaccines['HEPATITIS_A']) {
					registeredVaccines['HEPATITIS_A'] = [];
				}
				if (!registeredVaccines['HEPATITIS_B']) {
					registeredVaccines['HEPATITIS_B'] = [];
				}
				registeredVaccines['HEPATITIS_A'].push(v);
				registeredVaccines['HEPATITIS_B'].push(v);
			} else {
				if (!registeredVaccines[v.vaccine_type]) {
					registeredVaccines[v.vaccine_type] = [];
				}
				registeredVaccines[v.vaccine_type].push(v);
			}
		});
		
		// Ordenar vacunas registradas por fecha
		Object.keys(registeredVaccines).forEach(type => {
			registeredVaccines[type].sort((a, b) => a.application_date.localeCompare(b.application_date));
		});
		
		// Crear tabla exactamente como en la imagen
		vaccineStructure.forEach(vaccineGroup => {
			const vaccines = registeredVaccines[vaccineGroup.type] || [];
			
			for (let i = 0; i < vaccineGroup.doses; i++) {
				const tr = document.createElement('tr');
				const vaccine = vaccines[i]; // puede ser undefined si no existe
				
				// Determinar el número de dosis
				let doseNumber;
				if (vaccineGroup.isUnique) {
					doseNumber = 'UNICA';
				} else {
					doseNumber = i + 1;
				}
				
				// Fecha y lote (vacío si no hay vacuna registrada)
				const date = vaccine ? fmt(vaccine.application_date) : '';
				const batch = vaccine ? (vaccine.batch_number || '') : '';
				
				if (i === 0) {
					// Primera fila del grupo - incluir nombre de vacuna con rowspan
					tr.innerHTML = `
						<td class="border border-gray-300 text-center font-semibold bg-gray-50" rowspan="${vaccineGroup.doses}" style="vertical-align: middle;">${vaccineGroup.name}</td>
						<td class="border border-gray-300 text-center">${doseNumber}</td>
						<td class="border border-gray-300 text-center">${date}</td>
						<td class="border border-gray-300 text-center">${batch}</td>
					`;
				} else {
					// Filas subsecuentes - sin columna de nombre de vacuna
					tr.innerHTML = `
						<td class="border border-gray-300 text-center">${doseNumber}</td>
						<td class="border border-gray-300 text-center">${date}</td>
						<td class="border border-gray-300 text-center">${batch}</td>
					`;
				}
				
				vaccineCardTableBody.appendChild(tr);
			}
		});
		
		// Abrir modal
		vaccineCardModal.showModal();
	}

	function printVaccineCard(){
		// Crear ventana de impresión
		const printWindow = window.open('', '_blank');
		const vaccineCardContent = document.querySelector('#vaccineCardModal .modal-box').innerHTML;
		
		printWindow.document.write(`
			<!DOCTYPE html>
			<html>
			<head>
				<title>Carnet de Vacunas - {{ technical.first_name }} {{ technical.last_name }}</title>
				<style>
					body { font-family: Arial, sans-serif; margin: 20px; }
					table { width: 100%; border-collapse: collapse; margin: 20px 0; }
					th, td { border: 1px solid #333; padding: 8px; text-align: center; }
					th { background-color: #f0f0f0; font-weight: bold; }
					.header { background-color: #e3f2fd; padding: 15px; border: 1px solid #1976d2; margin-bottom: 20px; }
					.header h3 { margin: 0 0 10px 0; color: #1976d2; }
					.info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
					.info-item { font-size: 14px; }
					.info-label { font-weight: bold; color: #1976d2; }
					@media print { 
						body { margin: 0; } 
						.modal-action { display: none; }
					}
				</style>
			</head>
			<body>
				${vaccineCardContent.replace(/<button[^>]*>.*?<\/button>/g, '')}
			</body>
			</html>
		`);
		
		printWindow.document.close();
		printWindow.focus();
		setTimeout(() => {
			printWindow.print();
			printWindow.close();
		}, 250);
	}

	// Event listeners para modal
	openVaccineCardBtn && openVaccineCardBtn.addEventListener('click', openVaccineCardModal);
	printVaccineCardBtn && printVaccineCardBtn.addEventListener('click', printVaccineCard);

	// Inicializar
	state.passes = state.passes || []; state.vaccines = state.vaccines || [];
	refreshPassBloqueOptions(null);
	renderPassList(); renderVaccines();
})();
