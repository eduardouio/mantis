// App de gestión de Pases y Certificados para ficha de Vehículo (vanilla JS)
// Endpoints vehículos:
//  Pases:  GET/POST/PUT   /api/vehicles/pass_vehicle/
//          DELETE         /api/vehicles/pass_vehicle/<id>/
//  Certs:  GET/POST/PUT   /api/vehicles/cert_vehicle/
//          DELETE         /api/vehicles/cert_vehicle/<id>/

(function(){
  if(window.__VEH_PRES_INIT__) return; 
  window.__VEH_PRES_INIT__ = true;

  const jsonEl = document.getElementById('vehicle-data');
  if(!jsonEl) return;
  let state = { vehicle_id: null, passes: [], certifications: [] };
  try { state = Object.assign(state, JSON.parse(jsonEl.textContent.trim())); } catch(e){ console.error('JSON vehicle-data inválido', e); return; }
  if(!state.vehicle_id){ console.error('vehicle_id faltante en vehicle-data'); return; }

  // Utils
  const el = id => document.getElementById(id);
  const qs = sel => document.querySelector(sel);
  const fmt = d => {
    if (!d) return '';
    // Crear fecha local para evitar problemas de zona horaria
    const parts = d.split('-');
    if (parts.length === 3) {
      const date = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
      return date.toLocaleDateString('es-EC');
    }
    return new Date(d).toLocaleDateString('es-EC');
  };
  const setMsg = (container, msg, ok=true) => { if(!container) return; container.textContent = msg || ''; container.className = ok? 'text-xs text-green-600':'text-xs text-red-600'; };
  const csrftoken = document.cookie.split(';').map(c=>c.trim()).find(c=>c.startsWith('csrftoken='));
  async function fetchJSON(url, options={}){
    const headers = options.headers || {}; headers['Content-Type'] = 'application/json';
    if(csrftoken) headers['X-CSRFToken'] = csrftoken.split('=')[1];
    const resp = await fetch(url, {credentials:'same-origin', ...options, headers});
    let data; try { data = await resp.json(); } catch(_){ data = {success:false, error:'No JSON'}; }
    if(!resp.ok || data.success === false) throw new Error(data.error || 'Error HTTP');
    return data;
  }
  function daysRemaining(dateStr){ 
    if(!dateStr) return null; 
    const today = new Date(); 
    today.setHours(0,0,0,0); 
    const d = new Date(dateStr); 
    if(isNaN(d)) return null; 
    d.setHours(0,0,0,0); 
    // Usar la misma lógica que Django: diferencia en días
    return Math.floor((d - today) / (24 * 60 * 60 * 1000)); 
  }
  function badgeFromRemaining(days){ if(days===null) return ''; if(days<0) return '<span class="badge badge-error badge-xs">Vencido</span>'; if(days===0) return '<span class="badge badge-error badge-xs">HOY</span>'; if(days<15) return `<span class="badge badge-error badge-xs">${days}d</span>`; if(days<60) return `<span class="badge badge-warning badge-xs">${days}d</span>`; if(days<90) return `<span class="badge badge-info badge-xs">${days}d</span>`; return `<span class="badge badge-success badge-xs">${days}d</span>`; }

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

  let originalBloqueOptions = null;
  function cacheOriginalBloqueOptions(){
    if(originalBloqueOptions || !passBloque) return;
    originalBloqueOptions = Array.from(passBloque.options).map(o=>({value:o.value, text:o.textContent}));
  }
  function refreshPassBloqueOptions(currentEditingBloque=null){
    if(!passBloque) return;
    cacheOriginalBloqueOptions();
    const used = new Set((state.passes||[]).map(p=>p.bloque));
    if(currentEditingBloque) used.delete(currentEditingBloque);
    passBloque.innerHTML = '';
    originalBloqueOptions.forEach(o=>{
      if(!o.value) return; // saltar placeholders
      if(used.has(o.value)) return; // ocultar usados
      const opt = document.createElement('option'); opt.value = o.value; opt.textContent = o.text; passBloque.appendChild(opt);
    });
    // Agregar opción vacía al inicio
    const placeholder = document.createElement('option'); placeholder.value=''; placeholder.textContent='Seleccione'; placeholder.selected=true; placeholder.disabled=true; passBloque.insertBefore(placeholder, passBloque.firstChild);
  }

  function renderPassList(){
    if(!passList) return;
    passList.innerHTML = '';
    if(!state.passes || !state.passes.length){ passList.innerHTML = '<p class="text-sm text-gray-500">Sin pases</p>'; return; }
    state.passes.sort((a,b)=> a.fecha_caducidad.localeCompare(b.fecha_caducidad));
    state.passes.forEach(p=>{
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
    const map = { petroecuador:'Petroecuador', shaya:'Shaya', consorcio_shushufindi:'Consorcio Shushufindi', enap_sipec:'ENAP SIPEC', orion:'Tarjeta Orion', andes_petroleum:'Andes Petroleum', pardalis_services:'Pardalis Services', frontera_energy:'Frontera Energy', gran_tierra:'Gran Tierra', pcr:'PCR', halliburton:'Halliburton', gente_oil:'Gente Oil', tribiol_gas:'Tribiol Gas', adico:'Adico', cuyaveno_petro:'Cuyaveno Petro', geopark:'Geopark' };
    return map[code] || code;
  }
  function loadPass(id){
    const p = (state.passes||[]).find(x=>x.id===id); if(!p) return;
    passId.value = p.id; refreshPassBloqueOptions(p.bloque); passBloque.value = p.bloque; passBloque.disabled = true; passFecha.value = p.fecha_caducidad; passDeleteBtn && passDeleteBtn.classList.remove('hidden');
    if(passMeta && passMetaContent){
      passMetaContent.textContent = `ID: ${p.id}\nCreado: ${p.created_at||''}\nActualizado: ${p.updated_at||''}\nActivo: ${p.is_active? 'Sí':'No'}${p.notes? `\nNotas: ${p.notes}`:''}`;
      passMeta.classList.remove('hidden');
    }
  }
  function resetPass(){ if(passId) passId.value=''; if(passBloque){ passBloque.disabled=false; refreshPassBloqueOptions(null); passBloque.value=''; } if(passFecha) passFecha.value=''; passDeleteBtn && passDeleteBtn.classList.add('hidden'); setMsg(passMsg,'',true); passMeta && passMeta.classList.add('hidden'); }
  passResetBtn && passResetBtn.addEventListener('click', resetPass);

  let passSubmitting=false;
  passForm && passForm.addEventListener('submit', async (e)=>{
    e.preventDefault(); if(passSubmitting) return; passSubmitting=true; passSaveBtn && (passSaveBtn.disabled=true);
    try{
      const payload = { vehicle_id: state.vehicle_id, bloque: passBloque.value, fecha_caducidad: passFecha.value };
      const method = passId.value? 'PUT':'POST'; if(passId.value) payload.id = parseInt(passId.value,10);
      const data = await fetchJSON('/api/vehicles/pass_vehicle/', {method, body: JSON.stringify(payload)});
      const rec = data.data; const idx = (state.passes||[]).findIndex(x=>x.id===rec.id);
      if(idx>=0) state.passes[idx]=rec; else state.passes.push(rec);
      renderPassList(); setMsg(passMsg, passId.value? 'Actualizado':'Creado');
      if(!passId.value) resetPass(); else { refreshPassBloqueOptions(rec.bloque); passBloque.value = rec.bloque; }
    }catch(err){ setMsg(passMsg, err.message||'Error', false); }
    finally{ passSubmitting=false; passSaveBtn && (passSaveBtn.disabled=false); }
  });

  if(passDeleteBtn && !passDeleteBtn.dataset.bound){
    let deleting=false;
    passDeleteBtn.addEventListener('click', async ()=>{
      if(deleting) return; if(!passId.value) return; deleting=true;
      try{
        const ok = confirm('Eliminar pase?'); if(!ok){ deleting=false; return; }
        const id = parseInt(passId.value,10);
        await fetchJSON(`/api/vehicles/pass_vehicle/${id}/`, {method:'DELETE'});
        state.passes = (state.passes||[]).filter(p=>p.id!==id); renderPassList(); resetPass(); refreshPassBloqueOptions(null); setMsg(passMsg,'Eliminado');
      }catch(err){ setMsg(passMsg, err.message||'Error', false); }
      finally{ deleting=false; }
    });
    passDeleteBtn.dataset.bound = '1';
  }

  // ---- CERTIFICACIONES ----
  const certForm = el('certForm');
  const certId = el('cert_id');
  const certName = el('cert_name');
  const certDateStart = el('cert_date_start');
  const certDateEnd = el('cert_date_end');
  const certDescription = el('cert_description');
  const certSaveBtn = el('certSaveBtn');
  const certResetBtn = el('certResetBtn');
  const certDeleteBtn = el('certDeleteBtn');
  const certMsg = el('certFormMsg');
  const certList = el('certList');
  const certMeta = el('certMeta');
  const certMetaContent = el('certMetaContent');

  function renderCertList(){
    if(!certList) return;
    certList.innerHTML = '';
    if(!state.certifications || !state.certifications.length){ certList.innerHTML = '<p class="text-sm text-gray-500">Sin certificados</p>'; return; }
    state.certifications.sort((a,b)=> a.date_end.localeCompare(b.date_end));
    state.certifications.forEach(c=>{
      const remaining = daysRemaining(c.date_end);
      const badge = badgeFromRemaining(remaining);
      const div = document.createElement('div');
      div.className = 'p-2 border rounded-lg cursor-pointer hover:bg-blue-50 flex justify-between items-center gap-2';
      const name = c.name_display || c.name || 'Certificación';
      div.innerHTML = `<div><p class=\"text-sm font-medium\">${name}</p><p class=\"text-xs text-gray-500\">${fmt(c.date_start)} - ${fmt(c.date_end)} ${badge}</p>${c.description? `<p class=\"text-[11px] text-gray-500\">${c.description}</p>`:''}</div>`;
      div.addEventListener('click', ()=> loadCert(c.id));
      certList.appendChild(div);
    });
  }
  function loadCert(id){
    const c = (state.certifications||[]).find(x=>x.id===id); if(!c) return;
    certId.value = c.id; certName.value = c.name; certDateStart.value = c.date_start; certDateEnd.value = c.date_end; certDescription.value = c.description || ''; certDeleteBtn && certDeleteBtn.classList.remove('hidden');
    if(certMeta && certMetaContent){
      certMetaContent.textContent = `ID: ${c.id}\nCreado: ${c.created_at||''}\nActualizado: ${c.updated_at||''}\nActivo: ${c.is_active? 'Sí':'No'}`;
      certMeta.classList.remove('hidden');
    }
  }
  function resetCert(){ if(certId) certId.value=''; if(certName) certName.value=''; if(certDateStart) certDateStart.value=''; if(certDateEnd) certDateEnd.value=''; if(certDescription) certDescription.value=''; certDeleteBtn && certDeleteBtn.classList.add('hidden'); setMsg(certMsg,'',true); certMeta && certMeta.classList.add('hidden'); }
  certResetBtn && certResetBtn.addEventListener('click', resetCert);

  let certSubmitting=false;
  certForm && certForm.addEventListener('submit', async (e)=>{
    e.preventDefault(); if(certSubmitting) return; certSubmitting=true; certSaveBtn && (certSaveBtn.disabled=true);
    try{
      const payload = {
        vehicle_id: state.vehicle_id,
        name: certName.value,
        date_start: certDateStart.value,
        date_end: certDateEnd.value,
        description: certDescription.value || ''
      };
      const method = certId.value? 'PUT':'POST'; if(certId.value) payload.id = parseInt(certId.value,10);
      const data = await fetchJSON('/api/vehicles/cert_vehicle/', {method, body: JSON.stringify(payload)});
      const rec = data.data; const idx = (state.certifications||[]).findIndex(x=>x.id===rec.id);
      if(idx>=0) state.certifications[idx]=rec; else state.certifications.push(rec);
      renderCertList(); setMsg(certMsg, certId.value? 'Actualizado':'Creado'); if(!certId.value) resetCert();
    }catch(err){ setMsg(certMsg, err.message||'Error', false); }
    finally{ certSubmitting=false; certSaveBtn && (certSaveBtn.disabled=false); }
  });

  if(certDeleteBtn && !certDeleteBtn.dataset.bound){
    let deleting=false;
    certDeleteBtn.addEventListener('click', async ()=>{
      if(deleting) return; if(!certId.value) return; deleting=true;
      try{
        const ok = confirm('Eliminar certificación?'); if(!ok){ deleting=false; return; }
        const id = parseInt(certId.value,10);
        await fetchJSON(`/api/vehicles/cert_vehicle/${id}/`, {method:'DELETE'});
        state.certifications = (state.certifications||[]).filter(c=>c.id!==id); renderCertList(); resetCert(); setMsg(certMsg,'Eliminado');
      }catch(err){ setMsg(certMsg, err.message||'Error', false); }
      finally{ deleting=false; }
    });
    certDeleteBtn.dataset.bound = '1';
  }

  // ---- Carga inicial desde APIs ----
  async function bootstrap(){
    try{
      // Cargar pases
      const passData = await fetchJSON(`/api/vehicles/pass_vehicle/?vehicle_id=${state.vehicle_id}`);
      state.passes = passData.data || []; renderPassList(); refreshPassBloqueOptions(null);
    }catch(e){ console.warn('No se pudieron cargar pases', e.message); }
    try{
      // Cargar certificaciones
      const certData = await fetchJSON(`/api/vehicles/cert_vehicle/?vehicle_id=${state.vehicle_id}`);
      state.certifications = certData.data || []; renderCertList();
    }catch(e){ console.warn('No se pudieron cargar certificaciones', e.message); }
  }

  bootstrap();

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

  function rebuildRowButtons(row, fileUrl, fileName){
    const actionsDiv = row.querySelector('.flex.items-center.gap-1');
    if(!actionsDiv) return;
    actionsDiv.innerHTML = '';
    const fieldName = row.dataset.fieldName;
    const isImage = fieldName === 'vehicle_image';

    if(fileUrl){
      const link = document.createElement('a');
      link.href = fileUrl; link.target = '_blank';
      link.className = isImage ? 'btn btn-xs btn-info' : 'btn btn-xs btn-primary';
      link.title = isImage ? 'Ver' : 'Descargar';
      link.innerHTML = isImage ? '<i class="las la-eye"></i>' : '<i class="las la-download"></i>';
      actionsDiv.appendChild(link);

      const delBtn = document.createElement('button');
      delBtn.type = 'button';
      delBtn.className = 'btn btn-xs btn-error btn-file-delete'; delBtn.title = 'Eliminar archivo';
      delBtn.innerHTML = '<i class="las la-trash"></i>';
      actionsDiv.appendChild(delBtn);
    }

    const label = document.createElement('label');
    label.className = 'btn btn-xs btn-success btn-file-upload'; label.title = 'Subir archivo';
    const acceptType = isImage ? 'image/*' : '.pdf';
    label.innerHTML = `<i class="las la-upload"></i><input type="file" accept="${acceptType}" class="hidden file-input-hidden">`;
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
      showGlobalMsg('Archivo subido correctamente');
      rebuildRowButtons(row, data.data.file_url, data.data.file_name);
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

    if(!confirm('¿Eliminar este archivo?')) return;

    setRowLoading(row, true);
    try {
      const url = `${UPLOAD_API}?model_type=${modelType}&object_id=${objectId}&field_name=${fieldName}`;
      const resp = await fetch(url, { method: 'DELETE', credentials: 'same-origin' });
      const data = await resp.json();
      if(!resp.ok || !data.success) throw new Error(data.error || 'Error al eliminar');
      showGlobalMsg('Archivo eliminado correctamente');
      rebuildRowButtons(row, null, null);
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
