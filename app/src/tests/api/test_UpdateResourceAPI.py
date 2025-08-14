import pytest
import json
from django.test import Client
from datetime import date

from accounts.models import CustomUserModel
from equipment.models import ResourceItem


@pytest.mark.django_db
class TestUpdateResourceAPI:
    """Tests para el endpoint POST de actualización de ResourceItem."""

    @pytest.fixture
    def client_logged(self):
        user, _ = CustomUserModel.objects.get_or_create(
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
    def resource_item(self):
        # Crear un equipo mínimo
        return ResourceItem.objects.create(
            name='Lavamanos 1',
            type_equipment='LVMNOS'
        )

    def endpoint(self):
        return '/api/resources/update/'

    def test_update_success_basic_fields(self, client_logged, resource_item):
        payload = {
            'id': resource_item.id,
            'name': 'Lavamanos X',
            'stst_status_equipment': 'EN REPARACION',
            'date_purchase': date.today().strftime('%Y-%m-%d'),
            'have_soap_dispenser': True,
        }
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data['success'] is True
        assert data['message'] == 'Equipo actualizado correctamente'
        assert data['data']['id'] == resource_item.id
        assert data['data']['name'] == 'Lavamanos X'

        # Verificar en base de datos
        resource_item.refresh_from_db()
        assert resource_item.name == 'Lavamanos X'
        assert resource_item.stst_status_equipment == 'EN REPARACION'
        assert resource_item.have_soap_dispenser is True

    def test_update_missing_id(self, client_logged, resource_item):
        payload = {
            'name': 'Nuevo Nombre'
        }
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert data['success'] is False
        assert 'id es requerido' in data['error']

    def test_invalid_json(self, client_logged):
        resp = client_logged.post(
            self.endpoint(),
            data='{"id": ',  # JSON truncado/incorrecto
            content_type='application/json'
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert 'JSON inválido' in data['error']

    def test_invalid_date_format(self, client_logged, resource_item):
        payload = {
            'id': resource_item.id,
            'date_purchase': '2024-13-45',  # fecha inválida
        }
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert data['success'] is False
        assert 'field_errors' in data
        assert 'date_purchase' in data['field_errors']

    def test_nonexistent_id(self, client_logged):
        payload = {
            'id': 999999,
            'name': 'No Existe'
        }
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        # get_object_or_404 -> 404
        assert resp.status_code == 404

    def test_ignored_unknown_fields(self, client_logged, resource_item):
        payload = {
            'id': resource_item.id,
            'name': 'Nombre Válido',
            'campo_que_no_existe': 'valor',
        }
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data['success'] is True
        assert data.get('ignored_fields') is not None
        assert 'campo_que_no_existe' in data['ignored_fields']
