// App de gestión de Pases y Vacunas para ficha de Técnico (vanilla JS)
// Usa endpoints:
//  Pases:  POST/PUT   /api/technicals/create_update_pass_technical/
//          DELETE     /api/technicals/delete_pass_technical/
//  Vacunas: POST/PUT  /api/technicals/create_update_vaccine/
//           DELETE    /api/technicals/delete_vaccine/

(function(){
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
		passId.value = p.id; passBloque.value = p.bloque; passFecha.value = p.fecha_caducidad; passDeleteBtn.classList.remove('hidden');
		// Mostrar metadatos simples
		if(passMeta && passMetaContent){
			const remaining = daysRemaining(p.fecha_caducidad);
			const estado = remaining===null? 'Sin fecha': (remaining<0? 'Vencido': remaining+' días');
			passMetaContent.textContent = `ID: ${p.id}\nBloque: ${displayBloque(p.bloque)}\nCaducidad: ${fmt(p.fecha_caducidad)} (${estado})\nCreado: ${p.created_at||''}\nActualizado: ${p.updated_at||''}\nActivo: ${p.is_active? 'Sí':'No'}${p.notes? `\nNotas: ${p.notes}`:''}`;
			passMeta.classList.remove('hidden');
		}
	}

	function resetPass(){ passId.value=''; passBloque.value=''; passFecha.value=''; passDeleteBtn.classList.add('hidden'); setMsg(passMsg,'',true); if(passMeta) passMeta.classList.add('hidden'); }
	passResetBtn && passResetBtn.addEventListener('click', resetPass);

	passForm && passForm.addEventListener('submit', async e => {
		e.preventDefault();
		try {
			const payload = { technical_id: state.technical_id, bloque: passBloque.value, fecha_caducidad: passFecha.value };
			if(passId.value){ payload.id = parseInt(passId.value,10); }
			const method = passId.value ? 'PUT':'POST';
			const data = await fetchJSON('/api/technicals/create_update_pass_technical/', {method, body: JSON.stringify(payload)});
			const rec = data.data;
			const idx = state.passes.findIndex(p=>p.id===rec.id);
			if(idx>=0) state.passes[idx]=rec; else state.passes.push(rec);
			renderPassList();
			setMsg(passMsg, passId.value? 'Actualizado':'Creado');
			if(!passId.value) resetPass();
		} catch(err){ setMsg(passMsg, err.message,false); }
	});

	passDeleteBtn && passDeleteBtn.addEventListener('click', async ()=>{
		if(!passId.value) return; if(!confirm('Eliminar pase?')) return;
		try {
			await fetchJSON('/api/technicals/delete_pass_technical/', {method:'DELETE', body: JSON.stringify({id: parseInt(passId.value,10)})});
			state.passes = state.passes.filter(p=>p.id!==parseInt(passId.value,10));
			renderPassList(); resetPass(); setMsg(passMsg,'Eliminado');
		} catch(err){ setMsg(passMsg, err.message,false); }
	});

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
			vaccineTableBody.innerHTML = '<tr><td colspan="5" class="text-center text-xs text-gray-500">Sin vacunas</td></tr>';
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
				<td class="text-xs">${v.batch_number||''}</td>
				<td class="text-xs">${v.is_complete? '<span class="badge badge-success badge-xs">Completa</span>':'<span class="badge badge-warning badge-xs">Pendiente</span>'}</td>`;
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

	vaccineDeleteBtn && vaccineDeleteBtn.addEventListener('click', async ()=>{
		if(!vaccineId.value) return; if(!confirm('Eliminar vacuna?')) return;
		try {
			await fetchJSON('/api/technicals/delete_vaccine/', {method:'DELETE', body: JSON.stringify({id: parseInt(vaccineId.value,10)})});
			state.vaccines = state.vaccines.filter(v=>v.id!==parseInt(vaccineId.value,10));
			renderVaccines(); resetVaccine(); setMsg(vaccineMsg,'Eliminada');
		} catch(err){ setMsg(vaccineMsg, err.message,false); }
	});

	// ---- Cálculo helper expiración ----
	function daysRemaining(dateStr){ if(!dateStr) return null; const today = new Date(); today.setHours(0,0,0,0); const d = new Date(dateStr); if(isNaN(d)) return null; d.setHours(0,0,0,0); return Math.ceil((d - today)/86400000); }
	function badgeFromRemaining(days){ if(days===null) return ''; if(days<0) return '<span class="badge badge-error badge-xs">Vencido</span>'; if(days===0) return '<span class="badge badge-error badge-xs">HOY</span>'; if(days<15) return `<span class=\"badge badge-error badge-xs\">${days}d</span>`; if(days<60) return `<span class=\"badge badge-warning badge-xs\">${days}d</span>`; if(days<90) return `<span class=\"badge badge-info badge-xs\">${days}d</span>`; return `<span class=\"badge badge-success badge-xs\">${days}d</span>`; }

	// Inicializar
	state.passes = state.passes || []; state.vaccines = state.vaccines || [];
	renderPassList(); renderVaccines();
})();
