from django import forms
from projects.models import Project


class ProjectForm(forms.ModelForm):
    """Formulario de creación/edición de Project adaptado al nuevo modelo.

    Cambios respecto a la versión previa:
        - place  -> location
        - phone_contact -> contact_phone
        - is_active -> is_closed (antes check = activo, ahora check = cerrado)
        - Se elimina 'notes' (el modelo actual ya no lo expone)
        - end_date e is_closed se gestionan desde otros procesos de control
    """

    class Meta:
        model = Project
        fields = [
            'partner', 'location', 'contact_name', 'contact_phone',
            'start_date', 'notes'
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
            'notes': forms.Textarea(
                attrs={
                    'class': 'textarea textarea-bordered w-full',
                    'placeholder': 'Notas adicionales sobre el proyecto',
                    'rows': 4
                }
            ),
        }
