import pytest
import json
from django.test import Client
from datetime import date, timedelta

from accounts.models import CustomUserModel
from projects.models import Project, ProjectResourceItem, Partner
from equipment.models import ResourceItem
from api.projects.AddResourceProject import AddResourceProjectAPI


@pytest.mark.django_db
class TestAddResourceProjectAPI:
    """Tests para el endpoint de agregar recursos a proyectos"""

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
    def test_partner(self):
        """Partner de prueba"""
        return Partner.objects.create(
            name='Empresa Test',
            email='empresa@test.com',
            phone='0999999999'
        )

    @pytest.fixture
    def test_project(self, test_partner):
        """Proyecto de prueba"""
        return Project.objects.create(
            partner=test_partner,
            location='Campamento Norte',
            contact_name='Juan Pérez',
            contact_phone='0999888777',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180)
        )

    @pytest.fixture
    def test_resource(self):
        """Recurso disponible de prueba"""
        return ResourceItem.objects.create(
            name='Batería Sanitaria Hombre',
            code='BS-001',
            type_equipment='BTSNHM',
            brand='ACME',
            model='BS-2024',
            stst_status_equipment='FUNCIONANDO',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL'
        )

    @pytest.fixture
    def valid_resource_data(self, test_project, test_resource):
        """Datos válidos para agregar un recurso"""
        return {
            'project_id': test_project.id,
            'resource_item_id': test_resource.id,
            'rent_cost': 150.00,
            'maintenance_cost': 50.00,
            'maintenance_interval_days': 7,
            'operation_start_date': date.today().strftime('%Y-%m-%d'),
            'operation_end_date': (date.today() + timedelta(days=90)).strftime('%Y-%m-%d')
        }

    def test_add_resource_success(self, client_logged, valid_resource_data, test_resource):
        """Test agregar recurso exitosamente"""
        url = '/api/projects/resources/add'
        response = client_logged.post(
            url,
            data=json.dumps(valid_resource_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'agregado al proyecto' in data['message']
        assert data['data']['resource_code'] == 'BS-001'
        assert data['data']['rent_cost'] == '150.00'

        # Verificar que se creó en la base de datos
        project_resource = ProjectResourceItem.objects.get(
            id=data['data']['id']
        )
        assert project_resource.rent_cost == 150.00
        assert project_resource.is_retired is False

        # Verificar que se actualizó el ResourceItem
        test_resource.refresh_from_db()
        assert test_resource.stst_status_disponibility == 'RENTADO'
        assert test_resource.stst_current_project_id == valid_resource_data['project_id']
        assert test_resource.stst_current_location == 'Campamento Norte'

    def test_add_resource_missing_required_fields(self, client_logged):
        """Test agregar recurso con campos faltantes"""
        url = '/api/projects/resources/add'
        incomplete_data = {
            'project_id': 1,
            'resource_item_id': 1,
            # Faltan rent_cost, maintenance_cost, operation_start_date
        }

        response = client_logged.post(
            url,
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'requerido' in data['error']

    def test_add_resource_invalid_project(self, client_logged, test_resource):
        """Test agregar recurso con proyecto inexistente"""
        url = '/api/projects/resources/add'
        invalid_data = {
            'project_id': 99999,  # ID inexistente
            'resource_item_id': test_resource.id,
            'rent_cost': 150.00,
            'maintenance_cost': 50.00,
            'operation_start_date': date.today().strftime('%Y-%m-%d')
        }

        response = client_logged.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test_add_resource_invalid_resource(self, client_logged, test_project):
        """Test agregar recurso inexistente"""
        url = '/api/projects/resources/add'
        invalid_data = {
            'project_id': test_project.id,
            'resource_item_id': 99999,  # ID inexistente
            'rent_cost': 150.00,
            'maintenance_cost': 50.00,
            'operation_start_date': date.today().strftime('%Y-%m-%d')
        }

        response = client_logged.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test_add_resource_already_rented(
        self, client_logged, test_project, test_resource, valid_resource_data
    ):
        """Test agregar recurso que ya está rentado"""
        # Cambiar el estado del recurso a RENTADO
        test_resource.stst_status_disponibility = 'RENTADO'
        test_resource.save()

        url = '/api/projects/resources/add'
        response = client_logged.post(
            url,
            data=json.dumps(valid_resource_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'ya está rentado' in data['error']

    def test_add_resource_invalid_date_format(
        self, client_logged, test_project, test_resource
    ):
        """Test agregar recurso con formato de fecha inválido"""
        url = '/api/projects/resources/add'
        invalid_data = {
            'project_id': test_project.id,
            'resource_item_id': test_resource.id,
            'rent_cost': 150.00,
            'maintenance_cost': 50.00,
            'operation_start_date': '2024-13-45',  # Fecha inválida
        }

        response = client_logged.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'inválido' in data['error']

    def test_add_resource_end_date_before_start(
        self, client_logged, test_project, test_resource
    ):
        """Test agregar recurso con fecha fin anterior a fecha inicio"""
        url = '/api/projects/resources/add'
        invalid_data = {
            'project_id': test_project.id,
            'resource_item_id': test_resource.id,
            'rent_cost': 150.00,
            'maintenance_cost': 50.00,
            'operation_start_date': date.today().strftime('%Y-%m-%d'),
            'operation_end_date': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        }

        response = client_logged.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'no puede ser anterior' in data['error']

    def test_add_resource_without_end_date(
        self, client_logged, test_project, test_resource
    ):
        """Test agregar recurso sin fecha fin (usa fecha fin del proyecto)"""
        url = '/api/projects/resources/add'
        data_without_end = {
            'project_id': test_project.id,
            'resource_item_id': test_resource.id,
            'rent_cost': 150.00,
            'maintenance_cost': 50.00,
            'operation_start_date': date.today().strftime('%Y-%m-%d')
        }

        response = client_logged.post(
            url,
            data=json.dumps(data_without_end),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True

        # Verificar que usó la fecha fin del proyecto
        project_resource = ProjectResourceItem.objects.get(
            id=data['data']['id']
        )
        assert project_resource.operation_end_date == test_project.end_date

    def test_get_resources_by_project(
        self, client_logged, test_project, test_resource, valid_resource_data
    ):
        """Test listar recursos de un proyecto"""
        # Primero agregar un recurso
        url = '/api/projects/resources/add'
        client_logged.post(
            url,
            data=json.dumps(valid_resource_data),
            content_type='application/json'
        )

        # Luego listar
        url_get = f'/api/projects/resources/add?project_id={test_project.id}'
        response = client_logged.get(url_get)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['resource_code'] == 'BS-001'

    def test_get_resources_by_resource_id(
        self, client_logged, test_project, test_resource, valid_resource_data
    ):
        """Test ver en qué proyecto está un recurso"""
        # Primero agregar un recurso
        url = '/api/projects/resources/add'
        client_logged.post(
            url,
            data=json.dumps(valid_resource_data),
            content_type='application/json'
        )

        # Luego buscar por resource_id
        url_get = f'/api/projects/resources/add?resource_id={test_resource.id}'
        response = client_logged.get(url_get)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['project_id'] == test_project.id

    def test_get_without_parameters(self, client_logged):
        """Test GET sin parámetros debe fallar"""
        url = '/api/projects/resources/add'
        response = client_logged.get(url)

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'proporcionar' in data['error']

    def test_invalid_json(self, client_logged):
        """Test con JSON inválido"""
        url = '/api/projects/resources/add'
        response = client_logged.post(
            url,
            data='{ invalid json',
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'JSON inválido' in data['error']

    def test_commitment_date_logic_future_start(
        self, client_logged, test_project, test_resource
    ):
        """Test que commitment_date sea operation_start cuando es futuro"""
        url = '/api/projects/resources/add'
        future_date = date.today() + timedelta(days=30)
        future_data = {
            'project_id': test_project.id,
            'resource_item_id': test_resource.id,
            'rent_cost': 150.00,
            'maintenance_cost': 50.00,
            'operation_start_date': future_date.strftime('%Y-%m-%d')
        }

        response = client_logged.post(
            url,
            data=json.dumps(future_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        test_resource.refresh_from_db()
        assert test_resource.stst_commitment_date == future_date

    def test_commitment_date_logic_past_start(
        self, client_logged, test_project, test_resource
    ):
        """Test que commitment_date sea hoy cuando operation_start es pasado"""
        url = '/api/projects/resources/add'
        past_data = {
            'project_id': test_project.id,
            'resource_item_id': test_resource.id,
            'rent_cost': 150.00,
            'maintenance_cost': 50.00,
            'operation_start_date': date.today().strftime('%Y-%m-%d')
        }

        response = client_logged.post(
            url,
            data=json.dumps(past_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        test_resource.refresh_from_db()
        assert test_resource.stst_commitment_date == date.today()
