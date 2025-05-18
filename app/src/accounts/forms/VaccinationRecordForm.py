from django import forms
from accounts.models import VaccinationRecord


class VaccinationRecordForm(forms.ModelForm):
    class Meta:
        model = VaccinationRecord
        fields = [
            'technical', 'vaccine_type', 'application_date', 
            'dose_number', 'next_dose_date', 'notes'
        ]
        widgets = {
            'technical': forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'vaccine_type': forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'application_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'dose_number': forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'next_dose_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'border rounded px-3 py-2 w-full', 'rows': 3}),
        }
        labels = {
            'technical': 'Técnico',
            'vaccine_type': 'Tipo de Vacuna',
            'application_date': 'Fecha de Aplicación',
            'dose_number': 'Número de Dosis',
            'next_dose_date': 'Fecha Próxima Dosis',
            'notes': 'Notas Adicionales',
        }
        help_texts = {
            'technical': 'Seleccione el técnico asociado.',
            'vaccine_type': 'Seleccione el tipo de vacuna.',
            'application_date': 'Ingrese la fecha de aplicación de la vacuna.',
            'dose_number': 'Dejar en blanco si es dosis única o no aplica.',
            'next_dose_date': 'Fecha estimada para la siguiente dosis, si aplica.',
            'notes': 'Ingrese notas adicionales si es necesario.',
        }
        error_messages = {
            'technical': {
                'required': 'Este campo es obligatorio.',
            },
            'vaccine_type': {
                'required': 'Este campo es obligatorio.',
            },
            'application_date': {
                'required': 'Este campo es obligatorio.',
                'invalid': 'Ingrese una fecha válida.',
            },
        }