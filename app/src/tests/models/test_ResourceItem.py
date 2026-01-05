import pytest
from datetime import date, timedelta
from equipment.models.ResourceItem import ResourceItem


@pytest.mark.django_db
class TestResourceItem:

    def test_create_resource_item(self):
        resource = ResourceItem.objects.create(
            name="Bomba de Agua",
            type_equipment="EQUIPO",
            brand="Grundfos",
            model="CR-15",
            code="EQ-001",
            stst_status_equipment="DISPONIBLE",
        )
        assert resource.name == "Bomba de Agua"
        assert resource.type_equipment == "EQUIPO"
        assert resource.brand == "Grundfos"
        assert resource.model == "CR-15"
        assert resource.code == "EQ-001"
        assert resource.stst_status_equipment == "DISPONIBLE"

    def test_resource_item_str(self):
        resource = ResourceItem.objects.create(
            name="Compresor Industrial",
            type_equipment="LVMNOS",
            brand="Atlas Copco",
            code="COMP-001",
            stst_status_equipment="FUNCIONANDO",
        )
        assert str(resource) == "COMP-001 -> Compresor Industrial"

    def test_resource_item_defaults(self):
        resource = ResourceItem.objects.create(
            name="Servicio de Limpieza",
            code="SER-001",
            stst_status_equipment="FUNCIONANDO",
        )
        assert resource.type_equipment is None
        assert resource.brand is None
        assert resource.model == "N/A"

    def test_get_by_code_existing(self):
        resource = ResourceItem.objects.create(
            name="Generador Eléctrico",
            code="GEN-001",
            type_equipment="LVMNOS",
            stst_status_equipment="FUNCIONANDO",
        )

        found_resource = ResourceItem.get_by_code("GEN-001")
        assert found_resource == resource
        assert found_resource.name == "Generador Eléctrico"

    def test_get_by_code_non_existing(self):
        result = ResourceItem.get_by_code("NONEXISTENT")
        assert result is None

    def test_resource_active_status(self):

        active_eq = ResourceItem.objects.create(
            name="Equipo Activo",
            code="ACT-001",
            stst_status_equipment="FUNCIONANDO",
            is_active=True,
            type_equipment="LVMNOS",
        )
        assert active_eq.is_active is True

        inactive_eq = ResourceItem.objects.create(
            name="Equipo Inactivo",
            code="INACT-001",
            stst_status_equipment="FUNCIONANDO",
            is_active=False,
            type_equipment="LVMNOS",
        )
        assert inactive_eq.is_active is False

    def test_type_choices(self):
        lavamanos = ResourceItem.objects.create(
            name="Test Lavamanos",
            code="LV-TEST",
            type_equipment="LVMNOS",
            stst_status_equipment="FUNCIONANDO",
        )
        assert lavamanos.type_equipment == "LVMNOS"

        bateria = ResourceItem.objects.create(
            name="Test Batería",
            code="BT-TEST",
            type_equipment="BTSNHM",
            stst_status_equipment="FUNCIONANDO",
        )
        assert bateria.type_equipment == "BTSNHM"

    def test_status_choices(self):
        from equipment.models.ResourceItem import STATUS_EQUIPMENT

        resource = ResourceItem.objects.create(
            name="Test Status",
            code="STATUS-TEST",
            stst_status_equipment="FUNCIONANDO",
            type_equipment="LVMNOS",
        )

        for status_code, _ in STATUS_EQUIPMENT:
            resource.stst_status_equipment = status_code
            resource.save()
            resource.refresh_from_db()
            assert resource.stst_status_equipment == status_code

    def test_resource_dates(self):
        resource = ResourceItem.objects.create(
            name="Test Dates",
            code="DATE-TEST",
            stst_commitment_date=date(2024, 6, 1),
            stst_release_date=date(2024, 12, 31),
            stst_status_equipment="FUNCIONANDO",
            type_equipment="LVMNOS",
        )
        assert resource.stst_commitment_date == date(2024, 6, 1)
        assert resource.stst_release_date == date(2024, 12, 31)
