from django import forms
from projects.models import ProjectResourceItem


class ProjectResourceForm(forms.ModelForm):
    """Formulario para asociar un ResourceItem a un Project.

    Actualizado a los campos vigentes del modelo ProjectResourceItem:
        - cost -> rent_cost
        - cost_manteinance -> maintenance_cost
        - mantenance_frequency -> maintenance_interval_days (entero de días)
        - start_date / end_date -> operation_start_date / operation_end_date
        - is_active -> is_retired (semántica inversa, se muestra como retirado)
        - retired_date -> retirement_date
        - motive_retired -> retirement_reason
        - times_mantenance se elimina (no existe en el modelo actual)
    """

    class Meta:
        model = ProjectResourceItem
        fields = [
            'project', 'resource_item', 'cost', 'interval_days',
            'operation_start_date', 'operation_end_date', 'is_retired',
            'retirement_date', 'retirement_reason'
        ]
        widgets = {
            'project': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'resource_item': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'cost': forms.NumberInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'step': '0.01'
                }
            ),
            'interval_days': forms.NumberInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'min': '1'
                }
            ),
            'operation_start_date': forms.DateInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'operation_end_date': forms.DateInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'is_retired': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-md'}
            ),
            'retirement_date': forms.DateInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'retirement_reason': forms.Textarea(
                attrs={
                    'class': 'textarea textarea-bordered textarea-md w-full',
                    'rows': 3
                }
            )
        }

    def clean(self):
        data = super().clean()
        start = data.get('operation_start_date')
        end = data.get('operation_end_date')
        if start and end and end < start:
            self.add_error(
                'operation_end_date',
                'La fecha de fin de operación no puede ser anterior a la '
                'fecha de inicio.'
            )
        return data
