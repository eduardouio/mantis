export const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
};

export const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Intl.DateTimeFormat('es-GT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(new Date(date));
};
