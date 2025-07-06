// Variables globales para almacenar las listas temporales
let temporaryCertifications = [];
let temporaryPasses = [];

// Funciones para manejar modales de certificaciones
function openCertificationModal() {
  document.getElementById('certificationModal').classList.add('modal-open');
}

function closeCertificationModal() {
  document.getElementById('certificationModal').classList.remove('modal-open');
  document.getElementById('certificationForm').reset();
}

// Funciones para manejar modales de pases
function openPassModal() {
  document.getElementById('passModal').classList.add('modal-open');
}

function closePassModal() {
  document.getElementById('passModal').classList.remove('modal-open');
  document.getElementById('passForm').reset();
}

// Cerrar modales al hacer clic fuera
document.addEventListener('click', function(event) {
  const certModal = document.getElementById('certificationModal');
  const passModal = document.getElementById('passModal');
  
  if (event.target === certModal) {
    closeCertificationModal();
  }
  if (event.target === passModal) {
    closePassModal();
  }
});

// Función para agregar certificación vía AJAX
async function addCertification(formData) {
  try {
    const response = await fetch(window.location.href, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: JSON.stringify({
        action: 'add_certification',
        certification_type: formData.get('certification_type'),
        issue_date: formData.get('issue_date'),
        expiry_date: formData.get('expiry_date'),
        issuing_authority: formData.get('issuing_authority'),
        certificate_number: formData.get('certificate_number'),
        notes: formData.get('notes')
      })
    });

    const result = await response.json();
    
    if (result.success) {
      // Agregar a la lista temporal
      temporaryCertifications.push(result.data);
      updateCertificationsDisplay();
      updateCertificationsInput();
      closeCertificationModal();
      
      // Mostrar mensaje de éxito
      showToast('success', result.message);
    } else {
      showToast('error', result.message);
    }
  } catch (error) {
    console.error('Error al agregar certificación:', error);
    showToast('error', 'Error al procesar la certificación');
  }
}

// Función para agregar pase vía AJAX
async function addPass(formData) {
  try {
    const response = await fetch(window.location.href, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: JSON.stringify({
        action: 'add_pass',
        bloque: formData.get('bloque'),
        fecha_caducidad: formData.get('fecha_caducidad')
      })
    });

    const result = await response.json();
    
    if (result.success) {
      // Agregar a la lista temporal
      temporaryPasses.push(result.data);
      updatePassesDisplay();
      updatePassesInput();
      closePassModal();
      
      // Mostrar mensaje de éxito
      showToast('success', result.message);
    } else {
      showToast('error', result.message);
    }
  } catch (error) {
    console.error('Error al agregar pase:', error);
    showToast('error', 'Error al procesar el pase');
  }
}

// Funciones para actualizar la visualización
function updateCertificationsDisplay() {
  // Esta función actualizaría la lista visual de certificaciones
  // Para simplicidad, solo logueamos por ahora
  console.log('Certificaciones actuales:', temporaryCertifications);
}

function updatePassesDisplay() {
  // Esta función actualizaría la lista visual de pases
  // Para simplicidad, solo logueamos por ahora
  console.log('Pases actuales:', temporaryPasses);
}

// Funciones para actualizar los campos ocultos
function updateCertificationsInput() {
  const input = document.querySelector('input[name="certifications_data"]');
  if (input) {
    input.value = JSON.stringify(temporaryCertifications);
  }
}

function updatePassesInput() {
  const input = document.querySelector('input[name="passes_data"]');
  if (input) {
    input.value = JSON.stringify(temporaryPasses);
  }
}

// Función para eliminar certificación
function removeCertification(index) {
  temporaryCertifications.splice(index, 1);
  updateCertificationsDisplay();
  updateCertificationsInput();
}

// Función para eliminar pase
function removePass(index) {
  temporaryPasses.splice(index, 1);
  updatePassesDisplay();
  updatePassesInput();
}

// Función para mostrar mensajes toast
function showToast(type, message) {
  // Implementación simple de toast
  const toast = document.createElement('div');
  toast.className = `alert alert-${type === 'success' ? 'success' : 'error'} fixed top-4 right-4 z-50 w-auto`;
  toast.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${type === 'success' ? 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' : 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'}" />
    </svg>
    <span>${message}</span>
  `;
  
  document.body.appendChild(toast);
  
  // Remover después de 3 segundos
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// Event listeners para los formularios de modales
document.getElementById('certificationForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const formData = new FormData(this);
  addCertification(formData);
});

document.getElementById('passForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const formData = new FormData(this);
  addPass(formData);
});

// Inicializar cuando la página esté lista
document.addEventListener('DOMContentLoaded', function() {
  // Inicializar campos ocultos
  updateCertificationsInput();
  updatePassesInput();
});
