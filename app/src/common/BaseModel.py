"""
 Modelo base para todos los modelos de la aplicación, todos los modelos
    deben heredar de este modelo.

    Attributes:
        created_at (DateTime): Fecha de creación del registro.
        updated_at (DateTime): Fecha de actualización del registro.
        deleted_at (DateTime): Fecha de eliminación del registro.
        historical (HistoricalRecords): Registros históricos del modelo.

    Methods:
        save: Guarda el registro en la base de datos, 
              incluye el usuario creador y actualizador.
        get_user: Obtiene el usuario creador o actualizador del registro.

"""


from django.db import models
from simple_history.models import HistoricalRecords
from django.core.exceptions import ObjectDoesNotExist

# django-crum
from crum import get_current_user

# Modelo de usuario Peronalizado
from accounts.models.CustomUserModel import CustomUserModel


class BaseModel(models.Model):

    notes = models.TextField(
        'notas',
        blank=True,
        default=None,
        null=True,
        help_text='Notas del registro.'
    )

    created_at = models.DateTimeField(
        'fecha de creación',
        auto_now_add=True,
        help_text='Fecha de creación del registro.'
    )

    updated_at = models.DateTimeField(
        'fecha de actualización',
        auto_now=True,
        help_text='Fecha de ultima actualización del registro.'
    )

    is_active = models.BooleanField(
        'activo',
        default=True,
        help_text='Estado del registro.'
    )
    id_user_created = models.PositiveIntegerField(
        'usuario creador',
        default=0,
        blank=True,
        null=True,
        help_text='Identificador del usuario creador del registro 0 es anonimo.'
    )

    id_user_updated = models.PositiveIntegerField(
        'usuario actualizador',
        default=0,
        blank=True,
        null=True,
        help_text='Identificador del usuario actualizador del registro.'
    )

    history = HistoricalRecords(inherit=True)

    def filter(self, **kwargs):
        '''Retorna los registros activos filtrados por los argumentos.'''
        return self.__class__.objects.filter(is_active=True, **kwargs)

    def get_all(self):
        '''Retorna todos los registros activos.'''
        return self.objects.filter(is_active=True)

    def get(self, id):
        '''Retorna el registro por id.'''
        try:
            return self.__class__.objects.get(pk=id, is_active=True)
        except ObjectDoesNotExist:
            return None

    def get_ignore_deleted(self, id):
        '''Retorna el registro por id, ignorando el estado de eliminado.'''
        try:
            return self.__class__.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None

    def get_by_id_user(self, id_user):
        '''Retorna el registro por id_user.'''
        try:
            return self.__class__.objects.get(id_user_created=id_user, is_active=True)
        except ObjectDoesNotExist:
            return None

    def delete(self, *args, **kwargs):
        '''Marca el registro como inactivo en lugar de eliminarlo.'''
        self.is_active = False
        self.save(*args, **kwargs)

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user is None:
            return super().save(*args, **kwargs)

        if not self.pk:
            self.id_user_created = user.pk

        self.id_user_updated = user.pk
        return super().save(*args, **kwargs)

    def get_create_user(self):
        '''Retorna el usuario creador del registro.'''
        try:
            return CustomUserModel.objects.get(pk=self.id_user_created)
        except ObjectDoesNotExist:
            return None

    def get_update_user(self):
        '''Retorna el usuario ultimo en actualizar el registro '''
        try:
            return CustomUserModel.objects.get(pk=self.id_user_updated)
        except ObjectDoesNotExist:
            return None

    class Meta:
        abstract = True
        get_latest_by = 'created_at'
        ordering = ['-created_at']
