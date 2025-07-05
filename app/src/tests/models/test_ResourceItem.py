import pytest
from datetime import date, timedelta
from equipment.models.ResourceItem import ResourceItem


@pytest.mark.django_db
class TestResourceItem:

    def test_create_resource_item(self):
        resource = ResourceItem.objects.create(
            name='Bomba de Agua',
            type='EQUIPO',
            brand='Grundfos',
            model='CR-15',
            code='EQ-001',
            status='DISPONIBLE'
        )
        assert resource.name == 'Bomba de Agua'
        assert resource.type == 'EQUIPO'
        assert resource.brand == 'Grundfos'
        assert resource.model == 'CR-15'
        assert resource.code == 'EQ-001'
        assert resource.status == 'DISPONIBLE'

    def test_resource_item_str(self):
        resource = ResourceItem.objects.create(
            name='Compresor Industrial',
            type='EQUIPO',
            brand='Atlas Copco',
            code='COMP-001',  # Añadir code
            status='DISPONIBLE'  # Añadir status válido
        )
        assert str(resource) == 'Compresor Industrial'

    def test_resource_item_defaults(self):
        resource = ResourceItem.objects.create(
            name='Servicio de Limpieza',
            code='SER-001',
            status='DISPONIBLE'  # Añadir status válido
        )
        assert resource.type == 'EQUIPO'  # default
        assert resource.brand == 'SIN MARCA'  # default
        assert resource.model == 'N/A'  # default

    def test_get_by_id_existing(self):
        resource = ResourceItem.objects.create(
            name='Generador Eléctrico',
            code='GEN-001',
            type='EQUIPO',
            status='DISPONIBLE'  # Añadir status válido
        )

        found_resource = ResourceItem.get_by_id(resource.id)
        assert found_resource == resource
        assert found_resource.name == 'Generador Eléctrico'

    def test_get_by_id_non_existing(self):
        result = ResourceItem.get_by_id(999)  # Non-existing ID
        assert result is None

    def test_get_free_equipment(self):
        # Create equipment with different statuses
        yesterday = date.today() - timedelta(days=1)
        free_eq1 = ResourceItem.objects.create(
            name='Equipo Libre 1',
            code='FREE-001',
            status='DISPONIBLE',
            is_active=True,
            type='EQUIPO',
            release_date=yesterday  # Use yesterday to ensure it's "free"
        )
        free_eq2 = ResourceItem.objects.create(
            name='Equipo Libre 2',
            code='FREE-002',
            status='DISPONIBLE',
            is_active=True,
            type='EQUIPO',
            release_date=yesterday  # Use yesterday to ensure it's "free"
        )

        # Not free equipment
        ResourceItem.objects.create(
            name='Equipo Ocupado',
            code='BUSY-001',
            status='RENTADO',
            is_active=True
        )

        # Free but inactive
        ResourceItem.objects.create(
            name='Equipo Inactivo',
            code='INACTIVE-001',
            status='DISPONIBLE',
            is_active=False
        )

        free_equipment = ResourceItem.get_free_equipment()
        assert len(free_equipment) == 2
        assert free_eq1 in free_equipment
        assert free_eq2 in free_equipment

    def test_type_choices(self):
        equipo = ResourceItem.objects.create(
            name='Test Equipo',
            code='EQ-TEST',
            type='EQUIPO',
            status='DISPONIBLE'  # Añadir status válido
        )
        assert equipo.type == 'EQUIPO'

        servicio = ResourceItem.objects.create(
            name='Test Servicio',
            code='SER-TEST',
            type='SERVICIO',
            status='DISPONIBLE'  # Añadir status válido
        )
        assert servicio.type == 'SERVICIO'

    def test_status_choices(self):
        resource = ResourceItem.objects.create(
            name='Test Status',
            code='STATUS-TEST',
            status='DISPONIBLE'  # Estado inicial válido
        )

        for status_code, _ in ResourceItem.STATUS_CHOICES:
            resource.status = status_code
            # Añadir repair_reason si el estado es EN REPARACION
            if status_code == 'EN REPARACION':
                resource.repair_reason = 'Test motivo'
            elif resource.repair_reason and status_code != 'EN REPARACION':  # Limpiar si no es EN REPARACION
                resource.repair_reason = None
            resource.save()
            resource.refresh_from_db()
            assert resource.status == status_code

    def test_resource_dates(self):
        resource = ResourceItem.objects.create(
            name='Test Dates',
            code='DATE-TEST',
            commitment_date=date(2024, 6, 1),
            release_date=date(2024, 12, 31),
            status='DISPONIBLE'  # Añadir status válido
        )
        assert resource.commitment_date == date(2024, 6, 1)
        assert resource.release_date == date(2024, 12, 31)
