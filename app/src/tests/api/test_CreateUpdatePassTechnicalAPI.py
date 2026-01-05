import pytest
import json
from django.test import Client
from datetime import date, timedelta

from accounts.models import CustomUserModel
from accounts.models import Technical
from accounts.models.PassTechnical import PassTechnical


@pytest.mark.django_db
class TestCreateUpdatePassTechnicalAPI:
	"""Tests para CreateUpdatePassTechnicalAPI"""

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
			first_name='John',
			last_name='Doe',
			dni='1234567890',
			nro_phone='0999999999'
		)

	@pytest.fixture
	def valid_data(self, technical):
		return {
			'technical_id': technical.id,
			'bloque': 'petroecuador',
			'fecha_caducidad': (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')
		}

	def endpoint(self):
		return '/api/technicals/create_update_pass_technical/'

	def test_create_success(self, client_logged, valid_data):
		resp = client_logged.post(self.endpoint(), data=json.dumps(valid_data), content_type='application/json')
		assert resp.status_code == 200
		data = json.loads(resp.content)
		assert data['success'] is True
		assert 'Pase creado' in data['message']
		assert data['data']['bloque'] == 'petroecuador'
		assert PassTechnical.objects.filter(id=data['data']['id'], is_active=True).exists()

	def test_create_missing_fields(self, client_logged):
		payload = {'bloque': 'petroecuador'}
		resp = client_logged.post(self.endpoint(), data=json.dumps(payload), content_type='application/json')
		assert resp.status_code == 400
		data = json.loads(resp.content)
		assert data['success'] is False
		assert 'Campo' in data['error']

	def test_create_invalid_technical(self, client_logged, valid_data):
		valid_data['technical_id'] = 999999
		resp = client_logged.post(self.endpoint(), data=json.dumps(valid_data), content_type='application/json')
		assert resp.status_code == 500

	def test_create_invalid_date_format(self, client_logged, valid_data):
		valid_data['fecha_caducidad'] = '2024-13-45'
		resp = client_logged.post(self.endpoint(), data=json.dumps(valid_data), content_type='application/json')
		assert resp.status_code == 400
		data = json.loads(resp.content)
		assert 'fecha_cad formato' in data['error']

	def test_create_invalid_bloque(self, client_logged, valid_data):
		valid_data['bloque'] = 'bloque_invalido'
		resp = client_logged.post(self.endpoint(), data=json.dumps(valid_data), content_type='application/json')
		assert resp.status_code == 400
		data = json.loads(resp.content)
		assert 'bloque invalido' in data['error']

	def test_update_success(self, client_logged, technical):
		registro = PassTechnical.objects.create(
			technical=technical,
			bloque='petroecuador',
			fecha_caducidad=date.today() + timedelta(days=365)
		)
		payload = {
			'id': registro.id,
			'technical_id': technical.id,
			'bloque': 'shaya',
			'fecha_caducidad': (date.today() + timedelta(days=400)).strftime('%Y-%m-%d')
		}
		resp = client_logged.put(
			self.endpoint(),
			data=json.dumps(payload),
			content_type='application/json'
		)
		assert resp.status_code == 200
		data = json.loads(resp.content)
		assert data['success'] is True
		assert 'Pase actualizado' in data['message']
		registro.refresh_from_db()
		assert registro.bloque == 'shaya'

	def test_update_missing_id(self, client_logged, valid_data):
		resp = client_logged.put(
			self.endpoint(),
			data=json.dumps(valid_data),
			content_type='application/json'
		)
		assert resp.status_code == 400
		data = json.loads(resp.content)
		assert 'ID requerido' in data['error']

	def test_get_by_id(self, client_logged, technical):
		registro = PassTechnical.objects.create(
			technical=technical,
			bloque='petroecuador',
			fecha_caducidad=date.today() + timedelta(days=365)
		)
		url = f"{self.endpoint()}?id={registro.id}"
		resp = client_logged.get(url)
		assert resp.status_code == 200
		data = json.loads(resp.content)
		assert data['success'] is True
		assert data['data']['id'] == registro.id
		assert data['data']['bloque'] == 'petroecuador'

	def test_get_by_technical(self, client_logged, technical):
		PassTechnical.objects.create(
			technical=technical,
			bloque='petroecuador',
			fecha_caducidad=date.today() + timedelta(days=365)
		)
		PassTechnical.objects.create(
			technical=technical,
			bloque='shaya',
			fecha_caducidad=date.today() + timedelta(days=365)
		)
		url = f"{self.endpoint()}?technical_id={technical.id}"
		resp = client_logged.get(url)
		assert resp.status_code == 200
		data = json.loads(resp.content)
		assert data['success'] is True
		assert len(data['data']) == 2
		bloques = {r['bloque'] for r in data['data']}
		assert {'petroecuador', 'shaya'} <= bloques

	def test_get_all(self, client_logged, technical):
		PassTechnical.objects.create(
			technical=technical,
			bloque='petroecuador',
			fecha_caducidad=date.today() + timedelta(days=365)
		)
		resp = client_logged.get(self.endpoint())
		assert resp.status_code == 200
		data = json.loads(resp.content)
		assert data['success'] is True
		assert len(data['data']) >= 1

	def test_invalid_json(self, client_logged):
		resp = client_logged.post(
			self.endpoint(),
			data='invalid json',
			content_type='application/json'
		)
		assert resp.status_code == 400
		data = json.loads(resp.content)
		assert 'JSON invalido' in data['error']

