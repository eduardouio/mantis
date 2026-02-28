/**
 * Genera un calendario de mantenimientos para recursos del proyecto
 * basado en frequency_type: DAY (intervalo), WEEK (días semana), MONTH (días mes)
 */

/**
 * Genera fechas de mantenimiento según frequency_type
 * @param {Object} resource - Recurso con configuración de frecuencia
 * @param {Date} operationStart - Fecha original de inicio de operaciones del recurso
 * @param {Date} startDate - Fecha de inicio del rango visible (ej: primer día del mes)
 * @param {Date} endDate - Fecha de fin del rango visible
 * @returns {Date[]} Array de fechas de mantenimiento
 */
function generateMaintenanceDates(resource, operationStart, startDate, endDate) {
  const dates = [];
  const { frequency_type, interval_days, weekdays, monthdays } = resource;
  
  if (frequency_type === 'DAY') {
    // Intervalo de días (interval_days = 0 significa diario)
    const interval = interval_days === 0 ? 1 : interval_days;
    
    // Calcular la próxima fecha de mantenimiento alineada con operation_start_date
    // Se calcula cuántos intervalos completos han pasado desde el inicio hasta startDate
    let currentDate;
    if (operationStart >= startDate) {
      // El recurso inicia después del rango visible, empezar desde su fecha de inicio
      currentDate = new Date(operationStart);
    } else {
      // Alinear: encontrar el último mantenimiento antes o en startDate
      const diffTime = startDate.getTime() - operationStart.getTime();
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
      const intervalsPassed = Math.floor(diffDays / interval);
      currentDate = new Date(operationStart);
      currentDate.setDate(currentDate.getDate() + intervalsPassed * interval);
      
      // Si quedó antes del rango visible, avanzar un intervalo más
      if (currentDate < startDate) {
        currentDate.setDate(currentDate.getDate() + interval);
      }
    }
    
    while (currentDate <= endDate) {
      dates.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + interval);
    }
  } 
  else if (frequency_type === 'WEEK') {
    // Días específicos de la semana
    if (!weekdays || weekdays.length === 0) {
      console.warn('Recurso WEEK sin weekdays definidos:', resource);
      return dates;
    }
    
    let currentDate = new Date(startDate);
    while (currentDate <= endDate) {
      const dayOfWeek = (currentDate.getDay() + 6) % 7; // 0=Lunes, 1=Martes, ..., 6=Domingo
      if (weekdays.includes(dayOfWeek)) {
        dates.push(new Date(currentDate));
      }
      currentDate.setDate(currentDate.getDate() + 1);
    }
  } 
  else if (frequency_type === 'MONTH') {
    // Días específicos del mes
    if (!monthdays || monthdays.length === 0) {
      console.warn('Recurso MONTH sin monthdays definidos:', resource);
      return dates;
    }
    
    let currentDate = new Date(startDate);
    while (currentDate <= endDate) {
      const dayOfMonth = currentDate.getDate();
      if (monthdays.includes(dayOfMonth)) {
        dates.push(new Date(currentDate));
      }
      currentDate.setDate(currentDate.getDate() + 1);
    }
  }
  
  return dates;
}

/**
 * Genera el calendario de mantenimientos para los próximos N días
 * @param {Array} resources - Array de recursos del proyecto
 * @param {number} daysAhead - Número de días a futuro (por defecto 90)
 * @param {Date} fromDate - Fecha de inicio opcional (por defecto hoy)
 * @returns {Array} Lista de mantenimientos programados
 */
export function generateMaintenanceSchedule(resources, daysAhead = 90, fromDate = null) {
  const today = fromDate ? new Date(fromDate) : new Date();
  today.setHours(0, 0, 0, 0);
  
  const futureDate = new Date(today);
  futureDate.setDate(today.getDate() + daysAhead);
  
  const maintenanceSchedule = [];
  
  resources.forEach(resource => {
    // Filtrar recursos no activos o retirados
    if (!resource.is_active || resource.is_retired) {
      return;
    }

    // Solo procesar servicios, no equipos
    if (resource.type_resource !== 'SERVICIO') {
      return;
    }

    if (!resource.operation_start_date) {
      console.warn('Recurso sin fecha de inicio de operación:', resource);
      return;
    }

    // Parsear fecha de inicio
    const [year, month, day] = resource.operation_start_date.split('-').map(Number);
    const operationStart = new Date(year, month - 1, day);
    
    // Si el recurso tiene fecha de fin de operación y ya pasó, no procesar
    if (resource.operation_end_date) {
      const [ey, em, ed] = resource.operation_end_date.split('-').map(Number);
      const operationEnd = new Date(ey, em - 1, ed);
      if (operationEnd < today) {
        return;
      }
    }

    // El rango visible es [today, futureDate], pero el recurso puede haber iniciado antes
    const startDate = operationStart > today ? operationStart : today;
    
    // Si el recurso tiene fecha de fin, limitar el rango
    let effectiveEndDate = futureDate;
    if (resource.operation_end_date) {
      const [ey, em, ed] = resource.operation_end_date.split('-').map(Number);
      const operationEnd = new Date(ey, em - 1, ed);
      if (operationEnd < futureDate) {
        effectiveEndDate = operationEnd;
      }
    }
    
    const maintenanceDates = generateMaintenanceDates(resource, operationStart, startDate, effectiveEndDate);
    
    maintenanceDates.forEach(maintenanceDate => {
      maintenanceSchedule.push({
        resource_id: resource.id,
        resource_item_id: resource.resource_item_id,
        resource_code: resource.resource_item_code,
        resource_name: resource.resource_item_name,
        description: resource.detailed_description,
        cost: parseFloat(resource.cost),
        frequency_type: resource.frequency_type,
        interval_days: resource.interval_days,
        weekdays: resource.weekdays,
        monthdays: resource.monthdays,
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
 * Genera calendario para las próximas 4 semanas (compatibilidad)
 */
export function generateWeeklyMaintenanceSchedule(resources) {
  return generateMaintenanceSchedule(resources, 28);
}

/**
 * Genera calendario futuro (compatibilidad)
 */
export function generateFutureMaintenanceSchedule(resources, weeksAhead = 4) {
  return generateMaintenanceSchedule(resources, weeksAhead * 7);
}

/**
 * Obtiene el número de semana del año
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
 * Agrupa mantenimientos por mes
 */
export function groupMaintenanceByMonth(maintenanceSchedule) {
  return maintenanceSchedule.reduce((groups, maintenance) => {
    const date = new Date(maintenance.scheduled_date);
    const monthKey = date.toLocaleDateString('es-GT', { year: 'numeric', month: 'long' });
    if (!groups[monthKey]) {
      groups[monthKey] = [];
    }
    groups[monthKey].push(maintenance);
    return groups;
  }, {});
}

/**
 * Obtiene resumen de mantenimientos
 */
export function getMaintenanceSummary(maintenanceSchedule) {
  return {
    total_maintenances: maintenanceSchedule.length,
    total_cost: maintenanceSchedule.reduce((sum, m) => sum + m.cost, 0),
    resources_count: new Set(maintenanceSchedule.map(m => m.resource_id)).size,
    by_week: groupMaintenanceByWeek(maintenanceSchedule),
    by_month: groupMaintenanceByMonth(maintenanceSchedule)
  };
}
