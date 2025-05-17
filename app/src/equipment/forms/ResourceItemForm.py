from django import forms
from equipment.models import ResourceItem


class ResourceItemForm(forms.ModelForm):
    class Meta:
        model = ResourceItem
        fields = [
            'name', 'type', 'brand', 'model', 'code', 'date_purchase',
            'height', 'width', 'depth', 'weight', 'status', 'is_active',
            'notes'
        ]
        widgets = {
            'type': forms.Select(
                attrs={
                    'class': 'select select-bordered select-md w-full'
                }
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
            'notes': forms.TextInput(
                attrs={'class': 'input input-bordered input-md w-full'}
            ),
            'status': forms.Select(
                attrs={'class': 'select select-bordered select-md w-full'}
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'checkbox checkbox-md'}
            ),
        }
