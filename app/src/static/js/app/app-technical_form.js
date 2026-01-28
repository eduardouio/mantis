/**
 * Script para el manejo de certificados en el formulario de técnicos
 * Calcula y muestra los días restantes para el vencimiento de certificados
 */

const CERTIFICATE_CONFIG = {
  'license': {
    issueDateField: 'id_license_issue_date',
    expiryDateField: 'id_license_expiry_date',
    badgeId: 'licenseExpiryBadge',
    name: 'Licencia'
  },
  'defensiveDriving': {
    issueDateField: 'id_defensive_driving_certificate_issue_date',
    expiryDateField: 'id_defensive_driving_certificate_expiry_date',
    badgeId: 'defensiveDrivingExpiryBadge',
    name: 'Manejo Defensivo'
  },
  'mae': {
    issueDateField: 'id_mae_certificate_issue_date',
    expiryDateField: 'id_mae_certificate_expiry_date',
    badgeId: 'maeExpiryBadge',
    name: 'MAE'
  },
  'medical': {
    issueDateField: 'id_medical_certificate_issue_date',
    expiryDateField: 'id_medical_certificate_expiry_date',
    badgeId: 'medicalExpiryBadge',
    name: 'Médico'
  },
  'quest': {
    issueDateField: 'id_quest_start_date',
    expiryDateField: 'id_quest_end_date',
    badgeId: 'questExpiryBadge', // nuevo id en template
    name: 'Quest'
  }
};

/**
 * Calcula los días restantes entre hoy y una fecha
 */
function calculateDaysRemaining(dateString) {
  if (!dateString) return null;
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const targetDate = new Date(dateString);
  targetDate.setHours(0, 0, 0, 0);
  
  const timeDiff = targetDate.getTime() - today.getTime();
  const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
  
  return daysDiff;
}

// Nota: Quest ahora usa la misma lógica de días restantes (fecha fin) que los demás certificados.

/**
 * Obtiene la clase CSS y el texto según los días restantes
 */
function getExpiryStatus(daysRemaining) {
  if (daysRemaining === null) {
    return {
      class: 'badge-ghost',
      text: 'Sin fecha',
      color: '#6b7280'
    };
  }
  
  if (daysRemaining < 0) {
    return {
      class: 'badge-error',
      text: `Vencido hace ${Math.abs(daysRemaining)} día${Math.abs(daysRemaining) === 1 ? '' : 's'}`,
      color: '#dc2626'
    };
  } else if (daysRemaining === 0) {
    return {
      class: 'badge-error',
      text: 'Vence HOY',
      color: '#dc2626'
    };
  } else if (daysRemaining < 15) {
    return {
      class: 'badge-error',
      text: `${daysRemaining} día${daysRemaining === 1 ? '' : 's'} restante${daysRemaining === 1 ? '' : 's'}`,
      color: '#dc2626'
    };
  } else if (daysRemaining < 60) {
    return {
      class: 'badge-warning',
      text: `${daysRemaining} días restantes`,
      color: '#f59e0b'
    };
  } else if (daysRemaining < 90) {
    return {
      class: 'badge-info',
      text: `${daysRemaining} días restantes`,
      color: '#3b82f6'
    };
  } else {
    return {
      class: 'badge-success',
      text: `${daysRemaining} días restantes`,
      color: '#10b981'
    };
  }
}

// (Función getQuestStartStatus eliminada; Quest usa getExpiryStatus como los demás)

/**
 * Actualiza el badge de estado de un certificado
 */
function updateCertificateBadge(certificateKey) {
  const config = CERTIFICATE_CONFIG[certificateKey];
  if (!config) return;
  
  const expiryField = document.getElementById(config.expiryDateField);
  const badge = document.getElementById(config.badgeId);
  
  if (!expiryField || !badge) return;
  
  const expiryDate = expiryField.value;
  const daysRemaining = calculateDaysRemaining(expiryDate);
  const status = getExpiryStatus(daysRemaining);
  
  // Actualizar el badge
  badge.className = `badge badge-sm ${status.class}`;
  badge.textContent = status.text;
  badge.style.display = expiryDate ? 'inline-flex' : 'none';
  
  // Agregar animación para certificados críticos
  if (daysRemaining !== null && daysRemaining <= 0) {
    badge.style.animation = 'pulse 2s infinite';
  } else {
    badge.style.animation = 'none';
  }
}

// (Función específica de Quest eliminada; se trata como certificado normal)

/**
 * Configura los event listeners para los campos de fecha
 */
function setupCertificateWatchers() {
  Object.keys(CERTIFICATE_CONFIG).forEach(key => {
    const config = CERTIFICATE_CONFIG[key];
    
    // Observar cambios en el campo de fecha de caducidad
    const expiryField = document.getElementById(config.expiryDateField);
    if (expiryField) {
      expiryField.addEventListener('change', () => {
        updateCertificateBadge(key);
      });
      expiryField.addEventListener('input', () => {
        updateCertificateBadge(key);
      });
      
      // Actualizar badge inicial si ya hay un valor
      if (expiryField.value) {
        updateCertificateBadge(key);
      }
    }
  });
  
}

/**
 * Actualiza todos los badges de certificados
 */
function updateAllCertificateBadges() {
  Object.keys(CERTIFICATE_CONFIG).forEach(key => updateCertificateBadge(key));
}

/**
 * Manejo del botón de desactivación con confirmación en dos pasos
 */
function setupDeactivateButton() {
  const btnDeactivate = document.getElementById('btn-deactivate');
  
  if (!btnDeactivate) return;
  
  let confirmState = false;
  const originalText = '<i class="las la-trash text-xl"></i> Eliminar Técnico';
  const confirmText = '<i class="las la-check text-xl"></i> Confirmar Eliminación';
  const technicalName = btnDeactivate.dataset.technicalName;
  
  btnDeactivate.addEventListener('click', function() {
    if (!confirmState) {
      // Primera vez: cambiar a modo confirmación
      confirmState = true;
      btnDeactivate.innerHTML = confirmText;
      btnDeactivate.classList.remove('btn-error');
      btnDeactivate.classList.add('btn-warning', 'animate-pulse');
      
      // Resetear después de 5 segundos si no confirma
      setTimeout(function() {
        if (confirmState) {
          confirmState = false;
          btnDeactivate.innerHTML = originalText;
          btnDeactivate.classList.remove('btn-warning', 'animate-pulse');
          btnDeactivate.classList.add('btn-error');
        }
      }, 5000);
      
    } else {
      // Segunda vez: ejecutar la desactivación directamente
      document.getElementById('deactivate-form').submit();
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  setupCertificateWatchers();
  updateAllCertificateBadges();
  setupDeactivateButton();
  
  setInterval(updateAllCertificateBadges, 60000);
});
