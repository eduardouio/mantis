from django import forms
from equipment.models import Vehicle


class VehicleForm(forms.ModelForm):
    """Formulario simplificado: solo campos del modelo base Vehicle."""

    class Meta:
        model = Vehicle
        fields = [
            'brand', 'model', 'type_vehicle', 'year',
            'no_plate', 'owner_transport', 'status_vehicle',
            'color', 'chassis_number', 'engine_number', 'serial_number',
            'is_active', 'notes',
            # Campos de seguros
            'insurance_company', 'nro_poliza',
            'insurance_issue_date', 'insurance_expiration_date',
            'duedate_satellite',
            # Campos de documentos
            'date_matricula', 'due_date_matricula', 'due_date_cert_oper',
            'status_cert_oper', 'date_mtop', 'date_technical_review'
        ]
        widgets = {
            'brand': forms.TextInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'model': forms.TextInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'type_vehicle': forms.Select(attrs={
                'class': 'select select-bordered select-md w-full'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'no_plate': forms.TextInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'owner_transport': forms.Select(attrs={
                'class': 'select select-bordered select-md w-full'
            }),
            'status_vehicle': forms.Select(attrs={
                'class': 'select select-bordered select-md w-full'
            }),
            'color': forms.TextInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'chassis_number': forms.TextInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'engine_number': forms.TextInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-md'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered textarea-md w-full',
                'rows': 2
            }),
            # Widgets para campos de seguros
            'insurance_company': forms.TextInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'nro_poliza': forms.TextInput(attrs={
                'class': 'input input-bordered input-md w-full'
            }),
            'insurance_issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered input-md w-full',
                'type': 'date'
            }),
            'insurance_expiration_date': forms.DateInput(attrs={
                'class': 'input input-bordered input-md w-full',
                'type': 'date'
            }),
            'duedate_satellite': forms.DateInput(attrs={
                'class': 'input input-bordered input-md w-full',
                'type': 'date'
            }),
            # Widgets para campos de documentos
            'date_matricula': forms.DateInput(attrs={
                'class': 'input input-bordered input-md w-full',
                'type': 'date'
            }),
            'due_date_matricula': forms.DateInput(attrs={
                'class': 'input input-bordered input-md w-full',
                'type': 'date'
            }),
            'due_date_cert_oper': forms.DateInput(attrs={
                'class': 'input input-bordered input-md w-full',
                'type': 'date'
            }),
            'date_mtop': forms.DateInput(attrs={
                'class': 'input input-bordered input-md w-full',
                'type': 'date'
            }),
            'date_technical_review': forms.DateInput(attrs={
                'class': 'input input-bordered input-md w-full',
                'type': 'date'
            }),
            'status_cert_oper': forms.Select(attrs={
                'class': 'select select-bordered select-md w-full'
            }),
        }
