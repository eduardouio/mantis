from django import forms
from equipment.models import Vehicle


class VehicleForm(forms.ModelForm):
    """
    Formulario para crear y actualizar vehículos
    """

    # Campos ocultos para almacenar datos de certificaciones y pases
    certifications_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    passes_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = Vehicle
        fields = [
            'brand', 'model', 'type_vehicle', 'year',
            'no_plate', 'owner_transport', 'status_vehicle',
            'color', 'chassis_number', 'engine_number', 'serial_number',
            'is_active', 'notes'
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
        }
