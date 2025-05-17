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
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'resource_item': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'cost': forms.NumberInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'cost_manteinance': forms.NumberInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-md'}
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
            'mantenance_frequency': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'times_mantenance': forms.NumberInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'retired_date': forms.DateInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'motive_retired': forms.Textarea(
                attrs={'class': 'textarea textarea-bordered textarea-md w-full'}
            )
        }
