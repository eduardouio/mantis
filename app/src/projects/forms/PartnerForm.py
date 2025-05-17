from django import forms
from projects.models import Partner


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = [
            'business_tax_id', 'name', 'email', 'phone', 'address',
            'name_contact'
        ]
        widgets = {
            'business_tax_id': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'name': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'phone': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'address': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
            'name_contact': forms.TextInput(attrs={'class': 'input input-bordered input-md w-full'}),
        }
