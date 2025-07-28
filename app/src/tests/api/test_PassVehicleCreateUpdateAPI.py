import pytest
import json
from django.test import Client
from datetime import date, timedelta

from accounts.models import CustomUserModel
from equipment.models.Vehicle import Vehicle
from equipment.models.PassVehicle import PassVehicle


@pytest.mark.django_db
class TestPassVehicleCreateUpdateAPI:
    """Tests para el endpoint de crear y actualizar pases de vehículos"""
    
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
    def valid_pass_data(self, test_vehicle):
        """Datos válidos para crear un pase"""
        return {
            'vehicle_id': test_vehicle.id,
            'bloque': 'PETROECUADOR',
            'fecha_caducidad': (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')
        }
    
    def test_create_pass_success(self, client_logged, valid_pass_data):
        """Test crear pase exitosamente"""
        url = '/pass_vehicle/'
        response = client_logged.post(
            url,
            data=json.dumps(valid_pass_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'Pase de vehículo creado exitosamente' in data['message']
        assert data['data']['bloque'] == 'PETROECUADOR'
        assert data['data']['vehicle_id'] == valid_pass_data['vehicle_id']
        
        # Verificar que se creó en la base de datos
        pass_vehicle = PassVehicle.objects.get(id=data['data']['id'])
        assert pass_vehicle.bloque == 'PETROECUADOR'
        assert pass_vehicle.is_active is True
    
    def test_create_pass_missing_required_fields(self, client_logged):
        """Test crear pase con campos faltantes"""
        url = '/pass_vehicle/'
        incomplete_data = {
            'bloque': 'PETROECUADOR',
            # Faltan vehicle_id, fecha_caducidad
        }
        
        response = client_logged.post(
            url,
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'es requerido' in data['error']
    
    def test_create_pass_invalid_vehicle(self, client_logged):
        """Test crear pase con vehículo inexistente"""
        url = '/pass_vehicle/'
        invalid_data = {
            'vehicle_id': 99999,  # ID inexistente
            'bloque': 'PETROECUADOR',
            'fecha_caducidad': (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),
        }
        
        response = client_logged.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_create_pass_invalid_date_format(self, client_logged, test_vehicle):
        """Test crear pase con formato de fecha inválido"""
        url = '/pass_vehicle/'
        invalid_data = {
            'vehicle_id': test_vehicle.id,
            'bloque': 'PETROECUADOR',
            'fecha_caducidad': '2024-13-45',  # Fecha inválida
        }
        
        response = client_logged.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Formato de fecha inválido' in data['error']
    
    def test_create_pass_invalid_bloque(self, client_logged, test_vehicle):
        """Test crear pase con bloque inválido"""
        url = '/pass_vehicle/'
        invalid_data = {
            'vehicle_id': test_vehicle.id,
            'bloque': 'BLOQUE_INEXISTENTE',  # Bloque no válido
            'fecha_caducidad': (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),
        }
        
        response = client_logged.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Bloque inválido' in data['error']
    
    def test_update_pass_success(self, client_logged, test_vehicle):
        """Test actualizar pase exitosamente"""
        # Crear pase primero
        pass_vehicle = PassVehicle.objects.create(
            vehicle=test_vehicle,
            bloque='PETROECUADOR',
            fecha_caducidad=date.today() + timedelta(days=365)
        )
        
        url = '/pass_vehicle/'
        update_data = {
            'id': pass_vehicle.id,
            'vehicle_id': test_vehicle.id,
            'bloque': 'SHAYA',
            'fecha_caducidad': (date.today() + timedelta(days=730)).strftime('%Y-%m-%d')
        }
        
        response = client_logged.put(
            url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'Pase de vehículo actualizado exitosamente' in data['message']
        assert data['data']['bloque'] == 'SHAYA'
        
        # Verificar que se actualizó en la base de datos
        pass_vehicle.refresh_from_db()
        assert pass_vehicle.bloque == 'SHAYA'
    
    def test_update_pass_missing_id(self, client_logged, valid_pass_data):
        """Test actualizar pase sin ID"""
        url = '/pass_vehicle/'
        # Datos sin ID
        update_data = valid_pass_data.copy()
        
        response = client_logged.put(
            url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'ID del pase es requerido' in data['error']
    
    def test_get_pass_by_id(self, client_logged, test_vehicle):
        """Test obtener pase por ID"""
        pass_vehicle = PassVehicle.objects.create(
            vehicle=test_vehicle,
            bloque='PETROECUADOR',
            fecha_caducidad=date.today() + timedelta(days=365)
        )
        
        url = f'/pass_vehicle/?id={pass_vehicle.id}'
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['data']['id'] == pass_vehicle.id
        assert data['data']['bloque'] == 'PETROECUADOR'
        assert data['data']['vehicle_plate'] == test_vehicle.no_plate
    
    def test_get_passes_by_vehicle(self, client_logged, test_vehicle):
        """Test obtener pases por vehículo"""
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
        
        url = f'/pass_vehicle/?vehicle_id={test_vehicle.id}'
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert len(data['data']) == 2
        
        # Verificar que ambos pases están presentes
        pass_bloques = [pass_data['bloque'] for pass_data in data['data']]
        assert 'PETROECUADOR' in pass_bloques
        assert 'SHAYA' in pass_bloques
    
    def test_get_all_passes(self, client_logged, test_vehicle):
        """Test obtener todos los pases"""
        pass_vehicle = PassVehicle.objects.create(
            vehicle=test_vehicle,
            bloque='PETROECUADOR',
            fecha_caducidad=date.today() + timedelta(days=365)
        )
        
        url = '/pass_vehicle/'
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert len(data['data']) >= 1
        
        # Verificar que nuestro pase está en la lista
        pass_ids = [pass_data['id'] for pass_data in data['data']]
        assert pass_vehicle.id in pass_ids
    
    def test_invalid_json(self, client_logged):
        """Test con JSON inválido"""
        url = '/pass_vehicle/'
        response = client_logged.post(
            url,
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'JSON inválido' in data['error']
    
    def test_valid_bloque_choices(self, client_logged, test_vehicle):
        """Test con todas las opciones válidas de bloque"""
        valid_bloques = [
            'PETROECUADOR', 'SHAYA', 'CONSORCIO SHUSHUFINDI', 'ENAP SIPEC',
            'ORION', 'ANDES PETROLEUM', 'PARDALIS SERVICES', 'FRONTERA ENERGY',
            'GRAN TIERRA', 'PCR', 'HALLIBURTON', 'GENTE OIL', 'TRIBIOL GAS',
            'ADICO', 'CUYAVENO PETRO', 'GEOPARK'
        ]
        
        url = '/pass_vehicle/'
        
        for bloque in valid_bloques:
            pass_data = {
                'vehicle_id': test_vehicle.id,
                'bloque': bloque,
                'fecha_caducidad': (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')
            }
            
            response = client_logged.post(
                url,
                data=json.dumps(pass_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.content)
            assert data['success'] is True
            assert data['data']['bloque'] == bloque
