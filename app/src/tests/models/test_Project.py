import pytest
from datetime import date
from decimal import Decimal
from projects.models.Project import (
    Project, ProjectResourceItem, WorkOrder
)
from projects.models.Partner import Partner
from equipment.models.ResourceItem import ResourceItem
from accounts.models.Technical import Technical


@pytest.mark.django_db
class TestProject:

    def test_create_project(self):
        partner = Partner.objects.create(
            business_tax_id='1234567890001',
            name='Cliente Test',
            address='Dirección Test'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='Juan Pérez',
            phone_contact='0987654321',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            place='Campamento Norte',
            avrebiature='CN'
        )
        assert project.partner == partner
        assert project.contact_name == 'Juan Pérez'
        assert project.phone_contact == '0987654321'
        assert project.start_date == date(2024, 1, 1)
        assert project.end_date == date(2024, 12, 31)
        assert not project.is_closed

    def test_get_project_by_id_existing(self):
        partner = Partner.objects.create(
            business_tax_id='2345678901001',
            name='Cliente 2',
            address='Dirección 2'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='María García',
            phone_contact='0976543210',
            start_date=date(2024, 6, 1),
            end_date=date(2024, 11, 30)
        )

        found_project = Project.get_project_by_id(project.id)
        assert found_project == project
        assert found_project.contact_name == 'María García'

    def test_get_project_by_id_non_existing(self):
        result = Project.get_project_by_id(999)
        assert result is None

    def test_project_closed_status(self):
        partner = Partner.objects.create(
            business_tax_id='3456789012001',
            name='Cliente Cerrado',
            address='Dirección Cerrado'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='Luis Rodríguez',
            phone_contact='0965432109',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_closed=True
        )
        assert project.is_closed


@pytest.mark.django_db
class TestProjectResourceItem:

    def test_create_project_resource_item(self):
        partner = Partner.objects.create(
            business_tax_id='4567890123001',
            name='Cliente Equipo',
            address='Dirección Equipo'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='Ana López',
            phone_contact='0954321098',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        resource = ResourceItem.objects.create(
            name='Bomba de Agua',
            code='BOMBA-001',
            status='DISPONIBLE'
        )

        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            cost=Decimal('1500.00'),
            cost_manteinance=Decimal('200.00'),
            mantenance_frequency='MENSUAL',
            times_mantenance=12,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 12, 15)
        )

        assert project_resource.project == project
        assert project_resource.resource_item == resource
        assert project_resource.cost == Decimal('1500.00')
        assert project_resource.mantenance_frequency == 'MENSUAL'
        assert project_resource.times_mantenance == 12

    def test_project_resource_unique_together(self):
        partner = Partner.objects.create(
            business_tax_id='5678901234001',
            name='Cliente Único',
            address='Dirección Único'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='Carlos Martínez',
            phone_contact='0943210987',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        resource = ResourceItem.objects.create(
            name='Generador',
            code='GEN-001',
            status='DISPONIBLE'
        )
        
        ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            cost=Decimal('2000.00'),
            cost_manteinance=Decimal('300.00'),
            mantenance_frequency='TRIMESTRAL',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
         # Should raise IntegrityError for duplicate project-resource
        with pytest.raises(Exception):
            ProjectResourceItem.objects.create(
                project=project,
                resource_item=resource,
                cost=Decimal('2500.00'),
                cost_manteinance=Decimal('350.00'),
                mantenance_frequency='MENSUAL',
                start_date=date(2024, 2, 1),
                end_date=date(2024, 11, 30)
            )


@pytest.mark.django_db
class TestWorkOrder:
    
    def test_create_work_order(self):
        partner = Partner.objects.create(
            business_tax_id='6789012345001',
            name='Cliente Orden',
            address='Dirección Orden'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='Pedro González',
            phone_contact='0932109876',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        technical = Technical.objects.create(
            first_name='Técnico',
            last_name='Responsable',
            dni='1234567890',
            nro_phone='0987654321'
        )
        
        work_order = WorkOrder.objects.create(
            project=project,
            work_order='WO-001-2024',
            tecnical=technical,
            date=date(2024, 6, 15)
        )
        
        assert work_order.project == project
        assert work_order.work_order == 'WO-001-2024'
        assert work_order.tecnical == technical
        assert work_order.date == date(2024, 6, 15)
        assert str(work_order) == 'WO-001-2024'

    def test_get_by_project(self):
        partner = Partner.objects.create(
            business_tax_id='7890123456001',
            name='Cliente Múltiples OT',
            address='Dirección Múltiples'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='Elena Ruiz',
            phone_contact='0921098765',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        technical = Technical.objects.create(
            first_name='Técnico',
            last_name='Múltiple',
            dni='0987654321',
            nro_phone='0976543210'
        )
        
        # Create active work orders
        wo1 = WorkOrder.objects.create(
            project=project,
            work_order='WO-001',
            tecnical=technical,
            date=date(2024, 6, 1),
            is_active=True
        )
        wo2 = WorkOrder.objects.create(
            project=project,
            work_order='WO-002',
            tecnical=technical,
            date=date(2024, 6, 15),
            is_active=True
        )
        
        # Create inactive work order
        WorkOrder.objects.create(
            project=project,
            work_order='WO-003',
            tecnical=technical,
            date=date(2024, 7, 1),
            is_active=False
        )
        
        active_orders = WorkOrder.get_by_project(project)
        assert len(active_orders) == 2
        assert wo1 in active_orders
        assert wo2 in active_orders
