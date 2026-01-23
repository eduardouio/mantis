from django.db import models
from projects.models.Project import Project
from equipment.models.ResourceItem import ResourceItem
from common.BaseModel import BaseModel


class ShippingGuide(BaseModel):
	id = models.AutoField(
		primary_key=True
	)
	project = models.ForeignKey(
		Project,
		on_delete=models.PROTECT,
		verbose_name='proyecto'
	)
	guide_number = models.PositiveBigIntegerField(
		'Número de Guía',
		default=0,
		unique=True
	)
	issue_date = models.DateField(
		'Fecha de Emisión'
	)
	start_date = models.DateField(
		'Fecha de Inicio de Transporte',
		blank=True,
		null=True
	)
	end_date = models.DateField(
		'Fecha de Fin de Transporte',
		blank=True,
		null=True
	)
	origin_place = models.CharField(
		'Lugar de Origen',
		max_length=255,
		blank=True,
		null=True
	)
	destination_place = models.CharField(
		'Lugar de Destino',
		max_length=255,
		blank=True,
		null=True
	)
	carrier_name = models.CharField(
		'Transportista',
		max_length=255,
		blank=True,
		null=True,
		default=None
	)
	carrier_ci = models.CharField(
		'Cédula del Transportista',
		max_length=20,
		blank=True,
		null=True
	)
	vehicle_plate = models.CharField(
		'Placa del Vehículo',
		max_length=20,
		blank=True,
		null=True,
		default=None
	)
	dispatcher_name = models.CharField(
		'Nombre del Despachador',
		max_length=255,
		blank=True,
		null=True
	)
	dispatcher_ci = models.CharField(
		'Cédula del Despachador',
		max_length=20,
		blank=True,
		null=True
	)
	project = models.ForeignKey(
		Project,
		on_delete=models.PROTECT,
	)
	contact_name = models.CharField(
		'Nombre de Contacto en el Proyecto',
		max_length=255,
		blank=True,
		null=True
	)
	contact_phone = models.CharField(
		'Teléfono de Contacto en el Proyecto',
		max_length=15,
		blank=True,
		null=True
	)
	recibed_by = models.CharField(
		'Recibido Por',
		max_length=255,
		blank=True,
		null=True
	)
	recibed_ci = models.CharField(
		'Cédula de Quien Recibe',
		max_length=20,
		blank=True,
		null=True
	)

	class Meta:
		verbose_name = 'Guía de Envío'
		verbose_name_plural = 'Guías de Envío'

	def __str__(self):
		return f'Guía de Envío {self.guide_number} - Proyecto {self.project.id}'
	


class ShippingGuideDetail(BaseModel):
	id = models.AutoField(
		primary_key=True
	)
	shipping_guide = models.ForeignKey(
		ShippingGuide,
		on_delete=models.CASCADE,
		verbose_name='guía de envío'
	)
	description = models.CharField(
		'Descripción del Ítem',
		max_length=255
	)
	quantity = models.PositiveIntegerField(
		'Cantidad'
	)
	unit = models.DecimalField(
		'Unidad',
		max_digits=10,
		decimal_places=2
	)

	class Meta:
		verbose_name = 'Detalle de Guía de Envío'
		verbose_name_plural = 'Detalles de Guías de Envío'

	def __str__(self):
		return f'Detalle {self.id} de Guía de Envío {self.shipping_guide.guide_number}'