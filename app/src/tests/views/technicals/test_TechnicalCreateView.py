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
