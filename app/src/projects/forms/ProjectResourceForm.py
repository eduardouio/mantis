from django import forms
from projects.models import ProjectResourceItem


class ProjectResourceForm(forms.ModelForm):
    class Meta:
        model = ProjectResourceItem
        fields = [
            'project', 'resource_item', 'cost', 'cost_manteinance', 'is_active',
            'start_date', 'end_date', 'mantenance_frequency', 'times_mantenance',
            'retired_date', 'motive_retired'
        ]
        widgets = {
            'project': forms.Select(
                attrs={'class': 'form-select form-control-sm'}
            ),
            'resource_item': forms.Select(
                attrs={'class': 'form-select form-control-sm'}
            ),
            'cost': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'cost_manteinance': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
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
            'mantenance_frequency': forms.Select(
                attrs={'class': 'form-select form-control-sm'}
            ),
            'times_mantenance': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'retired_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-sm',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'motive_retired': forms.Textarea(
                attrs={'class': 'form-control form-control-sm'}
            )
        }
