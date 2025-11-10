export const formatCurrency = (value) => {
  // Parsear el valor si es texto o null/undefined
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  // Si no es un número válido, retornar 0.00 formateado
  if (isNaN(numValue) || numValue === null || numValue === undefined) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(0);
  }
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(numValue);
};

export const formatNumber = (value) => {
  // Parsear el valor si es texto o null/undefined
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  // Si no es un número válido, retornar 0.00
  if (isNaN(numValue) || numValue === null || numValue === undefined) {
    return '0.00';
  }
  
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(numValue);
};

export const formatDate = (date) => {
  if (!date) return '--';
  return new Intl.DateTimeFormat('es-GT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(new Date(date));
};
