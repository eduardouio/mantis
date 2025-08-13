from django import forms
from equipment.models import ResourceItem


class ResourceItemForm(forms.ModelForm):
    class Meta:
        model = ResourceItem
        fields = [
            'name', 'type', 'subtype', 'code', 'serial_number',
            'brand', 'model', 'date_purchase', 'height', 'width',
            'depth', 'weight', 'status', 'capacity_gallons',
            'plant_capacity', 'repair_reason', 'notes',
            # Specific fields for sinks
            'foot_pumps', 'sink_soap_dispenser', 'paper_towels',
            # Specific fields for sanitary batteries
            'paper_dispenser', 'soap_dispenser', 'napkin_dispenser',
            'urinals', 'seats', 'toilet_pump', 'sink_pump',
            'toilet_lid', 'bathroom_bases', 'ventilation_pipe',
            # Fields for special equipment
            'blower_brand', 'blower_model', 'engine_brand', 'engine_model',
            'engine_fases', 'belt_brand', 'belt_model', 'belt_type',
            'blower_pulley_brand', 'blower_pulley_model',
            'motor_pulley_brand', 'motor_pulley_model',
            'electrical_panel_brand', 'electrical_panel_model',
            'motor_guard_brand', 'motor_guard_model',
            # Potable plant components
            'pump_filter', 'pump_pressure', 'pump_dosing',
            'sand_carbon_filter', 'hidroneumatic_tank', 'uv_filter',
            # Residual plant relays
            'relay_engine', 'relay_blower'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'subtype': forms.Select(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'date_purchase': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control'}),
            'depth': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'capacity_gallons': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'plant_capacity': forms.Select(attrs={'class': 'form-control'}),
            'repair_reason': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            # Special fields for equipment
            'blower_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'blower_model': forms.TextInput(attrs={'class': 'form-control'}),
            'engine_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'engine_model': forms.TextInput(attrs={'class': 'form-control'}),
            'engine_fases': forms.Select(attrs={'class': 'form-control'}),
            'belt_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'belt_model': forms.TextInput(attrs={'class': 'form-control'}),
            'belt_type': forms.Select(attrs={'class': 'form-control'}),
            'blower_pulley_brand': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'blower_pulley_model': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'motor_pulley_brand': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'motor_pulley_model': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'electrical_panel_brand': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'electrical_panel_model': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'motor_guard_brand': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'motor_guard_model': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'pump_filter': forms.TextInput(attrs={'class': 'form-control'}),
            'pump_pressure': forms.TextInput(attrs={'class': 'form-control'}),
            'pump_dosing': forms.TextInput(attrs={'class': 'form-control'}),
            'sand_carbon_filter': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'hidroneumatic_tank': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'uv_filter': forms.TextInput(attrs={'class': 'form-control'}),
            'relay_engine': forms.TextInput(attrs={'class': 'form-control'}),
            'relay_blower': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hacer que ciertos campos no sean requeridos
        self.fields['serial_number'].required = False
        self.fields['date_purchase'].required = False
        self.fields['height'].required = False
        self.fields['width'].required = False
        self.fields['depth'].required = False
        self.fields['weight'].required = False
        self.fields['capacity_gallons'].required = False
        self.fields['plant_capacity'].required = False
        self.fields['repair_reason'].required = False
        self.fields['notes'].required = False

        # Special fields not required
        for field_name in [
            'blower_brand', 'blower_model', 'engine_brand', 'engine_model',
            'engine_fases', 'belt_brand', 'belt_model', 'belt_type',
            'blower_pulley_brand', 'blower_pulley_model',
            'motor_pulley_brand', 'motor_pulley_model',
            'electrical_panel_brand', 'electrical_panel_model',
            'motor_guard_brand', 'motor_guard_model', 'pump_filter',
            'pump_pressure', 'pump_dosing', 'sand_carbon_filter',
            'hidroneumatic_tank', 'uv_filter', 'relay_engine',
            'relay_blower'
        ]:
            if field_name in self.fields:
                self.fields[field_name].required = False
    # Definir campos booleanos con BooleanField + CheckboxInput
        boolean_fields = [
            'foot_pumps', 'sink_soap_dispenser', 'paper_dispenser',
            'soap_dispenser', 'napkin_dispenser', 'urinals', 'seats',
            'toilet_pump', 'sink_pump', 'toilet_lid', 'bathroom_bases',
            'ventilation_pipe'
        ]
        
        for field_name in boolean_fields:
            if field_name in self.fields:
                self.fields[field_name] = forms.BooleanField(
                    widget=forms.CheckboxInput(
                        attrs={
                            'class': 'checkbox checkbox-primary checkbox-md'
                        }
                    ),
                    required=False
                )

        # Make repair reason required if status is "EN REPARACION"
        if self.instance and self.instance.status == 'EN REPARACION':
            self.fields['repair_reason'].required = True

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        repair_reason = cleaned_data.get('repair_reason')
        subtype = cleaned_data.get('subtype')
        urinals = cleaned_data.get('urinals')

        # Validate repair reason
        if status == 'EN REPARACION' and not repair_reason:
            self.add_error(
                'repair_reason',
                'Repair reason required when status is EN REPARACION'
            )

        # Validate urinals are only used in men's bathrooms
        if subtype == 'BATERIA SANITARIA MUJER' and urinals:
            self.add_error(
                'urinals',
                'Urinals only allowed in men sanitary batteries'
            )

        return cleaned_data
