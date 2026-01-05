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
            cost=150.00,
            interval_days=7,
            operation_start_date=date.today(),
            operation_end_date=date.today() + timedelta(days=90)
        )

    def test_delete_resource_success(
        self, client_logged, test_project_resource, test_resource
    ):
        """Test eliminar recurso exitosamente"""
        url = f'/api/projects/resources/delete/{test_project_resource.id}/'
        
        response = client_logged.delete(url)

        assert response.status_code == 204
        
        # Verificar que el recurso fue eliminado
        assert not ProjectResourceItem.objects.filter(
            id=test_project_resource.id
        ).exists()

    def test_delete_resource_invalid_id(self, client_logged):
        """Test eliminar recurso con ID inexistente"""
        url = '/api/projects/resources/delete/99999/'
        
        response = client_logged.delete(url)

        assert response.status_code == 404

    def test_delete_with_custody_chain(
        self, client_logged, test_project_resource, mocker
    ):
        """Test que no se puede eliminar recurso con cadena de custodia"""
        # Mock para simular que existe cadena de custodia
        mocker.patch(
            'api.projects.DeleteResourceProject.ChainCustodyDetail.get_by_resource_id',
            return_value=True
        )
        
        url = f'/api/projects/resources/delete/{test_project_resource.id}/'
        response = client_logged.delete(url)
        
        assert response.status_code == 400
        assert 'cadena de custodia' in response.content.decode()
