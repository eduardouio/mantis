import pytest
from django.urls import reverse
from tests.BaseTestView import BaseTestView
from accounts.models import Technical
from datetime import date, timedelta


@pytest.mark.django_db
class TestTechnicalListView(BaseTestView):

    @pytest.fixture
    def url(self):
        return reverse('technical_list')

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db):
        Technical.objects.all().delete()

    @pytest.fixture
    def technical_data(self):
        technicals = []
        today = date.today()
        # Técnico 1: Activo, con todos los certificados
        tech1 = Technical.objects.create(
            first_name='Juan', last_name='Perez', email='juan.perez@example.com',
            nro_phone='123456789', dni='11111111A', work_area='MECHANICS', is_active=True,
            license_issue_date=today, defensive_driving_certificate_issue_date=today,
            mae_certificate_issue_date=today, medical_certificate_issue_date=today
        )
        technicals.append(tech1)

        # Técnico 2: Inactivo, sin certificados
        tech2 = Technical.objects.create(
            first_name='Ana', last_name='Gomez', email='ana.gomez@example.com',
            nro_phone='987654321', dni='22222222B', work_area='ELECTRICITY', is_active=False
        )
        technicals.append(tech2)

        # Técnico 3: Activo, algunos certificados
        tech3 = Technical.objects.create(
            first_name='Luis', last_name='Martinez', email='luis.martinez@example.com',
            nro_phone='555555555', dni='33333333C', work_area='MECHANICS', is_active=True,
            license_issue_date=today, medical_certificate_issue_date=today
        )
        technicals.append(tech3)
        return technicals

    def test_technical_list_view_loads_successfully(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'technicals' in response.context

    def test_technical_list_view_requires_login(self, client_not_logged, url):
        response = client_not_logged.get(url)
        assert response.status_code == 302
        assert 'login' in response.url

    def test_technical_list_displays_technicals(self, client_logged, url, technical_data):
        response = client_logged.get(url)
        assert response.status_code == 200
        # Por defecto, la vista podría mostrar todos o solo activos, ajusta según la implementación de Technical.objects.all()
        # Si Technical.objects.all() no filtra por is_active por defecto:
        assert len(response.context['technicals']) == 3
        technical_names = [
            t.first_name for t in response.context['technicals']]
        assert 'Juan' in technical_names
        assert 'Ana' in technical_names
        assert 'Luis' in technical_names

    def test_search_filter_by_name(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'search': 'Juan'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1
        assert response.context['technicals'][0].first_name == 'Juan'

    def test_search_filter_by_email(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'search': 'ana.gomez@example.com'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1
        assert response.context['technicals'][0].email == 'ana.gomez@example.com'

    def test_search_filter_by_dni(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'search': '33333333C'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1
        assert response.context['technicals'][0].dni == '33333333C'

    def test_filter_by_work_area(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'work_area': 'MECHANICS'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 2
        for tech in response.context['technicals']:
            assert tech.work_area == 'MECHANICS'

    def test_filter_by_is_active_true(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'is_active': 'true'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 2
        for tech in response.context['technicals']:
            assert tech.is_active is True

    def test_filter_by_is_active_false(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'is_active': 'false'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1
        assert response.context['technicals'][0].is_active is False

    def test_filter_has_license_true(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'has_license': 'true'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 2
        for tech in response.context['technicals']:
            assert tech.license_issue_date is not None

    def test_filter_has_license_false(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'has_license': 'false'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1
        assert response.context['technicals'][0].license_issue_date is None

    def test_filter_has_defensive_driving_true(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'has_defensive_driving': 'true'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1  # Solo Juan
        assert response.context['technicals'][0].first_name == 'Juan'

    def test_filter_has_mae_certificate_true(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'has_mae_certificate': 'true'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1  # Solo Juan
        assert response.context['technicals'][0].first_name == 'Juan'

    def test_filter_has_medical_certificate_true(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'has_medical_certificate': 'true'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 2  # Juan y Luis
        names = {tech.first_name for tech in response.context['technicals']}
        assert 'Juan' in names
        assert 'Luis' in names

    def test_combined_filters(self, client_logged, url, technical_data):
        response = client_logged.get(url, {
            'work_area': 'MECHANICS',
            'is_active': 'true',
            'has_license': 'true'
        })
        assert response.status_code == 200
        assert len(response.context['technicals']) == 2  # Juan y Luis
        for tech in response.context['technicals']:
            assert tech.work_area == 'MECHANICS'
            assert tech.is_active is True
            assert tech.license_issue_date is not None

    def test_search_no_results(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'search': 'NONEXISTENT'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 0

    def test_context_variables_present(self, client_logged, url, technical_data):
        response = client_logged.get(url, {
            'search': 'test', 'work_area': 'MECHANICS', 'is_active': 'true',
            'has_license': 'true', 'has_defensive_driving': 'false',
            'has_mae_certificate': 'true', 'has_medical_certificate': 'false'
        })
        assert response.status_code == 200
        assert response.context['search'] == 'test'
        assert response.context['work_area'] == 'MECHANICS'
        assert response.context['is_active'] == 'true'
        assert response.context['has_license'] == 'true'
        assert response.context['has_defensive_driving'] == 'false'
        assert response.context['has_mae_certificate'] == 'true'
        assert response.context['has_medical_certificate'] == 'false'
        assert 'work_area_choices' in response.context
        assert 'status_choices' in response.context
        assert 'certificate_choices' in response.context

    def test_template_used(self, client_logged, url, technical_data):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'lists/technical_list.html' in [
            t.name for t in response.templates]

    def test_empty_database(self, client_logged, url):
        # setup_test_data ya limpia la BD, así que no necesitamos technical_data aquí
        # Asegurar que está vacía para este test específico
        Technical.objects.all().delete()
        response = client_logged.get(url)
        assert response.status_code == 200
        assert len(response.context['technicals']) == 0

    def test_case_insensitive_search(self, client_logged, url, technical_data):
        response = client_logged.get(url, {'search': 'juan'})  # Minúscula
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1
        assert response.context['technicals'][0].first_name == 'Juan'

    def test_partial_search_match(self, client_logged, url, technical_data):
        response = client_logged.get(
            url, {'search': 'Mar'})  # Parcial para Martinez
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1
        assert response.context['technicals'][0].last_name == 'Martinez'

    def test_ordering_by_first_name(self, client_logged, url, technical_data):
        response = client_logged.get(url)
        assert response.status_code == 200
        technicals = response.context['technicals']
        names = [t.first_name for t in technicals]

        # La vista ordena por 'first_name' por defecto y no filtra por 'is_active' por defecto.
        # El orden de creación en el fixture es Juan, Ana, Luis.
        # El orden alfabético de 'first_name' es Ana, Juan, Luis.
        assert names == ['Ana', 'Juan', 'Luis']

    def test_filter_by_work_area_and_active(self, client_logged, url, technical_data):
        response = client_logged.get(
            url, {'work_area': 'MECHANICS', 'is_active': 'true'})
        assert response.status_code == 200
        assert len(response.context['technicals']) == 2  # Juan y Luis
        names = {tech.first_name for tech in response.context['technicals']}
        assert 'Juan' in names
        assert 'Luis' in names
        for tech in response.context['technicals']:
            assert tech.work_area == 'MECHANICS'
            assert tech.is_active is True

    def test_filter_by_certificates_combination(self, client_logged, url, technical_data):
        # Buscar técnicos activos con licencia PERO SIN certificado MAE
        response = client_logged.get(url, {
            'is_active': 'true',
            'has_license': 'true',
            'has_mae_certificate': 'false'  # Luis tiene licencia pero no MAE
        })
        assert response.status_code == 200
        assert len(response.context['technicals']) == 1
        assert response.context['technicals'][0].first_name == 'Luis'
        assert response.context['technicals'][0].is_active is True
        assert response.context['technicals'][0].license_issue_date is not None
        assert response.context['technicals'][0].mae_certificate_issue_date is None
