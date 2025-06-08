import pytest
from django.urls import reverse
from equipment.models import ResourceItem
from tests.BaseTestView import BaseTestView


@pytest.mark.django_db
class TestResourceItemListView(BaseTestView):

    @pytest.fixture
    def url(self):
        return reverse('resource_list')

    @pytest.fixture
    def sample_resources(self):
        ResourceItem.objects.all().delete()  # Limpiar datos existentes
        resources = [
            ResourceItem.objects.create(
                name="Laptop Dell XPS",
                code="LP001",
                brand="Dell",
                model="XPS 13",
                serial_number="DL001XPS",
                status='DISPONIBLE',
                is_active=True
            ),
            ResourceItem.objects.create(
                name="Monitor HP",
                code="MN002",
                brand="HP",
                model="24 inch",
                serial_number="HP002MON",
                status='EN REPARACION',
                is_active=True,
                motivo_reparacion="Pantalla rota"
            ),
            ResourceItem.objects.create(
                name="Teclado Logitech",
                code="KB003",
                brand="Logitech",
                model="K120",
                serial_number="LG003KEY",
                status='FUERA DE SERVICIO',  # Asegurar que está corregido
                is_active=False
            ),
            ResourceItem.objects.create(
                name="Servidor Dell PowerEdge",
                code="SRV004",
                brand="Dell",
                model="PowerEdge R740",
                serial_number="DL004SRV",
                status='DISPONIBLE',
                is_active=True
            )
        ]
        return resources

    def test_resource_list_view_uses_correct_template(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'lists/resource_list.html' in [
            t.name for t in response.templates]

    def test_resource_list_view_context_data(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert response.context['title_section'] == 'Listado De Equipos Registrados'
        assert response.context['title_page'] == 'Listado De Equipos'
        assert 'status_choices' in response.context
        assert 'active_choices' in response.context
        assert 'brand_choices' in response.context

    def test_resource_list_displays_all_items(self, client_logged, url, sample_resources):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert len(response.context['equipments']) == 4

        # Verificar que todos los recursos están en la respuesta
        content = response.content.decode()
        for resource in sample_resources:
            assert resource.name in content
            assert resource.code in content

    def test_resource_list_filter_by_search_name(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'search': 'Laptop'})
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 1
        assert equipments[0].name == "Laptop Dell XPS"

    def test_resource_list_filter_by_search_code(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'search': 'MN002'})
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 1
        assert equipments[0].code == "MN002"

    def test_resource_list_filter_by_search_brand(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'search': 'Dell'})
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 2
        dell_resources = [eq for eq in equipments if eq.brand == 'Dell']
        assert len(dell_resources) == 2

    def test_resource_list_filter_by_search_model(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'search': 'XPS'})
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 1
        assert "XPS" in equipments[0].model

    def test_resource_list_filter_by_search_serial_number(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'search': 'HP002MON'})
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 1
        assert equipments[0].serial_number == "HP002MON"

    def test_resource_list_filter_by_status_operative(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'status': 'DISPONIBLE'})  # Cambiado de 'operative'
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 2
        for equipment in equipments:
            assert equipment.status == 'DISPONIBLE'  # Cambiado de 'operative'

    def test_resource_list_filter_by_status_maintenance(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'status': 'EN REPARACION'})  # Cambiado de 'maintenance'
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 1
        assert equipments[0].status == 'EN REPARACION'  # Cambiado de 'maintenance'

    def test_resource_list_filter_by_status_damaged(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'status': 'FUERA DE SERVICIO'})  # Cambiado de 'DANADO'
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 1
        assert equipments[0].status == 'FUERA DE SERVICIO'  # Cambiado de 'DANADO'

    def test_resource_list_filter_by_brand_dropdown(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'brand': 'HP'})
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 1
        assert equipments[0].brand == 'HP'

    def test_resource_list_filter_by_is_active_true(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'is_active': 'true'})
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 3
        for equipment in equipments:
            assert equipment.is_active is True

    def test_resource_list_filter_by_is_active_false(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'is_active': 'false'})
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 1
        assert equipments[0].is_active is False

    def test_resource_list_filter_combined(self, client_logged, url, sample_resources):
        # Filtrar por Dell, operativo y activo
        response = client_logged.get(url, {
            'search': 'Dell',
            'status': 'DISPONIBLE',  # Cambiado de 'operative'
            'is_active': 'true'
        })
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 2
        for equipment in equipments:
            assert equipment.brand == 'Dell'
            assert equipment.status == 'DISPONIBLE'  # Cambiado de 'operative'
            assert equipment.is_active is True

    def test_resource_list_no_results_with_filters(self, client_logged, url, sample_resources):
        response = client_logged.get(url, {'search': 'NonExistentBrand'})
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 0
        content = response.content.decode()
        assert "No se encontraron equipos" in content

    def test_resource_list_filter_context_persistence(self, client_logged, url, sample_resources):
        params = {
            'search': 'TestSearch',
            'status': 'EN REPARACION',  # Cambiado de 'maintenance'
            'brand': 'HP',
            'is_active': 'true'
        }
        response = client_logged.get(url, params)
        assert response.status_code == 200
        assert response.context['search'] == 'TestSearch'
        assert response.context['status'] == 'EN REPARACION'  # Cambiado de 'maintenance'
        assert response.context['brand'] == 'HP'
        assert response.context['is_active'] == 'true'

    def test_resource_list_action_message_deleted(self, client_logged, url):
        response = client_logged.get(url, {'action': 'deleted'})
        assert response.status_code == 200
        assert response.context['action'] == 'deleted'
        assert response.context['message'] == 'El equipo ha sido eliminado con éxito.'

    def test_resource_list_empty_state_when_no_resources(self, client_logged, url):
        ResourceItem.objects.all().delete()  # Asegurar que no hay recursos
        # No crear recursos de muestra
        response = client_logged.get(url)
        assert response.status_code == 200
        equipments = response.context['equipments']
        assert len(equipments) == 0
        content = response.content.decode()
        assert "No se encontraron equipos" in content
        assert "Agregar primer equipo" in content

    def test_resource_list_brand_choices_context(self, client_logged, url, sample_resources):
        response = client_logged.get(url)
        assert response.status_code == 200
        brand_choices = list(response.context['brand_choices'])
        expected_brands = ['Dell', 'HP', 'Logitech']
        for brand in expected_brands:
            assert brand in brand_choices

    def test_resource_list_ordering_by_name(self, client_logged, url, sample_resources):
        response = client_logged.get(url)
        assert response.status_code == 200
        equipments = list(response.context['equipments'])
        equipment_names = [eq.name for eq in equipments]
        sorted_names = sorted(equipment_names)
        assert equipment_names == sorted_names

    def test_resource_list_queryset_distinct(self, client_logged, url, sample_resources):
        # Test multiple filters to ensure distinct() works
        response = client_logged.get(url, {
            'search': 'Dell',
            'brand': 'Dell'
        })
        assert response.status_code == 200
        equipments = response.context['equipments']
        # Verificar que no hay duplicados
        equipment_ids = [eq.id for eq in equipments]
        assert len(equipment_ids) == len(set(equipment_ids))

    def test_resource_list_context_object_name(self, client_logged, url, sample_resources):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'equipments' in response.context
        assert response.context['equipments'] is not None

    def test_resource_list_template_contains_filter_form(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="search"' in content
        assert 'name="status"' in content
        assert 'name="brand"' in content
        assert 'name="is_active"' in content
        assert 'Filtrar' in content
        assert 'Limpiar' in content
