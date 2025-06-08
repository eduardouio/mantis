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

    def test_context_data_includes_existing_records(self, client_logged, url, 
                                                   vaccination_record, pass_technical):
        """Test que el contexto incluye vacunas y pases existentes"""
        response = client_logged.get(url)
        assert response.status_code == 200
        
        # Verificar que se incluyen las vacunas existentes
        assert 'existing_vaccinations' in response.context
        existing_vaccinations = response.context['existing_vaccinations']
        assert len(existing_vaccinations) == 1
        assert existing_vaccinations[0]['vaccine_type'] == 'COVID'
        
        # Verificar que se incluyen los pases existentes
        assert 'existing_passes' in response.context
        existing_passes = response.context['existing_passes']
        assert len(existing_passes) == 1
        assert existing_passes[0]['bloque'] == 'petroecuador'

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

    def test_update_technical_with_new_vaccinations(self, client_logged, url, 
                                                   technical, valid_update_data):
        """Test actualizar técnico agregando nuevas vacunas"""
        vaccination_data = [
            {
                'vaccine_type': 'TETANUS',
                'application_date': '2023-02-15',
                'dose_number': 1,
                'batch_number': 'TET-456',
                'notes': 'Primera dosis de tétanos'
            }
        ]
        
        valid_update_data['vaccinations_data'] = json.dumps(vaccination_data)
        response = client_logged.post(url, valid_update_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que la nueva vacuna fue creada
        vaccination_count = VaccinationRecord.objects.filter(
            technical=technical, 
            is_active=True
        ).count()
        assert vaccination_count == 1

        # Verificar los datos de la nueva vacuna
        new_vaccination = VaccinationRecord.objects.get(
            technical=technical,
            vaccine_type='TETANUS'
        )
        assert new_vaccination.dose_number == 1
        assert new_vaccination.batch_number == 'TET-456'

    def test_update_technical_with_new_passes(self, client_logged, url, 
                                            technical, valid_update_data):
        """Test actualizar técnico agregando nuevos pases"""
        passes_data = [
            {
                'bloque': 'shaya',
                'fecha_caducidad': '2024-06-30'
            }
        ]
        
        valid_update_data['passes_data'] = json.dumps(passes_data)
        response = client_logged.post(url, valid_update_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que el nuevo pase fue creado
        pass_count = PassTechnical.objects.filter(technical=technical).count()
        assert pass_count == 1

        # Verificar los datos del nuevo pase
        new_pass = PassTechnical.objects.get(
            technical=technical,
            bloque='shaya'
        )
        assert str(new_pass.fecha_caducidad) == '2024-06-30'

    def test_update_existing_vaccination(self, client_logged, url, technical, 
                                       vaccination_record, valid_update_data):
        """Test actualizar una vacuna existente"""
        vaccination_data = [
            {
                'id': vaccination_record.id,
                'vaccine_type': 'COVID',
                'application_date': '2023-01-10',
                'dose_number': 3,  # Cambiar número de dosis
                'batch_number': 'COVID-789',  # Cambiar lote
                'next_dose_date': '2024-01-10',
                'notes': 'Tercera dosis COVID-19'
            }
        ]
        
        valid_update_data['vaccinations_data'] = json.dumps(vaccination_data)
        response = client_logged.post(url, valid_update_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que la vacuna fue actualizada
        vaccination_record.refresh_from_db()
        assert vaccination_record.dose_number == 3
        assert vaccination_record.batch_number == 'COVID-789'
        assert vaccination_record.notes == 'Tercera dosis COVID-19'

    def test_update_existing_pass(self, client_logged, url, technical, 
                                pass_technical, valid_update_data):
        """Test actualizar un pase existente"""
        passes_data = [
            {
                'id': pass_technical.id,
                'bloque': 'andes_petroleum',  # Cambiar bloque
                'fecha_caducidad': '2025-12-31'  # Cambiar fecha
            }
        ]
        
        valid_update_data['passes_data'] = json.dumps(passes_data)
        response = client_logged.post(url, valid_update_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que el pase fue actualizado
        pass_technical.refresh_from_db()
        assert pass_technical.bloque == 'andes_petroleum'
        assert str(pass_technical.fecha_caducidad) == '2025-12-31'

    def test_remove_vaccination_from_update(self, client_logged, url, technical, 
                                          vaccination_record, valid_update_data):
        """Test eliminar una vacuna durante la actualización"""
        # No incluir la vacuna existente en los datos de actualización
        valid_update_data['vaccinations_data'] = json.dumps([])
        response = client_logged.post(url, valid_update_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que la vacuna fue marcada como inactiva
        vaccination_record.refresh_from_db()
        assert vaccination_record.is_active == False

    def test_remove_pass_from_update(self, client_logged, url, technical, 
                                   pass_technical, valid_update_data):
        """Test eliminar un pase durante la actualización"""
        # No incluir el pase existente en los datos de actualización
        valid_update_data['passes_data'] = json.dumps([])
        response = client_logged.post(url, valid_update_data)

        # Verificar redirección exitosa
        assert response.status_code == 302

        # Verificar que el pase fue eliminado
        assert not PassTechnical.objects.filter(id=pass_technical.id).exists()

    def test_ajax_add_vaccination(self, client_logged, url, technical):
        """Test agregar vacuna vía AJAX"""
        data = {
            'action': 'add_vaccination',
            'vaccine_type': 'TETANUS',
            'application_date': '2023-02-15',
            'dose_number': 1,
            'batch_number': 'TET-456',
            'notes': 'Primera dosis de tétanos'
        }
        
        response = client_logged.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] == True
        assert 'Vacunación agregada correctamente' in response_data['message']

    def test_ajax_add_pass(self, client_logged, url, technical):
        """Test agregar pase vía AJAX"""
        data = {
            'action': 'add_pass',
            'bloque': 'shaya',
            'fecha_caducidad': '2024-06-30'
        }
        
        response = client_logged.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] == True
        assert 'Pase agregado correctamente' in response_data['message']

    def test_ajax_delete_vaccination(self, client_logged, url, vaccination_record):
        """Test eliminar vacuna vía AJAX"""
        data = {
            'action': 'delete_vaccination',
            'vaccination_id': vaccination_record.id
        }
        
        response = client_logged.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] == True
        assert 'Vacunación eliminada correctamente' in response_data['message']
        
        # Verificar que la vacuna fue marcada como inactiva
        vaccination_record.refresh_from_db()
        assert vaccination_record.is_active == False

    def test_ajax_delete_pass(self, client_logged, url, pass_technical):
        """Test eliminar pase vía AJAX"""
        data = {
            'action': 'delete_pass',
            'pass_id': pass_technical.id
        }
        
        response = client_logged.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] == True
        assert 'Pase eliminado correctamente' in response_data['message']
        
        # Verificar que el pase fue eliminado
        assert not PassTechnical.objects.filter(id=pass_technical.id).exists()

    def test_ajax_validation_errors_vaccination(self, client_logged, url, technical):
        """Test errores de validación en AJAX para vacunas"""
        data = {
            'action': 'add_vaccination',
            # Faltan campos requeridos
            'dose_number': 1
        }
        
        response = client_logged.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] == False
        assert 'requeridos' in response_data['message']

    def test_ajax_validation_errors_pass(self, client_logged, url, technical):
        """Test errores de validación en AJAX para pases"""
        data = {
            'action': 'add_pass',
            # Faltan campos requeridos
            'bloque': 'shaya'
        }
        
        response = client_logged.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] == False
        assert 'requeridos' in response_data['message']

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