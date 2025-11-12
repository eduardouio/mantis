/**
 * Genera un calendario de mantenimientos para recursos del proyecto
 * basado en la frecuencia de intervalos y fecha de inicio de operación
 */

/**
 * Obtiene el inicio de la semana actual (Lunes)
 * @returns {Date} Fecha del lunes de la semana actual
 */
function getStartOfCurrentWeek() {
  const today = new Date();
  const day = today.getDay();
  const diff = today.getDate() - day + (day === 0 ? -6 : 1); 
  const monday = new Date(today.setDate(diff));
  monday.setHours(0, 0, 0, 0);
  return monday;
}

/**
 * Obtiene el fin del período de 4 semanas desde el lunes actual
 * @returns {Date} Fecha del domingo de la 4ta semana
 */
function getEndOfFourWeeks() {
  const startOfWeek = getStartOfCurrentWeek();
  const endOfFourWeeks = new Date(startOfWeek);
  endOfFourWeeks.setDate(startOfWeek.getDate() + 27); // 4 semanas = 28 días - 1
  endOfFourWeeks.setHours(23, 59, 59, 999);
  return endOfFourWeeks;
}

/**
 * Genera todas las fechas de mantenimiento desde la fecha de inicio hasta el fin de las 4 semanas
 * @param {string} startDateStr - Fecha de inicio en formato YYYY-MM-DD
 * @param {number} intervalDays - Días entre cada mantenimiento
 * @returns {Date[]} Array de fechas de mantenimiento
 */
function generateMaintenanceDates(startDateStr, intervalDays) {
  // Parsear la fecha sin problemas de zona horaria
  const [year, month, day] = startDateStr.split('-').map(Number);
  const startDate = new Date(year, month - 1, day);
  const endOfFourWeeks = getEndOfFourWeeks();
  const maintenanceDates = [];
  
  let currentDate = new Date(startDate);
  
  while (currentDate <= endOfFourWeeks) {
    maintenanceDates.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + intervalDays);
  }
  
  return maintenanceDates;
}

/**
 * Genera el calendario de mantenimientos para las próximas 4 semanas
 * @param {Array} resources - Array de recursos del proyecto
 * @returns {Array} Lista de mantenimientos programados para las 4 semanas
 */
export function generateWeeklyMaintenanceSchedule(resources) {
  const startOfWeek = getStartOfCurrentWeek();
  const endOfFourWeeks = getEndOfFourWeeks();
  const maintenanceSchedule = [];
  
  resources.forEach(resource => {
    
    if (!resource.is_active) {
      return;
    }
    
    
    const maintenanceDates = generateMaintenanceDates(
      resource.operation_start_date,
      resource.interval_days
    );
    
    
    const fourWeeksMaintenance = maintenanceDates.filter(date => {
      return date >= startOfWeek && date <= endOfFourWeeks;
    });
    
    
    fourWeeksMaintenance.forEach(maintenanceDate => {
      maintenanceSchedule.push({
        resource_id: resource.id,
        resource_item_id: resource.resource_item_id,
        resource_code: resource.resource_item_code,
        resource_name: resource.resource_item_name,
        description: resource.detailed_description,
        cost: parseFloat(resource.cost),
        interval_days: resource.interval_days,
        operation_start_date: resource.operation_start_date,
        scheduled_date: maintenanceDate.toISOString().split('T')[0],
        day_of_week: maintenanceDate.toLocaleDateString('es-GT', { weekday: 'long' }),
        week_number: getWeekNumber(maintenanceDate)
      });
    });
  });
  
  
  return maintenanceSchedule.sort((a, b) => 
    new Date(a.scheduled_date) - new Date(b.scheduled_date)
  );
}

/**
 * Genera calendario de mantenimientos futuros (próximas N semanas)
 * @param {Array} resources - Array de recursos del proyecto
 * @param {number} weeksAhead - Número de semanas a futuro (por defecto 4)
 * @returns {Array} Lista de mantenimientos programados
 */
export function generateFutureMaintenanceSchedule(resources, weeksAhead = 4) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const futureDate = new Date(today);
  futureDate.setDate(today.getDate() + (weeksAhead * 7));
  
  const maintenanceSchedule = [];
  
  resources.forEach(resource => {
    if (!resource.is_active) {
      return;
    }
    
    const maintenanceDates = generateMaintenanceDates(
      resource.operation_start_date,
      resource.interval_days
    );
    
    
    const futureMaintenance = maintenanceDates.filter(date => {
      return date >= today && date <= futureDate;
    });
    
    futureMaintenance.forEach(maintenanceDate => {
      maintenanceSchedule.push({
        resource_id: resource.id,
        resource_item_id: resource.resource_item_id,
        resource_code: resource.resource_item_code,
        resource_name: resource.resource_item_name,
        description: resource.detailed_description,
        cost: parseFloat(resource.cost),
        interval_days: resource.interval_days,
        operation_start_date: resource.operation_start_date,
        scheduled_date: maintenanceDate.toISOString().split('T')[0],
        day_of_week: maintenanceDate.toLocaleDateString('es-GT', { weekday: 'long' }),
        week_number: getWeekNumber(maintenanceDate),
        days_until: Math.ceil((maintenanceDate - today) / (1000 * 60 * 60 * 24))
      });
    });
  });
  
  return maintenanceSchedule.sort((a, b) => 
    new Date(a.scheduled_date) - new Date(b.scheduled_date)
  );
}

/**
 * Obtiene el número de semana del año
 * @param {Date} date - Fecha
 * @returns {number} Número de semana
 */
function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

/**
 * Agrupa mantenimientos por semana
 * @param {Array} maintenanceSchedule - Lista de mantenimientos
 * @returns {Object} Mantenimientos agrupados por semana
 */
export function groupMaintenanceByWeek(maintenanceSchedule) {
  return maintenanceSchedule.reduce((groups, maintenance) => {
    const weekKey = `Semana ${maintenance.week_number}`;
    if (!groups[weekKey]) {
      groups[weekKey] = [];
    }
    groups[weekKey].push(maintenance);
    return groups;
  }, {});
}

/**
 * Obtiene resumen de mantenimientos
 * @param {Array} maintenanceSchedule - Lista de mantenimientos
 * @returns {Object} Resumen con totales
 */
export function getMaintenanceSummary(maintenanceSchedule) {
  return {
    total_maintenances: maintenanceSchedule.length,
    total_cost: maintenanceSchedule.reduce((sum, m) => sum + m.cost, 0),
    resources_count: new Set(maintenanceSchedule.map(m => m.resource_id)).size,
    by_week: groupMaintenanceByWeek(maintenanceSchedule)
  };
}
