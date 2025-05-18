from django import forms
from accounts.models import PassTechnical


class PassTechnicalForm(forms.ModelForm):
    class Meta:
        model = PassTechnical
        fields = ['technical', 'bloque', 'fecha_caducidad']
        widgets = {
            'technical': forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'bloque': forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'fecha_caducidad': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
        }