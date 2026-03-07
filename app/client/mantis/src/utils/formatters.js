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

  // Tomar solo la parte YYYY-MM-DD (ignorar tiempo/zona horaria si viene)
  const dateOnly = String(date).split('T')[0];
  const [year, month, day] = dateOnly.split('-');
  const localDate = new Date(year, month - 1, day);

  return new Intl.DateTimeFormat('es-EC', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(localDate);
};

export const getLocalDateString = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};
