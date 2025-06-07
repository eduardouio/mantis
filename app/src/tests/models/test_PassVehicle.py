# Archivo de pruebas para el modelo PassVehicle
# ...aquí van los tests para PassVehicle...
import pytest
from datetime import date
from equipment.models.PassVehicle import PassVehicle
from equipment.models.Vehicle import Vehicle


@pytest.mark.django_db
class TestPassVehicle:
    
    def test_create_pass_vehicle(self):
        vehicle = Vehicle.objects.create(
            brand='Toyota',
            model='Hilux',
            type_vehicle='CAMIONETA',
            no_plate='ABC123'
        )
        pass_vehicle = PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='petroecuador',
            fecha_caducidad=date(2025, 12, 31)
        )
        assert pass_vehicle.vehicle == vehicle
        assert pass_vehicle.bloque == 'petroecuador'
        assert pass_vehicle.fecha_caducidad == date(2025, 12, 31)

    def test_pass_vehicle_str(self):
        vehicle = Vehicle.objects.create(
            brand='Chevrolet',
            model='D-Max',
            type_vehicle='CAMIONETA',
            no_plate='XYZ789'
        )
        pass_vehicle = PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='shaya',
            fecha_caducidad=date(2025, 6, 30)
        )
        expected_str = 'XYZ789 - shaya'
        assert str(pass_vehicle) == expected_str

    def test_get_by_vehicle_with_passes(self):
        vehicle = Vehicle.objects.create(
            brand='Ford',
            model='Ranger',
            type_vehicle='CAMIONETA',
            no_plate='FOR123'
        )
        
        # Create active passes
        pass1 = PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='petroecuador',
            fecha_caducidad=date(2025, 12, 31),
            is_active=True
        )
        pass2 = PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='shaya',
            fecha_caducidad=date(2025, 6, 30),
            is_active=True
        )
        
        # Create inactive pass
        PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='orion',
            fecha_caducidad=date(2025, 3, 31),
            is_active=False
        )
        
        active_passes = PassVehicle.get_by_vehicle(vehicle.id)
        assert len(active_passes) == 2
        assert pass1 in active_passes
        assert pass2 in active_passes

    def test_get_by_vehicle_no_passes(self):
        vehicle = Vehicle.objects.create(
            brand='Nissan',
            model='Frontier',
            type_vehicle='CAMIONETA',
            no_plate='NIS456'
        )
        
        passes = PassVehicle.get_by_vehicle(vehicle.id)
        assert len(passes) == 0

    def test_bloque_choices(self):
        vehicle = Vehicle.objects.create(
            brand='Mazda',
            model='BT-50',
            type_vehicle='CAMIONETA',
            no_plate='MAZ789'
        )
        
        for bloque_code, _ in PassVehicle.BLOQUE_CHOICES:
            pass_vehicle = PassVehicle.objects.create(
                vehicle=vehicle,
                bloque=bloque_code,
                fecha_caducidad=date(2025, 12, 31)
            )
            assert pass_vehicle.bloque == bloque_code
            pass_vehicle.delete()  # Clean up
