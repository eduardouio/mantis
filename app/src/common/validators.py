"""
Validadores personalizados para archivos.
"""
from django.core.exceptions import ValidationError
import os


def validate_pdf_file(value):
    """
    Valida que el archivo sea un PDF.
    """
    if not value:
        return
    
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf']
    
    if ext not in valid_extensions:
        raise ValidationError(
            f'Solo se permiten archivos PDF. Extensión recibida: {ext}'
        )


def validate_image_file(value):
    """
    Valida que el archivo sea una imagen.
    """
    if not value:
        return
    
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    if ext not in valid_extensions:
        raise ValidationError(
            f'Solo se permiten archivos de imagen (jpg, jpeg, png, gif, bmp, webp). '
            f'Extensión recibida: {ext}'
        )
