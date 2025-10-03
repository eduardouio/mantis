// Manejo de badges de vencimiento para formulario de vehículos
// Basado en la lógica existente de app-technical_form.js

const VEHICLE_DATE_CONFIG = {
  insurance: {
    endField: 'id_insurance_expiration_date',
    badgeId: 'insuranceExpiryBadge',
    name: 'Seguro'
  },
  satellite: {
    endField: 'id_due_date_satellite',
    badgeId: 'satelliteExpiryBadge',
    name: 'Satelital'
  },
  matricula: {
    endField: 'id_due_date_matricula',
    badgeId: 'matriculaExpiryBadge',
    name: 'Matrícula'
  },
  certOper: {
    endField: 'id_due_date_cert_oper',
    badgeId: 'certOperExpiryBadge',
    name: 'Cert. Operación'
  },
  mtop: {
    endField: 'id_date_mtop',
    badgeId: 'mtopExpiryBadge',
    name: 'MTOP'
  },
  technicalReview: {
    endField: 'id_date_technical_review',
    badgeId: 'technicalReviewExpiryBadge',
    name: 'Rev. Técnica'
  }
};

function vfCalculateDaysRemaining(dateString) {
  if (!dateString) return null;
  const today = new Date();
  today.setHours(0,0,0,0);
  const target = new Date(dateString);
  if (isNaN(target)) return null;
  target.setHours(0,0,0,0);
  const diffMs = target.getTime() - today.getTime();
  return Math.ceil(diffMs / 86400000);
}

function vfGetExpiryStatus(days) {
  if (days === null) return { cls: 'badge-ghost', text: 'Sin fecha' };
  if (days < 0) return { cls: 'badge-error', text: `Vencido hace ${Math.abs(days)} días` };
  if (days === 0) return { cls: 'badge-error', text: 'Vence HOY' };
  if (days < 15) return { cls: 'badge-error', text: `${days} días restantes` };
  if (days < 60) return { cls: 'badge-warning', text: `${days} días` };
  if (days < 90) return { cls: 'badge-info', text: `${days} días` };
  return { cls: 'badge-success', text: `${days} días` };
}

function vfUpdateBadge(key) {
  const cfg = VEHICLE_DATE_CONFIG[key];
  if (!cfg) return;
  const field = document.getElementById(cfg.endField);
  const badge = document.getElementById(cfg.badgeId);
  if (!field || !badge) return;
  const val = field.value;
  const days = vfCalculateDaysRemaining(val);
  const status = vfGetExpiryStatus(days);
  badge.className = `badge badge-sm ${status.cls}`;
  badge.textContent = status.text;
  badge.classList.toggle('hidden', !val);
  if (days !== null && days <= 0) {
    badge.style.animation = 'pulse 2s infinite';
  } else {
    badge.style.animation = 'none';
  }
}

function vfSetupWatchers() {
  Object.keys(VEHICLE_DATE_CONFIG).forEach(key => {
    const { endField } = VEHICLE_DATE_CONFIG[key];
    const el = document.getElementById(endField);
    if (el) {
      ['change','input'].forEach(evt => el.addEventListener(evt, () => vfUpdateBadge(key)));
      if (el.value) vfUpdateBadge(key);
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  vfSetupWatchers();
  setInterval(() => {
    Object.keys(VEHICLE_DATE_CONFIG).forEach(vfUpdateBadge);
  }, 60000);
});
