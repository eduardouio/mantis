import pytest
from django.urls import reverse
from django.test import Client
from accounts.models import CustomUserModel
from equipment.models.ResourceItem import ResourceItem


@pytest.mark.django_db
class TestResourceItemCreateView:

    @pytest.fixture
    def setup_user(self):
        user = CustomUserModel.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
        return user

    @pytest.fixture
    def authenticated_client(self, setup_user):
        client = Client()
        client.force_login(setup_user)
        return client

    @pytest.fixture
    def valid_equipment_data(self):
        return {
            'name': 'Lavamanos Portátil',
            'type': 'EQUIPO',
            'type_equipment': 'LVMNOS',
            'brand': 'Tecniaguas',
            'code': 'LAV-001',
            'status': 'DISPONIBLE',
            'stst_status_disponibility': 'DISPONIBLE',
            'height': '120',
            'width': '60',
            'depth': '50',
            'weight': '35'
        }

    def test_login_required(self):
        client = Client()
        response = client.get(reverse('resource_create'))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_get_context_data(self, authenticated_client):
        response = authenticated_client.get(reverse('resource_create'))
        assert response.status_code == 200
        assert 'title_section' in response.context
        assert response.context['title_section'] == 'Registrar Nuevo Equipo'
        assert response.context['title_page'] == 'Registrar Nuevo Equipo'

    def test_get_request_renders_correct_template(self, authenticated_client):
        response = authenticated_client.get(reverse('resource_create'))
        assert response.status_code == 200
        assert 'forms/resource_item_form.html' in [t.name for t in response.templates]

    def test_create_equipment_successfully(self, authenticated_client, valid_equipment_data):
        import uuid
        initial_count = ResourceItem.objects.count()
        unique_code = f"TEST-{uuid.uuid4().hex[:8]}"
        valid_equipment_data['code'] = unique_code

        response = authenticated_client.post(
            reverse('resource_create'),
            data=valid_equipment_data,
            follow=True
        )

        if response.status_code == 200 and 'form' in response.context and response.context['form'].errors:
            print("Errores del formulario:", response.context['form'].errors)

        assert ResourceItem.objects.count() == initial_count + 1
        assert ResourceItem.objects.filter(code=unique_code).exists()

        created_equipment = ResourceItem.objects.get(code=unique_code)
        assert created_equipment.name == valid_equipment_data['name']
        assert created_equipment.type_equipment == valid_equipment_data['type_equipment']

        assert response.redirect_chain[0][0].startswith(f'/equipos/{created_equipment.pk}/')
        assert 'action=created' in response.redirect_chain[0][0]

    def test_form_validation_error(self, authenticated_client):
        invalid_data = {
            'name': '',
            'type': 'EQUIPO',
            'status': 'DISPONIBLE'
        }

        initial_count = ResourceItem.objects.count()
        response = authenticated_client.post(reverse('resource_create'), data=invalid_data)

        assert ResourceItem.objects.count() == initial_count
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        assert 'name' in response.context['form'].errors

    def test_form_subtype_specific_validation(self, authenticated_client):
        planta_data = {
            'name': 'Planta de Tratamiento X',
            'type': 'EQUIPO',
            'type_equipment': 'PTRTAR',
            'brand': 'AquaPure',
            'code': 'PT-001',
            'status': 'DISPONIBLE',
            'stst_status_disponibility': 'DISPONIBLE',
        }

        initial_count = ResourceItem.objects.count()
        response = authenticated_client.post(reverse('resource_create'), data=planta_data)
        
        # El objeto se crea pero sin plant_capacity, verificamos que existe
        assert ResourceItem.objects.count() == initial_count + 1
        created = ResourceItem.objects.get(code='PT-001')
        assert created.plant_capacity is None
        
        # Limpiamos para el siguiente test
        created.delete()

        planta_data['plant_capacity'] = '25M3'
        response = authenticated_client.post(reverse('resource_create'), data=planta_data, follow=True)
        assert ResourceItem.objects.filter(name=planta_data['name']).exists()
        
    def test_lavamanos_creation(self, authenticated_client):
        import uuid
        
        lavamanos_data = {
            'name': 'Lavamanos Test',
            'type': 'EQUIPO',
            'type_equipment': 'LVMNOS',
            'brand': 'Tecniaguas',
            'code': f'LAV-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'stst_status_disponibility': 'DISPONIBLE',
            'height': '100',
            'width': '60',
            'depth': '50',
            'weight': '35',
            'have_foot_pumps': 'on',
            'have_soap_dispenser': 'on',
            'have_paper_towels': 'on',
        }
        
        initial_count = ResourceItem.objects.count()
        response = authenticated_client.post(reverse('resource_create'), data=lavamanos_data, follow=True)
        
        assert ResourceItem.objects.count() == initial_count + 1
        created_equipment = ResourceItem.objects.get(code=lavamanos_data['code'])
        
        assert created_equipment.have_foot_pumps is True
        assert created_equipment.have_soap_dispenser is True
        assert created_equipment.have_paper_towels is True
        
    def test_bateria_sanitaria_mujer_creation(self, authenticated_client):
        import uuid
        
        bateria_data = {
            'name': 'Bateria Sanitaria Mujer Test',
            'type': 'EQUIPO',
            'type_equipment': 'BTSNMJ',
            'brand': 'Portasanit',
            'code': f'BSM-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'stst_status_disponibility': 'DISPONIBLE',
            'height': '220',
            'width': '110',
            'depth': '110',
            'weight': '80',
            'have_paper_dispenser': 'on',
            'have_soap_dispenser': 'on',
            'have_napkin_dispenser': 'on',
            'have_seat': 'on',
            'have_toilet_pump': 'on',
            'have_sink_pump': 'on',
            'have_toilet_lid': 'on',
            'have_bathroom_bases': 'on',
            'have_ventilation_pipe': 'on',
        }
        
        initial_count = ResourceItem.objects.count()
        response = authenticated_client.post(reverse('resource_create'), data=bateria_data, follow=True)
        
        assert ResourceItem.objects.count() == initial_count + 1
        created_equipment = ResourceItem.objects.get(code=bateria_data['code'])
        
        assert created_equipment.have_paper_dispenser is True
        assert created_equipment.have_soap_dispenser is True
        assert created_equipment.have_napkin_dispenser is True
        assert created_equipment.have_seat is True
        assert created_equipment.have_toilet_pump is True
        assert created_equipment.have_sink_pump is True
        assert created_equipment.have_toilet_lid is True
        assert created_equipment.have_bathroom_bases is True
        assert created_equipment.have_ventilation_pipe is True
        
    def test_planta_tratamiento_creation(self, authenticated_client):
        import uuid
        
        planta_data = {
            'name': 'Planta de Tratamiento Test',
            'type': 'EQUIPO',
            'type_equipment': 'PTRTAP',
            'brand': 'AquaPure',
            'code': f'PTA-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'stst_status_disponibility': 'DISPONIBLE',
            'height': '180',
            'width': '150',
            'depth': '150',
            'weight': '200',
            'plant_capacity': '10M3',
            'belt_type': 'A',
            'blower_brand': 'BlowerTech',
            'blower_model': 'BT-2000',
            'engine_brand': 'MotorMax',
            'engine_model': 'MM-500',
            'belt_brand': 'BeltPro',
            'belt_model': 'BP-100A',
            'blower_pulley_brand': 'PulleyTech',
            'blower_pulley_model': 'PT-A200',
            'motor_pulley_brand': 'PulleyPro',
            'motor_pulley_model': 'PP-A150',
            'electrical_panel_brand': 'ElecPanel',
            'electrical_panel_model': 'EP-2000',
            'engine_guard_brand': 'GuardTech',
            'engine_guard_model': 'GT-500',
        }
        
        initial_count = ResourceItem.objects.count()
        response = authenticated_client.post(reverse('resource_create'), data=planta_data, follow=True)
        
        assert ResourceItem.objects.count() == initial_count + 1
        created_equipment = ResourceItem.objects.get(code=planta_data['code'])
        
        assert created_equipment.plant_capacity == '10M3'
        assert created_equipment.belt_type == 'A'
        assert created_equipment.blower_brand == 'BlowerTech'
        assert created_equipment.engine_brand == 'MotorMax'
        assert created_equipment.electrical_panel_brand == 'ElecPanel'
        assert created_equipment.engine_guard_brand == 'GuardTech'
        
    def test_camper_bano_creation(self, authenticated_client):
        import uuid
        
        camper_data = {
            'name': 'Camper Baño Test',
            'type': 'EQUIPO',
            'type_equipment': 'CMPRBN',
            'brand': 'CamperTech',
            'code': f'CAM-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'stst_status_disponibility': 'DISPONIBLE',
            'height': '250',
            'width': '200',
            'depth': '200',
            'weight': '350',
            'have_paper_dispenser': 'on',
            'have_soap_dispenser': 'on',
            'have_napkin_dispenser': 'on',
            'have_urinals': 'on',
            'have_seat': 'on',
            'have_toilet_pump': 'on',
            'have_sink_pump': 'on',
            'have_toilet_lid': 'on',
            'have_bathroom_bases': 'on',
            'have_ventilation_pipe': 'on',
        }
        
        initial_count = ResourceItem.objects.count()
        response = authenticated_client.post(reverse('resource_create'), data=camper_data, follow=True)
        
        assert ResourceItem.objects.count() == initial_count + 1
        created_equipment = ResourceItem.objects.get(code=camper_data['code'])
        
        assert created_equipment.have_paper_dispenser is True
        assert created_equipment.have_soap_dispenser is True
        assert created_equipment.have_napkin_dispenser is True
        assert created_equipment.have_urinals is True
        assert created_equipment.have_seat is True
        assert created_equipment.have_toilet_pump is True
        assert created_equipment.have_sink_pump is True
        assert created_equipment.have_toilet_lid is True
        assert created_equipment.have_bathroom_bases is True
        assert created_equipment.have_ventilation_pipe is True
        
    def test_estacion_cuadruple_urinario_creation(self, authenticated_client):
        import uuid
        
        urinario_data = {
            'name': 'Estación Cuádruple Urinario Test',
            'type': 'EQUIPO',
            'type_equipment': 'EST4UR',
            'brand': 'UrinarioTech',
            'code': f'URI-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'stst_status_disponibility': 'DISPONIBLE',
            'height': '150',
            'width': '100',
            'depth': '50',
            'weight': '45',
        }
        
        initial_count = ResourceItem.objects.count()
        response = authenticated_client.post(reverse('resource_create'), data=urinario_data, follow=True)
        
        assert ResourceItem.objects.count() == initial_count + 1
        created_equipment = ResourceItem.objects.get(code=urinario_data['code'])
        
        assert created_equipment.name == urinario_data['name']
        assert created_equipment.brand == urinario_data['brand']
        assert created_equipment.height == int(urinario_data['height'])
        assert created_equipment.width == int(urinario_data['width'])
        assert created_equipment.depth == int(urinario_data['depth'])
        assert created_equipment.weight == int(urinario_data['weight'])
        assert created_equipment.stst_status_disponibility == urinario_data['stst_status_disponibility']
        
    def test_servicio_creation(self, authenticated_client):
        import uuid
        
        servicio_data = {
            'name': 'Servicio de Mantenimiento',
            'type': 'SERVICIO',
            'brand': 'PEISOL',
            'code': f'SRV-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'stst_status_disponibility': 'DISPONIBLE',
            'height': '0',
            'width': '0',
            'depth': '0',
            'weight': '0',
            'description': 'Servicio de mantenimiento preventivo y correctivo',
        }
        
        initial_count = ResourceItem.objects.count()
        response = authenticated_client.post(reverse('resource_create'), data=servicio_data, follow=True)
        
        assert ResourceItem.objects.count() == initial_count + 1
        created_service = ResourceItem.objects.get(code=servicio_data['code'])
        
        assert created_service.name == servicio_data['name']
        assert created_service.type_equipment is None
        assert created_service.brand == servicio_data['brand']
        assert created_service.code == servicio_data['code']
        assert created_service.stst_status_disponibility == servicio_data['stst_status_disponibility']
