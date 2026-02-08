import pytest
import json
from django.test import Client
from datetime import date, time, timedelta
from decimal import Decimal

from accounts.models import CustomUserModel
from accounts.models.Technical import Technical
from projects.models import Project, ProjectResourceItem, Partner
from projects.models.SheetProject import SheetProject
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from equipment.models import ResourceItem
from equipment.models.Vehicle import Vehicle


@pytest.mark.django_db
class TestAllInfoProjectAPI:
    """Tests para el endpoint de información completa de proyectos"""

    @pytest.fixture
    def client_logged(self):
        """Cliente autenticado para las pruebas"""
        user, created = CustomUserModel.objects.get_or_create(
            email="test@example.com",
            defaults={
                "first_name": "Test",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        client = Client(raise_request_exception=False)
        client.force_login(user)
        return client

    @pytest.fixture
    def test_user(self):
        """Usuario de prueba para los campos de auditoría"""
        user, created = CustomUserModel.objects.get_or_create(
            email="test@example.com",
            defaults={
                "first_name": "Test",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        return user

    @pytest.fixture
    def test_partner(self, test_user):
        """Partner de prueba"""
        return Partner.objects.create(
            name="ASESORIA Y REPRESENTACIONES COMERCIALES ARCOLANDS CIA.LTDA.",
            business_tax_id="1234567890001",
            email="empresa@test.com",
            phone="0999999999",
            address="Quito, Ecuador",
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    @pytest.fixture
    def test_project(self, test_partner, test_user):
        """Proyecto de prueba"""
        return Project.objects.create(
            partner=test_partner,
            location="MDC 40 / Sacha",
            contact_name="Ing. Catalina Velandia",
            contact_phone="+593984066240",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    @pytest.fixture
    def test_resource(self, test_user):
        """Recurso de prueba"""
        return ResourceItem.objects.create(
            name="Mantenimiento Y Limpieza General",
            code="MNT-001",
            type_equipment="SERVICIO",
            brand="PEISOL",
            model="STD-2024",
            stst_status_equipment="FUNCIONANDO",
            stst_status_disponibility="DISPONIBLE",
            stst_current_location="BASE PEISOL",
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    @pytest.fixture
    def test_technical(self, test_user):
        """Técnico de prueba"""
        return Technical.objects.create(
            first_name="JINSON ADRIAN",
            last_name="CEDEÑO GARCIA",
            dni="2101112353",
            email="jinson@test.com",
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    @pytest.fixture
    def test_vehicle(self, test_user):
        """Vehículo de prueba"""
        return Vehicle.objects.create(
            no_plate=f"PFH{date.today().strftime('%Y%m%d%H%M%S')[-6:]}",
            brand="FOTON",
            model="AUMARCK S BJ1088 AC 3.8 2P 4X2 TM",
            year=2020,
            type_vehicle="CAMION",
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    @pytest.fixture
    def test_project_resource(self, test_project, test_resource, test_user):
        """Recurso asociado al proyecto"""
        return ProjectResourceItem.objects.create(
            project=test_project,
            resource_item=test_resource,
            type_resource="SERVICIO",
            cost=150.00,
            frequency_type="DAY",
            interval_days=1,
            operation_start_date=date.today(),
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    @pytest.fixture
    def test_sheet_project(self, test_project, test_user):
        """Planilla de proyecto de prueba"""
        return SheetProject.objects.create(
            project=test_project,
            series_code="PSL-PS-2026-1001",
            period_start=date.today(),
            status="IN_PROGRESS",
            service_type="ALQUILER Y MANTENIMIENTO",
            contact_reference="Ing. Catalina Velandia",
            contact_phone_reference="+593984066240",
            subtotal=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total=Decimal("0.00"),
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    @pytest.fixture
    def test_custody_chain(self, test_sheet_project, test_technical, test_vehicle, test_user):
        """Cadena de custodia de prueba"""
        return CustodyChain.objects.create(
            sheet_project=test_sheet_project,
            technical=test_technical,
            vehicle=test_vehicle,
            consecutive="0000001",
            activity_date=date.today(),
            location="MDC 40 / Sacha",
            issue_date=date.today(),
            start_time=time(10, 2, 0),
            end_time=time(0, 3, 0),
            time_duration=Decimal("0.0"),
            contact_name="Ing. Catalina Velandia",
            dni_contact="",
            contact_position="",
            date_contact=date.today(),
            driver_name="JINSON ADRIAN CEDEÑO GARCIA",
            dni_driver="2101112353",
            driver_position="Proyectos de Plantas de tratamiento de agua",
            driver_date=date.today(),
            total_gallons=200,
            total_barrels=4,
            total_cubic_meters=0,
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    @pytest.fixture
    def test_chain_detail(self, test_custody_chain, test_project_resource, test_user):
        """Detalle de cadena de custodia"""
        return ChainCustodyDetail.objects.create(
            custody_chain=test_custody_chain,
            project_resource=test_project_resource,
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

    def test_get_all_info_success(
        self,
        client_logged,
        test_project,
        test_sheet_project,
        test_custody_chain,
        test_chain_detail,
    ):
        """Test obtener información completa de un proyecto exitosamente"""
        url = f"/api/projects/all-info/{test_project.id}/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Validar estructura principal
        assert data["success"] is True
        assert "data" in data
        
        # Validar estructura completa del proyecto
        assert "project" in data["data"]
        project_fields = [
            "id", "partner_id", "partner_name", "location", "cardinal_point",
            "contact_name", "contact_phone", "start_date", "end_date", "is_closed"
        ]
        for field in project_fields:
            assert field in data["data"]["project"], f"Campo '{field}' faltante en project"
        
        # Validar estructura de work_orders
        assert "work_orders" in data["data"]
        assert "work_orders_count" in data["data"]
        assert isinstance(data["data"]["work_orders"], list)
        assert len(data["data"]["work_orders"]) == 1
        
        work_order = data["data"]["work_orders"][0]
        # Validar campos de work_order
        required_wo_fields = [
            "id", "series_code", "issue_date", "period_start", "period_end",
            "status", "service_type", "total_gallons", "total_barrels",
            "total_cubic_meters", "client_po_reference", "contact_reference",
            "contact_phone_reference", "final_disposition_reference",
            "invoice_reference", "subtotal", "tax_amount", "total",
            "custody_chains", "custody_chains_count", "metadata"
        ]
        for field in required_wo_fields:
            assert field in work_order, f"Campo '{field}' faltante en work_order"
        
        # Validar estructura de custody_chains
        assert isinstance(work_order["custody_chains"], list)
        assert len(work_order["custody_chains"]) == 1
        
        chain = work_order["custody_chains"][0]
        # Validar campos de custody_chain
        required_chain_fields = [
            "id", "consecutive", "activity_date", "location", "issue_date",
            "start_time", "end_time", "time_duration", "contact_name",
            "dni_contact", "contact_position", "date_contact", "driver_name",
            "dni_driver", "driver_position", "driver_date", "total_gallons",
            "total_barrels", "total_cubic_meters", "sheet_project_id",
            "technical", "vehicle", "details", "details_count", "metadata"
        ]
        for field in required_chain_fields:
            assert field in chain, f"Campo '{field}' faltante en custody_chain"
        
        # Validar estructura de technical
        if chain["technical"] is not None:
            assert "id" in chain["technical"]
            assert "first_name" in chain["technical"]
            assert "last_name" in chain["technical"]
        
        # Validar estructura de vehicle
        if chain["vehicle"] is not None:
            assert "id" in chain["vehicle"]
            assert "no_plate" in chain["vehicle"]
            assert "brand" in chain["vehicle"]
            assert "model" in chain["vehicle"]
        
        # Validar estructura de details
        assert isinstance(chain["details"], list)
        assert len(chain["details"]) == 1
        
        detail = chain["details"][0]
        assert "id" in detail
        assert "project_resource_id" in detail
        assert "project_resource" in detail
        assert "metadata" in detail
        
        # Validar estructura de project_resource
        pr = detail["project_resource"]
        assert "id" in pr
        assert "resource_item_id" in pr
        assert "resource_item_name" in pr
        
        # Validar estructura de metadata
        metadata_fields = [
            "notes", "created_at", "updated_at", "is_active",
            "is_deleted", "id_user_created", "id_user_updated"
        ]
        for field in metadata_fields:
            assert field in chain["metadata"], f"Campo '{field}' faltante en metadata"
            assert field in detail["metadata"], f"Campo '{field}' faltante en detail metadata"
        
        # Validar contadores
        assert "total_custody_chains" in data["data"]
        assert isinstance(data["data"]["total_custody_chains"], int)

    def test_get_all_info_project_not_found(self, client_logged):
        """Test obtener información de proyecto inexistente"""
        url = "/api/projects/all-info/99999/"
        response = client_logged.get(url)

        assert response.status_code == 404

    def test_get_all_info_project_no_work_orders(self, client_logged, test_project):
        """Test proyecto sin planillas - validar solo estructura de respuesta"""
        url = f"/api/projects/all-info/{test_project.id}/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Validar estructura básica
        assert "success" in data
        assert data["success"] is True
        assert "data" in data
        
        # Validar que tenga las claves principales del proyecto
        assert "project" in data["data"]
        project_fields = [
            "id", "partner_id", "partner_name", "location", "cardinal_point",
            "contact_name", "contact_phone", "start_date", "end_date", "is_closed"
        ]
        for field in project_fields:
            assert field in data["data"]["project"]
        
        # Validar work_orders
        assert "work_orders" in data["data"]
        assert "work_orders_count" in data["data"]
        assert "total_custody_chains" in data["data"]
        
        # Validar que estén vacías
        assert isinstance(data["data"]["work_orders"], list)
        assert len(data["data"]["work_orders"]) == 0
        assert data["data"]["work_orders_count"] == 0
        assert data["data"]["total_custody_chains"] == 0

    def test_get_all_info_multiple_custody_chains(
        self,
        client_logged,
        test_project,
        test_sheet_project,
        test_custody_chain,
        test_chain_detail,
        test_technical,
        test_vehicle,
        test_project_resource,
        test_user,
    ):
        """Test proyecto con múltiples cadenas de custodia"""
        # Crear segunda cadena de custodia
        custody_chain_2 = CustodyChain.objects.create(
            sheet_project=test_sheet_project,
            technical=test_technical,
            vehicle=test_vehicle,
            consecutive="0000002",
            activity_date=date.today() - timedelta(days=1),
            location="MDC 40 / Sacha",
            issue_date=date.today() - timedelta(days=1),
            total_gallons=150,
            total_barrels=3,
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )
        ChainCustodyDetail.objects.create(
            custody_chain=custody_chain_2,
            project_resource=test_project_resource,
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

        url = f"/api/projects/all-info/{test_project.id}/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data["success"] is True
        work_order = data["data"]["work_orders"][0]
        assert len(work_order["custody_chains"]) == 2
        assert work_order["custody_chains_count"] == 2
        assert data["data"]["total_custody_chains"] == 2

    def test_get_all_info_chain_without_technical(
        self,
        client_logged,
        test_project,
        test_sheet_project,
        test_vehicle,
        test_project_resource,
        test_user,
    ):
        """Test cadena de custodia sin técnico asignado"""
        custody_chain = CustodyChain.objects.create(
            sheet_project=test_sheet_project,
            technical=None,
            vehicle=test_vehicle,
            consecutive="0000001",
            activity_date=date.today(),
            location="MDC 40 / Sacha",
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )
        ChainCustodyDetail.objects.create(
            custody_chain=custody_chain,
            project_resource=test_project_resource,
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

        url = f"/api/projects/all-info/{test_project.id}/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        
        chain = data["data"]["work_orders"][0]["custody_chains"][0]
        assert "technical" in chain
        assert chain["technical"] is None

    def test_get_all_info_chain_without_vehicle(
        self,
        client_logged,
        test_project,
        test_sheet_project,
        test_technical,
        test_project_resource,
        test_user,
    ):
        """Test cadena de custodia sin vehículo asignado"""
        custody_chain = CustodyChain.objects.create(
            sheet_project=test_sheet_project,
            technical=test_technical,
            vehicle=None,
            consecutive="0000001",
            activity_date=date.today(),
            location="MDC 40 / Sacha",
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )
        ChainCustodyDetail.objects.create(
            custody_chain=custody_chain,
            project_resource=test_project_resource,
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

        url = f"/api/projects/all-info/{test_project.id}/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        
        chain = data["data"]["work_orders"][0]["custody_chains"][0]
        assert "vehicle" in chain
        assert chain["vehicle"] is None

    def test_get_all_info_filters_deleted_records(
        self,
        client_logged,
        test_project,
        test_sheet_project,
        test_custody_chain,
        test_chain_detail,
    ):
        """Test que filtra correctamente registros eliminados"""
        test_custody_chain.is_deleted = True
        test_custody_chain.save()

        url = f"/api/projects/all-info/{test_project.id}/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        
        work_order = data["data"]["work_orders"][0]
        assert len(work_order["custody_chains"]) == 0
        assert work_order["custody_chains_count"] == 0

    def test_get_all_info_multiple_work_orders(
        self,
        client_logged,
        test_project,
        test_sheet_project,
        test_user,
    ):
        """Test proyecto con múltiples planillas - validar estructura"""
        SheetProject.objects.create(
            project=test_project,
            series_code="PSL-PS-2026-1002",
            period_start=date.today() - timedelta(days=30),
            period_end=date.today() - timedelta(days=1),
            status="INVOICED",
            service_type="ALQUILER",
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

        url = f"/api/projects/all-info/{test_project.id}/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Validar estructura
        assert "success" in data
        assert data["success"] is True
        assert "data" in data
        assert "work_orders" in data["data"]
        assert "work_orders_count" in data["data"]
        
        # Validar que hay múltiples work_orders
        assert isinstance(data["data"]["work_orders"], list)
        assert len(data["data"]["work_orders"]) == 2
        assert data["data"]["work_orders_count"] == 2

    def test_get_all_info_chain_with_multiple_details(
        self,
        client_logged,
        test_project,
        test_sheet_project,
        test_custody_chain,
        test_chain_detail,
        test_resource,
        test_user,
    ):
        """Test cadena de custodia con múltiples detalles"""
        # Crear segundo recurso y detalle
        resource_2 = ResourceItem.objects.create(
            name="Servicio Adicional",
            code="SRV-002",
            type_equipment="SERVICIO",
            stst_status_equipment="FUNCIONANDO",
            stst_status_disponibility="DISPONIBLE",
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )
        project_resource_2 = ProjectResourceItem.objects.create(
            project=test_project,
            resource_item=resource_2,
            type_resource="SERVICIO",
            cost=100.00,
            operation_start_date=date.today(),
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )
        ChainCustodyDetail.objects.create(
            custody_chain=test_custody_chain,
            project_resource=project_resource_2,
            id_user_created=test_user.id,
            id_user_updated=test_user.id,
        )

        url = f"/api/projects/all-info/{test_project.id}/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        
        chain = data["data"]["work_orders"][0]["custody_chains"][0]
        assert len(chain["details"]) == 2
        assert chain["details_count"] == 2

    def test_get_all_info_response_structure_types(
        self,
        client_logged,
        test_project,
        test_sheet_project,
        test_custody_chain,
        test_chain_detail,
    ):
        """Test validar tipos de datos en la respuesta"""
        url = f"/api/projects/all-info/{test_project.id}/"
        response = client_logged.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Validar tipos principales
        assert isinstance(data["success"], bool)
        assert isinstance(data["data"], dict)
        assert isinstance(data["data"]["project"], dict)
        assert isinstance(data["data"]["work_orders"], list)
        assert isinstance(data["data"]["work_orders_count"], int)
        assert isinstance(data["data"]["total_custody_chains"], int)
        
        # Validar tipos del proyecto
        project = data["data"]["project"]
        assert isinstance(project["id"], int)
        assert isinstance(project["partner_id"], int)
        assert isinstance(project["partner_name"], str)
        assert isinstance(project["is_closed"], bool)
        
        # Validar tipos en work_order
        wo = data["data"]["work_orders"][0]
        assert isinstance(wo["id"], int)
        assert isinstance(wo["series_code"], str)
        assert isinstance(wo["status"], str)
        assert isinstance(wo["service_type"], str)
        assert isinstance(wo["total_gallons"], int)
        assert isinstance(wo["total_barrels"], int)
        assert isinstance(wo["total_cubic_meters"], int)
        assert isinstance(wo["subtotal"], (int, float))
        assert isinstance(wo["tax_amount"], (int, float))
        assert isinstance(wo["total"], (int, float))
        assert isinstance(wo["custody_chains"], list)
        assert isinstance(wo["custody_chains_count"], int)
        assert isinstance(wo["metadata"], dict)
        
        # Validar tipos en custody_chain
        chain = wo["custody_chains"][0]
        assert isinstance(chain["id"], int)
        assert isinstance(chain["consecutive"], str)
        assert isinstance(chain["total_gallons"], int)
        assert isinstance(chain["total_barrels"], int)
        assert isinstance(chain["total_cubic_meters"], int)
        assert isinstance(chain["details"], list)
        assert isinstance(chain["details_count"], int)
        assert isinstance(chain["metadata"], dict)
        
        # Validar tipos en metadata
        assert isinstance(chain["metadata"]["is_active"], bool)
        assert isinstance(chain["metadata"]["is_deleted"], bool)
