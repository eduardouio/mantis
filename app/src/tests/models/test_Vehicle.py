# Archivo de pruebas para el modelo Vehicle
# ...aquí van los tests para Vehicle...

import pytest
from equipment.models.Vehicle import Vehicle


@pytest.mark.django_db
def test_create_vehicle():
    vehicle = Vehicle.objects.create(
        brand="Toyota",
        model="Hilux",
        type_vehicle="CAMIONETA",
        year=2022,
        no_plate="ABC123",
        status_vehicle="DISPONIBLE",
        owner_transport="PEISOL"
    )
    assert vehicle.id is not None
    assert vehicle.brand == "Toyota"
    assert vehicle.type_vehicle == "CAMIONETA"
    assert vehicle.no_plate == "ABC123"
    assert str(vehicle) == "ABC123"


@pytest.mark.django_db
def test_vehicle_str():
    vehicle = Vehicle.objects.create(
        brand="Chevrolet",
        model="D-Max",
        type_vehicle="CAMIONETA",
        year=2021,
        no_plate="XYZ789",
        status_vehicle="DISPONIBLE",
        owner_transport="PEISOL"
    )
    assert str(vehicle) == "XYZ789"
