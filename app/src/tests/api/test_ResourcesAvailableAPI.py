import pytest
import json
from django.test import Client

from accounts.models import CustomUserModel
from equipment.models import ResourceItem
from api.projects.ResourcesAvailable import ResourcesAvailableAPI


@pytest.mark.django_db
class TestResourcesAvailableAPI:
    """Tests para el endpoint de listar recursos disponibles"""

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
    def available_resources(self):
        """Crear varios recursos disponibles"""
        resources = []

        # Batería Sanitaria Hombre - DISPONIBLE
        resources.append(ResourceItem.objects.create(
            name='Batería Sanitaria Hombre 1',
            code='BS-001',
            type_equipment='BTSNHM',
            brand='ACME',
            model='BS-2024',
            stst_status_equipment='FUNCIONANDO',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL'
        ))

        # Lavamanos - DISPONIBLE
        resources.append(ResourceItem.objects.create(
            name='Lavamanos 1',
            code='LV-001',
            type_equipment='LVMNOS',
            brand='ACME',
            model='LV-2024',
            stst_status_equipment='FUNCIONANDO',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL'
        ))

        # Batería Sanitaria Mujer - DISPONIBLE
        resources.append(ResourceItem.objects.create(
            name='Batería Sanitaria Mujer 1',
            code='BSM-001',
            type_equipment='BTSNMJ',
            brand='ACME',
            model='BSM-2024',
            stst_status_equipment='FUNCIONANDO',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL'
        ))

        # Recurso RENTADO (no debe aparecer)
        ResourceItem.objects.create(
            name='Batería Sanitaria Hombre 2',
            code='BS-002',
            type_equipment='BTSNHM',
            brand='ACME',
            model='BS-2024',
            stst_status_equipment='FUNCIONANDO',
            stst_status_disponibility='RENTADO',
            stst_current_location='Proyecto X',
            stst_current_project_id=1
        )

        # Recurso INACTIVO (no debe aparecer)
        ResourceItem.objects.create(
            name='Batería Sanitaria Hombre 3',
            code='BS-003',
            type_equipment='BTSNHM',
            brand='ACME',
            model='BS-2024',
            stst_status_equipment='FUNCIONANDO',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL',
            is_active=False
        )

        # Recurso DAÑADO pero DISPONIBLE
        resources.append(ResourceItem.objects.create(
            name='Lavamanos 2',
            code='LV-002',
            type_equipment='LVMNOS',
            brand='ACME',
            model='LV-2024',
            stst_status_equipment='DAÑADO',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL'
        ))

        return resources

    def test_get_all_available_resources(
        self, client_logged, available_resources
    ):
        """Test obtener todos los recursos disponibles"""
        url = '/api/projects/resources/available'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['count'] == 4  # Solo los 4 DISPONIBLES y activos
        assert len(data['data']) == 4

        # Verificar que están ordenados por type_equipment y code
        codes = [item['code'] for item in data['data']]
        assert 'BS-001' in codes
        assert 'LV-001' in codes
        assert 'BSM-001' in codes
        assert 'LV-002' in codes
        # No deben aparecer los rentados o inactivos
        assert 'BS-002' not in codes
        assert 'BS-003' not in codes

    def test_filter_by_type_equipment(
        self, client_logged, available_resources
    ):
        """Test filtrar por tipo de equipo"""
        url = '/api/projects/resources/available?type_equipment=BTSNHM'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['count'] == 1
        assert data['data'][0]['code'] == 'BS-001'
        assert data['data'][0]['type_equipment'] == 'BTSNHM'

    def test_filter_by_status_equipment(
        self, client_logged, available_resources
    ):
        """Test filtrar por estado del equipo"""
        url = '/api/projects/resources/available?status_equipment=FUNCIONANDO'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['count'] == 3  # Los 3 que están FUNCIONANDO
        for item in data['data']:
            assert item['status_equipment'] == 'FUNCIONANDO'

    def test_filter_by_status_equipment_damaged(
        self, client_logged, available_resources
    ):
        """Test filtrar por equipos dañados"""
        url = '/api/projects/resources/available?status_equipment=DAÑADO'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['count'] == 1
        assert data['data'][0]['code'] == 'LV-002'
        assert data['data'][0]['status_equipment'] == 'DAÑADO'

    def test_search_by_code(self, client_logged, available_resources):
        """Test buscar por código"""
        url = '/api/projects/resources/available?search=BS-001'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['count'] == 1
        assert data['data'][0]['code'] == 'BS-001'

    def test_search_by_name(self, client_logged, available_resources):
        """Test buscar por nombre"""
        url = '/api/projects/resources/available?search=Lavamanos'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['count'] == 2  # LV-001 y LV-002
        assert all('Lavamanos' in item['name'] for item in data['data'])

    def test_search_case_insensitive(
        self, client_logged, available_resources
    ):
        """Test búsqueda insensible a mayúsculas/minúsculas"""
        url = '/api/projects/resources/available?search=lavamanos'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['count'] == 2

    def test_combined_filters(self, client_logged, available_resources):
        """Test combinar múltiples filtros"""
        url = '/api/projects/resources/available?type_equipment=LVMNOS&status_equipment=FUNCIONANDO'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['count'] == 1
        assert data['data'][0]['code'] == 'LV-001'
        assert data['data'][0]['type_equipment'] == 'LVMNOS'
        assert data['data'][0]['status_equipment'] == 'FUNCIONANDO'

    def test_exclude_services_default(self, client_logged):
        """Test que excluya servicios por defecto"""
        # Crear un servicio
        ResourceItem.objects.create(
            name='Servicio Test',
            code='SRV-001',
            type_equipment='SERVIC',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL'
        )

        url = '/api/projects/resources/available'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        # No debe incluir el servicio
        codes = [item['code'] for item in data['data']]
        assert 'SRV-001' not in codes

    def test_include_services_explicitly(self, client_logged):
        """Test incluir servicios explícitamente"""
        # Crear un servicio
        ResourceItem.objects.create(
            name='Servicio Test',
            code='SRV-001',
            type_equipment='SERVIC',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL'
        )

        url = '/api/projects/resources/available?exclude_services=false'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        # Ahora sí debe incluir el servicio
        codes = [item['code'] for item in data['data']]
        assert 'SRV-001' in codes

    def test_serialization_fields(
        self, client_logged, available_resources
    ):
        """Test que la serialización incluya todos los campos esperados"""
        url = '/api/projects/resources/available'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data['data']) > 0

        # Verificar campos del primer recurso
        resource = data['data'][0]
        assert 'id' in resource
        assert 'code' in resource
        assert 'name' in resource
        assert 'type_equipment' in resource
        assert 'type_equipment_display' in resource
        assert 'brand' in resource
        assert 'model' in resource
        assert 'status_equipment' in resource
        assert 'status_disponibility' in resource
        assert 'current_location' in resource
        assert 'capacity_gallons' in resource

    def test_type_equipment_display(
        self, client_logged, available_resources
    ):
        """Test que type_equipment_display retorne el nombre legible"""
        url = '/api/projects/resources/available?type_equipment=BTSNHM'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['data'][0]['type_equipment'] == 'BTSNHM'
        assert data['data'][0]['type_equipment_display'] == 'BATERIA SANITARIA HOMBRE'

    def test_empty_results(self, client_logged):
        """Test cuando no hay recursos disponibles"""
        # Marcar todos como rentados
        ResourceItem.objects.all().update(
            stst_status_disponibility='RENTADO'
        )

        url = '/api/projects/resources/available'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['count'] == 0
        assert len(data['data']) == 0

    def test_capacity_gallons_serialization(self, client_logged):
        """Test serialización de capacity_gallons"""
        ResourceItem.objects.create(
            name='Tanque con capacidad',
            code='TQ-001',
            type_equipment='TNQAAC',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL',
            capacity_gallons=500.75
        )

        url = '/api/projects/resources/available?search=TQ-001'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['data'][0]['capacity_gallons'] == '500.75'

    def test_capacity_gallons_null(self, client_logged):
        """Test cuando capacity_gallons es null"""
        ResourceItem.objects.create(
            name='Equipo sin capacidad',
            code='EQ-001',
            type_equipment='LVMNOS',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL',
            capacity_gallons=None
        )

        url = '/api/projects/resources/available?search=EQ-001'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['data'][0]['capacity_gallons'] is None

    def test_ordering(self, client_logged):
        """Test que los recursos estén ordenados correctamente"""
        # Crear recursos con diferentes tipos y códigos
        ResourceItem.objects.create(
            name='Z Resource',
            code='ZZ-001',
            type_equipment='LVMNOS',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL'
        )
        ResourceItem.objects.create(
            name='A Resource',
            code='AA-001',
            type_equipment='BTSNHM',
            stst_status_disponibility='DISPONIBLE',
            stst_current_location='BASE PEISOL'
        )

        url = '/api/projects/resources/available'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)

        # Verificar que están ordenados por type_equipment primero
        types = [item['type_equipment'] for item in data['data']]
        assert types == sorted(types)
