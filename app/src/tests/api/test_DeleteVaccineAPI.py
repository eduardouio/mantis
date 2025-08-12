import pytest
import json
from django.test import Client
from datetime import date

from accounts.models import CustomUserModel
from accounts.models import Technical
from accounts.models.VaccinationRecord import VaccinationRecord


@pytest.mark.django_db
class TestDeleteVaccineAPI:
    """Tests para DeleteVaccineAPI"""

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
    def technical(self):
        return Technical.objects.create(
            first_name='Luis',
            last_name='Gomez',
            dni='5566778899',
            nro_phone='0666666666'
        )

    @pytest.fixture
    def record(self, technical):
        return VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            application_date=date.today()
        )

    def endpoint(self):
        return '/api/technicals/delete_vaccine/'

    def test_delete_success(self, client_logged, record):
        payload = {'id': record.id}
        resp = client_logged.delete(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data['success'] is True
        record.refresh_from_db()
        assert record.is_active is False

    def test_delete_missing_id(self, client_logged):
        resp = client_logged.delete(
            self.endpoint(),
            data=json.dumps({}),
            content_type='application/json'
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert 'ID requerido' in data['error']

    def test_delete_not_found(self, client_logged):
        payload = {'id': 999999}
        resp = client_logged.delete(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 404

    def test_delete_already_deleted(self, client_logged, record):
        record.is_active = False
        record.save()
        payload = {'id': record.id}
        resp = client_logged.delete(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 404

    def test_delete_multiple_success(self, client_logged, technical):
        r1 = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            application_date=date.today()
        )
        r2 = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='TETANUS',
            application_date=date.today()
        )
        payload = {'ids': [r1.id, r2.id]}
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data['success'] is True
        r1.refresh_from_db()
        r2.refresh_from_db()
        assert r1.is_active is False and r2.is_active is False

    def test_delete_multiple_missing_ids(self, client_logged):
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps({}),
            content_type='application/json'
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert 'ids lista requerida' in data['error']

    def test_delete_multiple_invalid_ids(self, client_logged):
        payload = {'ids': 'no_lista'}
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert 'ids lista requerida' in data['error']

    def test_delete_multiple_mixed(self, client_logged, technical):
        r1 = VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            application_date=date.today()
        )
        payload = {'ids': [r1.id, 999999]}
        resp = client_logged.post(
            self.endpoint(),
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data['success'] is True
        r1.refresh_from_db()
        assert r1.is_active is False
        assert len(data['data']['errors']) == 1

    def test_invalid_json(self, client_logged):
        resp = client_logged.delete(
            self.endpoint(),
            data='invalid json',
            content_type='application/json'
        )
        assert resp.status_code == 400
        data = json.loads(resp.content)
        assert 'JSON invalido' in data['error']
