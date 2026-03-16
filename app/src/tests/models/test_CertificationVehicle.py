import pytest
from datetime import date
from equipment.models.CertificationVehicle import CertificationVehicle
from equipment.models.Vehicle import Vehicle


@pytest.mark.django_db
class TestCertificationVehicle:

    def test_create_certification_vehicle(self):
        vehicle = Vehicle.objects.create(
            brand='Toyota',
            model='Hilux',
            type_vehicle='CAMIONETA',
            no_plate='ABC0123'
        )
        certification = CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='INSPECCION_VOLUMETRICA',
            date_start=date(2024, 1, 1),
            date_end=date(2024, 12, 31),
            description='Inspección volumétrica anual'
        )
        assert certification.vehicle == vehicle
        assert certification.name == 'INSPECCION_VOLUMETRICA'
        assert certification.date_start == date(2024, 1, 1)
        assert certification.date_end == date(2024, 12, 31)
        assert certification.description == 'Inspección volumétrica anual'

    def test_certification_vehicle_str(self):
        vehicle = Vehicle.objects.create(
            brand='Chevrolet',
            model='D-Max',
            type_vehicle='CAMIONETA',
            no_plate='XYZ789'
        )
        certification = CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='MEDICION DE ESPESORES',
            date_start=date(2024, 6, 1),
            date_end=date(2025, 6, 1)
        )
        expected_str = 'MEDICION DE ESPESORES - XYZ789'
        assert str(certification) == expected_str

    def test_certification_name_free_text(self):
        vehicle = Vehicle.objects.create(
            brand='Ford',
            model='Ranger',
            type_vehicle='CAMIONETA',
            no_plate='FOR123'
        )

        for cert_code in ['INSPECCION VOLUMETRICA', 'MEDICION DE ESPESORES', 'Mi Nueva Certificación']:
            certification = CertificationVehicle.objects.create(
                vehicle=vehicle,
                name=cert_code,
                date_start=date(2024, 1, 1),
                date_end=date(2024, 12, 31)
            )
            assert certification.name == cert_code
            certification.delete()

    def test_get_unique_names(self):
        vehicle = Vehicle.objects.create(
            brand='Ford',
            model='Ranger',
            type_vehicle='CAMIONETA',
            no_plate='FOR124'
        )
        CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='INSPECCION VOLUMETRICA',
            date_start=date(2024, 1, 1),
            date_end=date(2024, 12, 31)
        )
        CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='PRUEBA HIDROSTATICA',
            date_start=date(2024, 1, 1),
            date_end=date(2024, 12, 31)
        )
        names = CertificationVehicle.get_unique_names()
        assert 'INSPECCION VOLUMETRICA' in names
        assert 'PRUEBA HIDROSTATICA' in names

    def test_certification_dates(self):
        vehicle = Vehicle.objects.create(
            brand='Nissan',
            model='Frontier',
            type_vehicle='CAMIONETA',
            no_plate='NIS456'
        )
        certification = CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='PRUEBA_HIDROSTATICA',
            date_start=date(2024, 3, 15),
            date_end=date(2025, 3, 15)
        )
        assert certification.date_start < certification.date_end
        assert certification.date_start == date(2024, 3, 15)
        assert certification.date_end == date(2025, 3, 15)
