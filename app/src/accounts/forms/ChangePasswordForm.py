"""
Formulario para cambio de contraseña
"""
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()


class ChangePasswordForm(PasswordChangeForm):
    """Formulario personalizado para cambio de contraseña"""
    
    old_password = forms.CharField(
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Ingresa tu contraseña actual',
            'autocomplete': 'current-password'
        }),
        help_text='Por seguridad, ingresa tu contraseña actual.'
    )
    
    new_password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Ingresa tu nueva contraseña',
            'autocomplete': 'new-password'
        }),
        help_text=(
            'Tu contraseña debe tener al menos 8 caracteres, '
            'no puede ser completamente numérica, '
            'y no debe ser muy común.'
        )
    )
    
    new_password2 = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirma tu nueva contraseña',
            'autocomplete': 'new-password'
        }),
        help_text='Ingresa la misma contraseña para confirmar.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error
        self.error_messages['password_incorrect'] = (
            'La contraseña actual es incorrecta.'
        )
        self.error_messages['password_mismatch'] = (
            'Las dos contraseñas no coinciden.'
        )
