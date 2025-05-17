from django import forms
from accounts.models import Technical


class TechnicalForm(forms.ModelForm):
    class Meta:
        model = Technical
        fields = [
            'date_joined', 'first_name', 'last_name', 'email', 'location', 'dni',
            'user', 'nro_phone', 'role', 'days_to_work', 'days_free', 'is_active'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'class': 'input input-bordered input-md w-full', 'type': 'date'}),
            'first_name': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'location': forms.Select(attrs={'class': 'select select-bordered select-md w-full'}),
            'dni': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'user': forms.Select(attrs={'class': 'select select-bordered select-md w-full'}),
            'nro_phone': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'role': forms.Select(attrs={'class': 'select select-bordered select-md w-full'}),
            'days_to_work': forms.NumberInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'days_free': forms.NumberInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-md'}),
        }
