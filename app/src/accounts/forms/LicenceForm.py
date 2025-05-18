from django import forms
from accounts.models import License


class LicenceForm(forms.ModelForm):
    class Meta:
        model = License
        fields = [
            'license_key', 'activated_on', 'expires_on', 'licence_file',
            'role', 'enterprise', 'is_active', 'url_server', 'user'
        ]
        widgets = {
            'license_key': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'activated_on': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'expires_on': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'licence_file': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'role': forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'enterprise': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'url_server': forms.URLInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'user': forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}),
        }
