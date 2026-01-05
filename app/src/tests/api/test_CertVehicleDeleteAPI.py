import pytest
import json
from django.test import Client
from datetime import date, timedelta

from accounts.models import CustomUserModel
from equipment.models.Vehicle import Vehicle
from equipment.models.CertificationVehicle import CertificationVehicle


@pytest.mark.django_db
class TestCertVehicleDeleteAPI:
    """Tests para el endpoint de eliminar certificaciones de vehículos"""
    
    @pytest.fixture
    def client_logged(self):
        """Cliente autenticado para las pruebas"""
        user, created = CustomUserModel.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        client = Client()
        client.force_login(user)
        return client
    
    @pytest.fixture
    def test_vehicle(self):
        """Vehículo de prueba"""
        return Vehicle.objects.create(
            no_plate='TEST-001',
            brand='Toyota',
            model='Hilux',
            type_vehicle='CAMIONETA',
            year=2020
        )
    
    @pytest.fixture
    def test_certification(self, test_vehicle):
        """Certificación de prueba"""
        return CertificationVehicle.objects.create(
            vehicle=test_vehicle,
            name='INSPECCION VOLUMETRICA',
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365)
        )
