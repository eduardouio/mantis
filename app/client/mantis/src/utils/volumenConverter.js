/**
 * Constantes de conversión
 * 1 barril = 42 galones (galones estadounidenses)
 * 1 barril = 0.158987 metros cúbicos
 * 1 galón = 0.00378541 metros cúbicos
 */

const GALLONS_PER_BARREL = 42
const M3_PER_BARREL = 0.158987
const M3_PER_GALLON = 0.00378541


export const fromGallons = (gallons) => {
  const value = parseFloat(gallons) || 0
  return {
    barrels: parseFloat((value / GALLONS_PER_BARREL).toFixed(2)),
    cubicMeters: parseFloat((value * M3_PER_GALLON).toFixed(2))
  }
}


export const fromBarrels = (barrels) => {
  const value = parseFloat(barrels) || 0
  return {
    gallons: parseFloat((value * GALLONS_PER_BARREL).toFixed(2)),
    cubicMeters: parseFloat((value * M3_PER_BARREL).toFixed(2))
  }
}


export const fromCubicMeters = (cubicMeters) => {
  const value = parseFloat(cubicMeters) || 0
  return {
    gallons: parseFloat((value / M3_PER_GALLON).toFixed(2)),
    barrels: parseFloat((value / M3_PER_BARREL).toFixed(2))
  }
}


export const convertVolume = (value, fromUnit) => {
  const amount = parseFloat(value) || 0
  
  switch(fromUnit.toLowerCase()) {
    case 'gallons':
    case 'galones':
      const fromGal = fromGallons(amount)
      return {
        gallons: amount,
        barrels: fromGal.barrels,
        cubicMeters: fromGal.cubicMeters
      }
    
    case 'barrels':
    case 'barriles':
      const fromBar = fromBarrels(amount)
      return {
        gallons: fromBar.gallons,
        barrels: amount,
        cubicMeters: fromBar.cubicMeters
      }
    
    case 'cubicmeters':
    case 'metroscubicos':
    case 'm3':
      const fromM3 = fromCubicMeters(amount)
      return {
        gallons: fromM3.gallons,
        barrels: fromM3.barrels,
        cubicMeters: amount
      }
    
    default:
      return {
        gallons: 0,
        barrels: 0,
        cubicMeters: 0
      }
  }
}


export const formatVolume = (value, decimals = 2) => {
  const num = parseFloat(value) || 0
  return num.toFixed(decimals)
}
