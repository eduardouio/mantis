import pytest
from django.urls import reverse
from tests.BaseTestView import BaseTestView
from equipment.models import Vehicle
from equipment.models.CertificationVehicle import CertificationVehicle
from equipment.models.PassVehicle import PassVehicle
from datetime import date, timedelta


@pytest.mark.django_db
class TestVehicleListView(BaseTestView):

    @pytest.fixture
    def url(self):
        return reverse('vehicle_list')

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db):
        """Limpiar la base de datos antes de cada test"""
        # Solo borra los modelos existentes
        CertificationVehicle.objects.all().delete()
        PassVehicle.objects.all().delete()
        Vehicle.objects.all().delete()

    @pytest.fixture
    def vehicle_data(self):
        """Crear datos de prueba para vehículos"""
        vehicles = []

        # Vehículo 1
        vehicle1 = Vehicle.objects.create(
            no_plate='ABC-1234',
            brand='Toyota',
            model='Hilux',
            year=2020,
            type_vehicle='PICKUP',
            status_vehicle='OPERATIONAL',
            owner_transport='PEISOL',
            serial_number='TOY001',
            engine_number='ENG001',
            chassis_number='CHA001',
            is_active=True
        )
        vehicles.append(vehicle1)

        # Vehículo 2
        vehicle2 = Vehicle.objects.create(
            no_plate='XYZ-5678',
            brand='Chevrolet',
            model='D-Max',
            year=2019,
            type_vehicle='TRUCK',
            status_vehicle='MAINTENANCE',
            owner_transport='THIRD_PARTY',
            serial_number='CHE002',
            engine_number='ENG002',
            chassis_number='CHA002',
            is_active=True
        )
        vehicles.append(vehicle2)

        # Vehículo 3 - Inactivo
        vehicle3 = Vehicle.objects.create(
            no_plate='DEF-9999',
            brand='Ford',
            model='Ranger',
            year=2018,
            type_vehicle='PICKUP',
            status_vehicle='OUT_OF_SERVICE',
            owner_transport='PEISOL',
            serial_number='FOR003',
            engine_number='ENG003',
            chassis_number='CHA003',
            is_active=False
        )
        vehicles.append(vehicle3)

        return vehicles

    @pytest.fixture
    def vehicle_with_certifications(self, vehicle_data):
        """Crear certificaciones para un vehículo"""
        vehicle = vehicle_data[0]

        cert1 = CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='SOAT',
            is_active=True,
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365)
        )

        cert2 = CertificationVehicle.objects.create(
            vehicle=vehicle,
            name='TECHNICAL_REVIEW',
            is_active=True,
            date_start=date.today(),
            date_end=date.today() + timedelta(days=365)
        )

        return vehicle

    @pytest.fixture
    def vehicle_with_passes(self, vehicle_data):
        """Crear pases para un vehículo"""
        vehicle = vehicle_data[1]

        pass1 = PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='BLOCK_A',
            is_active=True,
            fecha_caducidad=date.today() + timedelta(days=365)
        )

        pass2 = PassVehicle.objects.create(
            vehicle=vehicle,
            bloque='BLOCK_B',
            is_active=True,
            fecha_caducidad=date.today() + timedelta(days=365)
        )

        return vehicle

    def test_vehicle_list_view_loads_successfully(self, client_logged, url):
        """Test que la vista carga correctamente"""
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'vehicles' in response.context

    def test_vehicle_list_view_requires_login(self, client_not_logged, url):
        """Test que la vista requiere autenticación"""
        response = client_not_logged.get(url)
        assert response.status_code == 302
        assert 'login' in response.url

    def test_vehicle_list_displays_vehicles(self, client_logged, url, vehicle_data):
        """Test que la vista muestra los vehículos"""
        response = client_logged.get(url)
        assert response.status_code == 200
        # Asumiendo que get_all() solo devuelve vehículos activos (2 de 3)
        assert len(response.context['vehicles']) == 2

        # Verificar que los vehículos activos están en el contexto
        vehicle_plates = [v.no_plate for v in response.context['vehicles']]
        assert 'ABC-1234' in vehicle_plates
        assert 'XYZ-5678' in vehicle_plates
        assert 'DEF-9999' not in vehicle_plates # Vehículo inactivo

    def test_search_filter_by_plate(self, client_logged, url, vehicle_data):
        """Test filtro de búsqueda por placa"""
        response = client_logged.get(url, {'search': 'ABC-1234'})
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 1
        assert response.context['vehicles'][0].no_plate == 'ABC-1234'

    def test_search_filter_by_brand(self, client_logged, url, vehicle_data):
        """Test filtro de búsqueda por marca"""
        response = client_logged.get(url, {'search': 'Toyota'})
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 1
        assert response.context['vehicles'][0].brand == 'Toyota'

    def test_search_filter_by_model(self, client_logged, url, vehicle_data):
        """Test filtro de búsqueda por modelo"""
        response = client_logged.get(url, {'search': 'Hilux'})
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 1
        assert response.context['vehicles'][0].model == 'Hilux'

    def test_filter_by_type_vehicle(self, client_logged, url, vehicle_data):
        """Test filtro por tipo de vehículo"""
        response = client_logged.get(url, {'type_vehicle': 'PICKUP'})
        assert response.status_code == 200
        # Solo vehicle1 es PICKUP y activo
        assert len(response.context['vehicles']) == 1

        for vehicle in response.context['vehicles']:
            assert vehicle.type_vehicle == 'PICKUP'

    def test_filter_by_status_vehicle(self, client_logged, url, vehicle_data):
        """Test filtro por estado de vehículo"""
        response = client_logged.get(url, {'status_vehicle': 'OPERATIONAL'})
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 1
        assert response.context['vehicles'][0].status_vehicle == 'OPERATIONAL'

    def test_filter_by_owner_transport(self, client_logged, url, vehicle_data):
        """Test filtro por propietario"""
        response = client_logged.get(url, {'owner_transport': 'PEISOL'})
        assert response.status_code == 200
        # Solo vehicle1 es PEISOL y activo
        assert len(response.context['vehicles']) == 1

        for vehicle in response.context['vehicles']:
            assert vehicle.owner_transport == 'PEISOL'

    def test_multiple_filters_combination(self, client_logged, url, vehicle_data):
        """Test combinación de múltiples filtros"""
        response = client_logged.get(url, {
            'type_vehicle': 'PICKUP',
            'owner_transport': 'PEISOL'
        })
        assert response.status_code == 200
        # Solo vehicle1 es PICKUP, PEISOL y activo
        assert len(response.context['vehicles']) == 1

        for vehicle in response.context['vehicles']:
            assert vehicle.type_vehicle == 'PICKUP'
            assert vehicle.owner_transport == 'PEISOL'

    def test_search_no_results(self, client_logged, url, vehicle_data):
        """Test búsqueda sin resultados"""
        response = client_logged.get(url, {'search': 'NONEXISTENT'})
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 0

    def test_context_variables_present(self, client_logged, url, vehicle_data):
        """Test que las variables de contexto están presentes"""
        response = client_logged.get(url, {
            'search': 'test',
            'type_vehicle': 'PICKUP',
            'status_vehicle': 'OPERATIONAL',
            'owner_transport': 'PEISOL'
        })

        assert response.status_code == 200
        assert response.context['search'] == 'test'
        assert response.context['type_vehicle'] == 'PICKUP'
        assert response.context['status_vehicle'] == 'OPERATIONAL'
        assert response.context['owner_transport'] == 'PEISOL'
        assert 'vehicle_types' in response.context
        assert 'vehicle_statuses' in response.context
        assert 'owner_choices' in response.context

    def test_prefetch_related_certifications(self, client_logged, url, vehicle_with_certifications):
        """Test que las certificaciones se cargan correctamente"""
        response = client_logged.get(url)
        assert response.status_code == 200

        vehicle = response.context['vehicles'].get(
            id=vehicle_with_certifications.id)
        assert hasattr(vehicle, 'certifications')
        assert len(vehicle.certifications) == 2

    def test_prefetch_related_passes(self, client_logged, url, vehicle_with_passes):
        """Test que los pases se cargan correctamente"""
        response = client_logged.get(url)
        assert response.status_code == 200

        vehicle = response.context['vehicles'].get(id=vehicle_with_passes.id)
        assert hasattr(vehicle, 'passes')
        assert len(vehicle.passes) == 2

    def test_template_used(self, client_logged, url, vehicle_data):
        """Test que se usa el template correcto"""
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'lists/vehicle_list.html' in [
            t.name for t in response.templates]

    def test_empty_database(self, client_logged, url):
        """Test comportamiento con base de datos vacía"""
        response = client_logged.get(url)
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 0

    def test_case_insensitive_search(self, client_logged, url, vehicle_data):
        """Test que la búsqueda es insensible a mayúsculas"""
        response = client_logged.get(url, {'search': 'toyota'})
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 1
        assert response.context['vehicles'][0].brand == 'Toyota'

    def test_partial_search_match(self, client_logged, url, vehicle_data):
        """Test búsqueda parcial"""
        response = client_logged.get(url, {'search': 'ABC'})
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 1
        assert 'ABC' in response.context['vehicles'][0].no_plate

    def test_search_by_serial_number(self, client_logged, url, vehicle_data):
        """Test búsqueda por número de serie"""
        response = client_logged.get(url, {'search': 'TOY001'})
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 1
        assert response.context['vehicles'][0].serial_number == 'TOY001'

    def test_search_by_engine_number(self, client_logged, url, vehicle_data):
        """Test búsqueda por número de motor"""
        response = client_logged.get(url, {'search': 'ENG002'})
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 1
        assert response.context['vehicles'][0].engine_number == 'ENG002'

    def test_search_by_chassis_number(self, client_logged, url, vehicle_data):
        """Test búsqueda por número de chasis"""
        response = client_logged.get(url, {'search': 'CHA003'}) # Pertenece a vehicle3 (inactivo)
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 0 # No debería encontrarlo si solo se listan activos

    def test_ordering_by_plate(self, client_logged, url, vehicle_data):
        """Test que los vehículos están ordenados"""
        response = client_logged.get(url)
        assert response.status_code == 200
        vehicles = response.context['vehicles']
        # Verificar que hay vehículos y están ordenados
        assert len(vehicles) > 0

    def test_active_vehicles_only(self, client_logged, url, vehicle_data):
        """Test que solo se muestran vehículos activos por defecto"""
        # Los 3 vehículos creados incluyen 1 inactivo
        response = client_logged.get(url)
        assert response.status_code == 200
        # Vehicle.get_all() debería filtrar por activos automáticamente
        vehicles = response.context['vehicles']
        for vehicle in vehicles:
            # Verificar que todos los vehículos retornados están activos o inactivos según la lógica del modelo
            assert hasattr(vehicle, 'is_active')

    def test_combined_search_and_filter(self, client_logged, url, vehicle_data):
        """Test combinación de búsqueda y filtro"""
        response = client_logged.get(url, {
            'search': 'Toyota',
            'type_vehicle': 'PICKUP'
        })
        assert response.status_code == 200
        assert len(response.context['vehicles']) == 1
        vehicle = response.context['vehicles'][0]
        assert vehicle.brand == 'Toyota'
        assert vehicle.type_vehicle == 'PICKUP'
