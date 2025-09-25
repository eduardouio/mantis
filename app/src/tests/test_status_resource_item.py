"""
Tests para la clase StatusResourceItem

Estos tests verifican el correcto funcionamiento de la verificación
y limpieza del estado de equipos.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from equipment.models.ResourceItem import ResourceItem
from projects.models.Project import Project, ProjectResourceItem
from projects.models.Partner import Partner  # Asumiendo que existe
from common.StatusResourceItem import StatusResourceItem


class StatusResourceItemTestCase(TestCase):
    """Tests para StatusResourceItem."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        
        # Crear un partner de prueba (si no existe el modelo, ajustar)
        try:
            from projects.models.Partner import Partner
            self.partner = Partner.objects.create(
                name="Cliente de Prueba",
                contact_email="test@example.com",
                contact_phone="1234567890"
            )
        except ImportError:
            # Si no existe el modelo Partner, usar un mock o None
            self.partner = None
        
        # Crear proyecto de prueba
        self.project = Project.objects.create(
            partner=self.partner,
            location="Campamento Norte",
            contact_name="Juan Pérez",
            contact_phone="0987654321",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_closed=False
        )
        
        # Crear equipo de prueba - Lavamanos
        self.lavamanos = ResourceItem.objects.create(
            name="Lavamanos Portátil LV-001",
            code="LV-001",
            type_equipment="LVMNOS",
            brand="HigieneMax",
            model="LM-2000",
            serial_number="HM2000-001",
            height=120,
            width=80,
            depth=60,
            weight=45,
            capacity_gallons=50.0,
            # Checklist incompleto para pruebas
            have_foot_pumps=True,
            have_soap_dispenser=False,  # Falta
            have_napkin_dispenser=True,
            have_paper_towels=False,  # Falta
            # Estado inicial
            stst_status_equipment="FUNCIONANDO",
            stst_status_disponibility="DISPONIBLE"
        )
        
        # Crear equipo de servicio
        self.servicio = ResourceItem.objects.create(
            name="Servicio de Mantenimiento",
            code="SRV-001",
            is_service=True,
            stst_status_disponibility="DISPONIBLE"
        )
    
    def test_analisis_servicio(self):
        """Test: Los servicios siempre están completos."""
        
        analyzer = StatusResourceItem(self.servicio)
        report = analyzer.get_status_report()
        
        # Los servicios siempre están completos
        self.assertTrue(report['completeness']['is_complete'])
        self.assertEqual(report['completeness']['completion_percentage'], 100.0)
        self.assertEqual(len(report['completeness']['missing_items']), 0)
        
        # No deben tener inconsistencias
        self.assertFalse(report['inconsistencies']['needs_update'])
        self.assertEqual(len(report['inconsistencies']['found']), 0)
    
    def test_analisis_equipo_incompleto(self):
        """Test: Equipo con checklist incompleto."""
        
        analyzer = StatusResourceItem(self.lavamanos)
        report = analyzer.get_status_report()
        
        # El lavamanos debe estar incompleto (faltan 2 elementos)
        self.assertFalse(report['completeness']['is_complete'])
        self.assertEqual(len(report['completeness']['missing_items']), 2)
        self.assertLess(report['completeness']['completion_percentage'], 100.0)
        
        # Verificar que se identifican los elementos faltantes
        missing_fields = [item['field'] for item in report['completeness']['missing_items']]
        self.assertIn('have_soap_dispenser', missing_fields)
        self.assertIn('have_paper_towels', missing_fields)
    
    def test_equipo_disponible(self):
        """Test: Equipo disponible sin proyecto."""
        
        analyzer = StatusResourceItem(self.lavamanos)
        report = analyzer.get_status_report()
        
        # Debe estar disponible
        self.assertEqual(report['availability']['status'], 'DISPONIBLE')
        self.assertIsNone(report['project_info'])
        self.assertIsNone(report['rental_info'])
        
        # No debe tener inconsistencias de proyecto
        self.assertFalse(report['inconsistencies']['needs_update'])
    
    def test_equipo_rentado_con_proyecto_valido(self):
        """Test: Equipo rentado con proyecto válido."""
        
        # Configurar equipo como rentado
        self.lavamanos.stst_status_disponibility = "RENTADO"
        self.lavamanos.stst_current_project_id = self.project.id
        self.lavamanos.stst_current_location = "Campamento Norte"
        self.lavamanos.stst_commitment_date = date.today()
        self.lavamanos.stst_release_date = date.today() + timedelta(days=15)
        self.lavamanos.save()
        
        # Crear relación proyecto-recurso
        ProjectResourceItem.objects.create(
            project=self.project,
            resource_item=self.lavamanos,
            rent_cost=1500.00,
            maintenance_cost=200.00,
            maintenance_interval_days=7,
            operation_start_date=date.today(),
            operation_end_date=date.today() + timedelta(days=15)
        )
        
        analyzer = StatusResourceItem(self.lavamanos)
        report = analyzer.get_status_report()
        
        # Debe estar rentado
        self.assertEqual(report['availability']['status'], 'RENTADO')
        self.assertIsNotNone(report['project_info'])
        self.assertIsNotNone(report['rental_info'])
        
        # Información del proyecto
        project_info = report['project_info']
        self.assertEqual(project_info['project_id'], self.project.id)
        self.assertEqual(project_info['contact_name'], 'Juan Pérez')
        self.assertFalse(project_info['is_closed'])
        
        # Información de renta
        rental_info = report['rental_info']
        self.assertTrue(rental_info['is_currently_rented'])
        self.assertEqual(rental_info['rental_status'], 'ACTIVO')
        self.assertGreater(rental_info['remaining_days'], 0)
        
        # No debe tener inconsistencias
        self.assertFalse(report['inconsistencies']['needs_update'])
    
    def test_inconsistencia_rentado_sin_proyecto(self):
        """Test: Equipo marcado como rentado pero sin proyecto válido."""
        
        # Configurar equipo como rentado sin proyecto válido
        self.lavamanos.stst_status_disponibility = "RENTADO"
        self.lavamanos.stst_current_project_id = 99999  # ID inexistente
        self.lavamanos.save()
        
        analyzer = StatusResourceItem(self.lavamanos)
        report = analyzer.get_status_report()
        
        # Debe detectar inconsistencia
        self.assertTrue(report['inconsistencies']['needs_update'])
        self.assertGreater(len(report['inconsistencies']['found']), 0)
        
        # Verificar tipo de inconsistencia
        inconsistency_types = [inc['type'] for inc in report['inconsistencies']['found']]
        self.assertIn('NO_VALID_PROJECT', inconsistency_types)
    
    def test_correccion_automatica(self):
        """Test: Corrección automática de inconsistencias."""
        
        # Configurar equipo con inconsistencia
        self.lavamanos.stst_status_disponibility = "RENTADO"
        self.lavamanos.stst_current_project_id = 99999  # ID inexistente
        self.lavamanos.stst_current_location = "Ubicación Inválida"
        self.lavamanos.save()
        
        analyzer = StatusResourceItem(self.lavamanos)
        
        # Verificar que hay inconsistencias
        report_antes = analyzer.get_status_report()
        self.assertTrue(report_antes['inconsistencies']['needs_update'])
        
        # Aplicar corrección automática
        update_result = analyzer.update_equipment_status()
        
        # Verificar que se realizaron actualizaciones
        self.assertTrue(update_result['updated'])
        self.assertGreater(len(update_result['updates_made']), 0)
        
        # Verificar estado después de la corrección
        report_despues = analyzer.get_status_report()
        self.assertFalse(report_despues['inconsistencies']['needs_update'])
        self.assertEqual(report_despues['availability']['status'], 'DISPONIBLE')
    
    def test_proyecto_cerrado(self):
        """Test: Equipo en proyecto cerrado."""
        
        # Cerrar el proyecto
        self.project.is_closed = True
        self.project.save()
        
        # Configurar equipo como rentado en proyecto cerrado
        self.lavamanos.stst_status_disponibility = "RENTADO"
        self.lavamanos.stst_current_project_id = self.project.id
        self.lavamanos.save()
        
        analyzer = StatusResourceItem(self.lavamanos)
        report = analyzer.get_status_report()
        
        # Debe detectar inconsistencia de proyecto cerrado
        self.assertTrue(report['inconsistencies']['needs_update'])
        inconsistency_types = [inc['type'] for inc in report['inconsistencies']['found']]
        self.assertIn('CLOSED_PROJECT', inconsistency_types)
    
    def test_metodo_clase_analyze_equipment(self):
        """Test: Método de clase para análisis por ID."""
        
        report = StatusResourceItem.analyze_equipment(self.lavamanos.id)
        
        # Debe retornar reporte válido
        self.assertIn('equipment_info', report)
        self.assertIn('completeness', report)
        self.assertIn('availability', report)
        self.assertEqual(report['equipment_info']['id'], self.lavamanos.id)
    
    def test_equipo_inexistente(self):
        """Test: Análisis de equipo inexistente."""
        
        report = StatusResourceItem.analyze_equipment(99999)
        
        # Debe retornar error
        self.assertTrue(report.get('error', False))
        self.assertIn('message', report)
    
    def test_recomendaciones(self):
        """Test: Generación de recomendaciones."""
        
        analyzer = StatusResourceItem(self.lavamanos)
        report = analyzer.get_status_report()
        
        # Debe tener recomendaciones
        self.assertGreater(len(report['recommendations']), 0)
        
        # Como el equipo está incompleto, debe recomendar completar checklist
        recommendations_text = ' '.join(report['recommendations'])
        self.assertIn('checklist', recommendations_text.lower())


