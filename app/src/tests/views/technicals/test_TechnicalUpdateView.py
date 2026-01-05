import pytest
import json
from django.urls import reverse
from django.test import Client
from accounts.models import Technical, VaccinationRecord, PassTechnical
from tests.BaseTestView import BaseTestView


@pytest.mark.django_db
class TestTechnicalUpdateView(BaseTestView):

    @pytest.fixture
    def technical(self):
        """Crear un técnico de prueba"""
        return Technical.objects.create(
            first_name='Juan',
            last_name='Pérez García',
            email='juan.perez@example.com',
            dni='1234567890',
            nro_phone='0987654321',
            work_area='ASSISTANT',
            date_joined='2023-01-15',
            birth_date='1990-05-20',
            license_issue_date='2022-01-01',
            license_expiry_date='2024-01-01',
            is_iess_affiliated=True,
            has_life_insurance_policy=False,
            notes='Técnico de prueba',
            is_active=True
        )

    @pytest.fixture
    def vaccination_record(self, technical):
        """Crear un registro de vacunación de prueba"""
        return VaccinationRecord.objects.create(
            technical=technical,
            vaccine_type='COVID',
            application_date='2023-01-10',
            dose_number=2,
            batch_number='COVID-123',
            next_dose_date='2023-07-10',
            notes='Segunda dosis COVID-19',
            is_active=True
        )

    @pytest.fixture
    def pass_technical(self, technical):
        """Crear un pase técnico de prueba"""
        return PassTechnical.objects.create(
            technical=technical,
            bloque='petroecuador',
            fecha_caducidad='2024-12-31'
        )

    @pytest.fixture
    def url(self, technical):
        return reverse('technical_update', kwargs={'pk': technical.pk})

    @pytest.fixture
    def valid_update_data(self):
        return {
            'first_name': 'Juan Carlos',
            'last_name': 'Pérez García',
            'email': 'juan.carlos@example.com',
            'dni': '1234567890',
            'nro_phone': '0987654321',
            'work_area': 'SUPERVISOR',
            'date_joined': '2023-01-15',
            'birth_date': '1990-05-20',
            'license_issue_date': '2022-01-01',
            'license_expiry_date': '2024-01-01',
            'is_iess_affiliated': True,
            'has_life_insurance_policy': True,
            'notes': 'Técnico actualizado',
            'is_active': True
        }

    def test_get_update_view_success(self, client_logged, url, technical):
        """Test que la vista GET funciona correctamente para usuarios autenticados"""
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'forms/technical_form.html' in [
            t.name for t in response.templates]
        assert 'title_section' in response.context
        assert f'Actualizar Técnico {technical.first_name}' in response.context['title_section']

    def test_update_technical_basic_data(self, client_logged, url, technical, valid_update_data):
        """Test actualizar técnico con datos básicos solamente"""
        response = client_logged.post(url, valid_update_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que el técnico fue actualizado
        technical.refresh_from_db()
        assert technical.first_name == 'Juan Carlos'
        assert technical.work_area == 'SUPERVISOR'
        assert technical.has_life_insurance_policy == True
        assert technical.notes == 'Técnico actualizado'

    def test_redirect_url_after_update(self, client_logged, url, technical, valid_update_data):
        """Test que la redirección después de la actualización es correcta"""
        response = client_logged.post(url, valid_update_data)
        
        assert response.status_code == 302
        expected_url = f'/tecnicos/{technical.pk}/?action=updated'
        assert expected_url in response.url

    def test_update_with_invalid_data(self, client_logged, url, technical):
        """Test actualización con datos inválidos"""
        invalid_data = {
            'first_name': '',  # Campo requerido vacío
            'dni': '123',  # DNI muy corto
            'nro_phone': 'abc',  # Teléfono inválido
        }
        
        response = client_logged.post(url, invalid_data)
        
        # Debe permanecer en la página de formulario
        assert response.status_code == 200
        assert 'forms/technical_form.html' in [
            t.name for t in response.templates]

    def test_update_nonexistent_technical_404(self, client_logged):
        """Test que actualizar un técnico inexistente devuelve 404"""
        url = reverse('technical_update', kwargs={'pk': 99999})
        response = client_logged.get(url)
        assert response.status_code == 404

    def test_unauthorized_access_redirects(self, client):
        """Test que usuarios no autenticados son redirigidos"""
        technical = Technical.objects.create(
            first_name='Test',
            last_name='User',
            dni='1111111111',
            nro_phone='0999999999'
        )
        url = reverse('technical_update', kwargs={'pk': technical.pk})
        response = client.get(url)
        assert response.status_code == 302  # Redirección al login