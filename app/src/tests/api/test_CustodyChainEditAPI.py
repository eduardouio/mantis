from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, time
from decimal import Decimal
import json
import uuid

from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.SheetProject import SheetProject
from projects.models.Project import Project, ProjectResourceItem
from accounts.models.Technical import Technical
from equipment.models.Vehicle import Vehicle
from equipment.models.ResourceItem import ResourceItem
from projects.models.Partner import Partner


class CustodyChainEditAPITest(TestCase):
    """Tests para el endpoint de edición de cadenas de custodia."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        
        # Generar identificadores únicos para evitar conflictos
        unique_suffix = str(uuid.uuid4())[:8]
        
        # Crear partner
        self.partner = Partner.objects.create(
            name=f"TEST-ARCOLANDS-{unique_suffix}",
            email=f"test-{unique_suffix}@arcolands.com"
        )
        
        # Crear proyecto
        self.project = Project.objects.create(
            partner=self.partner,
            location=f"TEST-MDC-{unique_suffix}",
            cardinal_point=None,
            contact_name="TEST Ing. Catalina Velandia",
            contact_phone="+593900000000",
            start_date=date(2025, 1, 1),
            end_date=None,
            is_closed=False
        )
        
        # Crear hoja de proyecto (work order)
        self.sheet_project = SheetProject.objects.create(
            project=self.project,
            issue_date=None,
            period_start=date(2026, 1, 1),
            period_end=None,
            status="IN_PROGRESS",
            series_code=f"TEST-{unique_suffix}-1001",
            secuence_prefix="TST-PS",
            secuence_year=2026,
            secuence_number=int(unique_suffix[:4], 16),  # Número único basado en UUID
            service_type="ALQUILER Y MANTENIMIENTO",
            contact_reference="TEST Ing. Catalina Velandia",
            contact_phone_reference="+593900000000",
            total_gallons=0,
            total_barrels=0,
            total_cubic_meters=0,
            subtotal=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total=Decimal("0.00")
        )
        
        # Crear técnico
        self.technical = Technical.objects.create(
            first_name="TEST JINSON",
            last_name=f"CEDENO-{unique_suffix}",
            email=f"test-jinson-{unique_suffix}@test.com",
            dni=f"99{unique_suffix[:8]}",
            nro_phone="0900000000",
            work_area="PLANT_PROJECTS"
        )
        
        # Crear vehículos con placas únicas
        self.vehicle_1 = Vehicle.objects.create(
            brand="FOTON",
            model="TEST AUMARCK",
            type_vehicle="CAMION",
            year=2020,
            no_plate=f"T{unique_suffix[:6].upper()}",  # Placa única
            status_vehicle="DISPONIBLE"
        )
        
        self.vehicle_2 = Vehicle.objects.create(
            brand="JAC",
            model="TEST HFC1040",
            type_vehicle="CAMION",
            year=2021,
            no_plate=f"X{unique_suffix[:6].upper()}",  # Placa única diferente
            status_vehicle="DISPONIBLE"
        )
        
        # Crear recurso
        self.resource_item = ResourceItem.objects.create(
            name=f"TEST Mantenimiento-{unique_suffix}",
            code=f"TST-{unique_suffix[:6]}",
            type_equipment="SERVICIO"
        )
        
        # Crear project resources (varios para simular el caso real)
        self.project_resources = []
        for i in range(1, 10):
            pr = ProjectResourceItem.objects.create(
                project=self.project,
                resource_item=self.resource_item,
                type_resource="SERVICIO",
                detailed_description=f"TEST Mantenimiento Equipo {i} - {unique_suffix}",
                cost=Decimal("100.00"),
                operation_start_date=date(2026, 1, 1)
            )
            self.project_resources.append(pr)
        
        # Crear cadena de custodia inicial (similar a la del JSON)
        self.custody_chain = CustodyChain.objects.create(
            technical=self.technical,
            vehicle=self.vehicle_1,
            sheet_project=self.sheet_project,
            consecutive=f"T{unique_suffix[:6]}",
            activity_date=date(2026, 1, 24),
            location=f"TEST-MDC-{unique_suffix}",
            issue_date=date(2026, 1, 24),
            start_time=time(10, 2),
            end_time=time(14, 3),
            time_duration=Decimal("240.00"),
            contact_name="TEST Ing. Catalina Velandia",
            dni_contact="",
            contact_position="",
            date_contact=date(2026, 1, 24),
            driver_name=f"TEST JINSON CEDENO-{unique_suffix}",
            dni_driver=f"99{unique_suffix[:8]}",
            driver_position="TEST Proyectos de Plantas",
            driver_date=date(2026, 1, 24),
            total_gallons=200,
            total_barrels=4,
            total_cubic_meters=0
        )
        
        # Crear detalles iniciales (4 recursos como en el JSON)
        self.details = []
        for i in range(4):
            detail = ChainCustodyDetail.objects.create(
                custody_chain=self.custody_chain,
                project_resource=self.project_resources[i]
            )
            self.details.append(detail)

    def test_update_custody_chain_put_success(self):
        """Test actualizar cadena de custodia completa (PUT)."""
        data = {
            "custody_chain": {
                "technical_id": self.technical.id,
                "vehicle_id": self.vehicle_2.id,  # Cambiar vehículo
                "activity_date": "2026-01-25",
                "location": "MDC 40 / Sacha",
                "start_time": "11:54:00",
                "end_time": "16:54:00",
                "time_duration": "300.00",
                "contact_name": "Ing. Catalina Velandia",
                "dni_contact": "",
                "total_gallons": 250,
                "total_barrels": 5,
                "total_cubic_meters": 1,
                "meta": {
                    "notes": "Actualización de cadena de custodia",
                    "id_user_updated": 7
                }
            },
            "details": [
                {
                    "id": self.details[0].id,
                    "project_resource_id": self.project_resources[0].id
                },
                {
                    "id": self.details[1].id,
                    "project_resource_id": self.project_resources[1].id
                },
                {
                    "project_resource_id": self.project_resources[4].id  # Agregar nuevo
                },
                {
                    "project_resource_id": self.project_resources[5].id  # Agregar nuevo
                }
            ]
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # Verificar actualización en BD
        self.custody_chain.refresh_from_db()
        self.assertEqual(self.custody_chain.vehicle.id, self.vehicle_2.id)
        self.assertEqual(self.custody_chain.total_gallons, 250)
        self.assertEqual(self.custody_chain.total_barrels, 5)
        self.assertEqual(self.custody_chain.time_duration, Decimal("300.00"))
        
        # Verificar detalles (2 mantenidos + 2 nuevos = 4 total)
        details = ChainCustodyDetail.objects.filter(
            custody_chain=self.custody_chain,
            is_active=True
        )
        self.assertEqual(details.count(), 4)

    def test_update_custody_chain_patch_partial(self):
        """Test actualizar parcialmente cadena de custodia (PATCH)."""
        data = {
            "custody_chain": {
                "location": "TEST Cuenca",
                "total_gallons": 200
            }
        }
        
        response = self.client.patch(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.custody_chain.refresh_from_db()
        self.assertEqual(self.custody_chain.location, "TEST Cuenca")
        self.assertEqual(self.custody_chain.total_gallons, 200)
        # Verificar que otros campos no cambiaron
        self.assertEqual(self.custody_chain.contact_name, "TEST Ing. Catalina Velandia")

    def test_update_custody_chain_remove_detail(self):
        """Test eliminar detalle de cadena de custodia (soft delete)."""
        data = {
            "custody_chain": {},
            "details": []  # Sin detalles, se eliminan todos
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar soft delete del primer detalle
        self.details[0].refresh_from_db()
        self.assertFalse(self.details[0].is_active)
        
        # Verificar que no hay detalles activos
        active_details = ChainCustodyDetail.objects.filter(
            custody_chain=self.custody_chain,
            is_active=True
        )
        self.assertEqual(active_details.count(), 0)

    def test_update_custody_chain_add_new_detail(self):
        """Test agregar nuevo detalle a cadena existente."""
        data = {
            "custody_chain": {},
            "details": [
                {
                    "id": self.details[0].id,
                    "project_resource_id": self.project_resources[0].id
                },
                {
                    "project_resource_id": self.project_resources[4].id
                }
            ]
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        details = ChainCustodyDetail.objects.filter(
            custody_chain=self.custody_chain,
            is_active=True
        )
        self.assertEqual(details.count(), 2)

    def test_update_custody_chain_not_found(self):
        """Test actualizar cadena de custodia inexistente."""
        data = {
            "custody_chain": {
                "location": "Test"
            }
        }
        
        response = self.client.put(
            '/api/workorders/custody_chain/99999/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('no encontrada', response_data['error'])

    def test_update_custody_chain_invalid_json(self):
        """Test actualizar con JSON inválido."""
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('inválido', response_data['error'])

    def test_update_custody_chain_invalid_technical(self):
        """Test actualizar con técnico inexistente."""
        data = {
            "custody_chain": {
                "technical_id": 99999
            }
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('Técnico', response_data['error'])

    def test_update_custody_chain_invalid_vehicle(self):
        """Test actualizar con vehículo inexistente."""
        data = {
            "custody_chain": {
                "vehicle_id": 99999
            }
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('Vehículo', response_data['error'])

    def test_update_custody_chain_null_technical_vehicle(self):
        """Test actualizar removiendo técnico y vehículo (NULL permitido)."""
        data = {
            "custody_chain": {
                "technical_id": None,
                "vehicle_id": None
            }
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.custody_chain.refresh_from_db()
        self.assertIsNone(self.custody_chain.technical)
        self.assertIsNone(self.custody_chain.vehicle)

    def test_update_custody_chain_with_date_parsing(self):
        """Test parseo correcto de fechas y horas."""
        data = {
            "custody_chain": {
                "activity_date": "2024-02-15",
                "issue_date": "2024-02-15",
                "start_time": "10:30:00",
                "end_time": "19:45:00",
                "date_contact": "2024-02-16",
                "driver_date": "2024-02-17"
            }
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.custody_chain.refresh_from_db()
        self.assertEqual(self.custody_chain.activity_date, date(2024, 2, 15))
        self.assertEqual(self.custody_chain.start_time, time(10, 30, 0))
        self.assertEqual(self.custody_chain.end_time, time(19, 45, 0))

    def test_update_custody_chain_replace_detail(self):
        """Test reemplazar detalle existente por otro recurso."""
        data = {
            "custody_chain": {},
            "details": [
                {
                    "id": self.details[0].id,
                    "project_resource_id": self.project_resources[5].id
                }
            ]
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.details[0].refresh_from_db()
        self.assertEqual(self.details[0].project_resource, self.project_resources[5])

    def test_update_custody_chain_metadata(self):
        """Test actualizar metadatos de la cadena."""
        data = {
            "custody_chain": {
                "meta": {
                    "notes": "Notas actualizadas",
                    "id_user_updated": 5
                }
            }
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.custody_chain.refresh_from_db()
        self.assertEqual(self.custody_chain.notes, "Notas actualizadas")
        self.assertEqual(self.custody_chain.id_user_updated, 5)

    def test_update_custody_chain_invalid_project_resource(self):
        """Test actualizar con recurso de proyecto inexistente."""
        data = {
            "custody_chain": {},
            "details": [
                {
                    "project_resource_id": 99999
                }
            ]
        }
        
        response = self.client.put(
            f'/api/workorders/custody_chain/{self.custody_chain.id}/edit/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Debe ser exitoso pero ignorar el detalle inválido
        self.assertEqual(response.status_code, 200)
