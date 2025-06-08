from django import forms
from equipment.models import ResourceItem


class ResourceItemForm(forms.ModelForm):
    class Meta:
        model = ResourceItem
        fields = [
            'name', 'type', 'subtipo', 'brand', 'model', 'code', 'date_purchase',
            'height', 'width', 'depth', 'weight', 'status', 'is_active',
            'capacidad', 'unidad_capacidad', 'capacidad_planta', 'motivo_reparacion',
            # Campos específicos para lavamanos
            'bombas_pie', 'dispensador_jabon_lavamanos',
            # Campos específicos para baterías sanitarias
            'dispensador_papel', 'dispensador_jabon', 'dispensador_servilletas',
            'urinales', 'asientos', 'bomba_bano', 'bomba_lavamanos',
            'tapa_inodoro', 'bases_banos', 'tubo_ventilacion',
            'notes'
        ]
        widgets = {
            'type': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'subtipo': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'name': forms.TextInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'brand': forms.TextInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'model': forms.TextInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'code': forms.TextInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'date_purchase': forms.DateInput(
                attrs={'class': 'input input-bordered input-md w-full', 'type': 'date'}
            ),
            'capacidad': forms.NumberInput(
                attrs={
                    'class': 'input input-bordered input-md w-full',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': '0.00'
                }
            ),
            'unidad_capacidad': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'capacidad_planta': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'height': forms.NumberInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'width': forms.NumberInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'depth': forms.NumberInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'weight': forms.NumberInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'status': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'motivo_reparacion': forms.Textarea(
                attrs={
                    'class': 'textarea textarea-bordered w-full',
                    'rows': 3,
                    'placeholder': 'Especifique el motivo de reparación...'
                }
            ),
            'notes': forms.Textarea(
                attrs={'class': 'textarea textarea-bordered w-full'}
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-md'}
            ),
            # Campos booleanos con estilo mejorado
            'bombas_pie': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'dispensador_jabon_lavamanos': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'dispensador_papel': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'dispensador_jabon': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'dispensador_servilletas': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'urinales': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'asientos': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'bomba_bano': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'bomba_lavamanos': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'tapa_inodoro': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'bases_banos': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
            'tubo_ventilacion': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-primary checkbox-md'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer el motivo de reparación requerido si el estado es "EN REPARACION"
        if self.instance and self.instance.status == 'EN REPARACION':
            self.fields['motivo_reparacion'].required = True

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        motivo_reparacion = cleaned_data.get('motivo_reparacion')
        subtipo = cleaned_data.get('subtipo')
        urinales = cleaned_data.get('urinales')

        # Validar motivo de reparación
        if status == 'EN REPARACION' and not motivo_reparacion:
            self.add_error('motivo_reparacion', 
                'Debe especificar el motivo de reparación cuando el estado es "EN REPARACION"')

        # Validar que urinales solo se use en baterías de hombre
        if subtipo == 'BATERIA SANITARIA MUJER' and urinales:
            self.add_error('urinales', 
                'Los urinales solo aplican para baterías sanitarias de hombre')

        return cleaned_data
