from django import forms
from accounts.models import License, Technical

class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        fields = [
            'license_key', 'activated_on', 'expires_on', 'licence_file',
            'role', 'enterprise', 'is_active', 'url_server', 'user'
        ]
        widgets = {
            'license_key': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'activated_on': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'expires_on': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'licence_file': forms.TextInput(attrs={'class': 'form-control form-control-sm'}), # Considerar FileInput si es un archivo
            'role': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'enterprise': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'url_server': forms.URLInput(attrs={'class': 'form-control form-control-sm'}),
            'user': forms.Select(attrs={'class': 'form-select form-control-sm'}),
        }

# Si TechnicalForm no estaba aquí, debería añadirse también para consistencia.
# Ejemplo:
# class TechnicalForm(forms.ModelForm):
#     class Meta:
#         model = Technical
#         fields = '__all__' # o los campos específicos
#         # ... widgets ...
