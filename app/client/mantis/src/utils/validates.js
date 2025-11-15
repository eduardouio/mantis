/**
 * Verifica si una fecha está vencida
 */
export const isExpired = (date) => {
  if (!date) return false
  const today = new Date()
  const expiryDate = new Date(date)
  return expiryDate < today
}

/**
 * Verifica si una fecha está próxima a vencer (dentro de 30 días)
 */
export const isExpiringSoon = (date) => {
  if (!date) return false
  const today = new Date()
  const expiryDate = new Date(date)
  const daysUntilExpiry = Math.floor((expiryDate - today) / (1000 * 60 * 60 * 24))
  return daysUntilExpiry <= 30 && daysUntilExpiry > 0
}

/**
 * Valida los documentos de un técnico
 * Retorna un objeto con los problemas encontrados
 */
export const validateTechnical = (technical) => {
  if (!technical) return { hasErrors: false, hasWarnings: false, issues: [] }

  const issues = []
  let hasErrors = false
  let hasWarnings = false

  // Validar licencia de conducir
  if (isExpired(technical.license_expiry_date)) {
    issues.push({
      type: 'error',
      field: 'Licencia de Conducir',
      message: 'Licencia de conducir VENCIDA'
    })
    hasErrors = true
  } else if (isExpiringSoon(technical.license_expiry_date)) {
    issues.push({
      type: 'warning',
      field: 'Licencia de Conducir',
      message: 'Licencia de conducir próxima a vencer'
    })
    hasWarnings = true
  }

  // Validar certificado de conducción defensiva
  if (isExpired(technical.defensive_driving_certificate_expiry_date)) {
    issues.push({
      type: 'error',
      field: 'Conducción Defensiva',
      message: 'Certificado de conducción defensiva VENCIDO'
    })
    hasErrors = true
  } else if (isExpiringSoon(technical.defensive_driving_certificate_expiry_date)) {
    issues.push({
      type: 'warning',
      field: 'Conducción Defensiva',
      message: 'Certificado de conducción defensiva próximo a vencer'
    })
    hasWarnings = true
  }

  // Validar certificado médico
  if (isExpired(technical.medical_certificate_expiry_date)) {
    issues.push({
      type: 'error',
      field: 'Certificado Médico',
      message: 'Certificado médico VENCIDO'
    })
    hasErrors = true
  } else if (isExpiringSoon(technical.medical_certificate_expiry_date)) {
    issues.push({
      type: 'warning',
      field: 'Certificado Médico',
      message: 'Certificado médico próximo a vencer'
    })
    hasWarnings = true
  }

  // Validar pases de acceso
  if (technical.passes && technical.passes.length > 0) {
    technical.passes.forEach(pass => {
      if (isExpired(pass.fecha_caducidad)) {
        issues.push({
          type: 'error',
          field: `Pase ${pass.bloque_display || pass.bloque}`,
          message: `Pase de acceso VENCIDO`
        })
        hasErrors = true
      } else if (isExpiringSoon(pass.fecha_caducidad)) {
        issues.push({
          type: 'warning',
          field: `Pase ${pass.bloque_display || pass.bloque}`,
          message: `Pase de acceso próximo a vencer`
        })
        hasWarnings = true
      }
    })
  }

  // Validar afiliación IESS
  if (!technical.is_iess_affiliated) {
    issues.push({
      type: 'warning',
      field: 'IESS',
      message: 'No está afiliado al IESS'
    })
    hasWarnings = true
  }

  return { hasErrors, hasWarnings, issues }
}

/**
 * Valida los documentos de un vehículo
 * Retorna un objeto con los problemas encontrados
 */
export const validateVehicle = (vehicle) => {
  if (!vehicle) return { hasErrors: false, hasWarnings: false, issues: [] }

  const issues = []
  let hasErrors = false
  let hasWarnings = false

  // Validar matrícula
  if (isExpired(vehicle.due_date_matricula)) {
    issues.push({
      type: 'error',
      field: 'Matrícula',
      message: 'Matrícula VENCIDA'
    })
    hasErrors = true
  } else if (isExpiringSoon(vehicle.due_date_matricula)) {
    issues.push({
      type: 'warning',
      field: 'Matrícula',
      message: 'Matrícula próxima a vencer'
    })
    hasWarnings = true
  }

  // Validar certificado operacional
  if (vehicle.status_cert_oper === 'VENCIDO') {
    issues.push({
      type: 'error',
      field: 'Certificado Operacional',
      message: 'Certificado operacional VENCIDO'
    })
    hasErrors = true
  } else if (isExpiringSoon(vehicle.due_date_cert_oper)) {
    issues.push({
      type: 'warning',
      field: 'Certificado Operacional',
      message: 'Certificado operacional próximo a vencer'
    })
    hasWarnings = true
  }

  // Validar revisión técnica
  if (isExpired(vehicle.due_date_technical_review)) {
    issues.push({
      type: 'error',
      field: 'Revisión Técnica',
      message: 'Revisión técnica VENCIDA'
    })
    hasErrors = true
  } else if (isExpiringSoon(vehicle.due_date_technical_review)) {
    issues.push({
      type: 'warning',
      field: 'Revisión Técnica',
      message: 'Revisión técnica próxima a vencer'
    })
    hasWarnings = true
  }

  // Validar seguro
  if (isExpired(vehicle.insurance_expiration_date)) {
    issues.push({
      type: 'error',
      field: 'Seguro',
      message: 'Seguro VENCIDO'
    })
    hasErrors = true
  } else if (isExpiringSoon(vehicle.insurance_expiration_date)) {
    issues.push({
      type: 'warning',
      field: 'Seguro',
      message: 'Seguro próximo a vencer'
    })
    hasWarnings = true
  }

  // Validar satélite
  if (isExpired(vehicle.due_date_satellite)) {
    issues.push({
      type: 'error',
      field: 'Satélite',
      message: 'Certificado de satélite VENCIDO'
    })
    hasErrors = true
  } else if (isExpiringSoon(vehicle.due_date_satellite)) {
    issues.push({
      type: 'warning',
      field: 'Satélite',
      message: 'Certificado de satélite próximo a vencer'
    })
    hasWarnings = true
  }

  return { hasErrors, hasWarnings, issues }
}
