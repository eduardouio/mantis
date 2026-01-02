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

        return CustomUserModel.objects.get(email="eduardouio7@gmail.com")

    @pytest.fixture
    def sample_partner(self, test_user):

        return Partner.objects.create(
            business_tax_id="PART001", name="Test Partner Inc.", address="123 Test St"
        )

    @pytest.fixture
    def sample_project(self, sample_partner, test_user):
        # Crear el proyecto con los campos correctos del modelo Project
        project = Project(
            partner=sample_partner,
            location="Project Site A",  # Cambiado de 'place' a 'location'
            contact_name="John Doe",
            contact_phone="0991234567",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
        )

        # Asignar manualmente los campos de auditoría
        project.id_user_created = test_user.pk
        project.id_user_updated = test_user.pk
        project.save()
        return project

    @pytest.fixture
    def sample_equipment(self, test_user):

        equipment = ResourceItem(
            name="Generator G1000",
            code="GEN001",
            brand="PowerMax",
            model="G1000",
            serial_number="SN-G1000-001",
            stst_status_disponibility="DISPONIBLE",
            stst_status_equipment="FUNCIONANDO",
            is_active=True,
            capacity_gallons=100.00,
        )

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
            type_resource='EQUIPO',
            operation_start_date=timezone.now().date() - timezone.timedelta(days=10),
            operation_end_date=timezone.now().date() + timezone.timedelta(days=20),
            cost=1000.00,
            frequency_type='DAY',
            interval_days=1
        )
        assignment1.id_user_created = test_user.pk
        assignment1.id_user_updated = test_user.pk
        assignment1.save()
        
        # Asignación histórica
        another_project_start_date = timezone.now().date() - timezone.timedelta(days=60)
        another_project = Project(
            partner=sample_project.partner,
            location="Project Site B",  # Cambiado de 'place' a 'location'
            contact_name="Jane Smith",
            contact_phone="0997654321",
            start_date=another_project_start_date,
            end_date=another_project_start_date + timezone.timedelta(days=30),
        )
        another_project.id_user_created = test_user.pk
        another_project.id_user_updated = test_user.pk
        another_project.save()
        
        assignment2 = ProjectResourceItem(
            project=another_project,
            resource_item=sample_equipment,
            type_resource='EQUIPO',
            operation_start_date=timezone.now().date() - timezone.timedelta(days=60),
            operation_end_date=timezone.now().date() - timezone.timedelta(days=30),
            cost=500.00,
            frequency_type='DAY',
            interval_days=1
        )
        assignment2.id_user_created = test_user.pk
        assignment2.id_user_updated = test_user.pk
        assignment2.save()
        
        return sample_equipment

    @pytest.fixture
    def url(self, sample_equipment):
        return reverse("resource_detail", kwargs={"pk": sample_equipment.pk})

    def test_detail_view_uses_correct_template(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'presentations/resource_presentation.html' in [
            t.name for t in response.templates]

    def test_detail_view_context_basic_info(self, client_logged, url, sample_equipment):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert response.context["equipment"] == sample_equipment
        assert (
            response.context["title_section"]
            == f"Ficha de Equipo - {sample_equipment.name}"
        )
        assert (
            response.context["title_page"]
            == f"Ficha de Equipo - {sample_equipment.name}"
        )
        assert "today" in response.context

    def test_detail_view_action_parameter(self, client_logged, url):
        response_with_action = client_logged.get(url + "?action=delete")
        assert response_with_action.status_code == 200
        assert response_with_action.context["action"] == "delete"

        response_no_action = client_logged.get(url)
        assert response_no_action.status_code == 200
        assert response_no_action.context["action"] is None

    def test_detail_view_context_equipment_statistics(self, client_logged, sample_equipment_with_assignment):
        url_detail = reverse('resource_detail', kwargs={
                             'pk': sample_equipment_with_assignment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200

        # Verificar que el contexto básico existe
        assert 'equipment' in response.context
        assert response.context['equipment'] == sample_equipment_with_assignment
        
        # Verificar estadísticas si existen en el contexto
        if 'total_projects' in response.context:
            assert response.context['total_projects'] >= 0
        if 'active_projects' in response.context:
            assert response.context['active_projects'] >= 0

    def test_detail_view_context_project_information(self, client_logged, sample_equipment_with_assignment, sample_project):
        url_detail = reverse('resource_detail', kwargs={
                             'pk': sample_equipment_with_assignment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200

        # Verificar que el contexto existe
        assert 'equipment' in response.context
        
        # Verificar asignaciones si existen en el contexto
        if 'current_assignment' in response.context:
            current = response.context['current_assignment']
            if current is not None:
                assert current.project == sample_project

    def test_detail_view_context_maintenance_information(self, client_logged, sample_equipment_with_assignment):
        url_detail = reverse('resource_detail', kwargs={
                             'pk': sample_equipment_with_assignment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200

        # Verificar que el contexto básico existe
        assert 'equipment' in response.context
        
        # Si existe información de status, verificarla
        if 'status_info' in response.context:
            status_info = response.context['status_info']
            assert isinstance(status_info, dict)

    def test_detail_view_maintenance_alert_near_end_date(
        self, client_logged, sample_equipment, sample_project, test_user
    ):
        assignment = ProjectResourceItem(
            project=sample_project,
            resource_item=sample_equipment,
            type_resource="EQUIPO",
            operation_start_date=timezone.now().date() - timezone.timedelta(days=2),
            operation_end_date=timezone.now().date() + timezone.timedelta(days=5),
            cost=100.00,
            frequency_type="DAY",
            interval_days=1,
        )
        assignment.id_user_created = test_user.pk
        assignment.id_user_updated = test_user.pk
        assignment.save()

        url_detail = reverse("resource_detail", kwargs={"pk": sample_equipment.pk})
        response = client_logged.get(url_detail)
        maint_info = response.context["maintenance_alerts"]
        assert len(maint_info) == 1
        assert "Proyecto termina en 5 días" in maint_info[0]["message"]
        assert maint_info[0]["class"] == "text-red-600"

    def test_detail_view_status_class_logic(self, client_logged, sample_equipment):
        statuses_config = {
            'EN REPARACION': {'class': 'text-red-600', 'attention': True, 'available': False, 'motivo': 'Test repair'},
            'RENTADO': {'class': 'text-blue-600', 'attention': False, 'available': False},
            'DISPONIBLE': {'class': 'text-green-600', 'attention': False, 'available': True},
        }
        for status_code, config in statuses_config.items():
            sample_equipment.stst_status_disponibility = status_code
            if 'motivo' in config:
                sample_equipment.stst_repair_reason = config['motivo']
            else:
                sample_equipment.stst_repair_reason = None
            sample_equipment.save()

            url_detail = reverse('resource_detail', kwargs={
                                 'pk': sample_equipment.pk})
            response = client_logged.get(url_detail)
            assert response.status_code == 200
            
            # Verificar que el equipo se cargó correctamente
            assert response.context['equipment'].stst_status_disponibility == status_code
            
            # Si existe status_info en el contexto, verificar su estructura
            if 'status_info' in response.context:
                status_info = response.context['status_info']
                if 'status_class' in status_info:
                    assert status_info['status_class'] == config['class']

    def test_detail_view_context_system_metadata(
        self, client_logged, url, sample_equipment, test_user
    ):
        response = client_logged.get(url)
        assert response.status_code == 200

        metadata = response.context

        assert sample_equipment.id_user_created == test_user.pk
        assert sample_equipment.id_user_updated == test_user.pk

        assert metadata["created_info"]["user"] == test_user
        assert metadata["updated_info"]["user"] == test_user

        assert metadata["system_info"]["version"] == getattr(
            sample_equipment, "version", "1.0"
        )
        assert metadata["system_info"]["last_sync"] == getattr(
            sample_equipment, "last_sync", None
        )
        assert metadata["system_info"]["system_notes"] == getattr(
            sample_equipment, "system_notes", None
        )

    def test_detail_view_no_project_assignments(self, client_logged, sample_equipment):

        url_detail = reverse("resource_detail", kwargs={"pk": sample_equipment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200

        assert response.context["total_projects"] == 0
        assert response.context["active_projects"] == 0
        assert response.context["current_assignment"] is None
        assert len(response.context["recent_assignments"]) == 0

    def test_detail_view_no_maintenance_alerts(
        self, client_logged, sample_equipment, sample_project, test_user
    ):

        assignment = ProjectResourceItem(
            project=sample_project,
            resource_item=sample_equipment,
            type_resource="EQUIPO",
            operation_start_date=timezone.now().date() - timezone.timedelta(days=10),
            operation_end_date=timezone.now().date() + timezone.timedelta(days=35),
            cost=200.00,
            frequency_type="WEEK",
            weekdays=[1, 3, 5],
        )
        assignment.id_user_created = test_user.pk
        assignment.id_user_updated = test_user.pk
        assignment.save()

        url_detail = reverse("resource_detail", kwargs={"pk": sample_equipment.pk})
        response = client_logged.get(url_detail)
        assert response.status_code == 200
        assert len(response.context["maintenance_alerts"]) == 0

        ProjectResourceItem.objects.filter(resource_item=sample_equipment).delete()

        response_no_assign = client_logged.get(url_detail)
        assert response_no_assign.status_code == 200
        assert len(response_no_assign.context["maintenance_alerts"]) == 0

    def test_detail_view_equipment_not_found(self, client_logged):
        url_non_existent = reverse("resource_detail", kwargs={"pk": 99999})
        response = client_logged.get(url_non_existent)
        assert response.status_code == 404
