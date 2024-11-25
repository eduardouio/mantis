
from django import forms
from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'partner', 'place', 'contact_name', 'phone_contact', 'start_date',
            'end_date', 'is_active', 'notes'
        ]
        widgets = {
            'partner': forms.Select(
                attrs={'class': 'form-select form-control-sm'}
            ),
            'notes': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'place': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'contact_name': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'phone_contact': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'start_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-sm',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'end_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-sm',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            )
        }