class StatusResourceItemIntegrationTestCase(TestCase):
    """Tests de integración para múltiples equipos."""
    
    def setUp(self):
        """Crear múltiples equipos para pruebas de integración."""
        
        # Crear varios equipos con diferentes estados
        self.equipos = []
        
        for i in range(5):
            equipo = ResourceItem.objects.create(
                name=f"Equipo Test {i+1}",
                code=f"TEST-{i+1:03d}",
                type_equipment="LVMNOS",
                brand="TestBrand",
                stst_status_equipment="FUNCIONANDO",
                stst_status_disponibility="DISPONIBLE"
            )
            self.equipos.append(equipo)
        
        # Crear algunos con inconsistencias
        self.equipos[2].stst_status_disponibility = "RENTADO"
        self.equipos[2].stst_current_project_id = 99999  # Inexistente
        self.equipos[2].save()
        
        self.equipos[3].stst_status_disponibility = "RENTADO"
        self.equipos[3].stst_current_project_id = 99998  # Inexistente
        self.equipos[3].save()
    
    def test_analisis_masivo(self):
        """Test: Análisis masivo de equipos."""
        
        # Obtener IDs de los equipos de prueba
        equipment_ids = [equipo.id for equipo in self.equipos]
        
        # Realizar análisis masivo
        results = StatusResourceItem.bulk_analyze_and_clean(equipment_ids)
        
        # Verificar resultados
        self.assertEqual(results['total_analyzed'], 5)
        self.assertEqual(results['equipments_with_issues'], 2)  # Los 2 con inconsistencias
        self.assertEqual(results['equipments_updated'], 2)  # Se deben corregir automáticamente
        
        # Verificar que se generaron reportes para todos
        self.assertEqual(len(results['summary']), 5)
        self.assertEqual(len(results['detailed_reports']), 5)


if __name__ == '__main__':
    """
    Para ejecutar estos tests:
    
    python manage.py test common.tests.test_status_resource_item
    
    O si el archivo está en el directorio tests:
    python manage.py test tests.test_status_resource_item
    """
    pass