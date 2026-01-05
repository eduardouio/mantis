import pytest
import json
from django.test import Client
from datetime import date, timedelta

from accounts.models import CustomUserModel
from equipment.models.Vehicle import Vehicle
from equipment.models.CertificationVehicle import CertificationVehicle


@pytest.mark.django_db
class TestCertVehicleCreateUpdateAPI:
    """Tests para el endpoint de crear y actualizar certificaciones de vehículos"""

    @pytest.fixture
    def client_logged(self):
        """Cliente autenticado para las pruebas"""
        user, created = CustomUserModel.objects.get_or_create(
            email="test@example.com",
            defaults={
                "first_name": "Test",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        client = Client()
        client.force_login(user)
        return client

    @pytest.fixture
    def test_vehicle(self):
        """Vehículo de prueba"""
        return Vehicle.objects.create(
            no_plate="TEST-001",
            brand="Toyota",
            model="Hilux",
            type_vehicle="CAMIONETA",
            year=2020,
        )

    @pytest.fixture
    def valid_cert_data(self, test_vehicle):
        """Datos válidos para crear una certificación"""
        return {
            "vehicle_id": test_vehicle.id,
            "name": "INSPECCION VOLUMETRICA",
            "date_start": (date.today()).strftime("%Y-%m-%d"),
            "date_end": (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "description": "Certificación de prueba",
        }

    def test_create_certification_success(self, client_logged, valid_cert_data):
        """Test crear certificación exitosamente"""
        url = "/api/vehicles/cert_vehicle/"
        response = client_logged.post(
            url, data=json.dumps(valid_cert_data), content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert "Certificación de vehículo creada exitosamente" in data["message"]
        assert data["data"]["name"] == "INSPECCION VOLUMETRICA"
        assert data["data"]["vehicle_id"] == valid_cert_data["vehicle_id"]

        cert = CertificationVehicle.objects.get(id=data["data"]["id"])
        assert cert.name == "INSPECCION VOLUMETRICA"
        assert cert.is_active is True

    def test_create_certification_missing_required_fields(self, client_logged):
        """Test crear certificación con campos faltantes"""
        url = "/api/vehicles/cert_vehicle/"
        incomplete_data = {
            "name": "INSPECCION VOLUMETRICA",
        }

        response = client_logged.post(
            url, data=json.dumps(incomplete_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["success"] is False
        assert "es requerido" in data["error"]

    def test_create_certification_invalid_vehicle(self, client_logged):
        """Test crear certificación con vehículo inexistente"""
        url = "/api/vehicles/cert_vehicle/"
        invalid_data = {
            "vehicle_id": 99999,
            "name": "INSPECCION VOLUMETRICA",
            "date_start": date.today().strftime("%Y-%m-%d"),
            "date_end": (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"),
        }

        response = client_logged.post(
            url, data=json.dumps(invalid_data), content_type="application/json"
        )

        assert response.status_code == 500

    def test_create_certification_invalid_date_format(
        self, client_logged, test_vehicle
    ):
        """Test crear certificación con formato de fecha inválido"""
        url = "/api/vehicles/cert_vehicle/"
        invalid_data = {
            "vehicle_id": test_vehicle.id,
            "name": "INSPECCION VOLUMETRICA",
            "date_start": "2024-13-45",
            "date_end": "2025-01-01",
        }

        response = client_logged.post(
            url, data=json.dumps(invalid_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["success"] is False
        assert "Formato de fecha inválido" in data["error"]

    def test_create_certification_end_date_before_start(
        self, client_logged, test_vehicle
    ):
        """Test crear certificación con fecha fin anterior a fecha inicio"""
        url = "/api/vehicles/cert_vehicle/"
        invalid_data = {
            "vehicle_id": test_vehicle.id,
            "name": "INSPECCION VOLUMETRICA",
            "date_start": date.today().strftime("%Y-%m-%d"),
            "date_end": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
        }

        response = client_logged.post(
            url, data=json.dumps(invalid_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["success"] is False
        assert "La fecha de fin debe ser posterior" in data["error"]

    def test_create_certification_invalid_name(self, client_logged, test_vehicle):
        """Test crear certificación con nombre inválido"""
        url = "/api/vehicles/cert_vehicle/"
        invalid_data = {
            "vehicle_id": test_vehicle.id,
            "name": "CERTIFICACION_INEXISTENTE",
            "date_start": date.today().strftime("%Y-%m-%d"),
            "date_end": (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"),
        }

        response = client_logged.post(
            url, data=json.dumps(invalid_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["success"] is False
        assert "Nombre de certificación inválido" in data["error"]

    def test_update_certification_success(self, client_logged, test_vehicle):
        """Test actualizar certificación exitosamente"""

        cert = CertificationVehicle.objects.create(
            vehicle=test_vehicle,
            name="INSPECCION VOLUMETRICA",
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365),
            description="Descripción original",
        )

        url = "/api/vehicles/cert_vehicle/"
        update_data = {
            "id": cert.id,
            "vehicle_id": test_vehicle.id,
            "name": "MEDICION DE ESPESORES",
            "date_start": date.today().strftime("%Y-%m-%d"),
            "date_end": (date.today() + timedelta(days=730)).strftime("%Y-%m-%d"),
            "description": "Descripción actualizada",
        }

        response = client_logged.put(
            url, data=json.dumps(update_data), content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert "Certificación de vehículo actualizada exitosamente" in data["message"]
        assert data["data"]["name"] == "MEDICION DE ESPESORES"
        assert data["data"]["description"] == "Descripción actualizada"

        cert.refresh_from_db()
        assert cert.name == "MEDICION DE ESPESORES"
        assert cert.description == "Descripción actualizada"

    def test_update_certification_missing_id(self, client_logged, valid_cert_data):
        """Test actualizar certificación sin ID"""
        url = "/api/vehicles/cert_vehicle/"

        update_data = valid_cert_data.copy()

        response = client_logged.put(
            url, data=json.dumps(update_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["success"] is False
        assert "ID de la certificación es requerido" in data["error"]

    def test_get_certification_by_id(self, client_logged, test_vehicle):
        """Test obtener certificación por ID"""
        cert = CertificationVehicle.objects.create(
            vehicle=test_vehicle,
            name="INSPECCION VOLUMETRICA",
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365),
            description="Certificación de prueba",
        )

        url = f"/api/vehicles/cert_vehicle/?id={cert.id}"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert data["data"]["id"] == cert.id
        assert data["data"]["name"] == "INSPECCION VOLUMETRICA"
        assert data["data"]["vehicle_plate"] == test_vehicle.no_plate

    def test_get_certifications_by_vehicle(self, client_logged, test_vehicle):
        """Test obtener certificaciones por vehículo"""

        cert1 = CertificationVehicle.objects.create(
            vehicle=test_vehicle,
            name="INSPECCION VOLUMETRICA",
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365),
        )
        cert2 = CertificationVehicle.objects.create(
            vehicle=test_vehicle,
            name="MEDICION DE ESPESORES",
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365),
        )

        url = f"/api/vehicles/cert_vehicle/?vehicle_id={test_vehicle.id}"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert len(data["data"]) == 2

        cert_names = [cert["name"] for cert in data["data"]]
        assert "INSPECCION VOLUMETRICA" in cert_names
        assert "MEDICION DE ESPESORES" in cert_names

    def test_get_all_certifications(self, client_logged, test_vehicle):
        """Test obtener todas las certificaciones"""
        cert = CertificationVehicle.objects.create(
            vehicle=test_vehicle,
            name="INSPECCION VOLUMETRICA",
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365),
        )

        url = "/api/vehicles/cert_vehicle/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert len(data["data"]) >= 1

        cert_ids = [cert["id"] for cert in data["data"]]
        assert cert.id in cert_ids

    def test_invalid_json(self, client_logged):
        """Test con JSON inválido"""
        url = "/api/vehicles/cert_vehicle/"
        response = client_logged.post(
            url, data="invalid json", content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["success"] is False
        assert "JSON inválido" in data["error"]
