from django import forms
from accounts.models import Technical


class TechnicalForm(forms.ModelForm):
    class Meta:
        model = Technical
        fields = [
            'date_joined', 'first_name', 'last_name', 'email', 'work_area',
            'dni', 'nro_phone', 'birth_date', 'license_issue_date',
            'license_expiry_date', 'defensive_driving_certificate_issue_date',
            'defensive_driving_certificate_expiry_date',
            'mae_certificate_issue_date', 'mae_certificate_expiry_date',
            'medical_certificate_issue_date', 'medical_certificate_expiry_date',
            'is_iess_affiliated', 'has_life_insurance_policy',
            'quest_ncst_code', 'quest_instructor', 'quest_start_date',
            'quest_end_date', 'notes', 'is_active'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'first_name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'email': forms.EmailInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'work_area': forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'dni': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'nro_phone': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'birth_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'license_issue_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'license_expiry_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'defensive_driving_certificate_issue_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'defensive_driving_certificate_expiry_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'mae_certificate_issue_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'mae_certificate_expiry_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'medical_certificate_issue_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'medical_certificate_expiry_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'is_iess_affiliated': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'has_life_insurance_policy': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'quest_ncst_code': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'quest_instructor': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'quest_start_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'quest_end_date': forms.DateInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'border rounded px-3 py-2 w-full', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }
