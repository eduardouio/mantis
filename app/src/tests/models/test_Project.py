import pytest
from datetime import date
from decimal import Decimal
from projects.models.Project import Project, ProjectResourceItem
from projects.models.Partner import Partner
from equipment.models.ResourceItem import ResourceItem


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
            contact_phone='0987654321',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            location='Campamento Norte',
            cardinal_point='NORTE'
        )
        assert project.partner == partner
        assert project.contact_name == 'Juan Pérez'
        assert project.contact_phone == '0987654321'
        assert project.start_date == date(2024, 1, 1)
        assert project.end_date == date(2024, 12, 31)
        assert not project.is_closed
        assert project.location == 'Campamento Norte'
        assert project.cardinal_point == 'NORTE'

    def test_create_project_minimal_data(self):
        """Test de creación de proyecto con datos mínimos requeridos"""
        partner = Partner.objects.create(
            business_tax_id='2345678901001',
            name='Cliente Mínimo',
            address='Dirección Mínima'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='María García',
            contact_phone='0976543210',
            start_date=date(2024, 6, 1)
        )

        assert project.partner == partner
        assert project.contact_name == 'María García'
        assert project.end_date is None
        assert project.is_closed is False
        assert project.location is None
        assert project.cardinal_point is None

    def test_project_str_method(self):
        """Test del método __str__ del modelo Project"""
        partner = Partner.objects.create(
            business_tax_id='3456789012001',
            name='Cliente String',
            address='Dirección String'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='Carlos López',
            contact_phone='0965432109',
            start_date=date(2024, 1, 1)
        )
        
        expected_str = f'Proyecto {project.id} - {partner.name}'
        assert str(project) == expected_str

    def test_project_closed_status(self):
        partner = Partner.objects.create(
            business_tax_id='4567890123001',
            name='Cliente Cerrado',
            address='Dirección Cerrado'
        )
        project = Project.objects.create(
            partner=partner,
            contact_name='Luis Rodríguez',
            contact_phone='0954321098',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_closed=True
        )
        assert project.is_closed

    def test_project_cardinal_point_choices(self):
        """Test de las opciones válidas para punto cardinal"""
        partner = Partner.objects.create(
            business_tax_id='5678901234001',
            name='Cliente Cardinal',
            address='Dirección Cardinal'
        )
        
        valid_points = ['NORTE', 'SUR', 'ESTE', 'OESTE', 'NORESTE', 'NOROESTE', 'SURESTE', 'SUROESTE']
        
        for point in valid_points:
            project = Project.objects.create(
                partner=partner,
                contact_name='Test User',
                contact_phone='0987654321',
                start_date=date(2024, 1, 1),
                cardinal_point=point
            )
            assert project.cardinal_point == point
            project.delete()


@pytest.mark.django_db
class TestProjectResourceItem:

    @pytest.fixture
    def partner(self):
        return Partner.objects.create(
            business_tax_id='6789012345001',
            name='Cliente Recursos',
            address='Dirección Recursos'
        )

    @pytest.fixture
    def project(self, partner):
        return Project.objects.create(
            partner=partner,
            contact_name='Ana López',
            contact_phone='0943210987',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )

    @pytest.fixture
    def resource(self):
        return ResourceItem.objects.create(
            name='Bomba de Agua',
            code='BOMBA-001'
        )

    def test_create_project_resource_item_day_frequency(self, project, resource):
        """Test de creación de recurso con frecuencia por días"""
        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            type_resource='EQUIPO',
            cost=Decimal('1500.00'),
            frequency_type='DAY',
            interval_days=2,
            operation_start_date=date(2024, 1, 15),
            operation_end_date=date(2024, 12, 15)
        )

        assert project_resource.project == project
        assert project_resource.resource_item == resource
        assert project_resource.type_resource == 'EQUIPO'
        assert project_resource.cost == Decimal('1500.00')
        assert project_resource.frequency_type == 'DAY'
        assert project_resource.interval_days == 2
        assert not project_resource.is_retired

    def test_create_project_resource_item_week_frequency(self, project, resource):
        """Test de creación de recurso con frecuencia por días de la semana"""
        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            type_resource='SERVICIO',
            cost=Decimal('2000.00'),
            frequency_type='WEEK',
            weekdays=[0, 2, 4],  # Lunes, Miércoles, Viernes
            operation_start_date=date(2024, 1, 1),
            operation_end_date=date(2024, 12, 31)
        )

        assert project_resource.frequency_type == 'WEEK'
        assert project_resource.weekdays == [0, 2, 4]
        assert project_resource.monthdays is None

    def test_create_project_resource_item_month_frequency(self, project, resource):
        """Test de creación de recurso con frecuencia por días del mes"""
        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            type_resource='SERVICIO',
            cost=Decimal('2500.00'),
            frequency_type='MONTH',
            monthdays=[1, 15, 28],
            operation_start_date=date(2024, 1, 1),
            operation_end_date=date(2024, 12, 31)
        )

        assert project_resource.frequency_type == 'MONTH'
        assert project_resource.monthdays == [1, 15, 28]
        assert project_resource.weekdays is None

    def test_project_resource_str_method(self, project, resource):
        """Test del método __str__ del modelo ProjectResourceItem"""
        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            cost=Decimal('1000.00'),
            operation_start_date=date(2024, 1, 1)
        )

        expected_str = f'{project.partner.name} - {resource.name}'
        assert str(project_resource) == expected_str

    def test_retire_project_resource(self, project, resource):
        """Test de retiro de recurso del proyecto"""
        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            cost=Decimal('1500.00'),
            operation_start_date=date(2024, 1, 1)
        )

        # Retirar el recurso
        project_resource.is_retired = True
        project_resource.retirement_date = date(2024, 6, 30)
        project_resource.retirement_reason = 'Fin de contrato'
        project_resource.save()

        assert project_resource.is_retired
        assert project_resource.retirement_date == date(2024, 6, 30)
        assert project_resource.retirement_reason == 'Fin de contrato'

    def test_get_by_project(self, project, partner):
        """Test del método get_by_project"""
        resource1 = ResourceItem.objects.create(
            name='Recurso 1',
            code='REC-001'
        )
        resource2 = ResourceItem.objects.create(
            name='Recurso 2',
            code='REC-002'
        )

        # Crear recursos para el proyecto
        pr1 = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource1,
            cost=Decimal('1000.00'),
            operation_start_date=date(2024, 1, 1)
        )
        pr2 = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource2,
            cost=Decimal('2000.00'),
            operation_start_date=date(2024, 1, 1)
        )

        # Crear recurso marcado como eliminado
        pr3 = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource1,
            cost=Decimal('1500.00'),
            operation_start_date=date(2024, 2, 1),
            is_deleted=True
        )

        # Obtener recursos del proyecto
        resources = ProjectResourceItem.get_by_project(project.id)

        assert resources.count() == 2
        assert pr1 in resources
        assert pr2 in resources
        assert pr3 not in resources

    def test_delete_forever(self, project, resource):
        """Test del método delete_forever"""
        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            cost=Decimal('1000.00'),
            operation_start_date=date(2024, 1, 1)
        )

        resource_id = project_resource.id

        # Verificar que existe
        assert ProjectResourceItem.objects.filter(id=resource_id).exists()

        # Eliminar permanentemente
        ProjectResourceItem.delete_forever(resource_id)

        # Verificar que ya no existe
        assert not ProjectResourceItem.objects.filter(id=resource_id).exists()

    def test_project_resource_type_choices(self, project, resource):
        """Test de las opciones válidas para tipo de recurso"""
        # Tipo EQUIPO
        pr_equipo = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            type_resource='EQUIPO',
            cost=Decimal('1000.00'),
            operation_start_date=date(2024, 1, 1)
        )
        assert pr_equipo.type_resource == 'EQUIPO'

        # Tipo SERVICIO
        resource2 = ResourceItem.objects.create(
            name='Servicio Test',
            code='SERV-001'
        )
        pr_servicio = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource2,
            type_resource='SERVICIO',
            cost=Decimal('2000.00'),
            operation_start_date=date(2024, 1, 1)
        )
        assert pr_servicio.type_resource == 'SERVICIO'

    def test_project_resource_detailed_description(self, project, resource):
        """Test del campo detailed_description"""
        description = 'Bomba de agua para uso en campamento norte'
        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            detailed_description=description,
            cost=Decimal('1500.00'),
            operation_start_date=date(2024, 1, 1)
        )

        assert project_resource.detailed_description == description

    def test_project_resource_default_values(self, project, resource):
        """Test de valores por defecto del modelo"""
        project_resource = ProjectResourceItem.objects.create(
            project=project,
            resource_item=resource,
            operation_start_date=date(2024, 1, 1)
        )

        assert project_resource.type_resource == 'SERVICIO'
        assert project_resource.cost == Decimal('0.00')
        assert project_resource.frequency_type == 'DAY'
        assert project_resource.interval_days == 2
        assert project_resource.is_retired is False
        assert project_resource.retirement_date is None
        assert project_resource.retirement_reason is None
