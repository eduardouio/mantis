import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from projects.models import Partner
from tests.BaseTestView import BaseTestView


@pytest.mark.django_db
class TestPartnerCreateView(BaseTestView):

    @pytest.fixture
    def url(self):
        return reverse('partner_create')

    @pytest.fixture
    def valid_partner_data(self):
        return {
            'business_tax_id': '1234567890001',
            'name': 'Empresa Test S.A.',
            'email': 'contacto@empresatest.com',
            'phone': '0999123456',
            'address': 'Av. Principal 123, Quito',
            'name_contact': 'Juan Pérez',
            'notes': 'Notas de prueba para el socio',
            'is_active': True
        }

    @pytest.fixture
    def invalid_partner_data(self):
        return {
            'business_tax_id': '',  # Campo requerido vacío
            'name': '',  # Campo requerido vacío
            'email': 'email-invalido',  # Email con formato inválido
            'phone': '0999123456',
            'address': '',  # Campo requerido vacío
            'name_contact': 'Juan Pérez',
            'notes': 'Notas de prueba',
            'is_active': True
        }

    def test_get_partner_create_view_logged(self, client_logged, url):
        """Test que un usuario logueado puede acceder a la vista de crear socio"""
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'forms/partner_form.html' in [
            t.name for t in response.templates]
        assert 'form' in response.context
        assert response.context['title_section'] == 'Registrar Nuevo Socio de Negocio'
        assert response.context['title_page'] == 'Registrar Nuevo Socio de Negocio'

    def test_get_partner_create_view_not_logged(self, client_not_logged, url):
        """Test que un usuario no logueado es redirigido al login"""
        response = client_not_logged.get(url)
        expected_url = reverse('login') + '?next=' + url
        assert response.status_code == 302
        assert response.url == expected_url

    def test_post_partner_create_valid_data(self, client_logged, url, valid_partner_data):
        """Test de creación exitosa de socio con datos válidos"""
        # Verificar que no existe el socio antes
        assert not Partner.objects.filter(
            business_tax_id=valid_partner_data['business_tax_id']).exists()

        response = client_logged.post(url, valid_partner_data)

        # Verificar que se creó el socio
        partner = Partner.objects.get(
            business_tax_id=valid_partner_data['business_tax_id'])
        assert partner.name == valid_partner_data['name']
        assert partner.email == valid_partner_data['email']
        assert partner.phone == valid_partner_data['phone']
        assert partner.address == valid_partner_data['address']
        assert partner.name_contact == valid_partner_data['name_contact']
        assert partner.notes == valid_partner_data['notes']
        assert partner.is_active == valid_partner_data['is_active']

        # Verificar redirección a la página de detalle
        expected_url = reverse('partner_detail', kwargs={
                               'pk': partner.pk}) + '?action=created'
        assert response.status_code == 302
        assert response.url == expected_url

    def test_post_partner_create_invalid_data(self, client_logged, url, invalid_partner_data):
        """Test de creación fallida con datos inválidos"""
        partners_count_before = Partner.objects.count()

        response = client_logged.post(url, invalid_partner_data)

        # Verificar que no se creó ningún socio
        assert Partner.objects.count() == partners_count_before

        # Verificar que se muestra el formulario con errores
        assert response.status_code == 200
        assert 'form' in response.context
        form = response.context['form']
        assert form.errors
        assert 'business_tax_id' in form.errors
        assert 'name' in form.errors
        assert 'address' in form.errors

    def test_post_partner_create_duplicate_business_tax_id(self, client_logged, url, valid_partner_data):
        """Test que no permite crear socio con RUC duplicado"""
        # Crear un socio primero
        Partner.objects.create(**valid_partner_data)

        # Intentar crear otro con el mismo RUC
        response = client_logged.post(url, valid_partner_data)

        # Verificar que solo existe un socio con ese RUC
        assert Partner.objects.filter(
            business_tax_id=valid_partner_data['business_tax_id']).count() == 1

        # Verificar que se muestra error de validación
        assert response.status_code == 200
        assert 'form' in response.context
        form = response.context['form']
        assert form.errors
        assert 'business_tax_id' in form.errors

    def test_partner_create_with_minimal_data(self, client_logged, url):
        """Test de creación con datos mínimos requeridos"""
        minimal_data = {
            'business_tax_id': '9876543210001',
            'name': 'Empresa Mínima',
            'address': 'Dirección mínima',
            'is_active': True
        }

        response = client_logged.post(url, minimal_data)

        # Verificar que se creó el socio
        partner = Partner.objects.get(
            business_tax_id=minimal_data['business_tax_id'])
        assert partner.name == minimal_data['name']
        assert partner.address == minimal_data['address']
        assert partner.is_active == minimal_data['is_active']
        assert partner.email is None or partner.email == ''
        assert partner.phone is None or partner.phone == ''
        assert partner.name_contact is None or partner.name_contact == ''

        # Verificar redirección exitosa
        assert response.status_code == 302

    def test_partner_create_default_is_active_true(self, client_logged, url):
        """Test que el campo is_active tiene valor por defecto True"""
        response = client_logged.get(url)
        form = response.context['form']
        assert form.fields['is_active'].initial is True

    def test_partner_create_form_fields_present(self, client_logged, url):
        """Test que todos los campos esperados están presentes en el formulario"""
        response = client_logged.get(url)
        form = response.context['form']

        expected_fields = [
            'business_tax_id', 'name', 'email', 'phone',
            'address', 'name_contact', 'notes', 'is_active'
        ]

        for field in expected_fields:
            assert field in form.fields

    def test_partner_create_required_fields(self, client_logged, url):
        """Test que los campos requeridos están correctamente configurados"""
        response = client_logged.get(url)
        form = response.context['form']

        # Campos que deben ser requeridos
        required_fields = ['business_tax_id', 'name', 'address']

        for field in required_fields:
            assert form.fields[field].required is True

        # Campos que no deben ser requeridos
        optional_fields = ['email', 'phone', 'name_contact', 'notes']

        for field in optional_fields:
            assert form.fields[field].required is False

    def test_partner_create_form_widgets_classes(self, client_logged, url):
        """Test que los widgets tienen las clases CSS correctas"""
        response = client_logged.get(url)
        form = response.context['form']

        # Verificar clases de widgets de texto
        text_fields = ['business_tax_id', 'name',
                       'phone', 'address', 'name_contact']
        for field in text_fields:
            widget_attrs = form.fields[field].widget.attrs
            assert 'input input-bordered w-full' in widget_attrs.get(
                'class', '')

        # Verificar widget de email
        email_widget_attrs = form.fields['email'].widget.attrs
        assert 'input input-bordered w-full' in email_widget_attrs.get(
            'class', '')

        # Verificar widget de textarea
        notes_widget_attrs = form.fields['notes'].widget.attrs
        assert 'textarea textarea-bordered w-full min-h-20' in notes_widget_attrs.get(
            'class', '')

        # Verificar widget de checkbox
        checkbox_widget_attrs = form.fields['is_active'].widget.attrs
        assert 'checkbox checkbox-primary' in checkbox_widget_attrs.get(
            'class', '')

    def test_partner_create_placeholders(self, client_logged, url):
        """Test que los placeholders están configurados correctamente"""
        response = client_logged.get(url)
        form = response.context['form']

        expected_placeholders = {
            'business_tax_id': 'Ingrese el RUC',
            'name': 'Nombre de la empresa',
            'email': 'correo@empresa.com',
            'phone': 'Número de teléfono',
            'address': 'Dirección completa',
            'name_contact': 'Nombre del contacto principal',
            'notes': 'Observaciones adicionales sobre el socio de negocio'
        }

        for field, expected_placeholder in expected_placeholders.items():
            widget_attrs = form.fields[field].widget.attrs
            assert widget_attrs.get('placeholder') == expected_placeholder

    def test_partner_str_method(self, valid_partner_data):
        """Test del método __str__ del modelo Partner"""
        partner = Partner.objects.create(**valid_partner_data)
        assert str(partner) == valid_partner_data['name']

    def test_partner_create_business_tax_id_max_length(self, client_logged, url):
        """Test que el campo business_tax_id respeta la longitud máxima"""
        long_data = {
            'business_tax_id': '1234567890123456',  # 16 caracteres (max es 15)
            'name': 'Empresa Test',
            'address': 'Dirección test',
            'is_active': True
        }

        response = client_logged.post(url, long_data)

        # Verificar que no se creó el socio
        assert not Partner.objects.filter(name='Empresa Test').exists()

        # Verificar que hay errores en el formulario
        assert response.status_code == 200
        form = response.context['form']
        assert form.errors

    def test_partner_create_email_validation(self, client_logged, url):
        """Test de validación del campo email"""
        invalid_email_data = {
            'business_tax_id': '1234567890001',
            'name': 'Empresa Test',
            'email': 'email-invalido-sin-arroba',
            'address': 'Dirección test',
            'is_active': True
        }

        response = client_logged.post(url, invalid_email_data)

        # Verificar que no se creó el socio
        assert not Partner.objects.filter(name='Empresa Test').exists()

        # Verificar error en el campo email
        assert response.status_code == 200
        form = response.context['form']
        assert 'email' in form.errors
