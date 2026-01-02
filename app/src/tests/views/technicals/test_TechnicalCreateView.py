import pytest
import json
from django.urls import reverse
from django.test import Client
from accounts.models import Technical, VaccinationRecord, PassTechnical
from tests.BaseTestView import BaseTestView


@pytest.mark.django_db
class TestTechnicalCreateView(BaseTestView):

    @pytest.fixture
    def url(self):
        return reverse('technical_create')

    @pytest.fixture
    def valid_technical_data(self):
        return {
            'first_name': 'Juan',
            'last_name': 'Pérez García',
            'email': 'juan.perez@example.com',
            'dni': '1234567890',
            'nro_phone': '0987654321',
            'work_area': 'ASSISTANT',
            'date_joined': '2023-01-15',
            'birth_date': '1990-05-20',
            'license_issue_date': '2022-01-01',
            'license_expiry_date': '2024-01-01',
            'is_iess_affiliated': True,
            'has_life_insurance_policy': False,
            'notes': 'Técnico nuevo con experiencia previa',
            'is_active': True
        }

    @pytest.fixture
    def vaccination_data(self):
        return [
            {
                'vaccine_type': 'COVID',
                'application_date': '2023-01-10',
                'dose_number': 2,
                'batch_number': 'COVID-123',
                'next_dose_date': '2023-07-10',
                'notes': 'Segunda dosis COVID-19'
            },
            {
                'vaccine_type': 'TETANUS',
                'application_date': '2023-02-15',
                'dose_number': 1,
                'batch_number': 'TET-456',
                'notes': 'Primera dosis de tétanos'
            }
        ]

    @pytest.fixture
    def passes_data(self):
        return [
            {
                'bloque': 'petroecuador',
                'fecha_caducidad': '2024-12-31'
            },
            {
                'bloque': 'shaya',
                'fecha_caducidad': '2024-06-30'
            }
        ]

    def test_get_create_view_success(self, client_logged, url):
        """Test que la vista GET funciona correctamente para usuarios autenticados"""
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'forms/technical_form.html' in [
            t.name for t in response.templates]
        assert 'title_section' in response.context
        assert response.context['title_section'] == 'Registrar Nuevo Técnico'

    def test_create_technical_basic_data(self, client_logged, url, valid_technical_data):
        """Test crear técnico con datos básicos solamente"""
        response = client_logged.post(url, valid_technical_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que el técnico fue creado
        technical = Technical.objects.filter(
            dni=valid_technical_data['dni']).first()
        assert technical is not None
        assert technical.first_name == valid_technical_data['first_name']
        assert technical.last_name == valid_technical_data['last_name']
        assert technical.email == valid_technical_data['email']
        assert technical.is_active == True

    @pytest.mark.skip(reason="La funcionalidad de creación de vacunas junto con el técnico no está implementada")
    def test_create_technical_with_vaccinations(self, client_logged, url, valid_technical_data, vaccination_data):
        """Test crear técnico con datos de vacunación"""
        # Agregar datos de vacunación al formulario
        form_data = valid_technical_data.copy()
        form_data['vaccinations_data'] = json.dumps(vaccination_data)

        response = client_logged.post(url, form_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que el técnico fue creado
        technical = Technical.objects.filter(
            dni=valid_technical_data['dni']).first()
        assert technical is not None

        # Verificar que las vacunas fueron creadas
        vaccinations = VaccinationRecord.objects.filter(technical=technical)
        assert vaccinations.count() == 2

        # Verificar datos específicos de vacunación
        covid_vaccine = vaccinations.filter(vaccine_type='COVID').first()
        assert covid_vaccine is not None
        assert covid_vaccine.dose_number == 2
        assert covid_vaccine.batch_number == 'COVID-123'

    @pytest.mark.skip(reason="La funcionalidad de creación de pases junto con el técnico no está implementada")
    def test_create_technical_with_passes(self, client_logged, url, valid_technical_data, passes_data):
        """Test crear técnico con pases"""
        # Agregar datos de pases al formulario
        form_data = valid_technical_data.copy()
        form_data['passes_data'] = json.dumps(passes_data)

        response = client_logged.post(url, form_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que el técnico fue creado
        technical = Technical.objects.filter(
            dni=valid_technical_data['dni']).first()
        assert technical is not None

        # Verificar que los pases fueron creados
        passes = PassTechnical.objects.filter(technical=technical)
        assert passes.count() == 2

        # Verificar datos específicos de pases
        petroecuador_pass = passes.filter(bloque='petroecuador').first()
        assert petroecuador_pass is not None

    @pytest.mark.skip(reason="La funcionalidad de creación completa no está implementada")
    def test_create_technical_complete_data(self, client_logged, url, valid_technical_data, vaccination_data, passes_data):
        """Test crear técnico con todos los datos (básicos, vacunas y pases)"""
        # Combinar todos los datos
        form_data = valid_technical_data.copy()
        form_data['vaccinations_data'] = json.dumps(vaccination_data)
        form_data['passes_data'] = json.dumps(passes_data)

        response = client_logged.post(url, form_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que el técnico fue creado
        technical = Technical.objects.filter(
            dni=valid_technical_data['dni']).first()
        assert technical is not None

        # Verificar que las vacunas fueron creadas
        assert VaccinationRecord.objects.filter(
            technical=technical).count() == 2

        # Verificar que los pases fueron creados
        assert PassTechnical.objects.filter(technical=technical).count() == 2

    def test_form_validation_required_fields(self, client_logged, url):
        """Test validación de campos requeridos"""
        # Enviar formulario con datos incompletos
        incomplete_data = {
            'first_name': 'Juan',
            # Faltan campos requeridos: last_name, dni, nro_phone
            'email': 'juan@example.com'
        }

        response = client_logged.post(url, incomplete_data)

        # Debe retornar el formulario con errores, no redireccionar
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_dni_validation(self, client_logged, url, valid_technical_data):
        """Test validación de cédula"""
        # Test con cédula inválida (menos de 10 dígitos)
        invalid_data = valid_technical_data.copy()
        invalid_data['dni'] = '12345'

        response = client_logged.post(url, invalid_data)
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'dni' in response.context['form'].errors

    def test_phone_validation(self, client_logged, url, valid_technical_data):
        """Test validación de número de teléfono"""
        # Test con teléfono inválido
        invalid_data = valid_technical_data.copy()
        invalid_data['nro_phone'] = '123'

        response = client_logged.post(url, invalid_data)
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'nro_phone' in response.context['form'].errors

    @pytest.mark.skip(reason="La funcionalidad AJAX para agregar vacunación no está implementada")
    def test_ajax_add_vaccination(self, client_logged, url):
        """Test agregar vacunación vía AJAX"""
        vaccination_data = {
            'action': 'add_vaccination',
            'vaccine_type': 'COVID',
            'application_date': '2023-01-10',
            'dose_number': 1,
            'batch_number': 'COVID-123',
            'notes': 'Primera dosis'
        }

        response = client_logged.post(
            url,
            json.dumps(vaccination_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] == True
        assert 'message' in response_data

    @pytest.mark.skip(reason="La funcionalidad AJAX para agregar pase no está implementada")
    def test_ajax_add_pass(self, client_logged, url):
        """Test agregar pase vía AJAX"""
        pass_data = {
            'action': 'add_pass',
            'bloque': 'petroecuador',
            'fecha_caducidad': '2024-12-31'
        }

        response = client_logged.post(
            url,
            json.dumps(pass_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] == True
        assert 'message' in response_data

    @pytest.mark.skip(reason="La funcionalidad AJAX no está implementada")
    def test_ajax_validation_errors(self, client_logged, url):
        """Test validación de errores en requests AJAX"""
        # Test vacunación sin datos requeridos
        invalid_vaccination = {
            'action': 'add_vaccination',
            'vaccine_type': '',  # Campo requerido vacío
            'application_date': '2023-01-10'
        }

        response = client_logged.post(
            url,
            json.dumps(invalid_vaccination),
            content_type='application/json'
        )

        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] == False
        assert 'message' in response_data

    def test_redirect_url_after_creation(self, client_logged, url, valid_technical_data):
        """Test que la URL de redirección incluye el parámetro action=created"""
        response = client_logged.post(url, valid_technical_data)

        assert response.status_code == 302

        # Verificar que la redirección incluye el parámetro correcto
        technical = Technical.objects.filter(
            dni=valid_technical_data['dni']).first()
        expected_url = f'/tecnicos/{technical.pk}/?action=created'
        assert expected_url in response.url

    def test_context_data(self, client_logged, url):
        """Test que el contexto contiene los datos correctos"""
        response = client_logged.get(url)

        assert response.status_code == 200
        assert response.context['title_section'] == 'Registrar Nuevo Técnico'
        assert response.context['title_page'] == 'Registrar Nuevo Técnico'
