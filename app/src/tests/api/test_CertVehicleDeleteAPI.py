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
    
    @pytest.mark.skip(reason="El endpoint de eliminación de certificaciones no está implementado")
    def test_delete_certification_success(self, client_logged, test_certification):
        """Test eliminar certificación exitosamente"""
        url = f'/cert_vehicle/{test_certification.id}/'
        delete_data = {'id': test_certification.id}
        
        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'Certificación de vehículo eliminada exitosamente' in data['message']
        assert data['data']['id'] == test_certification.id
        
        # Verificar que se realizó soft delete
        test_certification.refresh_from_db()
        assert test_certification.is_active is False
    
    @pytest.mark.skip(reason="El endpoint de eliminación de certificaciones no está implementado")
    def test_delete_certification_missing_id(self, client_logged):
        """Test eliminar certificación sin ID"""
        url = '/cert_vehicle/1/'
        delete_data = {}  # Sin ID
        
        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'ID de la certificación es requerido' in data['error']
    
    @pytest.mark.skip(reason="El endpoint no está implementado")
    def test_delete_certification_not_found(self, client_logged):
        """Test eliminar certificación inexistente"""
        url = '/cert_vehicle/99999/'
        delete_data = {'id': 99999}
        
        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    @pytest.mark.skip(reason="El endpoint no está implementado")
    def test_delete_certification_already_deleted(self, client_logged, test_certification):
        """Test eliminar certificación ya eliminada"""
        # Eliminar la certificación primero
        test_certification.is_active = False
        test_certification.save()
        
        url = f'/cert_vehicle/{test_certification.id}/'
        delete_data = {'id': test_certification.id}
        
        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    @pytest.mark.skip(reason="El endpoint de eliminación múltiple no está implementado")
    def test_delete_multiple_certifications_success(self, client_logged, test_vehicle):
        """Test eliminar múltiples certificaciones exitosamente"""
        # Crear múltiples certificaciones
        cert1 = CertificationVehicle.objects.create(
            vehicle=test_vehicle,
            name='INSPECCION VOLUMETRICA',
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365)
        )
        cert2 = CertificationVehicle.objects.create(
            vehicle=test_vehicle,
            name='MEDICION DE ESPESORES',
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365)
        )
        
        url = '/cert_vehicle/1/'
        delete_data = {'ids': [cert1.id, cert2.id]}
        
        response = client_logged.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert '2 certificaciones eliminadas exitosamente' in data['message']
        assert data['data']['total_deleted'] == 2
        assert data['data']['total_errors'] == 0
        
        # Verificar que ambas certificaciones fueron eliminadas
        cert1.refresh_from_db()
        cert2.refresh_from_db()
        assert cert1.is_active is False
        assert cert2.is_active is False
    
    @pytest.mark.skip(reason="El endpoint de eliminación múltiple no está implementado")
    def test_delete_multiple_certifications_missing_ids(self, client_logged):
        """Test eliminar múltiples certificaciones sin IDs"""
        url = '/cert_vehicle/1/'
        delete_data = {}  # Sin IDs
        
        response = client_logged.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Lista de IDs es requerida' in data['error']
    
    @pytest.mark.skip(reason="El endpoint de eliminación múltiple no está implementado")
    def test_delete_multiple_certifications_invalid_ids(self, client_logged):
        """Test eliminar múltiples certificaciones con IDs inválidos"""
        url = '/cert_vehicle/1/'
        delete_data = {'ids': 'not_a_list'}  # IDs no es una lista
        
        response = client_logged.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Lista de IDs es requerida' in data['error']
    
    @pytest.mark.skip(reason="El endpoint de eliminación múltiple no está implementado")
    def test_delete_multiple_certifications_mixed_results(self, client_logged, test_vehicle):
        """Test eliminar múltiples certificaciones con resultados mixtos"""
        # Crear una certificación válida
        cert1 = CertificationVehicle.objects.create(
            vehicle=test_vehicle,
            name='INSPECCION VOLUMETRICA',
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365)
        )
        
        url = '/cert_vehicle/1/'
        delete_data = {'ids': [cert1.id, 99999]}  # Un ID válido, uno inválido
        
        response = client_logged.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert '1 certificaciones eliminadas exitosamente' in data['message']
        assert data['data']['total_deleted'] == 1
        assert data['data']['total_errors'] == 1
        
        # Verificar que la certificación válida fue eliminada
        cert1.refresh_from_db()
        assert cert1.is_active is False
        
        # Verificar que hay un error para el ID inválido
        assert len(data['data']['errors']) == 1
        assert data['data']['errors'][0]['id'] == 99999
    
    @pytest.mark.skip(reason="El endpoint no está implementado")
    def test_invalid_json(self, client_logged):
        """Test con JSON inválido"""
        url = '/cert_vehicle/1/'
        response = client_logged.delete(
            url,
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'JSON inválido' in data['error']
