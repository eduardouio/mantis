import pytest
from django.urls import reverse
from django.utils import timezone
from equipment.models import ResourceItem
from projects.models import Project, ProjectResourceItem, Partner
from accounts.models import CustomUserModel
from tests.BaseTestView import BaseTestView


@pytest.mark.django_db
class TestResourceItemDetailView(BaseTestView):

    @pytest.fixture
    def test_user(self, client_logged):
        # El usuario se crea en el fixture client_logged de BaseTestView
        return CustomUserModel.objects.get(email='eduardouio7@gmail.com')

    @pytest.fixture
    def sample_partner(self, test_user):
        # client_logged ya ha hecho login con test_user, crum lo detectará.
        return Partner.objects.create(
            business_tax_id="PART001",
            name="Test Partner Inc.",
            address="123 Test St"
            # created_by y updated_by se asignarán automáticamente por BaseModel
        )

    @pytest.fixture
    def sample_project(self, sample_partner, test_user):
        # Crear el proyecto con los campos mínimos necesarios
        # Basándome en los otros tests, parece que Project solo necesita partner y place
        project = Project(
            partner=sample_partner,
            place="Project Site A",
            start_date=timezone.now().date(),  # Añadir start_date
            end_date=timezone.now().date() + timezone.timedelta(days=30)  # Añadir end_date
        )
        # Asignar manualmente los campos de auditoría ya que crum podría no funcionar en tests
        project.id_user_created = test_user.pk
        project.id_user_updated = test_user.pk
        project.save()
        return project

    @pytest.fixture
    def sample_equipment(self, test_user):
        # Crear el equipo y asignar manualmente los campos de auditoría
        equipment = ResourceItem(
            name="Generator G1000",
            code="GEN001",
            brand="PowerMax",
            model="G1000",
            serial_number="SN-G1000-001",
            status='DISPONIBLE',
            is_active=True,
            capacidad=100,
            unidad_capacidad='LITROS'
        )
        # Asignar manualmente los campos de auditoría
        equipment.id_user_created = test_user.pk
        equipment.id_user_updated = test_user.pk
        equipment.save()
        return equipment

    @pytest.fixture
    def sample_equipment_with_assignment(self, sample_equipment, sample_project, test_user):
        # Asignación activa
        assignment1 = ProjectResourceItem(
            project=sample_project,
            resource_item=sample_equipment,
            start_date=timezone.now().date() - timezone.timedelta(days=10),
            end_date=timezone.now().date() + timezone.timedelta(days=20), # Termina en 20 días
            cost=1000.00,
            cost_manteinance=50.00,
            is_active=True
        )
        assignment1.id_user_created = test_user.pk
        assignment1.id_user_updated = test_user.pk
        assignment1.save()
        
        # Asignación histórica
        another_project_start_date = timezone.now().date() - timezone.timedelta(days=60)
        another_project = Project(
            partner=sample_project.partner,
            place="Project Site B",
            start_date=another_project_start_date, # Añadir start_date
            end_date=another_project_start_date + timezone.timedelta(days=30) # Añadir end_date
        )
        another_project.id_user_created = test_user.pk
        another_project.id_user_updated = test_user.pk
        another_project.save()
        
        assignment2 = ProjectResourceItem(
            project=another_project,
            resource_item=sample_equipment,
            start_date=timezone.now().date() - timezone.timedelta(days=60),
            end_date=timezone.now().date() - timezone.timedelta(days=30),
            cost=500.00,
            cost_manteinance=25.00,
            is_active=False
        )
        assignment2.id_user_created = test_user.pk
        assignment2.id_user_updated = test_user.pk
        assignment2.save()
        
        return sample_equipment

    @pytest.fixture
    def url(self, sample_equipment):
        return reverse('resource_detail', kwargs={'pk': sample_equipment.pk})

    def test_detail_view_uses_correct_template(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'presentations/equipment_presentation.html' in [
            t.name for t in response.templates]

    def test_detail_view_context_basic_info(self, client_logged, url, sample_equipment):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert response.context['equipment'] == sample_equipment
        assert response.context['title_section'] == f'Ficha de Equipo - {sample_equipment.name}'
        assert response.context['title_page'] == f'Ficha de Equipo - {sample_equipment.name}'
        assert 'today' in response.context

    def test_detail_view_action_parameter(self, client_logged, url):
        response_with_action = client_logged.get(url + '?action=delete')
        assert response_with_action.status_code == 200
        assert response_with_action.context['action'] == 'delete'

        response_no_action = client_logged.get(url)
        assert response_no_action.status_code == 200
        assert response_no_action.context['action'] is None

    def test_detail_view_context_equipment_statistics(self, client_logged, sample_equipment_with_assignment):
        url_detail = reverse('resource_detail', kwargs={
                             'pk': sample_equipment_with_assignment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200

        stats = response.context
        assert stats['total_projects'] == 2
        assert stats['active_projects'] == 1
        assert stats['historical_projects'] == 1
        assert stats['total_cost'] == 1500.00  # 1000 + 500
        assert stats['total_maintenance_cost'] == 75.00  # 50 + 25
        assert stats['total_revenue'] == 1575.00  # 1500 + 75

    def test_detail_view_context_project_information(self, client_logged, sample_equipment_with_assignment, sample_project):
        url_detail = reverse('resource_detail', kwargs={
                             'pk': sample_equipment_with_assignment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200

        project_info = response.context
        assert project_info['current_assignment'] is not None
        assert project_info['current_assignment'].project == sample_project
        assert project_info['current_assignment'].is_active is True
        assert len(project_info['recent_assignments']
                   ) == 2  # Muestra hasta 5, tenemos 2
        assert len(project_info['project_assignments']) == 2

    def test_detail_view_context_maintenance_information(self, client_logged, sample_equipment_with_assignment):
        url_detail = reverse('resource_detail', kwargs={
                             'pk': sample_equipment_with_assignment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200

        maint_info = response.context
        assert len(maint_info['maintenance_alerts']) == 1
        alert = maint_info['maintenance_alerts'][0]
        assert 'Proyecto termina en' in alert['message']  # Termina en 20 días
        assert alert['class'] == 'text-orange-600'  # > 7 días

        status_info = maint_info['status_info']
        assert status_info['status_class'] == 'text-green-600'  # DISPONIBLE
        assert status_info['needs_attention'] is False
        assert status_info['is_available'] is True

    def test_detail_view_maintenance_alert_near_end_date(self, client_logged, sample_equipment, sample_project, test_user):
        assignment = ProjectResourceItem(
            project=sample_project,
            resource_item=sample_equipment,
            start_date=timezone.now().date() - timezone.timedelta(days=2),
            end_date=timezone.now().date() + timezone.timedelta(days=5), # Termina en 5 días
            is_active=True,
            cost=100.00,  # Añadir cost
            cost_manteinance=10.00,  # Añadir cost_manteinance
            mantenance_frequency='DIARIO'  # Añadir mantenance_frequency
        )
        assignment.id_user_created = test_user.pk
        assignment.id_user_updated = test_user.pk
        assignment.save()
        
        url_detail = reverse('resource_detail', kwargs={'pk': sample_equipment.pk})
        response = client_logged.get(url_detail)
        maint_info = response.context['maintenance_alerts']
        assert len(maint_info) == 1
        assert 'Proyecto termina en 5 días' in maint_info[0]['message']
        assert maint_info[0]['class'] == 'text-red-600'  # <= 7 días

    def test_detail_view_status_class_logic(self, client_logged, sample_equipment):
        statuses_config = {
            'EN REPARACION': {'class': 'text-red-600', 'attention': True, 'available': False, 'motivo': 'Test repair'},
            'RENTADO': {'class': 'text-blue-600', 'attention': False, 'available': False},
            'FUERA DE SERVICIO': {'class': 'text-gray-600', 'attention': False, 'available': False},
            'DISPONIBLE': {'class': 'text-green-600', 'attention': False, 'available': True},
        }
        for status_code, config in statuses_config.items():
            sample_equipment.status = status_code
            if 'motivo' in config:
                sample_equipment.motivo_reparacion = config['motivo']
            else:
                sample_equipment.motivo_reparacion = None  # Limpiar por si acaso
            sample_equipment.save()

            url_detail = reverse('resource_detail', kwargs={
                                 'pk': sample_equipment.pk})
            response = client_logged.get(url_detail)
            assert response.status_code == 200
            status_info = response.context['status_info']

            assert status_info['status_class'] == config['class']
            assert status_info['needs_attention'] == config['attention']
            assert status_info['is_available'] == config['available']

    def test_detail_view_context_system_metadata(self, client_logged, url, sample_equipment, test_user):
        response = client_logged.get(url)
        assert response.status_code == 200

        metadata = response.context
        # Verificar que los campos de auditoría se asignaron correctamente
        assert sample_equipment.id_user_created == test_user.pk
        assert sample_equipment.id_user_updated == test_user.pk

        # Verificar que la vista retorna los usuarios correctos
        assert metadata['created_info']['user'] == test_user 
        assert metadata['updated_info']['user'] == test_user

        # Estos dependen de los valores por defecto o los que tenga el modelo ResourceItem
        assert metadata['system_info']['version'] == getattr(
            sample_equipment, 'version', '1.0')
        assert metadata['system_info']['last_sync'] == getattr(
            sample_equipment, 'last_sync', None)
        assert metadata['system_info']['system_notes'] == getattr(
            sample_equipment, 'system_notes', None)

    def test_detail_view_no_project_assignments(self, client_logged, sample_equipment):
        # sample_equipment se crea sin asignaciones inicialmente
        url_detail = reverse('resource_detail', kwargs={
                             'pk': sample_equipment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200

        assert response.context['total_projects'] == 0
        assert response.context['active_projects'] == 0
        assert response.context['current_assignment'] is None
        assert len(response.context['recent_assignments']) == 0

    def test_detail_view_no_maintenance_alerts(self, client_logged, sample_equipment, sample_project, test_user):
        # Crear una asignación que no genere alerta (termina en más de 30 días)
        assignment = ProjectResourceItem(
            project=sample_project,
            resource_item=sample_equipment,
            start_date=timezone.now().date() - timezone.timedelta(days=10),
            end_date=timezone.now().date() + timezone.timedelta(days=35),
            is_active=True,
            cost=200.00,  # Añadir cost
            cost_manteinance=20.00,  # Añadir cost_manteinance
            mantenance_frequency='SEMANAL'  # Añadir mantenance_frequency
        )
        assignment.id_user_created = test_user.pk
        assignment.id_user_updated = test_user.pk
        assignment.save()
        
        url_detail = reverse('resource_detail', kwargs={'pk': sample_equipment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200
        assert len(response.context['maintenance_alerts']) == 0

        # Limpiar asignaciones para el siguiente caso
        ProjectResourceItem.objects.filter(
            resource_item=sample_equipment).delete()

        # Probar sin ninguna asignación activa
        response_no_assign = client_logged.get(url_detail)
        assert response_no_assign.status_code == 200
        assert len(response_no_assign.context['maintenance_alerts']) == 0

    def test_detail_view_equipment_not_found(self, client_logged):
        url_non_existent = reverse('resource_detail', kwargs={
                                   'pk': 99999})  # ID improbable
        response = client_logged.get(url_non_existent)
        assert response.status_code == 404
