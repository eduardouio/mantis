import pytest
from django.urls import reverse
from django.test import RequestFactory, Client
from django.contrib.messages.storage.fallback import FallbackStorage
from accounts.models import CustomUserModel

from equipment.views.resources.ResourceItemCreateView import ResourceItemCreateView
from equipment.models.ResourceItem import ResourceItem
from equipment.forms.ResourceItemForm import ResourceItemForm


@pytest.mark.django_db
class TestResourceItemCreateView:

    @pytest.fixture
    def setup_user(self):
        # Crear un usuario para las pruebas usando el modelo personalizado
        # Solo pasamos email y password, que son los campos requeridos
        user = CustomUserModel.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
        return user

    @pytest.fixture
    def authenticated_client(self, setup_user):
        # Cliente con sesión iniciada
        client = Client()

        # En Django, authentication_backends puede estar configurado para autenticar de manera diferente
        # Vamos a forzar la autenticación directamente
        client.force_login(setup_user)
        return client

    @pytest.fixture
    def valid_equipment_data(self):
        # Datos válidos para crear un equipo
        return {
            'name': 'Lavamanos Portátil',
            'type': 'EQUIPO',
            'subtype': 'LAVAMANOS',  # Valor correcto según el modelo
            'brand': 'Tecniaguas',
            'code': 'LAV-001',
            'status': 'DISPONIBLE',  # Campo requerido
            'height': '120',
            'width': '60',
            'depth': '50',
            'weight': '35'
        }

    def test_login_required(self):
        # Verificar que la vista requiere autenticación
        client = Client()
        response = client.get(reverse('resource_create'))
        assert response.status_code == 302  # Redirección a página de login
        assert '/accounts/login/' in response.url

    def test_get_context_data(self, authenticated_client):
        # Verificar que el contexto contiene los títulos correctos
        # Usando un cliente autenticado para evitar el error de request
        response = authenticated_client.get(reverse('resource_create'))

        # Verificar primero que la respuesta sea exitosa
        assert response.status_code == 200

        # Comprobar el contexto de la respuesta
        assert 'title_section' in response.context
        assert response.context['title_section'] == 'Registrar Nuevo Equipo'
        assert response.context['title_page'] == 'Registrar Nuevo Equipo'

    def test_get_success_url(self):
        # Verificar la URL de redirección después de crear un equipo
        view = ResourceItemCreateView()
        view.object = ResourceItem.objects.create(
            name='Equipo Test',
            type='EQUIPO',
            code='TEST-001',
            status='DISPONIBLE'
        )

        success_url = view.get_success_url()
        expected_url = f'/equipo/{view.object.pk}/?action=created'

        assert 'action=created' in success_url
        assert str(view.object.pk) in success_url

    def test_get_request_renders_correct_template(self, authenticated_client):
        # Verificar que se renderiza el template correcto
        response = authenticated_client.get(reverse('resource_create'))

        assert response.status_code == 200
        assert 'forms/equipment_form.html' in [
            t.name for t in response.templates]

    def test_create_equipment_successfully(self, authenticated_client, valid_equipment_data):
        # Contar equipos antes de la prueba
        initial_count = ResourceItem.objects.count()

        # Asegurarse que el código sea único (para evitar conflictos con datos existentes)
        import uuid
        unique_code = f"TEST-{uuid.uuid4().hex[:8]}"
        valid_equipment_data['code'] = unique_code

        # Verificar la creación exitosa de un equipo
        response = authenticated_client.post(
            reverse('resource_create'),
            data=valid_equipment_data,
            follow=True
        )

        # Si hay errores de formulario, imprimir para depurar
        if response.status_code == 200 and 'form' in response.context and response.context['form'].errors:
            print("Errores del formulario:", response.context['form'].errors)

        # Verificar que se creó un nuevo equipo
        assert ResourceItem.objects.count() == initial_count + 1

        # Verificar que el equipo creado tiene el código esperado
        assert ResourceItem.objects.filter(code=unique_code).exists()

        # Obtener el equipo recién creado
        created_equipment = ResourceItem.objects.get(code=unique_code)

        # Verificar que los datos del equipo son correctos
        assert created_equipment.name == valid_equipment_data['name']
        assert created_equipment.type == valid_equipment_data['type']
        assert created_equipment.subtype == valid_equipment_data['subtype']

        # Verificar la redirección a la página de detalles
        assert response.redirect_chain[0][0].startswith(
            f'/equipos/{created_equipment.pk}/')
        assert 'action=created' in response.redirect_chain[0][0]

    def test_form_validation_error(self, authenticated_client):
        # Verificar validación de formulario con datos inválidos
        invalid_data = {
            'name': '',  # Nombre vacío (campo requerido)
            'type': 'EQUIPO',
            'status': 'DISPONIBLE'
        }

        # Contar equipos antes de intentar crear uno inválido
        initial_count = ResourceItem.objects.count()

        response = authenticated_client.post(
            reverse('resource_create'),
            data=invalid_data
        )

        # Verificar que no se creó ningún equipo nuevo
        assert ResourceItem.objects.count() == initial_count

        # Verificar que se muestra el formulario con errores
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        assert 'name' in response.context['form'].errors

    def test_form_subtype_specific_validation(self, authenticated_client):
        # Probar la validación específica para plantas de tratamiento
        # (que requiere capacidad)
        planta_data = {
            'name': 'Planta de Tratamiento X',
            'type': 'EQUIPO',
            'subtype': 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL',  # Verificado en el modelo
            'brand': 'AquaPure',
            'code': 'PT-001',
            'status': 'DISPONIBLE',
            # Falta plant_capacity que es obligatorio para este subtipo
        }

        # Contar equipos antes de intentar crear uno inválido
        initial_count = ResourceItem.objects.count()

        response = authenticated_client.post(
            reverse('resource_create'),
            data=planta_data
        )

        # Verificar que no se creó el equipo
        assert ResourceItem.objects.count() == initial_count

        # Añadir el campo faltante y verificar que ahora sí se crea
        planta_data['plant_capacity'] = '25M3'  # Valor correcto según CAPACIDAD_PLANTA_CHOICES

        response = authenticated_client.post(
            reverse('resource_create'),
            data=planta_data,
            follow=True
        )

        # Ahora debería crearse correctamente
        assert ResourceItem.objects.filter(name=planta_data['name']).exists()
        
    def test_lavamanos_creation(self, authenticated_client):
        """Test para creación de equipo tipo lavamanos"""
        import uuid
        
        # Datos para lavamanos con sus características específicas
        lavamanos_data = {
            'name': 'Lavamanos Test',
            'type': 'EQUIPO',
            'subtype': 'LAVAMANOS',
            'brand': 'Tecniaguas',
            'code': f'LAV-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'height': '100',
            'width': '60',
            'depth': '50',
            'weight': '35',
            'foot_pumps': 'on',  # Bomba de lavamanos
            'sink_soap_dispenser': 'on',  # Dispensador de jabón
            'paper_towels': 'on',  # Servilletas
        }
        
        initial_count = ResourceItem.objects.count()
        
        response = authenticated_client.post(
            reverse('resource_create'),
            data=lavamanos_data,
            follow=True
        )
        
        # Verificar que se creó el equipo
        assert ResourceItem.objects.count() == initial_count + 1
        
        # Obtener el equipo creado
        created_equipment = ResourceItem.objects.get(code=lavamanos_data['code'])
        
        # Verificar características específicas
        assert created_equipment.foot_pumps is True
        assert created_equipment.sink_soap_dispenser is True
        assert created_equipment.paper_towels is True
        
    def test_bateria_sanitaria_mujer_creation(self, authenticated_client):
        """Test para creación de equipo tipo bateria sanitaria mujer"""
        import uuid
        
        # Datos para bateria sanitaria mujer con sus características específicas
        bateria_data = {
            'name': 'Bateria Sanitaria Mujer Test',
            'type': 'EQUIPO',
            'subtype': 'BATERIA SANITARIA MUJER',
            'brand': 'Portasanit',
            'code': f'BSM-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'height': '220',
            'width': '110',
            'depth': '110',
            'weight': '80',
            'paper_dispenser': 'on',  # Dispensador de papel
            'soap_dispenser': 'on',  # Dispensador de jabón
            'napkin_dispenser': 'on',  # Dispensador de servilletas
            'seats': 'on',  # Asientos
            'toilet_pump': 'on',  # Bomba de baño
            'sink_pump': 'on',  # Bomba de lavamanos
            'toilet_lid': 'on',  # Tapa inodoro
            'bathroom_bases': 'on',  # Bases baños
            'ventilation_pipe': 'on',  # Tubo ventilación
        }
        
        initial_count = ResourceItem.objects.count()
        
        response = authenticated_client.post(
            reverse('resource_create'),
            data=bateria_data,
            follow=True
        )
        
        # Verificar que se creó el equipo
        assert ResourceItem.objects.count() == initial_count + 1
        
        # Obtener el equipo creado
        created_equipment = ResourceItem.objects.get(code=bateria_data['code'])
        
        # Verificar características específicas
        assert created_equipment.paper_dispenser is True
        assert created_equipment.soap_dispenser is True
        assert created_equipment.napkin_dispenser is True
        assert created_equipment.seats is True
        assert created_equipment.toilet_pump is True
        assert created_equipment.sink_pump is True
        assert created_equipment.toilet_lid is True
        assert created_equipment.bathroom_bases is True
        assert created_equipment.ventilation_pipe is True
        
    def test_planta_tratamiento_creation(self, authenticated_client):
        """Test para creación de equipo tipo planta de tratamiento de agua"""
        import uuid
        
        # Datos para planta de tratamiento con sus características específicas
        planta_data = {
            'name': 'Planta de Tratamiento Test',
            'type': 'EQUIPO',
            'subtype': 'PLANTA DE TRATAMIENTO DE AGUA',
            'brand': 'AquaPure',
            'code': f'PTA-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'height': '180',
            'width': '150',
            'depth': '150',
            'weight': '200',
            'plant_capacity': '10M3',  # Capacidad de la planta
            'belt_type': 'A',  # Tipo de banda
            'blower_brand': 'BlowerTech',  # Marca del blower
            'blower_model': 'BT-2000',  # Modelo del blower
            'engine_brand': 'MotorMax',  # Marca del motor
            'engine_model': 'MM-500',  # Modelo del motor
            'belt_brand': 'BeltPro',  # Marca de la banda
            'belt_model': 'BP-100A',  # Modelo de la banda
            'blower_pulley_brand': 'PulleyTech',  # Marca de pulley del blower
            'blower_pulley_model': 'PT-A200',  # Modelo de pulley del blower
            'motor_pulley_brand': 'PulleyPro',  # Marca de pulley del motor
            'motor_pulley_model': 'PP-A150',  # Modelo de pulley del motor
            'electrical_panel_brand': 'ElecPanel',  # Marca del panel eléctrico
            'electrical_panel_model': 'EP-2000',  # Modelo del panel eléctrico
            'motor_guard_brand': 'GuardTech',  # Marca de guarda motor
            'motor_guard_model': 'GT-500',  # Modelo de guarda motor
        }
        
        initial_count = ResourceItem.objects.count()
        
        response = authenticated_client.post(
            reverse('resource_create'),
            data=planta_data,
            follow=True
        )
        
        # Verificar que se creó el equipo
        assert ResourceItem.objects.count() == initial_count + 1
        
        # Obtener el equipo creado
        created_equipment = ResourceItem.objects.get(code=planta_data['code'])
        
        # Verificar características específicas
        assert created_equipment.plant_capacity == '10M3'
        assert created_equipment.belt_type == 'A'
        assert created_equipment.blower_brand == 'BlowerTech'
        assert created_equipment.engine_brand == 'MotorMax'
        assert created_equipment.electrical_panel_brand == 'ElecPanel'
        assert created_equipment.motor_guard_brand == 'GuardTech'
        
    def test_camper_bano_creation(self, authenticated_client):
        """Test para creación de equipo tipo camper baño"""
        import uuid
        
        # Datos para camper baño con sus características específicas
        # Comparte los campos de bateria sanitaria hombre/mujer
        camper_data = {
            'name': 'Camper Baño Test',
            'type': 'EQUIPO',
            'subtype': 'CAMPER BAÑO',
            'brand': 'CamperTech',
            'code': f'CAM-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'height': '250',
            'width': '200',
            'depth': '200',
            'weight': '350',
            'paper_dispenser': 'on',  # Dispensador de papel
            'soap_dispenser': 'on',  # Dispensador de jabón
            'napkin_dispenser': 'on',  # Dispensador de servilletas
            'urinals': 'on',  # Urinales
            'seats': 'on',  # Asientos
            'toilet_pump': 'on',  # Bomba de baño
            'sink_pump': 'on',  # Bomba de lavamanos
            'toilet_lid': 'on',  # Tapa inodoro
            'bathroom_bases': 'on',  # Bases baños
            'ventilation_pipe': 'on',  # Tubo ventilación
        }
        
        initial_count = ResourceItem.objects.count()
        
        response = authenticated_client.post(
            reverse('resource_create'),
            data=camper_data,
            follow=True
        )
        
        # Verificar que se creó el equipo
        assert ResourceItem.objects.count() == initial_count + 1
        
        # Obtener el equipo creado
        created_equipment = ResourceItem.objects.get(code=camper_data['code'])
        
        # Verificar características específicas
        assert created_equipment.paper_dispenser is True
        assert created_equipment.soap_dispenser is True
        assert created_equipment.napkin_dispenser is True
        assert created_equipment.urinals is True
        assert created_equipment.seats is True
        assert created_equipment.toilet_pump is True
        assert created_equipment.sink_pump is True
        assert created_equipment.toilet_lid is True
        assert created_equipment.bathroom_bases is True
        assert created_equipment.ventilation_pipe is True
        
    def test_estacion_cuadruple_urinario_creation(self, authenticated_client):
        """Test para creación de equipo tipo estación cuádruple urinario"""
        import uuid
        
        # Datos para estación cuádruple urinario con sus características específicas
        # Según la documentación, sólo tiene campos base
        urinario_data = {
            'name': 'Estación Cuádruple Urinario Test',
            'type': 'EQUIPO',
            'subtype': 'ESTACION CUADRUPLE URINARIO',
            'brand': 'UrinarioTech',
            'code': f'URI-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            'height': '150',
            'width': '100',
            'depth': '50',
            'weight': '45',
        }
        
        initial_count = ResourceItem.objects.count()
        
        response = authenticated_client.post(
            reverse('resource_create'),
            data=urinario_data,
            follow=True
        )
        
        # Verificar que se creó el equipo
        assert ResourceItem.objects.count() == initial_count + 1
        
        # Obtener el equipo creado
        created_equipment = ResourceItem.objects.get(code=urinario_data['code'])
        
        # Verificar campos básicos
        assert created_equipment.name == urinario_data['name']
        assert created_equipment.brand == urinario_data['brand']
        assert created_equipment.height == int(urinario_data['height'])
        assert created_equipment.width == int(urinario_data['width'])
        assert created_equipment.depth == int(urinario_data['depth'])
        assert created_equipment.weight == int(urinario_data['weight'])
        assert created_equipment.status == urinario_data['status']
        
    def test_servicio_creation(self, authenticated_client):
        """Test para creación de tipo servicio"""
        import uuid
        
        # Datos para servicio - usa el mismo modelo que equipos pero con tipo SERVICIO
        servicio_data = {
            'name': 'Servicio de Mantenimiento',
            'type': 'SERVICIO',  # Tipo servicio en lugar de equipo
            # No especificamos subtype ya que el modelo solo permite subtipos de equipos
            # El campo subtype admite null/blank=True
            'brand': 'PEISOL',  # Marca propia para servicios
            'code': f'SRV-{uuid.uuid4().hex[:8]}',
            'status': 'DISPONIBLE',
            # Los servicios no necesitan dimensiones físicas, pero el modelo las requiere
            'height': '0',
            'width': '0',
            'depth': '0',
            'weight': '0',
            'description': 'Servicio de mantenimiento preventivo y correctivo',
            'base_price': '250.00',  # Precio base del servicio
        }
        
        initial_count = ResourceItem.objects.count()
        
        response = authenticated_client.post(
            reverse('resource_create'),
            data=servicio_data,
            follow=True
        )
        
        # Verificar que se creó el servicio
        assert ResourceItem.objects.count() == initial_count + 1
        
        # Obtener el servicio creado
        created_service = ResourceItem.objects.get(code=servicio_data['code'])
        
        # Verificar campos básicos
        assert created_service.name == servicio_data['name']
        assert created_service.type == 'SERVICIO'
        assert created_service.subtype is None  # Para servicios, subtype debe ser None
        assert created_service.brand == servicio_data['brand']
        assert created_service.code == servicio_data['code']
        assert created_service.status == servicio_data['status']
