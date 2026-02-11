"""
Formulario para actualizar el perfil de usuario
"""
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserForm(forms.ModelForm):
    """Formulario para actualizar información del usuario"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'picture', 'notes', 'siganture_name', 'siganture_role']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ingresa tu nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ingresa tu apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'correo@ejemplo.com',
                'readonly': True  # El email no debería cambiarse fácilmente
            }),
            'picture': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Notas adicionales sobre tu perfil...'
            }),
            'siganture_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nombre para firmar documentos'
            }),
            'siganture_role': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Rol para firmar documentos'
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'picture': 'Foto de Perfil',
            'notes': 'Notas',
            'siganture_name': 'Nombre Firmante',
            'siganture_role': 'Rol Firmante',
        }
        help_texts = {
            'email': 'Este correo es tu identificador único en el sistema.',
            'picture': 'Formatos permitidos: JPG, PNG, GIF. Tamaño máximo: 2MB',
        }

    def clean_email(self):
        """Validar que el email no esté en uso por otro usuario"""
        email = self.cleaned_data.get('email')
        if email:
            # Verificar si otro usuario ya tiene este email
            user_with_email = User.objects.filter(email=email).exclude(
                pk=self.instance.pk
            ).first()
            if user_with_email:
                raise forms.ValidationError(
                    'Este correo electrónico ya está en uso por otro usuario.'
                )
        return email

    def clean_picture(self):
        """Validar el tamaño de la imagen"""
        picture = self.cleaned_data.get('picture')
        if picture:
            # Validar tamaño (2MB máximo)
            if picture.size > 2 * 1024 * 1024:
                raise forms.ValidationError(
                    'La imagen no puede ser mayor a 2MB.'
                )
        return picture
