from django import forms
from accounts.models import Technical


class TechnicalForm(forms.ModelForm):
    """
    Formulario para crear y actualizar técnicos
    """
    
    # Campos ocultos para almacenar datos de vacunas y pases
    vaccinations_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    passes_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    class Meta:
        model = Technical
        fields = [
            'first_name', 'last_name', 'email', 'dni', 'birth_date',
            'nro_phone', 'work_area', 'date_joined',
            'license_issue_date', 'license_expiry_date',
            'defensive_driving_certificate_issue_date', 'defensive_driving_certificate_expiry_date',
            'mae_certificate_issue_date', 'mae_certificate_expiry_date',
            'medical_certificate_issue_date', 'medical_certificate_expiry_date',
            'is_iess_affiliated', 'has_life_insurance_policy',
            'quest_ncst_code', 'quest_instructor', 'quest_start_date', 'quest_end_date',
            'notes', 'is_active'
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered',
                'placeholder': 'Ingrese los nombres'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered',
                'placeholder': 'Ingrese los apellidos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered',
                'placeholder': 'correo@ejemplo.com'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'input input-bordered',
                'placeholder': '0123456789'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'nro_phone': forms.TextInput(attrs={
                'class': 'input input-bordered',
                'placeholder': '0987654321'
            }),
            'work_area': forms.Select(attrs={
                'class': 'select select-bordered'
            }),
            'date_joined': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'license_issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'license_expiry_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'defensive_driving_certificate_issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'defensive_driving_certificate_expiry_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'mae_certificate_issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'mae_certificate_expiry_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'medical_certificate_issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'medical_certificate_expiry_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'quest_ncst_code': forms.TextInput(attrs={
                'class': 'input input-bordered',
                'placeholder': 'Código Quest'
            }),
            'quest_instructor': forms.TextInput(attrs={
                'class': 'input input-bordered',
                'placeholder': 'Nombre del instructor'
            }),
            'quest_start_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'quest_end_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered',
                'rows': 8,
                'placeholder': 'Observaciones adicionales sobre el técnico...'
            }),
            'is_iess_affiliated': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'has_life_insurance_policy': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-success'
            }),
        }
        
        labels = {
            'first_name': 'Nombres *',
            'last_name': 'Apellidos *',
            'email': 'Correo Electrónico',
            'dni': 'Cédula *',
            'birth_date': 'Fecha de Nacimiento',
            'nro_phone': 'Número de Celular *',
            'work_area': 'Área de Trabajo',
            'date_joined': 'Fecha de Ingreso',
            'license_issue_date': 'Fecha de Emisión',
            'license_expiry_date': 'Fecha de Caducidad',
            'defensive_driving_certificate_issue_date': 'Fecha de Emisión',
            'defensive_driving_certificate_expiry_date': 'Fecha de Caducidad',
            'mae_certificate_issue_date': 'Fecha de Emisión',
            'mae_certificate_expiry_date': 'Fecha de Caducidad',
            'medical_certificate_issue_date': 'Fecha de Emisión',
            'medical_certificate_expiry_date': 'Fecha de Caducidad',
            'quest_ncst_code': 'Código Quest NCST',
            'quest_instructor': 'Instructor Quest',
            'quest_start_date': 'Fecha de Inicio Quest',
            'quest_end_date': 'Fecha de Fin Quest',
            'notes': 'Notas',
            'is_iess_affiliated': 'Afiliado al IESS',
            'has_life_insurance_policy': 'Tiene Póliza de Vida',
            'is_active': 'Técnico Activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos requeridos
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['dni'].required = True
        self.fields['nro_phone'].required = True
        
        # Configuración adicional para campos específicos
        self.fields['work_area'].empty_label = "Seleccione un área"
        
        # Establecer is_active como True por defecto para nuevos registros
        if not self.instance.pk:
            self.fields['is_active'].initial = True
        
    def clean_dni(self):
        """Validación personalizada para la cédula"""
        dni = self.cleaned_data.get('dni')
        if dni:
            # Remover espacios y guiones
            dni = dni.replace(' ', '').replace('-', '')
            
            # Validar que solo contenga números
            if not dni.isdigit():
                raise forms.ValidationError("La cédula debe contener solo números.")
            
            # Validar longitud (Ecuador: 10 dígitos)
            if len(dni) != 10:
                raise forms.ValidationError("La cédula debe tener 10 dígitos.")
                
        return dni
    
    def clean_nro_phone(self):
        """Validación personalizada para el número de teléfono"""
        phone = self.cleaned_data.get('nro_phone')
        if phone:
            # Remover espacios, guiones y paréntesis
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Validar que solo contenga números
            if not phone.isdigit():
                raise forms.ValidationError("El número de teléfono debe contener solo números.")
            
            # Validar longitud (Ecuador: 9-10 dígitos)
            if len(phone) < 9 or len(phone) > 10:
                raise forms.ValidationError("El número de teléfono debe tener entre 9 y 10 dígitos.")
                
        return phone
    
    def clean(self):
        """Validaciones generales del formulario"""
        cleaned_data = super().clean()
        
        # Validar fechas de licencia
        license_issue = cleaned_data.get('license_issue_date')
        license_expiry = cleaned_data.get('license_expiry_date')
        
        if license_issue and license_expiry:
            if license_expiry <= license_issue:
                raise forms.ValidationError("La fecha de caducidad de la licencia debe ser posterior a la fecha de emisión.")
        
        # Validar fechas Quest
        quest_start = cleaned_data.get('quest_start_date')
        quest_end = cleaned_data.get('quest_end_date')
        
        if quest_start and quest_end:
            if quest_end <= quest_start:
                raise forms.ValidationError("La fecha de fin Quest debe ser posterior a la fecha de inicio.")
        
        return cleaned_data
