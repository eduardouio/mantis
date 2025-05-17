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
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'notes': forms.TextInput(  # Consider changing to Textarea if appropriate for DaisyUI styling
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'place': forms.TextInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'contact_name': forms.TextInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'phone_contact': forms.TextInput(
                attrs={'class': 'input input-bordered input-md w-full'}
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
            'is_active': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-md'}
            )
        }
