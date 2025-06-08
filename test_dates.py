#!/usr/bin/env python3
"""
Script para probar el formateo de fechas en Django
"""

# Simular el formateo de fechas como lo haría Django
from datetime import date

# Ejemplo de fecha de la base de datos
example_date = date(2024, 3, 15)
print(f"Fecha original: {example_date}")
print(f"Formato para HTML date input: {example_date.strftime('%Y-%m-%d')}")

# Simular datos como los que vendríían de la base de datos
vaccination_data = {
    'id': 1,
    'vaccine_type': 'COVID',
    'application_date': date(2024, 3, 15),
    'next_dose_date': date(2024, 6, 15),
    'dose_number': 1,
    'batch_number': 'ABC123',
    'notes': 'Primera dosis'
}

print("\nAntes del formateo:")
print(vaccination_data)

# Aplicar el formateo como lo hice en el código
if vaccination_data['application_date']:
    vaccination_data['application_date'] = vaccination_data['application_date'].strftime('%Y-%m-%d')
if vaccination_data['next_dose_date']:
    vaccination_data['next_dose_date'] = vaccination_data['next_dose_date'].strftime('%Y-%m-%d')

print("\nDespués del formateo:")
print(vaccination_data)
