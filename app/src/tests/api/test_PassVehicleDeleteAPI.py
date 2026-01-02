import pytest
import json
from django.test import Client
from datetime import date, timedelta

from accounts.models import CustomUserModel
from equipment.models.Vehicle import Vehicle
from equipment.models.PassVehicle import PassVehicle


@pytest.mark.django_db
class TestPassVehicleDeleteAPI:
    """Tests para el endpoint de eliminar pases de vehículos"""
    
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
    def test_pass(self, test_vehicle):
        """Pase de prueba"""
        return PassVehicle.objects.create(
            vehicle=test_vehicle,
            bloque='PETROECUADOR',
            fecha_caducidad=date.today() + timedelta(days=365)
        )
    
    @pytest.mark.skip(reason="El endpoint de eliminación de pases no está implementado")
    def test_delete_pass_success(self, client_logged, test_pass):
        """Test eliminar pase exitosamente"""
        url = f'/pass_vehicle/{test_pass.id}/'
        delete_data = {'id': test_pass.id}
        
        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'Pase de vehículo eliminado exitosamente' in data['message']
        assert data['data']['id'] == test_pass.id
        
        # Verificar que se realizó soft delete
        test_pass.refresh_from_db()
        assert test_pass.is_active is False
    
    @pytest.mark.skip(reason="El endpoint de eliminación de pases no está implementado")
    def test_delete_pass_missing_id(self, client_logged):
        """Test eliminar pase sin ID"""
        url = '/pass_vehicle/1/'
        delete_data = {}  # Sin ID
        
        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'ID del pase es requerido' in data['error']
    
    @pytest.mark.skip(reason="El endpoint no está implementado")
    def test_delete_pass_not_found(self, client_logged):
        """Test eliminar pase inexistente"""
        url = '/pass_vehicle/99999/'
        delete_data = {'id': 99999}
        
        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    @pytest.mark.skip(reason="El endpoint no está implementado")
    def test_delete_pass_already_deleted(self, client_logged, test_pass):
        """Test eliminar pase ya eliminado"""
        # Eliminar el pase primero
        test_pass.is_active = False
        test_pass.save()
        
        url = f'/pass_vehicle/{test_pass.id}/'
        delete_data = {'id': test_pass.id}
        
        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    @pytest.mark.skip(reason="El endpoint de eliminación múltiple no está implementado")
    def test_delete_multiple_passes_success(self, client_logged, test_vehicle):
        """Test eliminar múltiples pases exitosamente"""
        # Crear múltiples pases
        pass1 = PassVehicle.objects.create(
            vehicle=test_vehicle,
            bloque='PETROECUADOR',
            fecha_caducidad=date.today() + timedelta(days=365)
        )
        pass2 = PassVehicle.objects.create(
            vehicle=test_vehicle,
            bloque='SHAYA',
            fecha_caducidad=date.today() + timedelta(days=365)
        )
        
        url = '/pass_vehicle/1/'
        delete_data = {'ids': [pass1.id, pass2.id]}
        
        response = client_logged.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert '2 pases eliminados exitosamente' in data['message']
        assert data['data']['total_deleted'] == 2
        assert data['data']['total_errors'] == 0
        
        # Verificar que ambos pases fueron eliminados
        pass1.refresh_from_db()
        pass2.refresh_from_db()
        assert pass1.is_active is False
        assert pass2.is_active is False
    
    @pytest.mark.skip(reason="El endpoint de eliminación múltiple no está implementado")
    def test_delete_multiple_passes_missing_ids(self, client_logged):
        """Test eliminar múltiples pases sin IDs"""
        url = '/pass_vehicle/1/'
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
    def test_delete_multiple_passes_invalid_ids(self, client_logged):
        """Test eliminar múltiples pases con IDs inválidos"""
        url = '/pass_vehicle/1/'
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
    def test_delete_multiple_passes_mixed_results(self, client_logged, test_vehicle):
        """Test eliminar múltiples pases con resultados mixtos"""
        # Crear un pase válido
        pass1 = PassVehicle.objects.create(
            vehicle=test_vehicle,
            bloque='PETROECUADOR',
            fecha_caducidad=date.today() + timedelta(days=365)
        )
        
        url = '/pass_vehicle/1/'
        delete_data = {'ids': [pass1.id, 99999]}  # Un ID válido, uno inválido
        
        response = client_logged.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert '1 pases eliminados exitosamente' in data['message']
        assert data['data']['total_deleted'] == 1
        assert data['data']['total_errors'] == 1
        
        # Verificar que el pase válido fue eliminado
        pass1.refresh_from_db()
        assert pass1.is_active is False
        
        # Verificar que hay un error para el ID inválido
        assert len(data['data']['errors']) == 1
        assert data['data']['errors'][0]['id'] == 99999
    
    @pytest.mark.skip(reason="El endpoint no está implementado")
    def test_invalid_json(self, client_logged):
        """Test con JSON inválido"""
        url = '/pass_vehicle/1/'
        response = client_logged.delete(
            url,
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'JSON inválido' in data['error']
