from django import forms
from accounts.models import Technical


class TechnicalForm(forms.ModelForm):
    """
    Formulario simplificado para crear y actualizar técnicos
    Solo maneja campos del modelo base Technical
    """
    
    class Meta:
        model = Technical
        fields = [
            'first_name', 'last_name', 'email', 'dni', 'birth_date', 'sex',
            'nro_phone', 'work_area', 'date_joined',
            'file_number', 'medical_record_number',
            'license_issue_date', 'license_expiry_date',
            'defensive_driving_certificate_issue_date', 
            'defensive_driving_certificate_expiry_date',
            'mae_certificate_issue_date', 'mae_certificate_expiry_date',
            'medical_certificate_issue_date', 'medical_certificate_expiry_date',
            'is_iess_affiliated', 'has_life_insurance_policy',
            'quest_ncst_code', 'quest_instructor', 'quest_start_date', 
            'quest_end_date', 'notes', 'is_active'
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
            'sex': forms.Select(attrs={
                'class': 'select select-bordered'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
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
            }, format='%Y-%m-%d'),
            'file_number': forms.TextInput(attrs={
                'class': 'input input-bordered',
                'placeholder': 'N° de Archivo'
            }),
            'medical_record_number': forms.TextInput(attrs={
                'class': 'input input-bordered',
                'placeholder': 'N° de Historia Clínica'
            }),
            'license_issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'license_expiry_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'defensive_driving_certificate_issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'defensive_driving_certificate_expiry_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'mae_certificate_issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'mae_certificate_expiry_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'medical_certificate_issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'medical_certificate_expiry_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
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
            }, format='%Y-%m-%d'),
            'quest_end_date': forms.DateInput(attrs={
                'class': 'input input-bordered',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered',
                'rows': 8,
                'placeholder': 'Observaciones adicionales...'
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
            'file_number': 'Número de Archivo',
            'medical_record_number': 'Número de Historia Clínica',
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
            'sex': 'Sexo',
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
        self.fields['sex'].empty_label = "Seleccione el sexo"
        
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni:
            # Eliminar espacios y guiones
            dni = dni.replace(' ', '').replace('-', '')
            
            # Verificar que contiene solo números
            if not dni.isdigit():
                raise forms.ValidationError(
                    "La cédula debe contener solo números."
                )
            
            # Verificar longitud (10 dígitos para Ecuador)
            if len(dni) != 10:
                raise forms.ValidationError(
                    "La cédula debe tener exactamente 10 dígitos."
                )
        
        return dni
    
    def clean_nro_phone(self):
        phone = self.cleaned_data.get('nro_phone')
        if phone:
            # Eliminar espacios, guiones y paréntesis
            clean_phone = phone.replace(' ', '').replace('-', '').replace(
                '(', '').replace(')', '')
            
            # Verificar que contiene solo números
            if not clean_phone.isdigit():
                raise forms.ValidationError(
                    "El número de teléfono debe contener solo números."
                )
            
            # Verificar longitud mínima
            if len(clean_phone) < 7:
                raise forms.ValidationError(
                    "El número de teléfono debe tener al menos 7 dígitos."
                )
        
        return phone
