from django import forms
from projects.models import Project


class ProjectForm(forms.ModelForm):
    """Formulario de creación/edición de Project adaptado al nuevo modelo.

    Cambios respecto a la versión previa:
        - place  -> location
        - phone_contact -> contact_phone
        - is_active -> is_closed (antes check = activo, ahora check = cerrado)
        - Se elimina 'notes' (el modelo actual ya no lo expone)
    """

    class Meta:
        model = Project
        fields = [
            'partner', 'location', 'contact_name', 'contact_phone',
            'start_date', 'end_date', 'is_closed'
        ]
        widgets = {
            'partner': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'placeholder': 'Campamento / Ubicación'
                }
            ),
            'contact_name': forms.TextInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'placeholder': 'Nombre de contacto principal'
                }
            ),
            'contact_phone': forms.TextInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'placeholder': '+593...'  # Ajustar formato esperado
                }
            ),
            'start_date': forms.DateInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'end_date': forms.DateInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'is_closed': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-md'}
            )
        }

    def clean(self):
        data = super().clean()
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            self.add_error(
                'end_date',
                'La fecha de fin no puede ser anterior a la fecha de inicio.'
            )
        return data
