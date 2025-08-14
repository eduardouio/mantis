from django import forms
from equipment.models import ResourceItem


class ResourceItemForm(forms.ModelForm):
    class Meta:
        model = ResourceItem
        fields = [
            'name', 'code', 'type_equipment', 'brand', 'model', 
            'serial_number', 'date_purchase', 'height', 'width',
            'depth', 'weight', 'capacity_gallons', 'plant_capacity',
            # Estado y disponibilidad
            'stst_status_disponibility',
            'stst_repair_reason', 'stst_current_location',
            'stst_current_project_id', 'stst_commitment_date',
            'stst_release_date',
            # Características de lavamanos
            'have_foot_pumps', 'have_soap_dispenser', 'have_paper_towels',
            # Características de baterías sanitarias
            'have_paper_dispenser', 'have_napkin_dispenser', 'have_urinals',
            'have_seat', 'have_toilet_pump', 'have_sink_pump',
            'have_toilet_lid', 'have_bathroom_bases', 'have_ventilation_pipe',
            # Componentes de plantas de tratamiento
            'have_blower_brand', 'blower_brand', 'blower_model',
            'have_engine', 'engine_brand', 'engine_model', 'engine_fases',
            'have_belt_brand', 'belt_brand', 'belt_model', 'belt_type',
            'have_blower_pulley', 'blower_pulley_brand', 'blower_pulley_model',
            'have_motor_pulley', 'motor_pulley_brand', 'motor_pulley_model',
            'have_electrical_panel', 'electrical_panel_brand', 'electrical_panel_model',
            'have_motor_guard', 'engine_guard_brand', 'engine_guard_model',
            'have_relay_engine', 'relay_engine', 'have_relay_blower', 'relay_blower',
            'have_uv_filter', 'uv_filter',
            'have_pump_filter', 'pump_filter',
            'have_pump_pressure', 'pump_pressure',
            'have_pump_dosing', 'pump_dosing',
            'have_sand_carbon_filter', 'sand_carbon_filter',
            'have_hidroneumatic_tank', 'hidroneumatic_tank'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'code': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'type_equipment': forms.Select(attrs={'class': 'select select-bordered select-md w-full'}),
            'brand': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'model': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'serial_number': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'date_purchase': forms.DateInput(
                attrs={'class': 'input input-bordered input-md w-full', 'type': 'date'}
            ),
            'height': forms.NumberInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'width': forms.NumberInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'depth': forms.NumberInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'weight': forms.NumberInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'capacity_gallons': forms.NumberInput(
                attrs={'class': 'input input-bordered input-md w-full', 'step': '0.01'}
            ),
            'plant_capacity': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'stst_status_disponibility': forms.Select(attrs={'class': 'select select-bordered select-md w-full'}),
            'stst_repair_reason': forms.Textarea(
                attrs={'class': 'textarea textarea-bordered textarea-md w-full', 'rows': 3}
            ),
            'stst_current_location': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'stst_current_project_id': forms.NumberInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'stst_commitment_date': forms.DateInput(
                attrs={'class': 'input input-bordered input-md w-full', 'type': 'date'}
            ),
            'stst_release_date': forms.DateInput(
                attrs={'class': 'input input-bordered input-md w-full', 'type': 'date'}
            ),
            # Componentes de equipos
            'blower_brand': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'blower_model': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'engine_brand': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'engine_model': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'engine_fases': forms.Select(attrs={'class': 'select select-bordered select-md w-full'}),
            'belt_brand': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'belt_model': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'belt_type': forms.Select(attrs={'class': 'select select-bordered select-md w-full'}),
            'blower_pulley_brand': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'blower_pulley_model': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'motor_pulley_brand': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'motor_pulley_model': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'electrical_panel_brand': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'electrical_panel_model': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'engine_guard_brand': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'engine_guard_model': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'pump_filter': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'pump_pressure': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'pump_dosing': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'sand_carbon_filter': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'hidroneumatic_tank': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'uv_filter': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'relay_engine': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'relay_blower': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
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
        self.fields['stst_repair_reason'].required = False
        self.fields['stst_current_project_id'].required = False
        self.fields['stst_commitment_date'].required = False
        self.fields['stst_release_date'].required = False

        # Campos de componentes condicionales
        component_fields = [
            # Componentes de blower
            'blower_brand', 'blower_model', 'blower_pulley_brand', 
            'blower_pulley_model', 'have_blower_brand', 'have_blower_pulley',
            # Componentes de motor
            'engine_brand', 'engine_model', 'engine_fases',
            'motor_pulley_brand', 'motor_pulley_model',
            'have_engine', 'have_motor_pulley',
            # Bandas
            'belt_brand', 'belt_model', 'belt_type', 'have_belt_brand',
            # Panel eléctrico
            'electrical_panel_brand', 'electrical_panel_model', 'have_electrical_panel',
            # Guarda motor
            'engine_guard_brand', 'engine_guard_model', 'have_motor_guard',
            # Relés
            'relay_engine', 'relay_blower', 'have_relay_engine', 'have_relay_blower',
            # Componentes de plantas
            'pump_filter', 'pump_pressure', 'pump_dosing',
            'have_pump_filter', 'have_pump_pressure', 'have_pump_dosing',
            'sand_carbon_filter', 'have_sand_carbon_filter',
            'hidroneumatic_tank', 'have_hidroneumatic_tank',
            'uv_filter', 'have_uv_filter'
        ]

        for field_name in component_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

        # Configurar campos booleanos con CheckboxInput
        boolean_fields = [
            'have_foot_pumps', 'have_soap_dispenser', 'have_paper_towels',
            'have_paper_dispenser', 'have_napkin_dispenser', 'have_urinals',
            'have_seat', 'have_toilet_pump', 'have_sink_pump',
            'have_toilet_lid', 'have_bathroom_bases', 'have_ventilation_pipe',
            'have_blower_brand', 'have_engine', 'have_belt_brand',
            'have_blower_pulley', 'have_motor_pulley', 'have_electrical_panel',
            'have_motor_guard', 'have_relay_engine', 'have_relay_blower',
            'have_uv_filter', 'have_pump_filter', 'have_pump_pressure',
            'have_pump_dosing', 'have_sand_carbon_filter', 'have_hidroneumatic_tank'
        ]
        
        for field_name in boolean_fields:
            if field_name in self.fields:
                self.fields[field_name] = forms.BooleanField(
                    widget=forms.CheckboxInput(
                        attrs={
                            'class': 'checkbox checkbox-primary checkbox-md',
                            'data-toggle': 'toggle',
                            'data-on': 'Sí',
                            'data-off': 'No',
                            'data-onstyle': 'success',
                            'data-offstyle': 'danger'
                        }
                    ),
                    required=False,
                    label=self.fields[field_name].label if field_name in self.fields else field_name.replace('_', ' ').title()
                )

        # Hacer que el motivo de reparación sea requerido si el estado es "EN REPARACION"
        # Esta validación ahora se maneja en el modelo o en otra parte del sistema
        # ya que stst_status_equipment se gestiona automáticamente

    def clean(self):
        cleaned_data = super().clean()
        type_equipment = cleaned_data.get('type_equipment')
        have_urinals = cleaned_data.get('have_urinals', False)

        # Validar que los urinarios solo estén en baterías sanitarias de hombre
        if type_equipment == 'BTSNMJ' and have_urinals:
            self.add_error(
                'have_urinals',
                'Los urinarios solo están permitidos en baterías sanitarias para hombres'
            )

        # Validar fechas de compromiso y liberación
        commitment_date = cleaned_data.get('stst_commitment_date')
        release_date = cleaned_data.get('stst_release_date')
        
        if commitment_date and release_date and release_date < commitment_date:
            self.add_error(
                'stst_release_date',
                'La fecha de liberación no puede ser anterior a la fecha de compromiso'
            )

        # Validar campos condicionales
        self._validate_conditional_fields(cleaned_data)

        return cleaned_data
    
    def _validate_conditional_fields(self, cleaned_data):
        """Valida que los campos condicionales tengan los valores requeridos"""
        # Validar componentes de blower
        if cleaned_data.get('have_blower_brand'):
            if not cleaned_data.get('blower_brand'):
                self.add_error('blower_brand', 'Debe especificar la marca del blower')
            if not cleaned_data.get('blower_model'):
                self.add_error('blower_model', 'Debe especificar el modelo del blower')
        
        # Validar componentes de motor
        if cleaned_data.get('have_engine'):
            if not cleaned_data.get('engine_brand'):
                self.add_error('engine_brand', 'Debe especificar la marca del motor')
            if not cleaned_data.get('engine_model'):
                self.add_error('engine_model', 'Debe especificar el modelo del motor')
        
        # Validar que si se especifica un proyecto, se proporcione la ubicación
        if cleaned_data.get('stst_current_project_id') and not cleaned_data.get('stst_current_location'):
            self.add_error(
                'stst_current_location',
                'Debe especificar la ubicación actual del equipo'
            )
