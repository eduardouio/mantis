import pytest
from datetime import date
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
            brand='Atlas Copco'
        )
        assert str(resource) == 'Compresor Industrial'

    def test_resource_item_defaults(self):
        resource = ResourceItem.objects.create(
            name='Servicio de Limpieza',
            code='SER-001'
        )
        assert resource.type == 'EQUIPO'  # default
        assert resource.brand == 'SIN MARCA'  # default
        assert resource.model == 'N/A'  # default

    def test_get_by_id_existing(self):
        resource = ResourceItem.objects.create(
            name='Generador Eléctrico',
            code='GEN-001',
            type='EQUIPO'
        )
        
        found_resource = ResourceItem.get_by_id(resource.id)
        assert found_resource == resource
        assert found_resource.name == 'Generador Eléctrico'

    def test_get_by_id_non_existing(self):
        result = ResourceItem.get_by_id(999)  # Non-existing ID
        assert result is None

    def test_get_free_equipment(self):
        # Create equipment with different statuses
        free_eq1 = ResourceItem.objects.create(
            name='Equipo Libre 1',
            code='FREE-001',
            status='LIBRE',
            is_active=True
        )
        free_eq2 = ResourceItem.objects.create(
            name='Equipo Libre 2',
            code='FREE-002',
            status='LIBRE',
            is_active=True
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
            status='LIBRE',
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
            type='EQUIPO'
        )
        assert equipo.type == 'EQUIPO'
        
        servicio = ResourceItem.objects.create(
            name='Test Servicio',
            code='SER-TEST',
            type='SERVICIO'
        )
        assert servicio.type == 'SERVICIO'

    def test_status_choices(self):
        resource = ResourceItem.objects.create(
            name='Test Status',
            code='STATUS-TEST'
        )
        
        for status_code, _ in ResourceItem.STATUS_CHOICES:
            resource.status = status_code
            resource.save()
            resource.refresh_from_db()
            assert resource.status == status_code

    def test_resource_dates(self):
        resource = ResourceItem.objects.create(
            name='Test Dates',
            code='DATE-TEST',
            bg_date_commitment=date(2024, 6, 1),
            bg_date_free=date(2024, 12, 31)
        )
        assert resource.bg_date_commitment == date(2024, 6, 1)
        assert resource.bg_date_free == date(2024, 12, 31)