import pytest
from django.urls import reverse
from tests.BaseTestView import BaseTestView
from projects.models import Partner


@pytest.mark.django_db
class TestPartnerListView(BaseTestView):

    @pytest.fixture
    def url(self):
        return reverse('partner_list')

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db):
        Partner.objects.all().delete()

    @pytest.fixture
    def partner_data(self):
        partners = []
        
        # Partner 1: Cliente activo
        partner1 = Partner.objects.create(
            name='Empresa ABC S.A.',
            business_tax_id='1234567890001',
            email='contacto@empresaabc.com',
            phone='02-2345678',
            address='Av. Principal 123, Quito',
            name_contact='Juan Pérez',
            is_active=True
        )
        partners.append(partner1)

        # Partner 2: Proveedor inactivo
        partner2 = Partner.objects.create(
            name='Proveedor XYZ Ltda.',
            business_tax_id='0987654321001',
            email='ventas@proveedorxyz.com',
            phone='04-3456789',
            address='Calle Secundaria 456, Guayaquil',
            name_contact='María González',
            is_active=False
        )
        partners.append(partner2)

        # Partner 3: Cliente activo sin algunos campos
        partner3 = Partner.objects.create(
            name='Negocio DEF',
            business_tax_id='1122334455001',
            address='Centro Comercial 789, Cuenca',
            is_active=True
        )
        partners.append(partner3)

        return partners

    def test_partner_list_view_loads_successfully(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'partners' in response.context

    def test_partner_list_view_requires_login(self, client_not_logged, url):
        response = client_not_logged.get(url)
        assert response.status_code == 302
        assert 'login' in response.url

    def test_partner_list_displays_partners(self, client_logged, url, partner_data):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert len(response.context['partners']) == 3
        partner_names = [p.name for p in response.context['partners']]
        assert 'Empresa ABC S.A.' in partner_names
        assert 'Proveedor XYZ Ltda.' in partner_names
        assert 'Negocio DEF' in partner_names

    def test_search_filter_by_name(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': 'ABC'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].name == 'Empresa ABC S.A.'

    def test_search_filter_by_business_tax_id(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': '1234567890001'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].business_tax_id == '1234567890001'

    def test_search_filter_by_email(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': 'ventas@proveedorxyz.com'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].email == 'ventas@proveedorxyz.com'

    def test_search_filter_by_phone(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': '02-2345678'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].phone == '02-2345678'

    def test_search_filter_by_address(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': 'Quito'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert 'Quito' in response.context['partners'][0].address

    def test_search_filter_by_contact_name(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': 'María González'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].name_contact == 'María González'

    def test_filter_by_address_field(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'address': 'Av. Principal 123, Quito'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].address == 'Av. Principal 123, Quito'

    def test_filter_by_is_active_true(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'is_active': 'true'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 2
        for partner in response.context['partners']:
            assert partner.is_active is True

    def test_filter_by_is_active_false(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'is_active': 'false'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].is_active is False

    def test_combined_filters(self, client_logged, url, partner_data):
        response = client_logged.get(url, {
            'is_active': 'true',
            'search': 'ABC'
        })
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        partner = response.context['partners'][0]
        assert partner.is_active is True
        assert 'ABC' in partner.name

    def test_search_no_results(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': 'NONEXISTENT'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 0

    def test_context_variables_present(self, client_logged, url, partner_data):
        response = client_logged.get(url, {
            'search': 'test',
            'address': 'test address',
            'is_active': 'true'
        })
        assert response.status_code == 200
        assert response.context['search'] == 'test'
        assert response.context['address'] == 'test address'
        assert response.context['is_active'] == 'true'
        assert 'active_choices' in response.context
        assert 'address_choices' in response.context

    def test_template_used(self, client_logged, url, partner_data):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'lists/partner_list.html' in [t.name for t in response.templates]

    def test_empty_database(self, client_logged, url):
        Partner.objects.all().delete()
        response = client_logged.get(url)
        assert response.status_code == 200
        assert len(response.context['partners']) == 0

    def test_case_insensitive_search(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': 'abc'})  # Minúscula
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert 'ABC' in response.context['partners'][0].name

    def test_partial_search_match(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': 'Empresa'})  # Parcial
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert 'Empresa ABC S.A.' == response.context['partners'][0].name

    def test_ordering_by_name(self, client_logged, url, partner_data):
        response = client_logged.get(url)
        assert response.status_code == 200
        partners = response.context['partners']
        names = [p.name for p in partners]
        # Verificar que está ordenado alfabéticamente por nombre
        assert names == sorted(names)

    def test_search_by_ruc_partial(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': '123456'})  # Parcial del RUC
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].business_tax_id == '1234567890001'

    def test_filter_address_partial_match(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'address': 'Principal'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert 'Principal' in response.context['partners'][0].address

    def test_multiple_search_terms(self, client_logged, url, partner_data):
        # Buscar por múltiples términos que coincidan con diferentes campos
        response = client_logged.get(url, {'search': 'juan'})  # Nombre de contacto
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].name_contact == 'Juan Pérez'

    def test_filter_by_nonexistent_field(self, client_logged, url, partner_data):
        # Test con campo inexistente para verificar que no cause errores
        response = client_logged.get(url, {'nonexistent_field': 'value'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 3  # Todos los partners

    def test_context_title_variables(self, client_logged, url, partner_data):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert response.context['title_section'] == 'Listado de Socios de Negocio Registrados'
        assert response.context['title_page'] == 'Listado de Socios de Negocio'

    def test_action_message_deleted(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'action': 'deleted'})
        assert response.status_code == 200
        assert response.context['action'] == 'deleted'
        assert response.context['message'] == 'El socio de negocio ha sido eliminado con éxito.'

    def test_no_action_no_message(self, client_logged, url, partner_data):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'action' not in response.context or response.context.get('action') is None

    def test_distinct_queryset(self, client_logged, url, partner_data):
        # Test para verificar que distinct() funciona correctamente
        Partner.objects.create(
            name='Test Duplicate',
            business_tax_id='9999999999001',
            address='Av. Principal 123, Quito',  # Misma dirección que partner1
            is_active=True
        )
        
        response = client_logged.get(url, {'address': 'Av. Principal 123, Quito'})
        assert response.status_code == 200
        # Verificar que no hay duplicados
        partners = response.context['partners']
        partner_ids = [p.id for p in partners]
        assert len(partner_ids) == len(set(partner_ids))  # Todos los IDs únicos

    def test_search_multiple_fields(self, client_logged, url, partner_data):
        # Test búsqueda que coincida con múltiples campos
        response = client_logged.get(url, {'search': 'Empresa'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert 'Empresa' in response.context['partners'][0].name

    def test_address_filter_with_special_characters(self, client_logged, url, partner_data):
        # Test filtro por dirección con caracteres especiales
        response = client_logged.get(url, {'address': 'Av.'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert 'Av. Principal' in response.context['partners'][0].address

    def test_email_search_case_insensitive(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': 'CONTACTO@EMPRESAABC.COM'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].email == 'contacto@empresaabc.com'

    def test_phone_search_partial(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': '02-234'})  # Parcial del teléfono
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].phone == '02-2345678'

    def test_business_tax_id_exact_match(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': '1234567890001'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert response.context['partners'][0].business_tax_id == '1234567890001'

    def test_contact_name_search(self, client_logged, url, partner_data):
        response = client_logged.get(url, {'search': 'María'})
        assert response.status_code == 200
        assert len(response.context['partners']) == 1
        assert 'María' in response.context['partners'][0].name_contact

    def test_address_choices_context(self, client_logged, url, partner_data):
        response = client_logged.get(url)
        assert response.status_code == 200
        address_choices = response.context['address_choices']
        # Verificar que las direcciones están en las opciones
        addresses = list(address_choices)
        assert any('Quito' in addr for addr in addresses)
        assert any('Guayaquil' in addr for addr in addresses)
        assert any('Cuenca' in addr for addr in addresses)
