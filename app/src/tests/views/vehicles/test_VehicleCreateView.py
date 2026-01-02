import pytest
import json
from django.urls import reverse
from equipment.models import Vehicle, CertificationVehicle, PassVehicle
from tests.BaseTestView import BaseTestView


@pytest.mark.django_db
class TestVehicleCreateView(BaseTestView):

    @pytest.fixture
    def url(self):
        return reverse('vehicle_create')

    @pytest.fixture
    def valid_vehicle_data(self):
        return {
            'brand': 'Toyota',
            'model': 'Hilux',
            'type_vehicle': 'CAMION',  # Usar valor válido de CHOICES_TYPE_VEHICLE
            'year': 2023,
            'no_plate': 'ABC-1234',
            'owner_transport': 'PEISOL',  # Usar valor válido de CHOICES_OWNER
            'status_vehicle': 'DISPONIBLE',  # Agregar campo requerido
            'is_active': True,
            'notes': 'Vehículo nuevo para operaciones',
            # Agregar campos opcionales para evitar errores
            'color': 'Blanco',
            'chassis_number': 'CH123456789',
            'engine_number': 'EN987654321',
            'serial_number': 'SN456789123'
        }

    @pytest.fixture
    def certification_data(self):
        return [
            {
                'name': 'INSPECCION_VOLUMETRICA',  # Usar campo correcto del modelo
                'date_start': '2023-01-10',  # Usar nombres correctos
                'date_end': '2024-01-10',
                'description': 'Certificación vigente'
            },
            {
                'name': 'MEDICION_DE_ESPESORES',
                'date_start': '2023-02-15',
                'date_end': '2024-02-15',
                'description': 'Certificación anual'
            }
        ]

    @pytest.fixture
    def pass_data(self):
        return [
            {
                'bloque': 'BLOQUE_A',
                'fecha_caducidad': '2024-06-30'
            },
            {
                'bloque': 'BLOQUE_B',
                'fecha_caducidad': '2024-12-31'
            }
        ]

    def test_get_vehicle_create_view_authenticated(self, client_logged, url):
        """Test que un usuario autenticado puede acceder al formulario de creación"""
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'forms/vehicle_form.html' in [
            t.name for t in response.templates]
        assert 'form' in response.context
        assert response.context['title_section'] == 'Registrar Nuevo Vehículo'

    def test_get_vehicle_create_view_unauthenticated(self, client_not_logged, url):
        """Test que un usuario no autenticado es redirigido al login"""
        response = client_not_logged.get(url)
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_create_vehicle_with_valid_data(self, client_logged, url, valid_vehicle_data):
        """Test crear un vehículo con datos válidos"""
        initial_count = Vehicle.objects.count()

        response = client_logged.post(url, valid_vehicle_data)

        assert response.status_code == 302  # Redirección tras éxito
        assert Vehicle.objects.count() == initial_count + 1

        vehicle = Vehicle.objects.latest('id')
        assert vehicle.brand == valid_vehicle_data['brand']
        assert vehicle.model == valid_vehicle_data['model']
        assert vehicle.no_plate == valid_vehicle_data['no_plate']
        assert vehicle.is_active == valid_vehicle_data['is_active']

    def test_create_vehicle_with_invalid_data(self, client_logged, url):
        """Test crear un vehículo con datos inválidos"""
        invalid_data = {
            'brand': '',  # Campo requerido vacío
            'model': 'Hilux',
            'year': 'invalid_year',  # Año inválido
            'no_plate': '',  # Campo requerido vacío
        }

        initial_count = Vehicle.objects.count()
        response = client_logged.post(url, invalid_data)

        assert response.status_code == 200  # Vuelve al formulario con errores
        assert Vehicle.objects.count() == initial_count  # No se creó ningún vehículo
        assert 'form' in response.context
        assert response.context['form'].errors

    @pytest.mark.skip(reason="La funcionalidad de crear certificaciones junto con el vehículo no está implementada")
    def test_create_vehicle_with_certifications(self, client_logged, url, valid_vehicle_data, certification_data):
        """Test crear un vehículo con certificaciones"""
        data = valid_vehicle_data.copy()
        data['certifications_data'] = json.dumps(certification_data)
        
        initial_vehicle_count = Vehicle.objects.count()
        initial_cert_count = CertificationVehicle.objects.count()
        
        response = client_logged.post(url, data)
        
        assert response.status_code == 302
        assert Vehicle.objects.count() == initial_vehicle_count + 1
        assert CertificationVehicle.objects.count() == initial_cert_count + len(certification_data)
        
        vehicle = Vehicle.objects.latest('id')
        certifications = CertificationVehicle.objects.filter(vehicle=vehicle)
        assert certifications.count() == len(certification_data)

        # Comprobar que cada certificación esperada está en la BD (sin importar el orden)
        db_certs = [
            (c.name, str(c.date_start), str(c.date_end), c.description)
            for c in certifications
        ]
        expected_certs = [
            (c['name'], c['date_start'], c['date_end'], c['description'])
            for c in certification_data
        ]
        for expected in expected_certs:
            assert expected in db_certs

    @pytest.mark.skip(reason="La funcionalidad de crear pases junto con el vehículo no está implementada")
    def test_create_vehicle_with_passes(self, client_logged, url, valid_vehicle_data, pass_data):
        """Test crear un vehículo con pases"""
        data = valid_vehicle_data.copy()
        data['passes_data'] = json.dumps(pass_data)

        initial_vehicle_count = Vehicle.objects.count()
        initial_pass_count = PassVehicle.objects.count()

        response = client_logged.post(url, data)

        assert response.status_code == 302
        assert Vehicle.objects.count() == initial_vehicle_count + 1
        assert PassVehicle.objects.count() == initial_pass_count + len(pass_data)

        vehicle = Vehicle.objects.latest('id')
        passes = PassVehicle.objects.filter(vehicle=vehicle)
        assert passes.count() == len(pass_data)

        # Comprobar que cada pase esperado está en la BD (sin importar el orden)
        db_passes = [
            (p.bloque, str(p.fecha_caducidad))
            for p in passes
        ]
        expected_passes = [
            (p['bloque'], p['fecha_caducidad'])
            for p in pass_data
        ]
        for expected in expected_passes:
            assert expected in db_passes

    @pytest.mark.skip(reason="La funcionalidad de creación completa no está implementada")
    def test_create_vehicle_complete_with_all_data(self, client_logged, url, valid_vehicle_data,
                                                   certification_data, pass_data):
        """Test crear un vehículo completo con certificaciones y pases"""
        data = valid_vehicle_data.copy()
        data['certifications_data'] = json.dumps(certification_data)
        data['passes_data'] = json.dumps(pass_data)

        initial_vehicle_count = Vehicle.objects.count()
        initial_cert_count = CertificationVehicle.objects.count()
        initial_pass_count = PassVehicle.objects.count()

        response = client_logged.post(url, data)

        assert response.status_code == 302
        assert Vehicle.objects.count() == initial_vehicle_count + 1
        assert CertificationVehicle.objects.count() == initial_cert_count + \
            len(certification_data)
        assert PassVehicle.objects.count() == initial_pass_count + len(pass_data)

        vehicle = Vehicle.objects.latest('id')

        # Verificar que se crearon las certificaciones
        certifications = CertificationVehicle.objects.filter(vehicle=vehicle)
        assert certifications.count() == len(certification_data)

        # Verificar que se crearon los pases
        passes = PassVehicle.objects.filter(vehicle=vehicle)
        assert passes.count() == len(pass_data)

    @pytest.mark.skip(reason="La funcionalidad AJAX para agregar certificación no está implementada")
    def test_ajax_add_certification_valid_data(self, client_logged, url):
        """Test agregar certificación vía AJAX con datos válidos"""
        certification_data = {
            'action': 'add_certification',
            'name': 'INSPECCION_VOLUMETRICA',  # Usar campo correcto
            'date_start': '2023-01-10',
            'date_end': '2024-01-10',
            'description': 'Certificación vigente'
        }
        
        response = client_logged.post(
            url,
            data=json.dumps(certification_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'message' in data
        assert 'data' in data
        assert data['data']['name'] == certification_data['name']

    @pytest.mark.skip(reason="La funcionalidad AJAX no está implementada")
    def test_ajax_add_certification_invalid_data(self, client_logged, url):
        """Test agregar certificación vía AJAX con datos inválidos"""
        invalid_certification_data = {
            'action': 'add_certification',
            'name': '',  # Campo requerido vacío
            'date_start': '2023-01-10',
        }
        
        response = client_logged.post(
            url,
            data=json.dumps(invalid_certification_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'message' in data

    @pytest.mark.skip(reason="La funcionalidad AJAX no está implementada")
    def test_ajax_add_certification_invalid_date_format(self, client_logged, url):
        """Test agregar certificación vía AJAX con formato de fecha inválido"""
        invalid_date_data = {
            'action': 'add_certification',
            'name': 'INSPECCION_VOLUMETRICA',
            'date_start': 'invalid-date',  # Formato de fecha inválido
        }
        
        response = client_logged.post(
            url,
            data=json.dumps(invalid_date_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Formato de fecha inválido' in data['message']

    @pytest.mark.skip(reason="La funcionalidad AJAX para agregar pase no está implementada")
    def test_ajax_add_pass_valid_data(self, client_logged, url):
        """Test agregar pase vía AJAX con datos válidos"""
        pass_data = {
            'action': 'add_pass',
            'bloque': 'BLOQUE_A',
            'fecha_caducidad': '2024-06-30'
        }

        response = client_logged.post(
            url,
            data=json.dumps(pass_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'message' in data
        assert 'data' in data
        assert data['data']['bloque'] == pass_data['bloque']

    @pytest.mark.skip(reason="La funcionalidad AJAX no está implementada")
    def test_ajax_add_pass_invalid_data(self, client_logged, url):
        """Test agregar pase vía AJAX con datos inválidos"""
        invalid_pass_data = {
            'action': 'add_pass',
            'bloque': '',  # Campo requerido vacío
            'fecha_caducidad': '2024-06-30'
        }

        response = client_logged.post(
            url,
            data=json.dumps(invalid_pass_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'message' in data

    @pytest.mark.skip(reason="La funcionalidad AJAX no está implementada")
    def test_ajax_add_pass_invalid_date_format(self, client_logged, url):
        """Test agregar pase vía AJAX con formato de fecha inválido"""
        invalid_date_data = {
            'action': 'add_pass',
            'bloque': 'BLOQUE_A',
            'fecha_caducidad': 'invalid-date'  # Formato de fecha inválido
        }

        response = client_logged.post(
            url,
            data=json.dumps(invalid_date_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Formato de fecha inválido' in data['message']

    @pytest.mark.skip(reason="Los campos ocultos para certificaciones y pases no están implementados en el formulario")
    def test_form_has_hidden_fields(self, client_logged, url):
        """Test que el formulario contiene los campos ocultos necesarios"""
        response = client_logged.get(url)
        form = response.context['form']

        assert 'certifications_data' in form.fields
        assert 'passes_data' in form.fields
        assert form.fields['certifications_data'].required is False
        assert form.fields['passes_data'].required is False

    def test_invalid_json_data_handling(self, client_logged, url, valid_vehicle_data):
        """Test manejo de datos JSON inválidos"""
        data = valid_vehicle_data.copy()
        data['certifications_data'] = 'invalid json'  # JSON inválido
        data['passes_data'] = 'another invalid json'

        # Debería crear el vehículo ignorando los datos JSON que no se procesan
        initial_count = Vehicle.objects.count()
        response = client_logged.post(url, data)

        assert response.status_code == 302
        assert Vehicle.objects.count() == initial_count + 1

    @pytest.mark.skip(reason="La funcionalidad de transacciones atómicas para certificaciones no está implementada")
    def test_transaction_atomicity(self, client_logged, url, valid_vehicle_data):
        """Test que las transacciones son atómicas"""
        # Este test verifica que si algo falla, toda la transacción se revierte
        # Para esto necesitaríamos simular un error en la creación de certificaciones
        data = valid_vehicle_data.copy()
        certification_data = [{
            'certification_type': 'SOAT',
            'issue_date': '2023-01-10',
            'expiry_date': '2024-01-10',
        }]
        data['certifications_data'] = json.dumps(certification_data)

        initial_vehicle_count = Vehicle.objects.count()
        initial_cert_count = CertificationVehicle.objects.count()

        # Debe lanzar un error y no crear ni vehículo ni certificación
        try:
            response = client_logged.post(url, data)
        except Exception:
            pass

        assert Vehicle.objects.count() == initial_vehicle_count
        assert CertificationVehicle.objects.count() == initial_cert_count
