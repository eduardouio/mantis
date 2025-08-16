from django import forms
from projects.models import Partner


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = [
            'business_tax_id',
            'name',
            'email',
            'phone',
            'address',
            'name_contact',
            'notes',
            'is_active'
        ]
        widgets = {
            'business_tax_id': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ingrese el RUC',
                'maxlength': '15'
            }),
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nombre de la empresa'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'correo@empresa.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Número de teléfono'
            }),
            'address': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Dirección completa'
            }),
            'name_contact': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nombre del contacto principal'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full min-h-20',
                'rows': 4,
                'placeholder': (
                    'Observaciones adicionales sobre el socio de '
                    'negocio'
                )
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Campos requeridos
        self.fields['business_tax_id'].required = True
        self.fields['name'].required = True
        self.fields['address'].required = True

        # Configurar el campo is_active como True por defecto
        if not self.instance.pk:
            self.fields['is_active'].initial = True
