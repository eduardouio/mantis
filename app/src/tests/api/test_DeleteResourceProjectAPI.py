import pytest
import json
from django.test import Client
from datetime import date, timedelta

from accounts.models import CustomUserModel
from projects.models import Project, ProjectResourceItem, Partner
from equipment.models import ResourceItem
from api.projects.DeleteResourceProject import DeleteResourceProjectAPI


@pytest.mark.django_db
class TestDeleteResourceProjectAPI:
    """Tests para el endpoint de eliminar recursos de proyectos"""

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
        """Recurso de prueba"""
        return ResourceItem.objects.create(
            name='Batería Sanitaria Hombre',
            code='BS-001',
            type_equipment='BTSNHM',
            brand='ACME',
            model='BS-2024',
            stst_status_equipment='FUNCIONANDO',
            stst_status_disponibility='RENTADO',
            stst_current_location='Campamento Norte',
            stst_current_project_id=1,
            stst_commitment_date=date.today(),
            stst_release_date=date.today() + timedelta(days=90)
        )

    @pytest.fixture
    def test_project_resource(self, test_project, test_resource):
        """ProjectResourceItem de prueba"""
        return ProjectResourceItem.objects.create(
            project=test_project,
            resource_item=test_resource,
            rent_cost=150.00,
            maintenance_cost=50.00,
            maintenance_interval_days=7,
            operation_start_date=date.today(),
            operation_end_date=date.today() + timedelta(days=90)
        )

    def test_delete_resource_success(
        self, client_logged, test_project_resource, test_resource
    ):
        """Test eliminar recurso exitosamente"""
        url = '/api/projects/resources/delete'
        delete_data = {
            'project_resource_id': test_project_resource.id,
            'retirement_reason': 'Finalización del proyecto'
        }

        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'liberado del proyecto' in data['message']
        assert data['data']['resource_code'] == 'BS-001'
        assert data['data']['status'] == 'DISPONIBLE'
        assert data['data']['location'] == 'BASE PEISOL'

        # Verificar que se actualizó ProjectResourceItem
        test_project_resource.refresh_from_db()
        assert test_project_resource.is_retired is True
        assert test_project_resource.retirement_date == date.today()
        assert test_project_resource.retirement_reason == 'Finalización del proyecto'

        # Verificar que se actualizó ResourceItem
        test_resource.refresh_from_db()
        assert test_resource.stst_status_disponibility == 'DISPONIBLE'
        assert test_resource.stst_current_location == 'BASE PEISOL'
        assert test_resource.stst_current_project_id is None
        assert test_resource.stst_commitment_date is None
        assert test_resource.stst_release_date is None

    def test_delete_resource_without_reason(
        self, client_logged, test_project_resource, test_resource
    ):
        """Test eliminar recurso sin razón (usa razón por defecto)"""
        url = '/api/projects/resources/delete'
        delete_data = {
            'project_resource_id': test_project_resource.id
        }

        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True

        # Verificar razón por defecto
        test_project_resource.refresh_from_db()
        assert test_project_resource.retirement_reason == 'Liberado del proyecto'

    def test_delete_resource_missing_id(self, client_logged):
        """Test eliminar recurso sin proporcionar ID"""
        url = '/api/projects/resources/delete'
        delete_data = {
            'retirement_reason': 'Test'
        }

        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'project_resource_id requerido' in data['error']

    def test_delete_resource_invalid_id(self, client_logged):
        """Test eliminar recurso con ID inexistente"""
        url = '/api/projects/resources/delete'
        delete_data = {
            'project_resource_id': 99999
        }

        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test_delete_resource_already_retired(
        self, client_logged, test_project_resource
    ):
        """Test eliminar recurso que ya está retirado"""
        # Marcar como retirado
        test_project_resource.is_retired = True
        test_project_resource.save()

        url = '/api/projects/resources/delete'
        delete_data = {
            'project_resource_id': test_project_resource.id
        }

        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test_get_resource_info(self, client_logged, test_project_resource):
        """Test obtener información de un recurso en proyecto"""
        url = f'/api/projects/resources/delete?project_resource_id={test_project_resource.id}'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['data']['id'] == test_project_resource.id
        assert data['data']['resource_code'] == 'BS-001'
        assert data['data']['is_retired'] is False

    def test_get_resource_info_missing_id(self, client_logged):
        """Test GET sin proporcionar ID"""
        url = '/api/projects/resources/delete'
        response = client_logged.get(url)

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'proporcionar project_resource_id' in data['error']

    def test_get_resource_info_invalid_id(self, client_logged):
        """Test GET con ID inexistente"""
        url = '/api/projects/resources/delete?project_resource_id=99999'
        response = client_logged.get(url)

        assert response.status_code == 404

    def test_invalid_json(self, client_logged):
        """Test con JSON inválido"""
        url = '/api/projects/resources/delete'
        response = client_logged.delete(
            url,
            data='{ invalid json',
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'JSON inválido' in data['error']

    def test_delete_resource_transaction_rollback(
        self, client_logged, test_project_resource, test_resource, mocker
    ):
        """Test que la transacción se revierta en caso de error"""
        url = '/api/projects/resources/delete'
        delete_data = {
            'project_resource_id': test_project_resource.id
        }

        # Mock para forzar un error en el save
        mocker.patch.object(
            test_resource,
            'save',
            side_effect=Exception('Error simulado')
        )

        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        # Debe retornar error
        assert response.status_code == 500

        # Verificar que no se modificó nada (rollback)
        test_project_resource.refresh_from_db()
        assert test_project_resource.is_retired is False

    def test_serialization_with_all_fields(
        self, client_logged, test_project_resource
    ):
        """Test serialización con todos los campos"""
        # Marcar como retirado para tener todos los campos
        test_project_resource.is_retired = True
        test_project_resource.retirement_date = date.today()
        test_project_resource.retirement_reason = 'Test reason'
        test_project_resource.save()

        url = f'/api/projects/resources/delete?project_resource_id={test_project_resource.id}'
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['data']['is_retired'] is True
        assert data['data']['retirement_date'] is not None
        assert data['data']['retirement_reason'] == 'Test reason'

    def test_delete_inactive_resource(
        self, client_logged, test_project_resource
    ):
        """Test eliminar recurso inactivo"""
        test_project_resource.is_active = False
        test_project_resource.save()

        url = '/api/projects/resources/delete'
        delete_data = {
            'project_resource_id': test_project_resource.id
        }

        response = client_logged.delete(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 404
